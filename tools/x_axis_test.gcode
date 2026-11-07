; Safe X-axis test for a single motor without homing.
M115 ; Ask Marlin for firmware information.
M119 ; Report endstop states so you can see whether X is blocked.
M84 S5 ; Auto-disable steppers after 5 seconds of inactivity.
M17 X ; Enable only the X driver.
M211 S0 ; Disable software endstops for bench testing.
G92 X0 ; Set the current X position to zero for an easy reference.
G91 ; Use relative positioning.
G0 X1000 F30000 ; Move X forward by 10 mm at 240 mm/min.
G0 X-10 F240 ; Move X backward by 10 mm.
M84 ; Disable the steppers.

