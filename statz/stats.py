try:
    from ._getMacInfo import _get_mac_specs, _get_mac_temps
    from ._getWindowsInfo import _get_windows_specs, _get_windows_temps
    from ._getLinuxInfo import _get_linux_specs, _get_linux_temps
    from ._getUsage import _get_usage, _get_top_n_processes
except ImportError:
    from _getMacInfo import _get_mac_specs, _get_mac_temps
    from _getWindowsInfo import _get_windows_specs, _get_windows_temps
    from _getLinuxInfo import _get_linux_specs, _get_linux_temps
    from _getUsage import _get_usage, _get_top_n_processes

import platform
from datetime import datetime, date
import json

def get_hardware_usage(get_cpu=True, get_ram=True, get_disk=True, get_network=True, get_battery=True):
    '''
    Get real-time usage data for specified system components. 

    This function allows you to specify which components to fetch data for, improving performance by avoiding unnecessary computations.

    Args:
        get_cpu (bool): Whether to fetch CPU usage data.
        get_ram (bool): Whether to fetch RAM usage data.
        get_disk (bool): Whether to fetch disk usage data.
        get_network (bool): Whether to fetch network usage data.
        get_battery (bool): Whether to fetch battery usage data.

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

def get_system_temps():
    '''
    Get temperature readings from system sensors across all platforms.
    
    This function provides cross-platform temperature monitoring by detecting the operating system
    and calling the appropriate platform-specific temperature reading function.
    
    Returns:
        dict or None: Temperature data structure varies by platform:
        
        **macOS**: Dictionary with sensor names as keys and temperatures in Celsius as values
        Example: {"CPU": 45.2, "GPU": 38.5, "Battery": 32.1}
        
        **Linux**: Dictionary with sensor names as keys and temperatures in Celsius as values
        Example: {"coretemp-isa-0000": 42.0, "acpi-0": 35.5}
        
        **Windows**: Dictionary with thermal zone names as keys and temperatures in Celsius as values
        Example: {"ThermalZone _TZ.TZ00": 41.3, "ThermalZone _TZ.TZ01": 38.9}
        
        Returns None if temperature sensors are not available or accessible on the system.
    
    Raises:
        Exception: If temperature reading fails due to system access issues or sensor unavailability.
    
    Note:
        - Temperature readings may require elevated privileges on some systems
        - Not all systems expose temperature sensors through standard interfaces
        - Results vary based on available hardware sensors and system configuration
    '''
    operatingSystem = platform.system()

    if operatingSystem == "Darwin": # macOS
        return _get_mac_temps()
    elif operatingSystem == "Linux":  # Linux
        return _get_linux_temps()
    elif operatingSystem == "Windows": # Windows:
        return _get_windows_temps()

def get_top_n_processes(n=5, type="cpu"):
    '''
    Get the top N processes sorted by CPU or memory usage.
    
    This function retrieves a list of the most resource-intensive processes currently running
    on the system, sorted by either CPU usage percentage or memory usage percentage.
    
    Args:
        n (int, optional): Number of top processes to return. Defaults to 5.
        type (str, optional): Sort criteria - either "cpu" for CPU usage or "mem" for memory usage. 
                             Defaults to "cpu".
    
    Returns:
        list: List of dictionaries containing process information, sorted by the specified usage type.
        Each dictionary contains:
        - "pid" (int): Process ID
        - "name" (str): Process name/command
        - "usage" (float): CPU percentage (0-100) or memory percentage (0-100) depending on type
        
        Example:
        [
            {"pid": 1234, "name": "chrome", "usage": 15.2},
            {"pid": 5678, "name": "python", "usage": 8.7},
            {"pid": 9012, "name": "code", "usage": 5.3}
        ]
    
    Raises:
        TypeError: If n is not an integer or type is not "cpu" or "mem".
        
    Note:
        - CPU usage is measured as a percentage of total CPU capacity
        - Memory usage is measured as a percentage of total system memory
        - Processes with None values for the requested metric are filtered out
        - Some processes may not be accessible due to permission restrictions
    '''
    return _get_top_n_processes(n, type)

def export_into_file(function):
    '''
    Export the output of a function to a text file.
    
    This utility function takes another function as input, executes it,
    and writes the output to a file named "statz_export_{date}_{time}.json".
    
    Args:
        function (callable): The function whose output is to be exported.
    '''
    try:
        output = function()
        time = datetime.now().strftime("%H-%M-%S")
        path_to_export = f"statz_export_{date.today()}_{time}.json"
        with open(path_to_export, "x") as f:
            json.dump(output, f, indent=2)
    except Exception as e:
        print(f"Error exporting to file: {e}")

if __name__ == "__main__":
    # print(get_hardware_usage())
    # print(get_system_specs())
    # print(get_system_temps())
    # print(get_top_n_processes())
    export_into_file(get_hardware_usage)