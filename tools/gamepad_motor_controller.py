#!/usr/bin/env python3
"""Minimal gamepad -> Marlin motor control.

Move one axis with an analog stick. Edit the CONFIG block, then run:
  python tools/gamepad_motor_controller.py

This is intentionally small and easy to extend.
"""

from __future__ import annotations

import os
import time

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame
import serial

# ----------------------------------------------------------------------------
# Config - edit these
# ----------------------------------------------------------------------------
SERIAL_PORT = "COM6"  # set to "" to test without a board (prints commands)
BAUD_RATE = 115200

GAMEPAD_INDEX = 0
STICK_AXIS = 0  # analog axis number
INVERT_STICK = False

MOTOR_AXIS = "X"  # X, Y, Z or E
DEADZONE = 0.03  # ignore small stick noise
POLL_INTERVAL = 0.02  # seconds between moves
STEP_MM = 3.0  # distance per move at full stick
FEEDRATE = 20000  # mm/min
EXPO = 5.0  # response curve: 1.0 = linear, higher = finer at low stick


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def read_stick(joystick: pygame.joystick.Joystick) -> float:
    """Return the stick value in [-1, 1] after deadzone, or 0.0 when centered."""
    value = joystick.get_axis(STICK_AXIS)
    if INVERT_STICK:
        value = -value
    if abs(value) <= DEADZONE:
        return 0.0
    return max(-1.0, min(1.0, value))


def motion_command(stick: float) -> str:
    """Build a relative G0 move for the current stick value."""
    shaped = (abs(stick) ** EXPO) * (1 if stick >= 0 else -1)
    distance = shaped * STEP_MM
    return f"G0 {MOTOR_AXIS}{distance:.3f} F{FEEDRATE}"


# ----------------------------------------------------------------------------
# Serial
# ----------------------------------------------------------------------------
class Board:
    """Thin serial wrapper. With no port set, it just prints commands."""

    def __init__(self, port_name: str, baud: int) -> None:
        self.port = serial.Serial(port_name, baud, timeout=0.1) if port_name else None

    def send(self, command: str) -> None:
        print(f"> {command}")
        if self.port:
            self.port.write(f"{command}\n".encode("ascii"))
            self.port.flush()

    def drain(self) -> None:
        """Discard pending replies so the input buffer does not fill up."""
        if self.port and self.port.in_waiting:
            self.port.read(self.port.in_waiting)

    def close(self) -> None:
        if self.port:
            self.port.close()


# ----------------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------------

def loop(joystick: pygame.joystick.Joystick, board: Board):
    moving = False

    while True:
        pygame.event.pump()
        stick = read_stick(joystick)

        if stick != 0.0:
            board.send(motion_command(stick))
            moving = True
        elif moving:
            board.send("M410")  # stop immediately when stick is centered
            moving = False

        board.drain()
        time.sleep(POLL_INTERVAL)


def main() -> int:
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No gamepad detected.")
        return 1

    joystick = pygame.joystick.Joystick(GAMEPAD_INDEX)
    joystick.init()
    print(f"Using gamepad [{GAMEPAD_INDEX}] {joystick.get_name()}")
    print("Press Ctrl+C to stop.")

    board = Board(SERIAL_PORT, BAUD_RATE)
    time.sleep(2.0)  # let the board boot
    board.send("M17")  # enable steppers
    board.send("G91")  # relative moves


    try:
        loop(joystick, board)
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        board.send("M410")
        board.send("G90")
        board.send("M84")
        board.close()
        pygame.quit()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
