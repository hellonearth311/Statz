'''System monitoring and statistics module for cross-platform systems.
This module provides a unified interface to retrieve hardware usage, system specifications,
top processes, and export data to files in JSON or CSV format.'''

from .internal._getMacInfo import _get_mac_specs
from .internal._getWindowsInfo import _get_windows_specs
from .internal._getLinuxInfo import _get_linux_specs
from .internal._crossPlatform import _get_usage, _get_top_n_processes

import platform


__version__ = "2.4.0"

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
        usage = _get_usage(get_cpu, get_ram, get_disk, get_network, get_battery)
        return usage
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

def connected_device_monitoring():
    """
    Get information on connected USB devices across all platforms.
    
    This function provides comprehensive information about USB-connected devices
    including specifications, device types, and connection details.
    
    Returns:
        dict: Dictionary containing connected device information with the following structure:
        {
            'total_usb_devices': int,
            'devices': [list of device dictionaries],
            'summary': {
                'hubs': int,
                'storage_devices': int,
                'input_devices': int,
                'audio_devices': int,
                'network_devices': int,
                'other_devices': int
            },
            'method_used': str,
            'platform': str
        }
        
        Each device dictionary contains:
        - device_id: Unique device identifier
        - name: Human-readable device name
        - manufacturer: Device manufacturer
        - device_class: Device class/category
        - status: Device status
        - connection_type: Connection type (USB)
        - specs: Dictionary with detailed specifications including:
            - vendor_id: USB vendor ID
            - product_id: USB product ID
            - interface_version: USB version (1.1, 2.0, 3.0+)
            - speed: Transfer speed
            - device_type: Classified device type
            - function: Device function/purpose
    
    Raises:
        OSError: If the operating system is unsupported.
        
    Note:
        - Windows: Uses WMI and PowerShell for device detection
        - Linux: Uses lsusb command and sysfs filesystem
        - macOS: Uses system_profiler command
    """
    try:
        from .internal._connectedDevicesMonitoring import get_connected_usb_devices
        return get_connected_usb_devices()
    except ImportError as e:
        return {
            'total_usb_devices': 0,
            'devices': [],
            'summary': {},
            'error': f"Connected device monitoring module not available: {str(e)}",
            'platform': platform.system().lower()
        }
    except Exception as e:
        return {
            'total_usb_devices': 0,
            'devices': [],
            'summary': {},
            'error': f"Failed to get connected devices: {str(e)}",
            'platform': platform.system().lower()
        }

def get_connected_device_by_name(device_name):
    """
    Get a specific connected USB device by name.
    
    Args:
        device_name (str): Name or partial name of the device to search for
        
    Returns:
        dict or None: Device information dictionary if found, None otherwise
    """
    try:
        from .internal._connectedDevicesMonitoring import get_device_by_name
        return get_device_by_name(device_name)
    except ImportError:
        return None
    except Exception:
        return None

def get_connected_devices_by_type(device_type):
    """
    Get connected USB devices filtered by type.
    
    Args:
        device_type (str): Type of devices to filter by (e.g., 'storage', 'hid', 'audio', 'network')
        
    Returns:
        dict: Dictionary containing filtered devices with structure:
        {
            'device_type': str,
            'count': int,
            'devices': [list of matching devices],
            'platform': str
        }
    """
    try:
        from .internal._connectedDevicesMonitoring import get_devices_by_type
        return get_devices_by_type(device_type)
    except ImportError:
        return {
            'device_type': device_type, 
            'count': 0, 
            'devices': [], 
            'error': 'Connected device monitoring module not available',
            'platform': platform.system().lower()
        }
    except Exception as e:
        return {
            'device_type': device_type, 
            'count': 0, 
            'devices': [], 
            'error': str(e),
            'platform': platform.system().lower()
        }

def system_integrity_check():
    """
    Scans your system to check for the existence of critical files.
    Returns:
     missing_files (list): A list of missing critical system files.
    """
    userOS = platform.system()
    if userOS == "Windows":
        pass
    else:
        return ["system integrity check is not supported on this os"]