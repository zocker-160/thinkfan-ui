# ![](images/thinkfan-icon.png) Thinkfan UI

Small and simple application for controlling fan speed on IBM/Lenovo ThinkPads,
it can also monitor CPU temp and fan RPM.

![Screenshot](images/screenshot_PyQt6.png)

This is a complete rewrite of [scientifichackers/thinkfan-control-gui](https://github.com/scientifichackers/thinkfan-control-gui) using ~~PyQt5~~ **PyQt6**.

It is written for **Linux only**. For Windows, see [speedfan](http://www.almico.com/speedfan.php).

## How it Works?

- Parses `sensors` command to show CPU temp
- Modifies `/proc/acpi/ibm/fan` to change fan speed

## CLI Arguments

- `--no-tray` disables tray icon
- `--hide` hides main window on start

## Dependencies

### Ubuntu LTS
`sudo apt install lm-sensors policykit-1 python3 python3-pyqt6`

### Fedora
`sudo dnf install lm_sensors polkit python3 python3-pyqt6`

## Install

### Arch / Manjaro

AUR: [thinkfan-ui](https://aur.archlinux.org/packages/thinkfan-ui/)

### Ubuntu LTS

- Download `.deb` from [release page](https://github.com/zocker-160/thinkfan-ui/releases)
- Install using package manager of your choice or in terminal with `apt install ./<packagename>.deb`

### Manual

- Install all required dependencies
- Open this file, using command -- `sudo nano /etc/modprobe.d/thinkpad_acpi.conf`
- Add line `options thinkpad_acpi fan_control=1`
- Reboot
- Clone this repository and navigate to the `src` folder
- Run `python3 main.py`

---

Note: You are required to have the Linux kernel with `thinkpad-acpi` patch. (Ubuntu, Solus and a few others already seem to have this)
