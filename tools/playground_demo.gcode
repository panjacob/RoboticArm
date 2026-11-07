; Playground demo for MKS TinyBee.
; This file uses small relative moves so you can test one connected motor at a time.
; Run with:
; python serial_gcode_sender.py --port COM9 --file .\playground_demo.gcode --monitor-seconds 5 --log-file .\playground_demo.log

M115 ; Ask Marlin for firmware information.
M119 ; Report endstop states so you can see whether any switch is stuck triggered.
M302 P1 ; Allow extrusion moves without heating a hotend first.
M84 S5 ; Auto-disable steppers after 5 seconds of inactivity.
M211 S0 ; Disable software endstops so small bench-test moves are not blocked by configured limits.
M17 ; Enable / energize all stepper drivers.
G91 ; Switch to relative positioning so each move is measured from the current position.
G0 X10 F240 ; Move X forward by 10 mm at 240 mm/min.
G0 X-10 F240 ; Move X back by 10 mm to return to the starting point.
G0 Y10 F240 ; Move Y forward by 10 mm at 240 mm/min.
G0 Y-10 F240 ; Move Y back by 10 mm.
G0 Z2 F120 ; Move Z up by 2 mm at 120 mm/min.
G0 Z-2 F120 ; Move Z back down by 2 mm.
T0 ; Select tool / extruder 0.
G1 E10 F120 ; Move E0 forward by 10 mm at 120 mm/min.
G1 E-10 F120 ; Move E0 backward by 10 mm.
T1 ; Select tool / extruder 1.
G1 E10 F120 ; Move E1 forward by 10 mm at 120 mm/min.
G1 E-10 F120 ; Move E1 backward by 10 mm.
M114 ; Report the final logical position stored by Marlin.
M84 ; Disable all steppers so the motors stop holding torque.

