; Z-only motor demo.
; This file targets the Z axis only.
; Run with:
; python serial_gcode_sender.py --port COM9 --file .\z_only_demo.gcode --monitor-seconds 5 --log-file .\z_only_demo.log

M115 ; Ask Marlin for firmware information.
M119 ; Report endstop states so you can see whether Z is blocked.
M84 S5 ; Auto-disable steppers after 5 seconds of inactivity.
M211 S0 ; Disable software endstops for bench testing.
M17 Z ; Enable only the Z driver.
G91 ; Use relative positioning.
G92 Z0 ; Set the current Z position to zero for an easy reference.
G0 Z2 F120 ; Move Z up by 2 mm at 120 mm/min.
M400 ; Wait until all queued motion finishes.
M114 ; Report the current position.
G0 Z-2 F120 ; Move Z down by 2 mm.
M400 ; Wait until all queued motion finishes.
M114 ; Report the position again so you can confirm Z returned.
M84 ; Disable the steppers.

