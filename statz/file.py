from datetime import datetime, date
import json

def export_into_file(function, csv=False, params=(False, None)):
    '''
    Export the output of a function to a JSON or CSV file.
    
    This utility function takes another function as input, executes it,
    and writes the output to a file named "statz_export_{date}_{time}.json" or ".csv".
    
    Args:
        function (callable): The function whose output is to be exported.
        csv (bool): If True, exports as CSV. If False, exports as JSON. Defaults to False.
        params (tuple): Additional parameters to pass to the function. Put (False, None) if no parameters are needed. Otherwise, put (True, [values, values, values, ...]).

    Note:
        CSV export works best with functions that return lists of dictionaries or simple data structures.
        Complex nested data will be flattened or converted to strings for CSV compatibility.
    '''
    import csv as csv_module
    
    def flatten_for_csv(data, prefix=''):
        """Flatten complex nested data structures for CSV export."""
        flattened = {}
        
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    flattened.update(flatten_for_csv(value, new_key))
                else:
                    flattened[new_key] = str(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_key = f"{prefix}[{i}]" if prefix else f"item_{i}"
                if isinstance(item, (dict, list)):
                    flattened.update(flatten_for_csv(item, new_key))
                else:
                    flattened[new_key] = str(item)
        else:
            key = prefix if prefix else 'value'
            flattened[key] = str(data)
            
        return flattened

    def format_hardware_usage_csv(data, writer):
        """Special formatting for hardware usage data to make it more readable."""
        if len(data) != 5:
            # Not hardware usage format, use generic flattening
            flattened = flatten_for_csv(data)
            writer.writerow(['Key', 'Value'])
            for key, value in flattened.items():
                writer.writerow([key, value])
            return
        
        # Hardware usage specific formatting
        cpu_data, ram_data, disk_data, network_data, battery_data = data
        
        # Write a more structured CSV for hardware usage
        writer.writerow(['Component', 'Metric', 'Value', 'Unit'])
        
        # CPU data
        if cpu_data:
            for core, usage in cpu_data.items():
                writer.writerow(['CPU', core, str(usage), '%'])
        
        # RAM data  
        if ram_data:
            for metric, value in ram_data.items():
                unit = 'MB' if metric in ['total', 'used', 'free'] else '%'
                writer.writerow(['RAM', metric, str(value), unit])
        
        # Disk data
        if disk_data:
            for i, disk in enumerate(disk_data):
                for metric, value in disk.items():
                    unit = 'MB/s' if 'Speed' in metric else ''
                    writer.writerow(['Disk', f"{disk.get('device', f'Disk{i+1}')}.{metric}", str(value), unit])
        
        # Network data
        if network_data:
            for metric, value in network_data.items():
                writer.writerow(['Network', metric, str(value), 'MB/s'])
        
        # Battery data
        if battery_data:
            for metric, value in battery_data.items():
                unit = '%' if metric == 'percent' else 'minutes' if metric == 'timeLeftMins' else ''
                writer.writerow(['Battery', metric, str(value), unit])

    def format_system_specs_csv(data, writer):
        """Special formatting for system specs data to make it more readable."""
        writer.writerow(['Component', 'Property', 'Value'])
        
        if len(data) == 4:
            # macOS/Linux format: [os_info, cpu_info, mem_info, disk_info]
            components = ['OS', 'CPU', 'Memory', 'Disk']
        elif len(data) == 7:
            # Windows format: [os_data, cpu_data, gpu_data_list, ram_data_list, storage_data_list, network_data, battery_data]
            components = ['OS', 'CPU', 'GPU', 'Memory', 'Storage', 'Network', 'Battery']
        else:
            # Fallback to generic formatting
            flattened = flatten_for_csv(data)
            writer.writerow(['Key', 'Value'])
            for key, value in flattened.items():
                writer.writerow([key, value])
            return
        
        for i, component_data in enumerate(data):
            component_name = components[i]
            
            if isinstance(component_data, dict):
                for prop, value in component_data.items():
                    writer.writerow([component_name, prop, str(value)])
            elif isinstance(component_data, list):
                for j, item in enumerate(component_data):
                    if isinstance(item, dict):
                        for prop, value in item.items():
                            writer.writerow([f"{component_name} {j+1}", prop, str(value)])
                    else:
                        writer.writerow([f"{component_name} {j+1}", 'value', str(item)])
            else:
                writer.writerow([component_name, 'value', str(component_data)])

    def format_simple_dict_csv(data, writer, component_name='Temperature'):
        """Format simple dictionaries like temperature data."""
        writer.writerow(['Component', 'Sensor', 'Value', 'Unit'])
        for sensor, value in data.items():
            # Extract numeric value and determine unit
            if isinstance(value, (int, float)):
                temp_value = str(value)
                unit = '°C'
            elif isinstance(value, str) and '°C' in value:
                temp_value = value.replace('°C', '').strip()
                unit = '°C'
            else:
                temp_value = str(value)
                unit = ''
            
            writer.writerow([component_name, sensor, temp_value, unit])
    
    try:
        if params[0]:
            output = function(*params[1])
        else:
            output = function()
        time = datetime.now().strftime("%H-%M-%S")
        
        if not csv:
            # JSON Export
            path_to_export = f"statz_export_{date.today()}_{time}.json"
            with open(path_to_export, "w") as f:
                json.dump(output, f, indent=2)
        else:
            # CSV Export
            path_to_export = f"statz_export_{date.today()}_{time}.csv"
            with open(path_to_export, "w", newline='') as f:
                writer = csv_module.writer(f)
                
                if isinstance(output, list):
                    # Check if it's a simple list of dictionaries
                    if output and all(isinstance(item, dict) for item in output):
                        # Standard case: list of dictionaries (like process data)
                        keys = output[0].keys()
                        writer.writerow(keys)
                        for item in output:
                            writer.writerow([str(item.get(key, '')) for key in keys])
                    else:
                        # Check if this looks like hardware usage data (list of 5 items with specific structure)
                        if (len(output) == 5 and 
                            isinstance(output[0], dict) and  # CPU data
                            isinstance(output[1], dict) and  # RAM data
                            isinstance(output[2], list)):    # Disk data
                            format_hardware_usage_csv(output, writer)
                        # Check if this looks like system specs data
                        elif len(output) in [4, 7] and all(isinstance(item, (dict, list)) for item in output):
                            format_system_specs_csv(output, writer)
                        else:
                            # Generic complex list with mixed types or nested structures
                            flattened = flatten_for_csv(output)
                            writer.writerow(['Key', 'Value'])
                            for key, value in flattened.items():
                                writer.writerow([key, value])
                elif isinstance(output, dict):
                    # Check if this looks like temperature data or other simple key-value dicts
                    if all(isinstance(v, (int, float, str)) for v in output.values()):
                        # Simple dictionary - likely temperature or similar sensor data
                        format_simple_dict_csv(output, writer, 'Sensor')
                    else:
                        # Complex dictionary with nested structures
                        flattened = flatten_for_csv(output)
                        writer.writerow(['Key', 'Value'])
                        for key, value in flattened.items():
                            writer.writerow([key, value])
                elif isinstance(output, tuple):
                    # Tuple - treat as multiple columns in one row
                    writer.writerow([f'Column_{i+1}' for i in range(len(output))])
                    writer.writerow([str(item) for item in output])
                else:
                    # Single value or other types
                    writer.writerow(['Value'])
                    writer.writerow([str(output)])
        
        print(f"Export completed: {path_to_export}")
        
    except Exception as e:
        print(f"Error exporting to file: {e}")

def compare(current_specs_path, baseline_specs_path):
    '''
    Compare current system specs against a baseline file (JSON or CSV).
    
    Args:
        current_specs_path (str): Path to current specs file to compare.
        baseline_specs_path (str): Path to baseline specs file to compare against.
    
    Returns:
        dict: Dictionary with 'added', 'removed', and 'changed' keys showing differences.
    '''
    import csv as csv_module
    
    def load_json_file(path):
        """Load JSON file and return data."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def load_csv_file(path):
        """Load CSV file and convert to dictionary structure."""
        data = {}
        with open(path, 'r', newline='') as f:
            reader = csv_module.DictReader(f)
            for i, row in enumerate(reader):
                component = row.get('Component', f'row_{i}')
                property_name = row.get('Property', f'prop_{i}')
                value = row.get('Value', '')
                
                if component not in data:
                    data[component] = {}
                
                data[component][property_name] = value
        return data
    
    def normalize_json_data(data):
        """Convert JSON list format to comparable dictionary structure."""
        if isinstance(data, list):
            # Convert list of dictionaries to component-based structure
            normalized = {}
            component_counters = {}
            
            for item in data:
                if isinstance(item, dict):
                    # Try to determine component type from the data
                    if 'system' in item or 'version' in item:
                        component_name = 'OS'
                    elif 'name' in item and ('Intel' in str(item.get('name', '')) or 'AMD' in str(item.get('name', '')) or 'Core' in str(item.get('name', ''))):
                        if 'Graphics' in str(item.get('name', '')) or 'NVIDIA' in str(item.get('name', '')):
                            component_counters['GPU'] = component_counters.get('GPU', 0) + 1
                            component_name = f"GPU {component_counters['GPU']}"
                        else:
                            component_name = 'CPU'
                    elif 'capacity' in item or ('speed' in item and 'name' not in item):
                        component_counters['Memory'] = component_counters.get('Memory', 0) + 1
                        component_name = f"Memory {component_counters['Memory']}"
                    elif 'size' in item or 'model' in item:
                        component_counters['Storage'] = component_counters.get('Storage', 0) + 1
                        component_name = f"Storage {component_counters['Storage']}"
                    elif 'adapter' in item or ('description' in item and 'Intel' not in str(item.get('description', ''))):
                        component_counters['Network'] = component_counters.get('Network', 0) + 1
                        component_name = f"Network {component_counters['Network']}"
                    elif 'percent' in item or 'pluggedIn' in item:
                        component_name = 'Battery'
                    else:
                        # Unknown component
                        component_counters['Unknown'] = component_counters.get('Unknown', 0) + 1
                        component_name = f"Unknown {component_counters['Unknown']}"
                    
                    # Convert all values to strings for consistent comparison
                    string_item = {}
                    for k, v in item.items():
                        string_item[k] = str(v)
                    
                    normalized[component_name] = string_item
                elif isinstance(item, list):
                    # Handle nested lists (like GPU arrays)
                    for j, subitem in enumerate(item):
                        if isinstance(subitem, dict):
                            component_counters['GPU'] = component_counters.get('GPU', 0) + 1
                            # Convert all values to strings
                            string_subitem = {}
                            for k, v in subitem.items():
                                string_subitem[k] = str(v)
                            normalized[f"GPU {component_counters['GPU']}"] = string_subitem
            
            return normalized
        return data
    
    def deep_compare(dict1, dict2, path=""):
        """Recursively compare two dictionaries."""
        differences = {'added': {}, 'removed': {}, 'changed': {}}
        
        # Ensure both inputs are dictionaries
        if not isinstance(dict1, dict):
            dict1 = {}
        if not isinstance(dict2, dict):
            dict2 = {}
        
        # Check for removed and changed items
        for key in dict1:
            # Ensure key is hashable (string)
            key_str = str(key)
            current_path = f"{path}.{key_str}" if path else key_str
            
            if key not in dict2:
                differences['removed'][current_path] = str(dict1[key])[:100]
            elif isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                # Recursively compare nested dictionaries
                nested_diff = deep_compare(dict1[key], dict2[key], current_path)
                differences['added'].update(nested_diff['added'])
                differences['removed'].update(nested_diff['removed'])
                differences['changed'].update(nested_diff['changed'])
            elif str(dict1[key]) != str(dict2[key]):  # Compare as strings for consistency
                # Only add to changed if the values are actually different
                val1 = str(dict1[key]).strip()
                val2 = str(dict2[key]).strip()
                if val1 != val2:
                    differences['changed'][current_path] = {
                        'from': val1[:100],  # Limit string length
                        'to': val2[:100]     # Limit string length
                    }
        
        # Check for added items
        for key in dict2:
            key_str = str(key)
            current_path = f"{path}.{key_str}" if path else key_str
            if key not in dict1:
                differences['added'][current_path] = str(dict2[key])[:100]  # Limit string length
        
        return differences
    
    try:
        current_ext = current_specs_path.split(".")[-1].lower()
        baseline_ext = baseline_specs_path.split(".")[-1].lower()
        
        if current_ext == "json":
            current_data = load_json_file(current_specs_path)
            current_data = normalize_json_data(current_data)
        elif current_ext == "csv":
            current_data = load_csv_file(current_specs_path)
        else:
            raise ValueError(f"Unsupported file type: {current_ext}")
        
        if baseline_ext == "json":
            baseline_data = load_json_file(baseline_specs_path)
            baseline_data = normalize_json_data(baseline_data)
        elif baseline_ext == "csv":
            baseline_data = load_csv_file(baseline_specs_path)
        else:
            raise ValueError(f"Unsupported file type: {baseline_ext}")
        
        differences = deep_compare(baseline_data, current_data)
        
        differences['summary'] = {
            'total_added': len(differences['added']),
            'total_removed': len(differences['removed']),
            'total_changed': len(differences['changed']),
            'current_file': current_specs_path,
            'baseline_file': baseline_specs_path
        }
        
        return differences
        
    except FileNotFoundError as e:
        return {
            "added": {"error": f"File not found: {e}"},
            "removed": {"error": f"File not found: {e}"},
            "changed": {"error": f"File not found: {e}"}
        }
    except Exception as e:
        return {
            "added": {"error": f"Comparison failed: {str(e)}"},
            "removed": {"error": f"Comparison failed: {str(e)}"},
            "changed": {"error": f"Comparison failed: {str(e)}"}
        }


if __name__ == "__main__":
    print(compare("C:\\Users\\sarik\\Documents\\Code\\statz\\statz\\statz_export_2025-07-23_15-13-05.json", "C:\\Users\\sarik\\Documents\\Code\\statz\\statz\\statz_export_2025-07-23_15-13-13.csv"))