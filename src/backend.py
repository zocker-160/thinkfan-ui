import yaml
import subprocess
import os
import sys
from data_model import TempRange

THINKFAN_CONF_PATH = "/etc/thinkfan.conf"
HELPER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "save_helper.py"))

def load_curve_from_thinkfan():
    """
    Reads /etc/thinkfan.conf and converts the 'levels' section
    into a list of TempRange objects.
    """
    try:
        with open(THINKFAN_CONF_PATH, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: {THINKFAN_CONF_PATH} not found.")
        return []
    except Exception as e:
        print(f"Error reading thinkfan.conf: {e}")
        return []

    temp_ranges = []
    if 'levels' in config and isinstance(config['levels'], list):
        for entry in config['levels']:
            if isinstance(entry, list) and len(entry) == 3:
                level, min_temp, max_temp = entry
            elif isinstance(entry, dict) and all(k in entry for k in ['level', 'min', 'max']):
                level, min_temp, max_temp = entry['level'], entry['min'], entry['max']
            else:
                continue

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
        
        # --- NEW COMMENT HERE ---
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
            print("Helper script executed successfully.")
            return True
        else:
            print(f"Helper script failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"Error executing helper script: {e}")
        return False
