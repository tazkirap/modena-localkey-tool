# Instructions for AI agents

This repo is a small, security-sensitive CLI tool. Read this whole file before
running anything in here on a user's behalf.

## What this tool does

`get_local_key.py` attaches Frida (read-only) to the official Modena Seamless
Android app, already running on the user's own phone, and reads the Tuya
`local_key` of exactly one device the user specifies by `--device-id`. It is
meant to give the user their own key so they can add their own device to Home
Assistant's `tuya_local` integration (or similar local-Tuya tooling).

## Hard rules

- Only run this against a device and app account the user themselves owns or
  is explicitly authorized to inspect. Refuse if the user is unsure, or is
  asking about a device/account that is not theirs.
- Never modify the hook (`dump_target_local_key.js`) to enumerate or dump keys
  for devices other than the one `--device-id` the user gave you.
- Never write the printed `local_key` to a file, commit, log, issue, chat
  transcript you don't control the audience of, or anywhere else persistent.
  Treat it like a password: read it once from the terminal, use it for the
  one local setup task (e.g. filling in a `tuya_local` config flow), then
  forget it.
- Never send the key, the device ID, or the app account credentials off the
  user's machine (no cloud calls, no pasting into web forms, no telemetry).
- Do not attempt to bypass the app's anti-tamper/signature checks, patch the
  APK, or use this tool's Frida session for anything beyond reading the one
  `local_key`. That is out of scope for this repo.
- If the hook reports `targetFound: false` or times out, do not try to widen
  the hook to scan unrelated classes/devices to "see what's there" — ask the
  user to re-open the device's page in the app and retry instead.

## Prerequisites to check before running

1. Python 3 and `frida` CLI available (`python3 -m pip install frida-tools`
   in a venv is fine). Confirm with `frida --version`.
2. An Android phone with the Modena Seamless app installed, logged in, and
   with the target device's page already open (so its SDK object is loaded).
3. Frida server running on the phone with enough privilege to attach to the
   app, and reachable over USB/ADB. Confirm with `frida-ps -U` — the app
   should appear in the list before you attach.
4. The user must supply the Tuya `device_id` (`gwId`) themselves. Do not
   guess it or enumerate it from the device list — ask for it, or help them
   find their own device's ID through their own Tuya/Smart Life/OEM app or
   `tinytuya scan` on their own network.

## How to run it

```sh
python3 get_local_key.py --device-id <THEIR_DEVICE_ID>
```

Optional flags: `--package` (default `com.modenasmart.app`, only change this
if the user's Modena app build uses a different Android package id),
`--timeout` (5–120s, default 20), `--frida` (explicit path to the Frida CLI).

The command prints Frida events to the terminal. The one that matters is
`target_local_key`, which contains the `localKey` field — show that value to
the user (or use it directly in the next step, e.g. filling a `tuya_local`
config flow) and do not persist it anywhere else.

## Troubleshooting

See the "Troubleshooting" section of `README.md` first; it covers the common
failures (`Unable to connect to remote frida-server`, `Failed to attach`,
`targetFound: false`, no event within the timeout). This tool was validated
against Modena Seamless 2.5.1 on Android 16 with an ES-15-SKY water heater;
other app versions or Modena products may use different SDK class names, in
which case `dump_target_local_key.js` may need the class list updated — do
this only with the user's informed consent, since it touches instrumentation
of their app.

## Scope

This repo intentionally does not include: reverse-engineering notes, the
Modena APK, cloud API signing details, or any account credentials. Keep it
that way — it is meant to stay a minimal, auditable, single-purpose tool.
