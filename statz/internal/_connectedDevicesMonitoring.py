"""
Cross-Platform Connected Devices Monitoring
Gets detailed information about USB-connected devices on Windows, macOS, and Linux
"""

import subprocess
import json
import re
import platform
import os
from typing import Dict, List, Optional, Any

# Platform-specific imports
CURRENT_OS = platform.system().lower()

if CURRENT_OS == "windows":
    try:
        import ctypes
        from ctypes import wintypes, Structure, POINTER, byref, c_char_p, c_wchar_p
        import winreg
        WINDOWS_API_AVAILABLE = True
    except ImportError:
        WINDOWS_API_AVAILABLE = False
else:
    WINDOWS_API_AVAILABLE = False

def get_usb_devices_linux():
    """Get USB devices on Linux using lsusb and sysfs"""
    devices = []
    
    try:
        # Method 1: Use lsusb command
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    # Parse lsusb output: Bus 001 Device 002: ID 1d6b:0002 Linux Foundation 2.0 root hub
                    match = re.match(r'Bus (\d+) Device (\d+): ID ([0-9a-fA-F]{4}):([0-9a-fA-F]{4}) (.+)', line)
                    if match:
                        bus, device, vid, pid, name = match.groups()
                        
                        device_info = {
                            'device_id': f"USB\\VID_{vid.upper()}&PID_{pid.upper()}",
                            'name': name.strip(),
                            'manufacturer': 'Unknown',
                            'device_class': 'USB Device',
                            'status': 'OK',
                            'connection_type': 'USB',
                            'bus': bus,
                            'device_number': device,
                            'specs': {
                                'vendor_id': vid.upper(),
                                'product_id': pid.upper(),
                                'bus_number': bus,
                                'device_number': device,
                                'interface_version': 'USB',
                                'speed': 'Unknown',
                                'device_type': classify_device_linux(name),
                                'function': get_device_function(name)
                            }
                        }
                        
                        # Get additional info from sysfs
                        sysfs_info = get_sysfs_info(bus, device)
                        device_info['specs'].update(sysfs_info)
                        
                        devices.append(device_info)
        
        # Method 2: Parse /sys/bus/usb/devices/ directly
        if not devices:
            devices = get_usb_devices_sysfs()
    
    except Exception as e:
        pass
    
    return devices

def get_sysfs_info(bus, device):
    """Get additional USB device info from sysfs on Linux"""
    info = {}
    
    try:
        # Find device in sysfs
        sysfs_paths = [
            f"/sys/bus/usb/devices/{bus}-{device}",
            f"/sys/bus/usb/devices/usb{bus}/{bus}-{device}"
        ]
        
        for sysfs_path in sysfs_paths:
            if os.path.exists(sysfs_path):
                # Read various attributes
                attributes = [
                    ('manufacturer', 'manufacturer'),
                    ('product', 'product'),
                    ('serial', 'serial'),
                    ('speed', 'speed'),
                    ('version', 'version'),
                    ('maxchild', 'maxchild'),
                    ('bDeviceClass', 'bDeviceClass'),
                    ('bDeviceSubClass', 'bDeviceSubClass')
                ]
                
                for attr_name, file_name in attributes:
                    try:
                        with open(os.path.join(sysfs_path, file_name), 'r') as f:
                            info[attr_name] = f.read().strip()
                    except:
                        pass
                break
    
    except Exception as e:
        pass
    
    return info

def get_usb_devices_sysfs():
    """Get USB devices by parsing sysfs directly on Linux"""
    devices = []
    
    try:
        usb_devices_path = "/sys/bus/usb/devices"
        if os.path.exists(usb_devices_path):
            for device_dir in os.listdir(usb_devices_path):
                device_path = os.path.join(usb_devices_path, device_dir)
                if os.path.isdir(device_path) and re.match(r'\d+-\d+', device_dir):
                    device_info = parse_sysfs_device(device_path, device_dir)
                    if device_info:
                        devices.append(device_info)
    
    except Exception as e:
        pass
    
    return devices

