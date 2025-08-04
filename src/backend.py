import yaml
import subprocess
import os
import sys
import re
import json
from data_model import TempRange

THINKFAN_CONF_PATH = "/etc/thinkfan.conf"
HELPER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "save_helper.py"))

def discover_sensors():
    """
    Runs 'sensors -j' and parses the output to get a list of all
    individual temperature sensors on the system.
    """
    try:
        result = subprocess.run(
            ["sensors", "-j"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        sensor_data = json.loads(result.stdout)
    except Exception as e:
        print(f"Error discovering sensors: {e}", file=sys.stderr)
        return []

    all_sensors = []
    for device_name, device_info in sensor_data.items():
        hwmon_name = device_name.split('-')[0]
        for feature_name, feature_data in device_info.items():
            if not isinstance(feature_data, dict): continue
            for key in feature_data:
                if key.endswith("_input") and key.startswith("temp"):
                    index = int(re.search(r'temp(\d+)_input', key).group(1))
                    all_sensors.append({
                        'device': hwmon_name,
                        'label': feature_name,
                        'index': index
                    })
    return all_sensors

def load_curve_from_thinkfan():
    """
    Reads /etc/thinkfan.conf and converts the 'levels' section
    into a list of TempRange objects, supporting both simple and detailed syntax.
    """
    try:
        with open(THINKFAN_CONF_PATH, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading {THINKFAN_CONF_PATH}: {e}", file=sys.stderr)
        return []

    if 'levels' not in config or not isinstance(config['levels'], list):
        return []

    total_sensor_inputs = 0
    if 'sensors' in config and isinstance(config['sensors'], list):
        for sensor_block in config['sensors']:
            if isinstance(sensor_block, dict) and 'indices' in sensor_block:
                total_sensor_inputs += len(sensor_block['indices'])

    temp_ranges = []
    for entry in config['levels']:
        level, min_temp, max_temp = None, None, None

        if isinstance(entry, list) and len(entry) == 3:
            level, min_temp, max_temp = entry

        elif isinstance(entry, dict) and all(k in entry for k in ['speed', 'lower_limit', 'upper_limit']):
            level = entry['speed']
            lower_limits = entry['lower_limit']
            upper_limits = entry['upper_limit']

            for temp in lower_limits:
                if temp != 0:
                    min_temp = temp
                    break
            for temp in upper_limits:
                if temp != 120:
                    max_temp = temp
                    break
        
        if all(v is not None for v in [level, min_temp, max_temp]):
            if level == 127:
                level = "Disengaged"
            temp_ranges.append(TempRange(min_temp=min_temp, max_temp=max_temp, level=level))
    
    return temp_ranges


def save_curve_to_thinkfan(temp_ranges):
    """
    Writes a list of TempRange objects to the 'levels' section
    of /etc/thinkfan.conf, preserving existing comments and structure.
    """
    header_lines = []
    try:
        with open(THINKFAN_CONF_PATH, 'r') as f:
            for line in f:
                if line.strip().startswith('levels:'):
                    break
                header_lines.append(line)
    except FileNotFoundError:
        header_lines.append("# thinkfan configuration file\n\n")
        header_lines.append("fans:\n")
        header_lines.append("  - tpacpi: /proc/acpi/ibm/fan\n\n")
        header_lines.append("sensors:\n")
        header_lines.append("  - hwmon: /sys/class/hwmon\n")
        header_lines.append("    name: coretemp\n")
        header_lines.append("    indices: [1]\n\n")

    final_content = "".join(header_lines).strip() + "\n\nlevels:\n"

    disengaged_comment_added = False
    for temp_range in temp_ranges:
        level = temp_range.level
        is_disengaged = False
        if str(level) == 'Disengaged':
            level = 127
            is_disengaged = True
        
        if is_disengaged and not disengaged_comment_added:
            final_content += "  # BEWARE: 127 aka disengaged or full-speed. In this level, the EC disables\n"
            final_content += "  # the speed-locked closed-loop fan control and drives the fan as fast as\n"
            final_content += "  # it can go, which might exceed hardware limits. Use with caution.\n"
            disengaged_comment_added = True
            
        final_content += f"  - [{level}, {temp_range.min_temp}, {temp_range.max_temp}]\n"

    try:
        command = ["pkexec", sys.executable, HELPER_PATH, THINKFAN_CONF_PATH, final_content]
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"Helper script failed: {result.stderr}", file=sys.stderr)
            return False

    except Exception as e:
        print(f"Error executing helper script: {e}", file=sys.stderr)
        return False
