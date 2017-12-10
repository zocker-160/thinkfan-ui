# Thinkfan-control-gui
Minimal Gui to monitor CPU temp and fan RPM and, to control fan speed on thinkpad devices for Linux (Ubuntu)
 - Parses `sensors` command to show CPU temp and fan RPM
 - Modifies `/proc/acpi/ibm/fan` to change fan speed

## Dependencies
`sudo apt install lm-sensors thinkfan python3.6 python3-tk`

## Setup
open/create ` /etc/modprobe.d/thinkpad_acpi.conf` and add line `options thinkpad_acpi fan_control=1`
 
open `sudo nano /etc/default/thinkfan` and add line `START=yes` (to start thinkfan on startup)


## Usage
`sudo python3 fan.py`
(sudo is needed to modify speed)