def parse_sysfs_device(device_path, device_dir):
    """Parse individual USB device from sysfs"""
    try:
        device_info = {
            'device_id': f"USB\\{device_dir}",
            'name': 'Unknown Device',
            'manufacturer': 'Unknown',
            'device_class': 'USB Device',
            'status': 'OK',
            'connection_type': 'USB',
            'specs': {
                'interface_version': 'USB',
                'speed': 'Unknown',
                'device_type': 'Generic USB Device',
                'function': 'Unknown'
            }
        }
        
        # Read device attributes
        attributes = {
            'idVendor': 'vendor_id',
            'idProduct': 'product_id',
            'manufacturer': 'manufacturer',
            'product': 'product',
            'serial': 'serial_number',
            'speed': 'speed',
            'version': 'interface_version'
        }
        
        for file_name, info_key in attributes.items():
            try:
                with open(os.path.join(device_path, file_name), 'r') as f:
                    value = f.read().strip()
                    if info_key in ['manufacturer', 'product']:
                        if info_key == 'manufacturer':
                            device_info['manufacturer'] = value
                        elif info_key == 'product':
                            device_info['name'] = value
                    else:
                        device_info['specs'][info_key] = value
            except:
                pass
        
        # Classify device type
        device_info['specs']['device_type'] = classify_device_linux(device_info['name'])
        device_info['specs']['function'] = get_device_function(device_info['name'])
        
        return device_info
    
    except Exception as e:
        return None

