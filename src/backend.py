import yaml
import subprocess
import os
import sys # <-- IMPORT SYS MODULE
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
                
                if level == 127:
                    level = "Disengaged"
                
                temp_ranges.append(TempRange(min_temp=min_temp, max_temp=max_temp, level=level))
    
    return temp_ranges


def save_curve_to_thinkfan(temp_ranges):
    """
    Writes a list of TempRange objects to the 'levels' section
    of /etc/thinkfan.conf by calling a privileged helper script.
    """
    try:
        with open(THINKFAN_CONF_PATH, 'r') as f:
            config = yaml.safe_load(f)
    except (FileNotFoundError, Exception):
        config = {}

    new_levels = []
    for temp_range in temp_ranges:
        level = temp_range.level
        if str(level) == 'Disengaged':
            level = 127
        
        new_levels.append([level, temp_range.min_temp, temp_range.max_temp])

    config['levels'] = new_levels
    
    yaml_content = yaml.dump(config, sort_keys=False, default_flow_style=False)

    try:
        command = ["pkexec", sys.executable, HELPER_PATH, THINKFAN_CONF_PATH, yaml_content]
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
