# Thinkpad Fan Control GUI

This is program for controlling fan speed on IBM/Lenovo ThinkPads  
It can also monitor CPU temp and fan RPM   
It is written for Linux only. For windows, see http://www.almico.com/speedfan.php   
Written in Python, using Tkinter   

## How it Works?
 - Parses `sensors` command to show CPU temp and fan RPM
 - Modifies `/proc/acpi/ibm/fan` to change fan speed

## Dependencies
`sudo apt install lm-sensors thinkfan python3.6 python3-tk`

## Setup
+ `sudo nano /etc/modprobe.d/thinkpad_acpi.conf` -> add line `options thinkpad_acpi fan_control=1`
 
+ `sudo nano /etc/default/thinkfan` -> add line `START=yes` (to start thinkfan on startup)

+ Reboot. 

Now you'll be able to use this program easily.

Notes - You are required to have the Linux kernel with 'thinkpad-acpi' patch. You must also enable manual control for your fans. For Linux 2.6.22 and above, you must add 'fan_control=1' as a module parameter to 'thinkpad-acpi'. For example, in Debian Lenny (and Ubuntu 8.04), you must add the following to "/etc/modprobe.d/options": options thinkpad_acpi fan_control=1 In Ubuntu 9.10 you need to add this line to file "/etc/modprobe.d/alsa-base.conf"


## Usage
`sudo python3 fan.py`
(sudo is needed to modify speed)
