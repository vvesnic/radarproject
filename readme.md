## System for Radar Detection

An obstacle detection radar system based on the BBC micro:bit microcontroller, 
an ultrasonic sensor, and a Python (Pygame) visual interface. 
The system scans the environment using a servo motor, processes angle and distance parameters, 
and displays detected targets on a radar screen.

### Key Features:

Real-time Scanning: 
Asynchronous serial communication (pySerial) between the micro:bit and PC at a 115200 baud rate.

Radar Interface: 
Graphical display featuring concentric distance rings (10–50 cm) and radial angle lines (0°–180°).

Target Detection & Visual Trail: 
Detected targets are rendered at exact coordinates along with a semi-transparent 
projection beam extending toward the outer edge of the radar.

Smooth Animation & Noise Filtering:
Motion-smoothing algorithm for the sweeping line (smooth_angle) paired with 
out-of-range measurement filtering.

Asynchronous Audio Alarm: 
Audio alert (winsound) triggered upon object detection within the target range, 
executed in a separate thread to maintain a stable 60 FPS.

HUD: 
Real-time display of the current azimuth (angle) in the bottom-left corner 
and live system status on-screen.

### Hardware Components:
Microcontroller: BBC micro:bit v1

Sensor: Ultrasonic HC-SR04/Sonar (Trigger: P1, Echo: P2)

Actuator: SG90 9G Micro Servo Motor (P0)