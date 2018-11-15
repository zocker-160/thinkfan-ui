# Thinkpad Fan Control GUI

![Screenshot](https://i.imgur.com/UXII1Mg.png)

This is program for controlling fan speed on IBM/Lenovo ThinkPads  
It can also monitor CPU temp and fan RPM   
It is written for Linux only. For windows, see http://www.almico.com/speedfan.php   
Written in Python, using Tkinter   

## How it Works?
 + Parses `sensors` command to show CPU temp and fan RPM
 + Modifies `/proc/acpi/ibm/fan` to change fan speed

## Dependencies
`sudo apt install lm-sensors thinkfan python3 python3-tk`

## Setup
+ `sudo nano /etc/modprobe.d/thinkpad_acpi.conf` -> add line `options thinkpad_acpi fan_control=1` ( enables fan control )
 
+ `sudo nano /etc/default/thinkfan` -> add line `START=yes` ( starts thinkfan on startup )

+ Reboot. 

Now you'll be able to use this program easily.

Notes - You are required to have the Linux kernel with 'thinkpad-acpi' patch. You must also enable manual control for your fans. For Linux 2.6.22 and above, you must add 'fan_control=1' as a module parameter to 'thinkpad-acpi'. For example, in Debian Lenny (and Ubuntu 8.04), you must add the following to "/etc/modprobe.d/options": options thinkpad_acpi fan_control=1 In Ubuntu 9.10 you need to add this line to file "/etc/modprobe.d/alsa-base.conf"


## Usage
`python3 fan.py`
( you might need to use it with sudo to modify speed )
