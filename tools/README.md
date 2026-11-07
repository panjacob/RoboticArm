# Serial motion tools

Python utilities for driving the MKS TinyBee (Marlin) over USB serial.

## Files

| File | Purpose |
|------|---------|
| `serial_gcode_sender.py` | Send single commands or a whole G-code file and print the board replies |
| `gamepad_motor_controller.py` | Jog one axis (X/Y/Z/E) with a gamepad analog stick |
| `x_axis_test.gcode` | Short X-axis test move without homing |
| `x_only_demo.gcode`, `y_only_demo.gcode`, `z_only_demo.gcode` | Single-axis demo moves |
| `e0_only_demo.gcode`, `e1_only_demo.gcode` | Single-extruder demo moves |
| `playground_demo.gcode` | Multi-axis demo |
| `requirements.txt` | Python dependencies (`pyserial`, `pygame`) |

## Requirements

- Python 3.9 or newer (tested with 3.12)
- The board connected over USB (CH340 USB-serial driver on Windows)
- For the gamepad tool: any controller recognised by SDL/pygame (Xbox, DualShock/DualSense, generic USB pads)

## Install

From the repository root:

```powershell
python -m venv tools\venv
tools\venv\Scripts\Activate.ps1
python -m pip install -r tools\requirements.txt
```

On Linux/macOS use `python3 -m venv tools/venv` and `source tools/venv/bin/activate`.

## Gamepad setup

1. Connect the gamepad (USB or Bluetooth) and make sure the OS sees it
   (Windows: run `joy.cpl` to check the axes move).
2. Connect the board over USB and find its serial port
   (Windows: Device Manager → *Ports (COM & LPT)*; Linux: `/dev/ttyUSB0`).
3. Close any other program that holds the port (Pronterface, PlatformIO monitor, Cura, ...).
4. Open `tools/gamepad_motor_controller.py` and edit the config block at the top:

   | Setting | Meaning |
   |---------|---------|
   | `SERIAL_PORT` | Board port, e.g. `"COM6"`. Set to `""` to only print commands (no board needed) |
   | `BAUD_RATE` | Must match `BAUDRATE` in `Marlin/Configuration.h` (default `115200`) |
   | `GAMEPAD_INDEX` | Which controller to use when several are connected (`0` = first) |
   | `STICK_AXIS` | Analog axis number: usually `0` = left stick X, `1` = left stick Y |
   | `INVERT_STICK` | Flip the direction |
   | `MOTOR_AXIS` | `"X"`, `"Y"`, `"Z"` or `"E"` |
   | `DEADZONE` | Ignore stick values below this (stick drift) |
   | `POLL_INTERVAL` | Seconds between moves |
   | `STEP_MM` | Distance per move at full stick deflection |
   | `FEEDRATE` | Move speed in mm/min |
   | `EXPO` | Response curve: `1.0` = linear, higher = finer control near the centre |

5. Run:

   ```powershell
   python tools\gamepad_motor_controller.py
   ```

6. Press `Ctrl+C` to stop.

The script sends `M17` (enable steppers) and `G91` (relative mode) on start.
Each poll sends a relative `G0` move; when the stick returns to centre it sends `M410` (quick stop).
On exit it sends `M410`, `G90` and `M84` (disable steppers).

> **Tip:** first run with `SERIAL_PORT = ""` and move the stick to confirm `STICK_AXIS` produces
> `G0` commands in the console, then start with a small `STEP_MM` (e.g. `0.5`) until direction and wiring are confirmed.

## Serial G-code sender examples

Read firmware info:

```powershell
python tools\serial_gcode_sender.py --port COM6 --command M115
```

Preview commands without opening the port:

```powershell
python tools\serial_gcode_sender.py --port COM6 --file tools\x_axis_test.gcode --dry-run
```

Run the built-in X-axis test and keep listening for 10 seconds:

```powershell
python tools\serial_gcode_sender.py --port COM6 --x-test --monitor-seconds 10
```

Send a file:

```powershell
python tools\serial_gcode_sender.py --port COM6 --file tools\playground_demo.gcode
```

Reset the board first and log the whole session:

```powershell
python tools\serial_gcode_sender.py --port COM6 --reset-on-connect --command M115 --log-file tools\last_session.log
```

Run `python tools\serial_gcode_sender.py --help` for all options.

## Notes

- None of the demo files home the machine. Make sure axes have room to move.
- The X test uses `M211 S0`, which disables software endstops.
- `*.log` files are git-ignored.
