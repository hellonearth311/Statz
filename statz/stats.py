from ._getMacInfo import _get_mac_specs, _get_mac_temps
from ._getWindowsInfo import _get_windows_specs, _get_windows_temps
from ._getLinuxInfo import _get_linux_specs, _get_linux_temps
from ._getUsage import _get_usage, _get_top_n_processes

import platform

def get_hardware_usage():
    '''
    Get real-time usage data for most system components. \n
    GPU Usage is **not** supported due to lack of a Python binding for AMD and Intel GPUs.\n

    This function returns a list:\n
    [cpu_usage (dict), ram_usage (dict), disk_usages (list of dicts), network_usage (dict), battery_usage (dict)]

    ### Structure of returned data:
    - cpu_usage (dict):\n
        { "core1": usage percent, "core2": usage percent, ... }\n
    - ram_usage (dict):\n
        { "total": MB, "used": MB, "free": MB, "percent": percent_used }\n
    - disk_usages (list of dicts):\n
        [\n
            {\n
                "device": device_name,\n
                "readSpeed": current_read_speed_MBps,\n
                "writeSpeed": current_write_speed_MBps,\n
            },\n
            ...\n
        ]\n
    - network_usage (dict):\n
        { "up": upload_speed_mbps, "down": download_speed_mbps }\n
    - battery_usage (dict):\n
        { "percent": percent_left, "pluggedIn": is_plugged_in, "timeLeftMins": minutes_left (2147483640 = unlimited) }\n
    ''' 
    operatingSystem = platform.system()

    if operatingSystem == "Darwin" or operatingSystem == "Linux" or operatingSystem == "Windows":
        return _get_usage()
    else:
        raise OSError("Unsupported operating system")

def get_system_specs():
    '''
    # Get system specs on all platforms.\n
    ## On Windows:
    Returns 7 lists/dictionaries: os_data, cpu_data, gpu_data_list, ram_data_list, storage_data_list, network_data, and battery_data
    #### os_data
    {
    "system": The name of your operating system. Ex. Microsoft Windows 10 Pro\n
    "version": OS version number. Ex. 10.0.19042\n
    "buildNumber": OS build number. Ex. 19042\n
    "servicePackMajorVersion": Service pack version. Ex. 0\n
    "architecture": OS architecture. Ex. 64-bit\n
    "manufacturer": OS manufacturer. Ex. Microsoft Corporation\n
    "serialNumber": OS serial number\n
    }
    #### cpu_data
    {
    "name": The name of your CPU. Ex. 11th Gen Intel(R) Core(TM) i5-1135G7 @2.40GHz\n
    "manufacturer": Manufacturer of your CPU. Ex. GenuineIntel\n
    "description": Some architecture information about your CPU. Ex. Intel64 Family 6 Model 140 Stepping 1\n
    "coreCount": Core count of your CPU. Ex. 4\n
    "clockSpeed": The clock speed of your CPU in megahertz. Ex. 2419}
    #### gpu_data_list (list of dicts)
    [
      {\n
        "name": ..., "driverVersion": ..., "videoProcessor": ..., "videoModeDesc": ..., "VRAM": ...\n
      },\n
      ...\n
    ]
    #### ram_data_list (list of dicts)
    [
      {\n
        "capacity": ..., "speed": ..., "manufacturer": ..., "partNumber": ...
      },\n
      ...\n
    ]
    #### storage_data_list (list of dicts)[
      {\n
        "model": ..., "interfaceType": ..., "mediaType": ..., "size": ..., "serialNumber": ...\n
      },\n
      ...\n
    ]
    #### network_data{
    "name": The name of the network adapter. Ex. Intel(R) Wireless-AC 9462\n
    "macAddress": Your MAC Address. Ex. DC:21:48:DF:E9:68\n
    "manufacturer": Who made the device. Ex. Intel Corporation\n
    "adapterType": The type of the adapter, like Ethernet or WiFi. Ex. Ethernet 802.3\n
    "speed": The speed of the adapter in MBPS. Ex. 433.3\n}
    #### battery_data{
    "name": The model of your battery. Ex. NVMe BC711 NVMe SK hynix 256GB\n
    "estimatedChargeRemaining": How much percentage battery you have left. Ex. SCSI\n
    "batteryStatus": Status of the battery. Ex. Charging\n
    "designCapacity": The design capacity of the battery. Ex. 5000 mWh\n
    "fullChargeCapacity": The current capacity of the battery. Ex. 4950 mWh} 

    ### Notes:
    * If anything returns None, it means it could not be found.\n
    * For the GPU, RAM, and Storage, it will return a list with all of your hardware of that category.\n

    ## On Mac
    Returns 4 dictionaries: os_info, cpu_info, mem_info, disk_info
    #### os_info
    {\n
    "system": System/OS Name,\n
    "nodeName": Computer's network name,\n
    "release": Release of the OS,\n
    "version": Release version of the OS,\n
    "machine": Machine type,\n
    }
    #### cpu_info
    {\n
    "processor": Processor name, **not** cpu name eg: amdk6,\n
    "coreCountPhysical": Physical core count,\n
    "coreCountLogical": Logical core count,\n
    "cpuName": Name of the CPU,\n
    "cpuFrequency": CPU Frequency in MHz,\n
    }
    #### mem_info
    {\n
    "totalRAM": Total system memory in GB,\n
    "ramFrequency": RAM frequency in MHZ,\n
    }
    #### disk_info
    {\n
    "totalSpace": Total space in GB,\n
    "usedSpace": Used space in GB,\n
    "freeSpace": Free space in GB,\n

    ## On Linux
    Returns 4 dictionaries: os_info, cpu_info, mem_info, disk_info
    #### os_info
    {\n
    "system": System/OS Name,\n
    "nodeName": Computer's network name,\n
    "release": Release of the OS,\n
    "version": Release version of the OS,\n
    "machine": Machine type,\n
    }
    #### cpu_info
    {\n
    "processor": Processor name, **not** cpu name eg: amdk6,\n
    "coreCountPhysical": Physical core count,\n
    "coreCountLogical": Logical core count,\n
    "cpuName": Name of the CPU,\n
    "cpuFrequency": CPU Frequency in MHz,\n
    }
    #### mem_info
    {\n
    "totalRAM": Total system memory in GB,\n
    "ramFrequency": RAM frequency in MHZ,\n
    }
    #### disk_info
    {\n
    "totalSpace": Total space in GB,\n
    "usedSpace": Used space in GB,\n
    "freeSpace": Free space in GB,\n
    }
    '''
    operatingSystem = platform.system()

    if operatingSystem == "Darwin": # macOS
        return _get_mac_specs()
    elif operatingSystem == "Linux": # Linux
        return _get_linux_specs()
    elif operatingSystem == "Windows": # Windows
        return _get_windows_specs()
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

if __name__ == "__main__":
    print(get_hardware_usage())
    print(get_system_specs())
    print(get_system_temps())
    print(get_top_n_processes())