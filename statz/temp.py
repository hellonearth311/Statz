'''Temperature monitoring module for cross-platform system sensors.
This module provides a unified interface to retrieve temperature readings'''

import platform

from .internal._getMacInfo import _get_mac_temps
from .internal._getLinuxInfo import _get_linux_temps
from .internal._getWindowsInfo import _get_windows_temps

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