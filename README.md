# MKS TinyBee – Marlin firmware + gamepad motor control

Marlin 2.0.9.2 configured for the **MKS TinyBee** (ESP32) board, plus Python tools to
send G-code over USB and jog motors with a gamepad.

## Repository layout

| Path | Contents |
|------|----------|
| `Marlin/` | Firmware source. Machine settings live in `Marlin/Configuration.h` and `Marlin/Configuration_adv.h` |
| `platformio.ini`, `ini/` | PlatformIO build configuration (default env: `mks_tinybee`) |
| `buildroot/` | Marlin build scripts and helpers |
| `tools/` | Python serial / gamepad tools – see [tools/README.md](tools/README.md) |

## What you need

### Hardware

- MKS TinyBee board (ESP32, 5× TMC2209 in standalone mode by default)
- USB cable (the board uses a CH340 USB-serial chip)
- 12–24 V power supply for the motors
- Stepper motors connected to X / Y / Z / E0 / E1
- A gamepad (Xbox, PlayStation or generic USB/Bluetooth controller) for the gamepad tool

### Software

- [Python 3.9+](https://www.python.org/downloads/) (tested with 3.12)
- [VS Code](https://code.visualstudio.com/) with the **PlatformIO IDE** extension
  (or PlatformIO Core: `pip install platformio`)
- [CH340 driver](https://www.wch-ic.com/downloads/CH341SER_EXE.html) on Windows if the board does not show up as a COM port

## 1. Build and flash the firmware

1. Open the repository folder in VS Code; PlatformIO will download the ESP32 toolchain on first open.
2. Adjust `Marlin/Configuration.h` if needed (steps/mm, driver types, endstops, `BAUDRATE`, ...).
3. Connect the board over USB.
4. Build and upload:

   ```powershell
   pio run -e mks_tinybee -t upload
   ```

   or use the PlatformIO toolbar (✓ Build, → Upload).
   If the wrong port is picked, set `upload_port = COMx` under `[env:mks_tinybee]` in `ini/esp32.ini`.
5. Verify with the serial monitor (`pio device monitor -b 115200`) or:

   ```powershell
   python tools\serial_gcode_sender.py --port COM6 --command M115
   ```

## 2. Set up the Python tools

```powershell
python -m venv tools\venv
tools\venv\Scripts\Activate.ps1
python -m pip install -r tools\requirements.txt
```

Linux/macOS:

```bash
python3 -m venv tools/venv
source tools/venv/bin/activate
pip install -r tools/requirements.txt
```

## 3. Set up the gamepad

1. Connect the gamepad and check that the OS detects it
   (Windows: press `Win+R`, run `joy.cpl`, and move the sticks).
2. Find the board's serial port (Windows: Device Manager → *Ports (COM & LPT)*).
   Close any other app that uses this port.
3. Edit the config block at the top of `tools/gamepad_motor_controller.py`:

   ```python
   SERIAL_PORT = "COM6"   # "" = dry run, only prints commands
   GAMEPAD_INDEX = 0      # first connected controller
   STICK_AXIS = 0         # 0 = left stick X, 1 = left stick Y (typical)
   MOTOR_AXIS = "X"       # X, Y, Z or E
   STEP_MM = 3.0          # distance per move at full stick
   FEEDRATE = 20000       # mm/min
   ```

4. Do a dry run first (`SERIAL_PORT = ""`) to confirm the stick produces commands,
   then set the real port and start with a small `STEP_MM`.
5. Run:

   ```powershell
   python tools\gamepad_motor_controller.py
   ```

   Stop with `Ctrl+C` – the motors are stopped (`M410`) and disabled (`M84`).

Full list of settings and serial sender examples: [tools/README.md](tools/README.md).

## Safety

- The tools do **not** home the machine; make sure axes have room to move.
- Keep moves small until motor direction and wiring are confirmed.
- Keep a hand near the power switch the first time you drive motors.

## License

Marlin is licensed under the GNU GPL v3 – see [LICENSE](LICENSE).
