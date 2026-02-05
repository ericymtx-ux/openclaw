# Operations Scripts

This directory contains scripts for managing OpenClaw as a system service.

## Files

- `install_gateway_service.sh`: A script to automatically generate and install the necessary `launchd` plist and a control script (`~/clawd_control.sh`) for the current user and repository location.

## Usage

Run the installer:

```bash
./install_gateway_service.sh
```

Then use the control script to manage the service:

```bash
~/clawd_control.sh start
~/clawd_control.sh status
~/clawd_control.sh log
~/clawd_control.sh restart
```
