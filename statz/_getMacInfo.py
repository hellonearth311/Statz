import platform
import psutil
import subprocess
import re
import shutil

def _get_mac_specs():
    '''
    Get system specifications for Mac systems.\n
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
    
    # get cpu name using sysctl
    try:
        cpu_name_result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                                       capture_output=True, text=True)
        cpu_info["cpuName"] = cpu_name_result.stdout.strip()
    except:
        cpu_info["cpuName"] = "Unknown"
    
    # get cpu freq using sysctl hw.cpufrequency or hw.cpufrequency_max for AS macs
    try:
        cpu_freq_result = subprocess.run(['sysctl', '-n', 'hw.cpufrequency'], 
                                       capture_output=True, text=True)
        if cpu_freq_result.returncode == 0 and cpu_freq_result.stdout.strip():
            cpu_freq_hz = int(cpu_freq_result.stdout.strip())
            cpu_info["cpuFrequency"] = f"{cpu_freq_hz / 1000000:.2f} MHz"
        else:
            cpu_freq_result = subprocess.run(['sysctl', '-n', 'hw.cpufrequency_max'], 
                                           capture_output=True, text=True)
            if cpu_freq_result.returncode == 0 and cpu_freq_result.stdout.strip():
                cpu_freq_hz = int(cpu_freq_result.stdout.strip())
                cpu_info["cpuFrequency"] = f"{cpu_freq_hz / 1000000:.2f} MHz"
            else:
                cpu_info["cpuFrequency"] = "Unknown"
    except:
        cpu_info["cpuFrequency"] = "Unknown"

    # ram info
    mem_info = {}

    svmem = psutil.virtual_memory()
    mem_info["totalRAM"] = f"{svmem.total / (1024**3):.2f} GB"
    
    # get ram freq using system profiler
    try:
        memory_result = subprocess.run(['system_profiler', 'SPMemoryDataType'], 
                                     capture_output=True, text=True)
        if memory_result.returncode == 0:
            memory_output = memory_result.stdout
            speed_match = re.search(r'Speed:\s*(\d+)\s*MHz', memory_output, re.IGNORECASE)
            if speed_match:
                mem_info["ramFrequency"] = f"{speed_match.group(1)} MHz"
            else:
                speed_match = re.search(r'(\d+)\s*MHz', memory_output)
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

def _get_mac_temps():
    if not shutil.which("iSMC"):
        return {"error": "iSMC not found. Install it by following the instructions in the README.md"}

    try:
        output = subprocess.check_output(["iSMC", "temp"]).decode("utf-8")

        temps = {}
        lines = output.splitlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            line = line.strip()
            
            if (not line or 
                line.startswith('Temperature') or 
                line.startswith('DESCRIPTION') or
                line.startswith('KEY') or
                line.startswith('VALUE') or
                line.startswith('TYPE')):
                continue

            if '°C' in line:
                temp_match = re.search(r'([\d\.]+)\s*°C', line)
                if temp_match:
                    temp_value = float(temp_match.group(1))
                    
                    parts = re.split(r'\s{2,}', line)
                    
                    if len(parts) >= 3:
                        description = parts[0].strip()
                        key = parts[1].strip()
                        
                        sensor_name = description if description else key
                        
                        temps[sensor_name] = f"{temp_value}°C"

        return temps if temps else {"error": "No temperature data found after parsing"}

    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to run iSMC: {e}"}
    except Exception as e:
        return {"error": f"Error parsing iSMC output: {e}"}