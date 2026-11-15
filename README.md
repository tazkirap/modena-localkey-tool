# Modena Local Key Tool

Read the Tuya `localKey` for a Modena device from the Modena Seamless app's
live SDK objects using Frida. The hook only emits a key when the device ID
matches the ID supplied by the user.

Use this only with devices and app accounts that you own or are authorized to
inspect. This tool does not contact Tuya cloud, change device settings, or
write the key to disk. The key is printed in the terminal, so keep the output
private and do not redirect it to a log file.

## Requirements

- macOS or Linux computer with Python 3
- Frida CLI (`frida` from `frida-tools`) available on `PATH`
- Android phone with the official Modena Seamless app installed and logged in
- Frida server running on the phone with sufficient privileges
- ADB/Frida USB connection working (`frida-ps -U` should list the app)
- The target device ID (Tuya `device_id` / `gwId`)

Install Frida CLI in a virtual environment (recommended):

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install frida-tools
```

Use a Frida server build matching the installed Frida version and the phone's
CPU architecture.

The default app identifier is `com.modenasmart.app`. Use `--package` if your
Modena app build uses a different Android package identifier.

The hook's SDK bean class names were validated with Modena Seamless 2.5.1 on
Android 16 and an ES-15-SKY heater. Other app versions or Modena products may
use different SDK classes and may need a hook update.

## Usage

Open the target device's page in Modena Seamless first so its SDK object is in
memory. Then run:

```sh
python3 get_local_key.py --device-id YOUR_DEVICE_ID
```

The tool attaches to the already-running app, scans the SDK objects for the
requested device, and waits up to 20 seconds. If found, Frida prints an event
named `target_local_key`; the key is in that event's `localKey` field. Press
Ctrl+C to stop early.

Options:

```text
--device-id   Required Tuya device ID to match
--package     Android package identifier (default: com.modenasmart.app)
--timeout     Seconds to wait for hook events (default: 20, range: 5–120)
--frida       Path to Frida CLI (default: find `frida` on PATH)
```

Example with a custom app package and Frida installation:

```sh
python3 get_local_key.py \
  --device-id YOUR_DEVICE_ID \
  --package com.example.modena \
  --frida "$HOME/.local/bin/frida"
```

## Troubleshooting

- **Unable to connect to remote frida-server:** start Frida server on the
  phone and confirm USB/ADB connectivity with `frida-ps -U`.
- **Failed to attach:** confirm the package identifier with `frida-ps -Uai`
  and pass it with `--package`.
- **`scan_complete` says `targetFound: false`:** reopen the device page in the
  app, verify the device ID, and run again. The supported SDK bean class names
  are listed in the hook; other app/SDK builds may use different classes.
- **No key appears within the timeout:** this SDK build may not expose the
  same getter or Frida may be blocked by the app/runtime. The tool does not
  bypass app protections or extract account tokens.

## Privacy

The device ID is passed only to the local Frida script. The script does not
enumerate or print keys for other devices. The local key is sent from the
instrumented process to Frida and displayed in the current terminal session;
it is not saved by this tool. Avoid shell transcript recording, terminal
session logging, screenshots, and output redirection while the key is shown.

## License

MIT. See [LICENSE](LICENSE).
