def parse_key_value_string(input_string):
    """
    Parses a string with format "key1=val1,key2=val2,...,keyn=valn" into a dictionary.
    Splits only on the first '=' in each pair.

    Args:
        input_string (str): Input string with key-value pairs.

    Returns:
        dict: A dictionary with keys and corresponding values.
    
    Raises:
        ValueError: If the input string is not in the expected format.
    """
    if not input_string:  # Empty string is considered valid
        return {}

    key_value_pairs = input_string.split(',')
    key_value_map = {}
    for pair in key_value_pairs:
        if '=' not in pair:
            raise ValueError("Invalid input string format.")
        
        key, value = pair.split('=', 1) 
        key_value_map[key.strip()] = value.strip()
    
    return key_value_map

def build_buildvar_strings(key_value_map):
    """
    Builds '--buildvar' strings for each key-value pair in the dictionary.

    Args:
        key_value_map (dict): A dictionary with keys and corresponding values.

    Returns:
        list: A list of '--buildvar' strings for each key-value pair.
    """
    buildvar_strings = []
    for key, value in key_value_map.items():
        buildvar_string = f"--buildvar {key}={value}"
        buildvar_strings.append(buildvar_string)
    
    return buildvar_strings