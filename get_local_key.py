#!/usr/bin/env python3
"""Attach Frida to Modena Seamless and read one selected device's local key."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent
HOOK_TEMPLATE = APP_ROOT / "dump_target_local_key.js"
DEFAULT_PACKAGE = "com.modenasmart.app"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read the localKey for one selected Modena device from the live "
            "Modena Seamless app process."
        )
    )
    parser.add_argument(
        "--device-id",
        required=True,
        help="Tuya device ID (gwId) to match; no other device keys are emitted",
    )
    parser.add_argument(
        "--package",
        default=DEFAULT_PACKAGE,
        help=f"Android package identifier (default: {DEFAULT_PACKAGE})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Seconds to wait for Frida events (5–120; default: 20)",
    )
    parser.add_argument(
        "--frida",
        help="Path to Frida CLI; by default, find `frida` on PATH",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", args.device_id):
        print("Error: device ID contains unsupported characters.", file=sys.stderr)
        return 2
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,255}", args.package):
        print("Error: invalid Android package identifier.", file=sys.stderr)
        return 2
    if not 5 <= args.timeout <= 120:
        print("Error: timeout must be between 5 and 120 seconds.", file=sys.stderr)
        return 2

    frida_cli = args.frida or shutil.which("frida")
    if not frida_cli:
        configured_path = os.environ.get("FRIDA_CLI")
        if configured_path and Path(configured_path).is_file():
            frida_cli = configured_path
    if not frida_cli:
        print(
            "Error: Frida CLI not found. Install frida-tools or pass --frida.",
            file=sys.stderr,
        )
        return 2

    try:
        template = HOOK_TEMPLATE.read_text(encoding="utf-8")
    except OSError as error:
        print(f"Error: cannot read Frida hook: {error}", file=sys.stderr)
        return 2

    hook_source = template.replace(
        "__DEVICE_ID_JSON__", json.dumps(args.device_id)
    )
    if hook_source == template:
        print("Error: device ID placeholder missing from hook.", file=sys.stderr)
        return 2

    print(
        "Attach is read-only. Keep the device page open; the key, if found, "
        "will be printed in this terminal and not saved by this tool."
    )
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".js", prefix="modena-hook-"
        ) as hook_file:
            hook_file.write(hook_source)
            hook_file.flush()
            command = [
                frida_cli,
                "-U",
                "-N",
                args.package,
                "-l",
                hook_file.name,
                "--runtime=v8",
                "-q",
                "-t",
                str(args.timeout),
            ]
            return subprocess.run(command, check=False).returncode
    except FileNotFoundError:
        print(f"Error: Frida CLI not found at {frida_cli!r}.", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nStopped.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
