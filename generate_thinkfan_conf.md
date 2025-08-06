# Overview
`generate_thinkfan_conf.py` standalone script to bootstrap a safe and valid `/etc/thinkfan.conf` file.
Scans the system sensors, generates a CPU sensorbased thinkfan.conf, while providing commented-out entries for all other detected sensors.

### Dependencies
-    `lm-sensors`: The script requires `lm-sensors`, as it relies on `sensors -j` to discover hardware sensors.

### Usage

Redirect the output to `thinkfan.conf` file, root privileges needed to read all sensors.

**Example Command**:
``` bash
	sudo python3 generate_thinkfan_conf.py > /etc/thinkfan.conf
```
**Features and Logic**

1.    Sensor Discovery: It runs `sensors -j` to get a JSON list of all available temperature sensors on the system.

2.    Primary CPU Detection: It identifies the primary CPU temperature sensor by searching for common `hwmon` device names (like `coretemp` or `k10temp`) and specific sensor labels (like "Package id 0", "Tctl", or "Tdie").

3.    Safe-by-Default Configuration:

-    The generated `sensors`: section includes an entry for every sensor device found on the system.

-    However, only the identified primary CPU sensor is enabled (uncommented).

-    All remaining sensor blocks are commented out, thus preventing them from influencing fan control unless the user manually enables them.

4. **Index-to-Label Mapping**: It generates helpful comments that map the numerical sensor `index` to its human-readable `label`, making the configuration easier to read and edit.
    ``` yaml
    # Mappings for coretemp:
    #   1: Package id 0
    #   2: Core 0
    ```
5. **Default Fan Curve**: It provides a default fan curve in the `levels`: section using `thinkfan`'s simple syntax (`- [level, min, max]`). A comment is included to explain that this syntax is valid because only one sensor group is active by default.

6. **Detailed Syntax Example**: For users who wish to enable multiple sensors, the script includes a comprehensive, commented-out example of the **detailed syntax**. It generates a formatted header that maps each column in the `limit` arrays to the corresponding sensor label, which simplifies the process of creating a multi-sensor configuration.
    ``` yaml
		#     Format:      [temp1, Package_id_0, Core_0, Core_1, ...]
		#
		# levels:
		#   - speed: 2
		#     lower_limit: [55   , 0           , 0     , 0     , ...]
		#     upper_limit: [65   , 120         , 120   , 120   , ...]
    ```