def get_usb_devices_macos():
    """Get USB devices on macOS using system_profiler"""
    devices = []
    
    try:
        # Use system_profiler to get USB information
        result = subprocess.run(['system_profiler', 'SPUSBDataType', '-json'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            usb_data = data.get('SPUSBDataType', [])
            
            for usb_controller in usb_data:
                devices.extend(parse_macos_usb_tree(usb_controller))
    
    except Exception as e:
        pass
    
    return devices

def parse_macos_usb_tree(usb_node, parent_path=""):
    """Recursively parse macOS USB device tree"""
    devices = []
    
    try:
        # Parse current node if it's a device
        if '_name' in usb_node and usb_node['_name'] != 'USB Bus':
            device_info = {
                'device_id': f"USB\\{usb_node.get('location_id', 'Unknown')}",
                'name': usb_node.get('_name', 'Unknown Device'),
                'manufacturer': usb_node.get('manufacturer', 'Unknown'),
                'device_class': 'USB Device',
                'status': 'OK',
                'connection_type': 'USB',
                'specs': {
                    'vendor_id': usb_node.get('vendor_id', 'Unknown'),
                    'product_id': usb_node.get('product_id', 'Unknown'),
                    'serial_number': usb_node.get('serial_num', 'Unknown'),
                    'speed': usb_node.get('speed', 'Unknown'),
                    'interface_version': f"USB {usb_node.get('usb_version', 'Unknown')}",
                    'location_id': usb_node.get('location_id', 'Unknown'),
                    'device_type': classify_device_macos(usb_node.get('_name', '')),
                    'function': get_device_function(usb_node.get('_name', ''))
                }
            }
            
            # Add power information if available
            if 'current_available' in usb_node:
                device_info['specs']['current_available'] = f"{usb_node['current_available']} mA"
            if 'current_required' in usb_node:
                device_info['specs']['current_required'] = f"{usb_node['current_required']} mA"
            
            devices.append(device_info)
        
        # Recursively parse child devices
        if '_items' in usb_node:
            for child in usb_node['_items']:
                devices.extend(parse_macos_usb_tree(child, parent_path))
    
    except Exception as e:
        pass
    
    return devices

def classify_device_linux(device_name):
    """Classify device type based on name for Linux"""
    name_lower = device_name.lower()
    
    if 'hub' in name_lower or 'root hub' in name_lower:
        return 'USB Hub'
    elif 'storage' in name_lower or 'disk' in name_lower or 'mass storage' in name_lower:
        return 'Mass Storage'
    elif 'mouse' in name_lower:
        return 'HID Device'
    elif 'keyboard' in name_lower:
        return 'HID Device'
    elif 'camera' in name_lower or 'webcam' in name_lower:
        return 'Video Device'
    elif 'audio' in name_lower or 'sound' in name_lower:
        return 'Audio Device'
    elif 'network' in name_lower or 'ethernet' in name_lower or 'wifi' in name_lower:
        return 'Network Adapter'
    elif 'bluetooth' in name_lower:
        return 'Bluetooth Adapter'
    elif 'printer' in name_lower:
        return 'Printer'
    else:
        return 'Generic USB Device'

def classify_device_macos(device_name):
    """Classify device type based on name for macOS"""
    return classify_device_linux(device_name)  # Same logic works for macOS

def get_device_function(device_name):
    """Get device function based on its type"""
    device_type = classify_device_linux(device_name)
    
    function_map = {
        'USB Hub': 'Port Expansion',
        'Mass Storage': 'Data Storage',
        'HID Device': 'Human Interface',
        'Video Device': 'Video Capture',
        'Audio Device': 'Audio Processing',
        'Network Adapter': 'Network Communication',
        'Bluetooth Adapter': 'Wireless Communication',
        'Printer': 'Document Printing'
    }
    
    return function_map.get(device_type, 'Unknown')

def get_usb_devices_windows():
    """Get USB devices on Windows using WMI and PowerShell"""
    devices = []
    
    try:
        # Method 1: Use WMI via wmic command
        cmd = ['wmic', 'path', 'Win32_PnPEntity', 'where', 
               'PNPDeviceID like "USB%"', 'get', 
               'Name,Manufacturer,DeviceID,Status,PNPClass', '/format:csv']
        
        result = subprocess.run(cmd, capture_output=True, text=True, 
                              creationflags=subprocess.CREATE_NO_WINDOW)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                if line.strip() and ',' in line:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 6 and parts[1]:  # Has device ID
                        device_info = {
                            'device_id': parts[1],
                            'name': parts[5] if parts[5] else 'Unknown Device',
                            'manufacturer': parts[4] if parts[4] else 'Unknown Manufacturer',
                            'status': parts[6] if len(parts) > 6 and parts[6] else 'Unknown',
                            'device_class': parts[3] if parts[3] else 'USB Device',
                            'connection_type': 'USB',
                            'specs': parse_usb_specs_windows(parts[1], parts[5] if parts[5] else '')
                        }
                        devices.append(device_info)
        
        # Method 2: Fallback to PowerShell if WMI fails
        if not devices:
            devices = get_usb_devices_powershell()
    
    except Exception as e:
        # Final fallback to PowerShell
        try:
            devices = get_usb_devices_powershell()
        except:
            pass
    
    return devices

def parse_usb_specs_windows(device_id, device_name):
    """Parse USB device specifications from Windows device ID and name"""
    specs = {
        'interface_version': 'Unknown',
        'speed': 'Unknown',
        'vendor_id': 'Unknown',
        'product_id': 'Unknown',
        'revision': 'Unknown',
        'device_type': 'Generic USB Device',
        'function': 'Unknown'
    }
    
    try:
        # Parse VID (Vendor ID) and PID (Product ID)
        vid_match = re.search(r'VID_([0-9A-Fa-f]{4})', device_id)
        pid_match = re.search(r'PID_([0-9A-Fa-f]{4})', device_id)
        rev_match = re.search(r'REV_([0-9A-Fa-f]{4})', device_id)
        
        if vid_match:
            specs['vendor_id'] = vid_match.group(1).upper()
        if pid_match:
            specs['product_id'] = pid_match.group(1).upper()
        if rev_match:
            specs['revision'] = rev_match.group(1).upper()
        
        # Determine USB version from device ID
        if 'USB\\VID_' in device_id.upper():
            if 'USB30' in device_id.upper() or 'USB3' in device_id.upper():
                specs['interface_version'] = 'USB 3.0+'
                specs['speed'] = 'SuperSpeed (5 Gbps)'
            elif 'USB20' in device_id.upper() or 'USB2' in device_id.upper():
                specs['interface_version'] = 'USB 2.0'
                specs['speed'] = 'High Speed (480 Mbps)'
            elif 'USB11' in device_id.upper() or 'USB1' in device_id.upper():
                specs['interface_version'] = 'USB 1.1'
                specs['speed'] = 'Full Speed (12 Mbps)'
            else:
                specs['interface_version'] = 'USB (Version Unknown)'
        
        # Classify device type
        specs['device_type'] = classify_device_linux(device_name)  # Same logic works
        specs['function'] = get_device_function(device_name)
    
    except Exception as e:
        pass
    
    return specs

def get_usb_devices_powershell():
    """Get USB devices using PowerShell as Windows fallback method"""
    devices = []
    
    try:
        powershell_cmd = '''
        Get-WmiObject -Class Win32_PnPEntity | Where-Object {$_.DeviceID -like "USB*"} | ForEach-Object {
            $props = @{
                DeviceID = $_.DeviceID
                Name = $_.Name
                Manufacturer = $_.Manufacturer
                Status = $_.Status
                PNPClass = $_.PNPClass
            }
            $props | ConvertTo-Json -Compress
        }
        '''
        
        result = subprocess.run(['powershell', '-Command', powershell_cmd], 
                              capture_output=True, text=True, 
                              creationflags=subprocess.CREATE_NO_WINDOW)
        
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    try:
                        device_data = json.loads(line)
                        device_info = {
                            'device_id': device_data.get('DeviceID', 'Unknown'),
                            'name': device_data.get('Name', 'Unknown Device'),
                            'manufacturer': device_data.get('Manufacturer', 'Unknown Manufacturer'),
                            'status': device_data.get('Status', 'Unknown'),
                            'device_class': device_data.get('PNPClass', 'USB Device'),
                            'connection_type': 'USB',
                            'specs': parse_usb_specs_windows(
                                device_data.get('DeviceID', ''), 
                                device_data.get('Name', '')
                            )
                        }
                        devices.append(device_info)
                    except json.JSONDecodeError:
                        continue
    
    except Exception as e:
        pass
    
    return devices

def get_connected_usb_devices():
    """
    Cross-platform function to get connected USB devices
    
    Returns:
        dict: Dictionary containing USB device information
    """
    try:
        devices = []
        method_used = "Unknown"
        
        if CURRENT_OS == "linux":
            devices = get_usb_devices_linux()
            method_used = "Linux lsusb/sysfs"
        elif CURRENT_OS == "darwin":  # macOS
            devices = get_usb_devices_macos()
            method_used = "macOS system_profiler"
        elif CURRENT_OS == "windows":
            devices = get_usb_devices_windows()
            method_used = "Windows Setup API/WMI"
        else:
            return {
                'total_usb_devices': 0,
                'devices': [],
                'summary': {},
                'error': f"Unsupported operating system: {CURRENT_OS}"
            }
        
        # Remove duplicates and sort
        unique_devices = {}
        for device in devices:
            device_id = device.get('device_id', 'Unknown')
            if device_id not in unique_devices:
                unique_devices[device_id] = device
        
        devices_list = list(unique_devices.values())
        devices_list.sort(key=lambda x: x.get('name', 'Unknown'))
        
        return {
            'total_usb_devices': len(devices_list),
            'devices': devices_list,
            'summary': {
                'hubs': len([d for d in devices_list if 'hub' in d.get('specs', {}).get('device_type', '').lower()]),
                'storage_devices': len([d for d in devices_list if 'storage' in d.get('specs', {}).get('device_type', '').lower()]),
                'input_devices': len([d for d in devices_list if 'hid' in d.get('specs', {}).get('device_type', '').lower()]),
                'audio_devices': len([d for d in devices_list if 'audio' in d.get('specs', {}).get('device_type', '').lower()]),
                'network_devices': len([d for d in devices_list if 'network' in d.get('specs', {}).get('device_type', '').lower()]),
                'other_devices': len([d for d in devices_list if d.get('specs', {}).get('device_type', '') == 'Generic USB Device'])
            },
            'method_used': method_used,
            'platform': CURRENT_OS
        }
    
    except Exception as e:
        return {
            'total_usb_devices': 0,
            'devices': [],
            'summary': {},
            'error': f"Failed to get USB devices: {str(e)}",
            'platform': CURRENT_OS
        }

# Keep the existing helper functions for backwards compatibility
def get_device_by_name(device_name):
    """Get specific USB device by name (cross-platform)"""
    try:
        all_devices = get_connected_usb_devices()
        for device in all_devices.get('devices', []):
            if device_name.lower() in device.get('name', '').lower():
                return device
        return None
    except Exception as e:
        return None

def get_devices_by_type(device_type):
    """Get USB devices filtered by type (cross-platform)"""
    try:
        all_devices = get_connected_usb_devices()
        filtered_devices = []
        
        for device in all_devices.get('devices', []):
            device_specs = device.get('specs', {})
            if device_type.lower() in device_specs.get('device_type', '').lower():
                filtered_devices.append(device)
        
        return {
            'device_type': device_type,
            'count': len(filtered_devices),
            'devices': filtered_devices,
            'platform': CURRENT_OS
        }
    except Exception as e:
        return {'device_type': device_type, 'count': 0, 'devices': [], 'error': str(e), 'platform': CURRENT_OS}

# Example usage and testing
if __name__ == "__main__":
    print(f"USB Connected Devices Monitor - {platform.system()}")
    print("=" * 50)
    
    usb_info = get_connected_usb_devices()
    
    print(f"Platform: {usb_info.get('platform', 'Unknown')}")
    print(f"Total USB Devices: {usb_info['total_usb_devices']}")
    print(f"Method Used: {usb_info.get('method_used', 'Unknown')}")
    
    if usb_info.get('error'):
        print(f"Error: {usb_info['error']}")
    
    if usb_info.get('summary'):
        print("\nDevice Summary:")
        for device_type, count in usb_info['summary'].items():
            print(f"  {device_type.replace('_', ' ').title()}: {count}")
    
    print("\nDetailed Device Information:")
    print("-" * 50)
    
    for i, device in enumerate(usb_info.get('devices', []), 1):
        print(f"\n{i}. {device.get('name', 'Unknown Device')}")
        print(f"   Manufacturer: {device.get('manufacturer', 'Unknown')}")
        print(f"   Device Class: {device.get('device_class', 'Unknown')}")
        print(f"   Status: {device.get('status', 'Unknown')}")
        
        specs = device.get('specs', {})
        if specs:
            print(f"   Specifications:")
            for spec_key, spec_value in specs.items():
                if spec_value and spec_value != 'Unknown':
                    print(f"     {spec_key.replace('_', ' ').title()}: {spec_value}")