; X-only motor demo.
; This file targets the X axis only.
; Run with:
; python serial_gcode_sender.py --port COM9 --file .\x_only_demo.gcode --monitor-seconds 5 --log-file .\x_only_demo.log

M115 ; Ask Marlin for firmware information.
M119 ; Report endstop states so you can see whether X is blocked.
M84 S5 ; Auto-disable steppers after 5 seconds of inactivity.
M211 S0 ; Disable software endstops for bench testing.
M17 X ; Enable only the X driver.
G91 ; Use relative positioning.
G92 X0 ; Set the current X position to zero for an easy reference.
G0 X10 F5000 ; Move X forward by 10 mm at 240 mm/min.
M400 ; Wait until all queued motion finishes.
M114 ; Report the current position.
G0 X-10 F1500 ; Move X backward by 10 mm.
M400 ; Wait until all queued motion finishes.
M114 ; Report the position again so you can confirm X returned.
M84 ; Disable the steppers.

