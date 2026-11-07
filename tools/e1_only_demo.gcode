; E1-only motor demo.
; This file targets the second extruder motor path only.
; Run with:
; python serial_gcode_sender.py --port COM9 --file .\e1_only_demo.gcode --monitor-seconds 5 --log-file .\e1_only_demo.log

M115 ; Ask Marlin for firmware information.
M84 S5 ; Auto-disable steppers after 5 seconds of inactivity.
M302 P1 ; Allow extrusion moves without heating a hotend.
T1 ; Select tool / extruder 1 so the next E moves drive E1.
M17 E ; Enable only the extruder driver(s).
G91 ; Use relative positioning for the E moves below.
G1 E10 F120 ; Move E1 forward by 10 mm at 120 mm/min.
M400 ; Wait until all queued motion finishes.
M114 ; Report the current position, including E.
G1 E-10 F120 ; Move E1 backward by 10 mm.
M400 ; Wait again until all motion is done.
M114 ; Report the position once more so you can confirm E returned.
M84 ; Disable the steppers.

