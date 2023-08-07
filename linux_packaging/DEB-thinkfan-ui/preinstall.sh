#! /usr/bin/env bash

# enable fan control in thinkpad_acpi kernel module
echo "options thinkpad_acpi fan_control=1" > /etc/modprobe.d/thinkpad_acpi.conf

# reload thinkpad_acpi kernel module
modprobe -r thinkpad_acpi
modprobe thinkpad_acpi
