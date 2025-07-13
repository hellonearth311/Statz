from ._getMacInfo import _get_mac_specs
from ._getWindowsInfo import _get_windows_specs
from ._getLinuxInfo import _get_linux_specs
from ._getUsage import _get_usage

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
    if platform.system() == "Darwin" or platform.system() == "Linux" or platform.system() == "Windows":
        return _get_usage()
    else:
        raise OSError("Unsupported operating system")

def get_system_specs():
    '''
    # Get system specs on all platforms.\n
    ## On Windows:
    Returns 6 lists/dictionaries: cpu_data, gpu_data_list, ram_data_list, storage_data_list, network_data, and battery_data
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

    if platform.system() == "Darwin": # macOS
        return _get_mac_specs()
    elif platform.system() == "Linux": # Linux
        return _get_linux_specs()
    elif platform.system() == "Windows": # Windows
        return _get_windows_specs()
    else:
        raise OSError("Unsupported operating system")

if __name__ == "__main__":
    print(get_hardware_usage())
    print(get_system_specs())