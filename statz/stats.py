'''System monitoring and statistics module for cross-platform systems.
This module provides a unified interface to retrieve hardware usage, system specifications,
top processes, and export data to files in JSON or CSV format.'''

from .internal._getMacInfo import _get_mac_specs
from .internal._getWindowsInfo import _get_windows_specs
from .internal._getLinuxInfo import _get_linux_specs
from .internal._crossPlatform import _get_usage, _get_top_n_processes

import platform
from datetime import datetime, date
import json

__version__ = "2.0.0"

def get_hardware_usage(get_cpu=True, get_ram=True, get_disk=True, get_network=True, get_battery=True, **kwargs):
    '''
    Get real-time usage data for specified system components. 

    This function allows you to specify which components to fetch data for, improving performance by avoiding unnecessary computations.

    Args:
        get_cpu (bool): Whether to fetch CPU usage data.
        get_ram (bool): Whether to fetch RAM usage data.
        get_disk (bool): Whether to fetch disk usage data.
        get_network (bool): Whether to fetch network usage data.
        get_battery (bool): Whether to fetch battery usage data.
        **kwargs: Additional keyword arguments to ensure compatibility with CLI logic.

    Returns:
        list: A list containing usage data for the specified components in the following order:
        [cpu_usage (dict), ram_usage (dict), disk_usages (list of dicts), network_usage (dict), battery_usage (dict)]
    ''' 
    operatingSystem = platform.system()

    if operatingSystem == "Darwin" or operatingSystem == "Linux" or operatingSystem == "Windows":
        return _get_usage(get_cpu, get_ram, get_disk, get_network, get_battery)
    else:
        raise OSError("Unsupported operating system")

def get_system_specs(get_os=True, get_cpu=True, get_gpu=True, get_ram=True, get_disk=True, get_network=True, get_battery=True):
    '''
    Get system specs on all platforms with selective fetching.

    This function allows you to specify which components to fetch data for, improving performance by avoiding unnecessary computations.

    Args:
        get_os (bool): Whether to fetch OS specs.
        get_cpu (bool): Whether to fetch CPU specs.
        get_gpu (bool): Whether to fetch GPU specs (Windows only).
        get_ram (bool): Whether to fetch RAM specs.
        get_disk (bool): Whether to fetch disk specs.
        get_network (bool): Whether to fetch network specs (Windows only).
        get_battery (bool): Whether to fetch battery specs (Windows only).

    Returns:
        list: A list containing specs data for the specified components. The structure of the list varies by platform:

        **macOS/Linux**:
        [os_info (dict), cpu_info (dict), mem_info (dict), disk_info (dict)]

        **Windows**:
        [os_data (dict), cpu_data (dict), gpu_data_list (list of dicts), ram_data_list (list of dicts),
        storage_data_list (list of dicts), network_data (dict), battery_data (dict)]

    Raises:
        OSError: If the operating system is unsupported.

    Note:
        - On macOS and Linux, GPU, network, and battery specs are not available.
        - On Windows, GPU, network, and battery specs are included if requested.
    '''
    operatingSystem = platform.system()

    if operatingSystem == "Darwin":  # macOS
        return _get_mac_specs(get_os, get_cpu, get_ram, get_disk)
    elif operatingSystem == "Linux":  # Linux
        return _get_linux_specs(get_os, get_cpu, get_ram, get_disk)
    elif operatingSystem == "Windows":  # Windows
        return _get_windows_specs(get_os, get_cpu, get_gpu, get_ram, get_disk, get_network, get_battery)
    else:
        raise OSError("Unsupported operating system")

def get_top_n_processes(n=5, type="cpu"):
    '''
    Get the top N processes sorted by CPU or memory usage.
    
    This function retrieves a list of the most resource-intensive processes currently running
    on the system, sorted by either CPU usage percentage or memory usage in MB/GB.
    
    Args:
        n (int, optional): Number of top processes to return. Defaults to 5.
        type (str, optional): Sort criteria - either "cpu" for CPU usage or "mem" for memory usage. 
                             Defaults to "cpu".
    
    Returns:
        list: List of dictionaries containing process information, sorted by the specified usage type.
        Each dictionary contains:
        - "pid" (int): Process ID
        - "name" (str): Process name/command
        - "usage" (float or str): For CPU: percentage (0-100), For memory: formatted string like "512 MB" or "1.2 GB"
        
        Example (CPU):
        [
            {"pid": 1234, "name": "chrome", "usage": 15.2},
            {"pid": 5678, "name": "python", "usage": 8.7}
        ]
        
        Example (Memory):
        [
            {"pid": 1234, "name": "chrome", "usage": "1.2 GB"},
            {"pid": 5678, "name": "python", "usage": "512 MB"}
        ]
    
    Raises:
        TypeError: If n is not an integer or type is not "cpu" or "mem".
        
    Note:
        - CPU usage is measured as a percentage of total CPU capacity
        - Memory usage is shown in absolute values (MB/GB) for better clarity
        - Processes with None values for the requested metric are filtered out
        - Some processes may not be accessible due to permission restrictions
    '''
    return _get_top_n_processes(n, type)

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