import platform
import psutil
import subprocess
import re
import shutil

def _get_mac_specs(get_os, get_cpu, get_ram, get_disk):
    """
    Get system specifications for Mac systems with selective fetching.

    This function allows you to specify which components to fetch data for, improving performance by avoiding unnecessary computations.

    Args:
        get_os (bool): Whether to fetch OS specs.
        get_cpu (bool): Whether to fetch CPU specs.
        get_ram (bool): Whether to fetch RAM specs.
        get_disk (bool): Whether to fetch disk specs.

    Returns:
        list: A list containing specs data for the specified components:
        [os_info (dict), cpu_info (dict), mem_info (dict), disk_info (dict)].

    Raises:
        Exception: If fetching data for a specific component fails.

    Note:
        - Components not requested will return None in the corresponding list position.
    """

    specs = []

    # os info
    if get_os:
        os_info = {}
        try:
            os_info["system"] = platform.system()
            os_info["nodeName"] = platform.node()
            os_info["release"] = platform.release()
            os_info["version"] = platform.version()
            os_info["machine"] = platform.machine()
        except:
            os_info = {key: "Error" for key in ["system", "nodeName", "release", "version", "machine"]}
        specs.append(os_info)
    else:
        specs.append(None)

    # cpu info
    if get_cpu:
        cpu_info = {}
        try:
            cpu_info["processor"] = platform.processor()
            cpu_info["coreCountPhysical"] = psutil.cpu_count(logical=False)
            cpu_info["coreCountLogical"] = psutil.cpu_count()
            try:
                cpu_name_result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], capture_output=True, text=True)
                cpu_info["cpuName"] = cpu_name_result.stdout.strip()
            except:
                cpu_info["cpuName"] = "Unknown"
            try:
                cpu_freq_result = subprocess.run(['sysctl', '-n', 'hw.cpufrequency'], capture_output=True, text=True)
                if cpu_freq_result.returncode == 0 and cpu_freq_result.stdout.strip():
                    cpu_freq_hz = int(cpu_freq_result.stdout.strip())
                    cpu_info["cpuFrequency"] = f"{cpu_freq_hz / 1000000:.2f} MHz"
                else:
                    cpu_info["cpuFrequency"] = "Unknown"
            except:
                cpu_info["cpuFrequency"] = "Unknown"
        except:
            cpu_info = {key: "Error" for key in ["processor", "coreCountPhysical", "coreCountLogical", "cpuName", "cpuFrequency"]}
        specs.append(cpu_info)
    else:
        specs.append(None)

    # ram info
    if get_ram:
        mem_info = {}
        try:
            svmem = psutil.virtual_memory()
            mem_info["totalRAM"] = f"{svmem.total / (1024**3):.2f} GB"
            try:
                memory_result = subprocess.run(['system_profiler', 'SPMemoryDataType'], capture_output=True, text=True)
                if memory_result.returncode == 0:
                    memory_output = memory_result.stdout
                    speed_match = re.search(r'Speed:\s*(\d+)\s*MHz', memory_output, re.IGNORECASE)
                    mem_info["ramFrequency"] = f"{speed_match.group(1)} MHz" if speed_match else "Unknown"
                else:
                    mem_info["ramFrequency"] = "Unknown"
            except:
                mem_info["ramFrequency"] = "Unknown"
        except:
            mem_info = {key: "Error" for key in ["totalRAM", "ramFrequency"]}
        specs.append(mem_info)
    else:
        specs.append(None)

    # disk info
    if get_disk:
        disk_info = {}
        try:
            disk_usage = psutil.disk_usage('/')
            disk_info["totalSpace"] = f"{disk_usage.total / (1024**3):.2f} GB"
            disk_info["usedSpace"] = f"{disk_usage.used / (1024**3):.2f} GB"
            disk_info["freeSpace"] = f"{disk_usage.free / (1024**3):.2f} GB"
        except:
            disk_info = {key: "Error" for key in ["totalSpace", "usedSpace", "freeSpace"]}
        specs.append(disk_info)
    else:
        specs.append(None)

    return specs

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