import yaml
from data_model import TempRange

THINKFAN_CONF_PATH = "/etc/thinkfan.conf"

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
                
                # --- CORRECTED MAPPING ---
                if level == 127:
                    level = "Disengaged"
                
                temp_ranges.append(TempRange(min_temp=min_temp, max_temp=max_temp, level=level))
    
    return temp_ranges


def save_curve_to_thinkfan(temp_ranges):
    """
    Writes a list of TempRange objects to the 'levels' section
    of /etc/thinkfan.conf, preserving the rest of the file.
    """
    try:
        with open(THINKFAN_CONF_PATH, 'r') as f:
            config = yaml.safe_load(f)
    except (FileNotFoundError, Exception):
        config = {}

    new_levels = []
    for temp_range in temp_ranges:
        level = temp_range.level
        # --- CORRECTED MAPPING ---
        if str(level) == 'Disengaged':
            level = 127
        
        new_levels.append([level, temp_range.min_temp, temp_range.max_temp])

    config['levels'] = new_levels

    try:
        with open(THINKFAN_CONF_PATH, 'w') as f:
            yaml.dump(config, f, sort_keys=False, default_flow_style=False)
        print(f"Successfully saved levels to {THINKFAN_CONF_PATH}")
        return True
    except Exception as e:
        print(f"Error writing to {THINKFAN_CONF_PATH}: {e}")
        return False
