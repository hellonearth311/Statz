import platform
import psutil
import subprocess
import re

def _get_linux_specs():
    '''
    Get system specifications for Linux systems.\n
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
    # os info
    os_info = {}

    os_info["system"] = platform.system()
    os_info["nodeName"] = platform.node()
    os_info["release"] = platform.release()
    os_info["version"] = platform.version()
    os_info["machine"] = platform.machine()

    # cpu info
    cpu_info = {}   

    cpu_info["processor"] = platform.processor()
    cpu_info["coreCountPhysical"] = psutil.cpu_count(logical=False)
    cpu_info["coreCountLogical"] = psutil.cpu_count()
    
    # get cpu name from /proc/cpuinfo
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if 'model name' in line:
                    cpu_info["cpuName"] = line.split(':')[1].strip()
                    break
        if "cpuName" not in cpu_info:
            cpu_info["cpuName"] = "Unknown"
    except:
        cpu_info["cpuName"] = "Unknown"
    
    # get cpu frequency from /proc/cpuinfo
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if 'cpu MHz' in line:
                    freq = float(line.split(':')[1].strip())
                    cpu_info["cpuFrequency"] = f"{freq:.2f} MHz"
                    break
        if "cpuFrequency" not in cpu_info:
            cpu_info["cpuFrequency"] = "Unknown"
    except:
        cpu_info["cpuFrequency"] = "Unknown"

    # ram info
    mem_info = {}

    svmem = psutil.virtual_memory()
    mem_info["totalRAM"] = f"{svmem.total / (1024**3):.2f} GB"
    
    # get ram frequency using dmidecode
    try:
        memory_result = subprocess.run(['dmidecode', '-t', 'memory'], 
                                     capture_output=True, text=True)
        if memory_result.returncode == 0:
            memory_output = memory_result.stdout
            speed_match = re.search(r'Speed:\s*(\d+)\s*MT/s', memory_output, re.IGNORECASE)
            if speed_match:
                mem_info["ramFrequency"] = f"{speed_match.group(1)} MHz"
            else:
                speed_match = re.search(r'Speed:\s*(\d+)\s*MHz', memory_output, re.IGNORECASE)
                if speed_match:
                    mem_info["ramFrequency"] = f"{speed_match.group(1)} MHz"
                else:
                    mem_info["ramFrequency"] = "Unknown"
        else:
            mem_info["ramFrequency"] = "Unknown"
    except:
        mem_info["ramFrequency"] = "Unknown"

    # disk info
    disk_info = {}

    disk_usage = psutil.disk_usage('/')
    disk_info["totalSpace"] = f"{disk_usage.total / (1024**3):.2f} GB"
    disk_info["usedSpace"] = f"{disk_usage.used / ((1024**3) / 10):.2f} GB"
    disk_info["freeSpace"] = f"{disk_usage.free / (1024**3):.2f} GB"

    return os_info, cpu_info, mem_info, disk_info

def _get_linux_temps():
    temps = {}
    
    try:
        sensors = psutil.sensors_temperatures()
        if sensors:
            for sensor_name, sensor_list in sensors.items():
                for sensor in sensor_list:
                    label = sensor.label if sensor.label else sensor_name
                    if sensor.current:
                        temps[label] = f"{sensor.current:.1f}°C"
                        
                        if sensor.high:
                            temps[f"{label} (High)"] = f"{sensor.high:.1f}°C"
                        if sensor.critical:
                            temps[f"{label} (Critical)"] = f"{sensor.critical:.1f}°C"
    except:
        pass
    
    if not temps:
        try:
            import os
            import glob
            
            thermal_zones = glob.glob('/sys/class/thermal/thermal_zone*/temp')
            for zone_path in thermal_zones:
                try:
                    with open(zone_path, 'r') as f:
                        temp_millidegree = int(f.read().strip())
                        temp_celsius = temp_millidegree / 1000.0
                        
                        zone_dir = os.path.dirname(zone_path)
                        zone_name = os.path.basename(zone_dir)
                        
                        try:
                            with open(os.path.join(zone_dir, 'type'), 'r') as type_file:
                                zone_type = type_file.read().strip()
                                sensor_name = f"{zone_type} ({zone_name})"
                        except:
                            sensor_name = zone_name
                        
                        temps[sensor_name] = f"{temp_celsius:.1f}°C"
                except:
                    continue
        except:
            pass
    
    if not temps:
        try:
            result = subprocess.run(['sensors', '-A'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.splitlines()
                current_chip = None
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if ':' not in line and not line.startswith(' '):
                        current_chip = line
                        continue
                    
                    if '°C' in line and ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            sensor_name = parts[0].strip()
                            temp_part = parts[1].strip()
                            
                            temp_match = re.search(r'([+-]?\d+\.?\d*)°C', temp_part)
                            if temp_match:
                                temp_value = float(temp_match.group(1))
                                
                                if current_chip:
                                    full_name = f"{current_chip} - {sensor_name}"
                                else:
                                    full_name = sensor_name
                                
                                temps[full_name] = f"{temp_value:.1f}°C"
        except:
            pass
    
    return temps if temps else {"error": "No temperature sensors found"}