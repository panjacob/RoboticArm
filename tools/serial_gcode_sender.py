#!/usr/bin/env python3
"""Send G-code commands to a Marlin board over a serial port.

Examples:
  python serial_gcode_sender.py --port COM9 --command M115
  python serial_gcode_sender.py --port COM9 --x-test
  python serial_gcode_sender.py --port COM9 --file commands.gcode
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Iterable, List, Optional, TextIO

import serial
from serial import SerialException

DEFAULT_BAUD = 115200
DEFAULT_TIMEOUT = 2.0
DEFAULT_BOOT_WAIT = 2.5
DEFAULT_SESSION_TIMEOUT = 60.0
DEFAULT_MONITOR_SECONDS = 0.0
LINE_ENDINGS = {
    "lf": "\n",
    "crlf": "\r\n",
    "cr": "\r",
}


X_TEST_COMMANDS = [
    "M115",
    "M119",
    "M17",
    "M211 S0",
    "G92 X0",
    "G91",
    "G0 X5 F120",
    "G0 X-5 F120",
    "M84",
]


class GCodeSenderError(RuntimeError):
    """Raised when G-code sender input or serial communication fails."""


def make_timestamp() -> str:
    return time.strftime("%H:%M:%S")


def emit(message: str, log_handle: Optional[TextIO] = None) -> None:
    print(message)
    if log_handle:
        log_handle.write(message + "\n")
        log_handle.flush()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send G-code to a Marlin board over serial.")
    parser.add_argument("--port", required=True, help="Serial port, for example COM9")
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD, help=f"Serial baud rate (default: {DEFAULT_BAUD})")
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Read timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--boot-wait",
        type=float,
        default=DEFAULT_BOOT_WAIT,
        help=f"Seconds to wait after opening the port (default: {DEFAULT_BOOT_WAIT})",
    )
    parser.add_argument(
        "--command",
        action="append",
        default=[],
        help="G-code command to send. Repeat this flag for multiple commands.",
    )
    parser.add_argument("--file", type=Path, help="Path to a .gcode or text file with one command per line")
    parser.add_argument(
        "--x-test",
        action="store_true",
        help="Send a safe X-axis test sequence for a single motor without homing.",
    )
    parser.add_argument(
        "--reset-on-connect",
        action="store_true",
        help="Toggle DTR/RTS after opening the port to reset the board before reading startup logs.",
    )
    parser.add_argument(
        "--startup-read-seconds",
        type=float,
        default=2.0,
        help="Seconds to read startup text before sending commands (default: 2.0)",
    )
    parser.add_argument(
        "--per-command-wait",
        type=float,
        default=1.0,
        help="Seconds to keep reading after each command (default: 1.0)",
    )
    parser.add_argument(
        "--session-timeout",
        type=float,
        default=DEFAULT_SESSION_TIMEOUT,
        help=f"Maximum total session length in seconds (default: {DEFAULT_SESSION_TIMEOUT})",
    )
    parser.add_argument(
        "--monitor-seconds",
        type=float,
        default=DEFAULT_MONITOR_SECONDS,
        help="Continue reading and printing board output after all commands are sent (default: 0.0)",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Optional path to a log file where sent commands and board replies will be saved.",
    )
    parser.add_argument(
        "--line-ending",
        choices=tuple(LINE_ENDINGS),
        default="lf",
        help="Line ending appended to each command (default: lf)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the commands that would be sent, without opening the serial port.",
    )
    return parser.parse_args()


def load_commands(args: argparse.Namespace) -> List[str]:
    commands: List[str] = []

    if args.file:
        if not args.file.exists():
            raise GCodeSenderError(f"Command file not found: {args.file}")
        for line in args.file.read_text(encoding="utf-8").splitlines():
            stripped = line.split(";", 1)[0].strip()
            if stripped and not stripped.startswith(";"):
                commands.append(stripped)

    commands.extend(cmd.strip() for cmd in args.command if cmd.strip())

    if args.x_test:
        commands.extend(X_TEST_COMMANDS)

    if not commands:
        raise GCodeSenderError("No commands provided. Use --command, --file, or --x-test.")

    return commands


def drain_serial(port: serial.Serial, duration: float, log_handle: Optional[TextIO] = None) -> List[str]:
    lines: List[str] = []
    deadline = time.monotonic() + max(duration, 0.0)
    pending = ""
    original_timeout = port.timeout
    port.timeout = 0

    try:
        while time.monotonic() < deadline:
            waiting = port.in_waiting
            raw = port.read(waiting or 1)
            if raw:
                pending += raw.decode("utf-8", errors="replace")
                pending = pending.replace("\r", "")
                while "\n" in pending:
                    text, pending = pending.split("\n", 1)
                    text = text.rstrip()
                    if text:
                        lines.append(text)
                        emit(f"[{make_timestamp()}] < {text}", log_handle)
            else:
                time.sleep(0.05)

        tail = pending.strip()
        if tail:
            lines.append(tail)
            emit(f"[{make_timestamp()}] < {tail}", log_handle)
    finally:
        port.timeout = original_timeout

    return lines


def reset_board(port: serial.Serial) -> None:
    port.dtr = False
    port.rts = True
    time.sleep(0.15)
    port.reset_input_buffer()
    port.dtr = True
    port.rts = False
    time.sleep(0.4)


def send_commands(
    port_name: str,
    baud: int,
    timeout: float,
    boot_wait: float,
    startup_read_seconds: float,
    per_command_wait: float,
    session_timeout: float,
    monitor_seconds: float,
    commands: Iterable[str],
    reset_on_connect: bool,
    log_file: Optional[Path],
    line_ending: str,
) -> int:
    log_handle: Optional[TextIO] = None
    try:
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            log_handle = log_file.open("a", encoding="utf-8")
            emit(f"[{make_timestamp()}] Logging serial session to {log_file}", log_handle)

        with serial.Serial(port=port_name, baudrate=baud, timeout=timeout, write_timeout=timeout) as port:
            session_deadline = time.monotonic() + max(session_timeout, 1.0)
            emit(f"[{make_timestamp()}] Opened {port_name} at {baud} baud", log_handle)
            time.sleep(max(boot_wait, 0.0))

            if reset_on_connect:
                emit(f"[{make_timestamp()}] Resetting board using DTR/RTS...", log_handle)
                reset_board(port)

            port.reset_input_buffer()
            emit(f"[{make_timestamp()}] Reading startup output...", log_handle)
            startup_lines = drain_serial(port, startup_read_seconds, log_handle)
            emit(f"[{make_timestamp()}] Startup lines captured: {len(startup_lines)}", log_handle)

            for command in commands:
                if time.monotonic() >= session_deadline:
                    raise GCodeSenderError("Session timeout reached before all commands were sent.")
                payload = f"{command}{line_ending}".encode("ascii", errors="ignore")
                emit(f"[{make_timestamp()}] > {command}", log_handle)
                port.write(payload)
                port.flush()
                reply_lines = drain_serial(port, per_command_wait, log_handle)
                if reply_lines:
                    emit(f"[{make_timestamp()}] Reply lines for '{command}': {len(reply_lines)}", log_handle)
                else:
                    emit(f"[{make_timestamp()}] No reply captured for '{command}' within {per_command_wait:.2f}s", log_handle)

            if monitor_seconds > 0:
                emit(f"[{make_timestamp()}] Monitoring board output for {monitor_seconds:.2f}s after commands...", log_handle)
                monitor_lines = drain_serial(port, monitor_seconds, log_handle)
                emit(f"[{make_timestamp()}] Post-command monitor lines captured: {len(monitor_lines)}", log_handle)

        return 0
    except SerialException as exc:
        raise GCodeSenderError(f"Serial error on {port_name}: {exc}") from exc
    finally:
        if log_handle:
            log_handle.close()


def main() -> int:
    args = parse_args()

    try:
        commands = load_commands(args)
    except GCodeSenderError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(f"Dry run for {args.port} at {args.baud} baud")
        for command in commands:
            print(f"> {command}")
        return 0

    try:
        return send_commands(
            port_name=args.port,
            baud=args.baud,
            timeout=args.timeout,
            boot_wait=args.boot_wait,
            startup_read_seconds=args.startup_read_seconds,
            per_command_wait=args.per_command_wait,
            session_timeout=args.session_timeout,
            monitor_seconds=args.monitor_seconds,
            commands=commands,
            reset_on_connect=args.reset_on_connect,
            log_file=args.log_file,
            line_ending=LINE_ENDINGS[args.line_ending],
        )
    except GCodeSenderError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


