def on_forever():
    # 45 - 135 degrees
    angle = 45
    while angle <= 135:
        pins.servo_write_pin(AnalogPin.P0, angle)
        basic.pause(45)

        # Measuring distance
        dist = sonar.ping(DigitalPin.P2, DigitalPin.P1, PingUnit.CENTIMETERS)

        # Filtering
        if dist == 0 or dist > 80:
            dist = 80

        serial.write_line(str(angle) + "," + str(dist))
        angle += 2

    # Reverse
    angle = 134
    while angle >= 45:
        pins.servo_write_pin(AnalogPin.P0, angle)
        basic.pause(45)

        dist = sonar.ping(DigitalPin.P2, DigitalPin.P1, PingUnit.CENTIMETERS)

        if dist == 0 or dist > 80:
            dist = 80

        serial.write_line(str(angle) + "," + str(dist))
        angle -= 2

basic.forever(on_forever)