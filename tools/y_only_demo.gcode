; Y-only motor demo.
; This file targets the Y axis only.
; Run with:
; python serial_gcode_sender.py --port COM9 --file .\y_only_demo.gcode --monitor-seconds 5 --log-file .\y_only_demo.log

M115 ; Ask Marlin for firmware information.
M119 ; Report endstop states so you can see whether Y is blocked.
M84 S5 ; Auto-disable steppers after 5 seconds of inactivity.
M211 S0 ; Disable software endstops for bench testing.
M17 Y ; Enable only the Y driver.
G91 ; Use relative positioning.
G92 Y0 ; Set the current Y position to zero for an easy reference.
G0 Y10 F240 ; Move Y forward by 10 mm at 240 mm/min.
M400 ; Wait until all queued motion finishes.
M114 ; Report the current position.
G0 Y-10 F240 ; Move Y backward by 10 mm.
M400 ; Wait until all queued motion finishes.
M114 ; Report the position again so you can confirm Y returned.
M84 ; Disable the steppers.

