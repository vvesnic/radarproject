import pygame
import serial
import math
import sys
import winsound
import threading
import time

# --- SETTINGS ---
COM_PORT = 'COM3'
BAUD_RATE = 115200
MAX_DISTANCE = 50
MIN_DISTANCE = 10

BLACK = (10, 14, 20)
DARK_GRAY = (35, 45, 55)
GRAY = (120, 135, 150)
CYAN = (0, 215, 255)
DARK_GREEN = (0, 80, 40)
BRIGHT_GREEN = (0, 245, 120)
RED = (245, 40, 50)
RED_TRANSLUCENT = (245, 40, 50, 110)
WHITE = (240, 245, 250)

WIDTH, HEIGHT = 800, 500
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT - 50
RADIUS = 400

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("System for radar detection (UAV/SHM)")

font_main = pygame.font.SysFont('consolas', 18, bold=True)
font_small = pygame.font.SysFont('consolas', 12, bold=True)

# Memory for radar data
radar_memory = [MAX_DISTANCE + 1] * 181

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=0)
except Exception as e:
    print(f"Error due to opening port {COM_PORT}: {e}")
    sys.exit()

def draw_radar_background():
    screen.fill(BLACK)

    # Half-circles
    for r in range(100, RADIUS + 1, 100):
        pygame.draw.arc(screen, DARK_GRAY, (CENTER_X - r, CENTER_Y - r, r * 2, r * 2), 0, math.pi, 1)
        dist_val = int((r / RADIUS) * MAX_DISTANCE)
        dist_label = font_small.render(f"{dist_val}cm", True, GRAY)
        screen.blit(dist_label, (CENTER_X + 6, CENTER_Y - r - 8))

    for angle in [0, 30, 60, 90, 120, 150, 180]:
        rad = math.radians(180 - angle)
        x = CENTER_X + math.cos(rad) * RADIUS
        y = CENTER_Y - math.sin(rad) * RADIUS
        pygame.draw.line(screen, DARK_GRAY, (CENTER_X, CENTER_Y), (x, y), 1)

        text_x = CENTER_X + math.cos(rad) * (RADIUS + 22) - 10
        text_y = CENTER_Y - math.sin(rad) * (RADIUS + 22) - 8
        angle_label = font_small.render(f"{angle}°", True, CYAN)
        screen.blit(angle_label, (text_x, text_y))

# Asynchronous sound
last_beep_time = 0
beep_cooldown = 0.25

def play_beep_async(freq=850, duration=120):
    global last_beep_time
    now = time.time()
    if now - last_beep_time >= beep_cooldown:
        last_beep_time = now
        threading.Thread(target=winsound.Beep, args=(freq, duration), daemon=True).start()

running = True
target_angle = 0
smooth_angle = 0.0
current_distance = MAX_DISTANCE + 1

clock = pygame.time.Clock()
serial_buffer = ""

overlay_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Reading data from micro:bit
    if ser.in_waiting > 0:
        try:
            raw_data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            serial_buffer += raw_data

            while '\n' in serial_buffer:
                line, serial_buffer = serial_buffer.split('\n', 1)
                line = line.strip()

                if "," in line:
                    parts = line.split(',')
                    if len(parts) == 2:
                        try:
                            temp_angle = int(parts[0])
                            temp_distance = int(float(parts[1]))

                            # Angle validation
                            if 45 <= temp_angle <= 135:
                                target_angle = 180 - temp_angle
                                current_distance = temp_distance

                                # Noise filtering
                                if MIN_DISTANCE <= current_distance < MAX_DISTANCE:
                                    radar_memory[target_angle] = current_distance
                                else:
                                    radar_memory[target_angle] = MAX_DISTANCE + 1

                        except ValueError:
                            pass
        except Exception:
            pass

    smooth_angle += (target_angle - smooth_angle) * 0.15

    draw_radar_background()

    overlay_surface.fill((0, 0, 0, 0))

    # Target display
    for angle in range(181):
        dist = radar_memory[angle]
        if dist < MAX_DISTANCE:
            rad = math.radians(180 - angle)
            dist_scaled = (dist / MAX_DISTANCE) * RADIUS

            x_in = CENTER_X + math.cos(rad) * dist_scaled
            y_in = CENTER_Y - math.sin(rad) * dist_scaled

            x_out = CENTER_X + math.cos(rad) * RADIUS
            y_out = CENTER_Y - math.sin(rad) * RADIUS

            # Red pattern
            pygame.draw.line(overlay_surface, RED_TRANSLUCENT, (x_in, y_in), (x_out, y_out), 6)

            # Target itself
            pygame.draw.circle(screen, RED, (int(x_in), int(y_in)), 5)
            pygame.draw.circle(screen, WHITE, (int(x_in), int(y_in)), 2)

    screen.blit(overlay_surface, (0, 0))

    # Sweeping line
    rad_current = math.radians(180 - smooth_angle)
    x_line = CENTER_X + math.cos(rad_current) * RADIUS
    y_line = CENTER_Y - math.sin(rad_current) * RADIUS
    pygame.draw.line(screen, BRIGHT_GREEN, (CENTER_X, CENTER_Y), (x_line, y_line), 3)

    # HUD:
    current_angle_deg = int(round(smooth_angle))
    angle_text = font_main.render(f"AZIMUTH: {current_angle_deg:03d}°", True, CYAN)
    screen.blit(angle_text, (20, HEIGHT - 40))

    if MIN_DISTANCE <= current_distance < MAX_DISTANCE:
        dist_text = font_main.render(f"OBJECT DETECTED: {current_distance} cm", True, RED)
        pygame.draw.rect(screen, RED, (0, 0, WIDTH, HEIGHT), 3)
        play_beep_async(850, 120)
    else:
        dist_text = font_main.render(f"CLEAR. MAX RANGE: {MAX_DISTANCE} cm", True, BRIGHT_GREEN)

    screen.blit(dist_text, (WIDTH - 380, HEIGHT - 40))

    pygame.display.flip()
    clock.tick(60)

ser.close()
pygame.quit()