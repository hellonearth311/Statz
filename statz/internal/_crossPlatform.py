import psutil
import time
import platform
import math
import gc
import os
import tempfile

# Import platform-specific temperature functions
try:
    from ._getMacInfo import _get_mac_temps
    from ._getWindowsInfo import _get_windows_temps
    from ._getLinuxInfo import _get_linux_temps
except ImportError:
    from _getMacInfo import _get_mac_temps
    from _getWindowsInfo import _get_windows_temps
    from _getLinuxInfo import _get_linux_temps

def _get_usage(get_cpu, get_ram, get_disk, get_network, get_battery):
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

    ### Structure of returned data:
    - cpu_usage (dict):
        { "core1": usage percent, "core2": usage percent, ... }
    - ram_usage (dict):
        { "total": MB, "used": MB, "free": MB, "percent": percent_used }
    - disk_usages (list of dicts):
        [
            {
                "device": device_name,
                "readSpeed": current_read_speed_MBps,
                "writeSpeed": current_write_speed_MBps,
            },
            ...
        ]
    - network_usage (dict):
        { "up": upload_speed_mbps, "down": download_speed_mbps }
    - battery_usage (dict):
        { "percent": percent_left, "pluggedIn": is_plugged_in, "timeLeftMins": minutes_left (2147483640 = unlimited) }

    Note:
        Specify `False` for components you do not need to fetch to improve performance.
    ''' 
    stats = []

    if get_cpu:
        try:
            # cpu usage
            psutil.cpu_percent(percpu=True)
            time.sleep(0.1)
            cpu_usage_list = psutil.cpu_percent(percpu=True)

            cpu_usage = {}
            for i, core in enumerate(cpu_usage_list, 1):
                cpu_usage[f"core{i}"] = core
            stats.append(cpu_usage)
        except:
            stats.append(None)
    else:
        stats.append(None)

    if get_ram:
        try:
            # ram usage
            ram = psutil.virtual_memory()

            ram_usage = {
                "total": round(ram.total / (1024 ** 2), 1),
                "used": round(ram.used / (1024 ** 2), 1),
                "free": round(ram.available / (1024 ** 2), 1),
                "percent": ram.percent
            }
            stats.append(ram_usage)
        except:
            stats.append(None)
    else:
        stats.append(None)

    if get_disk:
        try:
            # disk usage
            disk_usages = []
            disk_counters_1 = psutil.disk_io_counters(perdisk=True)
            time.sleep(1)
            disk_counters_2 = psutil.disk_io_counters(perdisk=True)

            for device in disk_counters_1:
                read_bytes_1 = disk_counters_1[device].read_bytes
                write_bytes_1 = disk_counters_1[device].write_bytes
                read_bytes_2 = disk_counters_2[device].read_bytes
                write_bytes_2 = disk_counters_2[device].write_bytes

                read_speed = (read_bytes_2 - read_bytes_1) / (1024 * 1024)
                write_speed = (write_bytes_2 - write_bytes_1) / (1024 * 1024)

                disk_usages.append({
                    "device": device,
                    "readSpeed": round(read_speed, 2),
                    "writeSpeed": round(write_speed, 2),
                })
            stats.append(disk_usages)
        except:
            stats.append(None)
    else:
        stats.append(None)

    if get_network:
        try:
            # network usage
            net1 = psutil.net_io_counters()
            time.sleep(1)
            net2 = psutil.net_io_counters()

            upload_speed = round((net2.bytes_sent - net1.bytes_sent) / 1024 ** 2, 2)
            download_speed = round((net2.bytes_recv - net1.bytes_recv) / 1024 ** 2, 2)

            network_usage = {
                "up": upload_speed,
                "down": download_speed
            }
            stats.append(network_usage)
        except:
            stats.append(None)
    else:
        stats.append(None)

    if get_battery:
        try:
            # battery stats
            battery = psutil.sensors_battery()
            battery_usage = {
                "percent": battery.percent,
                "pluggedIn": battery.power_plugged,
                "timeLeftMins": battery.secsleft // 60 if battery.secsleft != psutil.POWER_TIME_UNLIMITED else 2147483640
            }
            stats.append(battery_usage)
        except:
            stats.append(None)
    else:
        stats.append(None)

    return stats

def _get_top_n_processes(n=5, type="cpu"):
    try:
        try:
            int(n)
        except:
            raise TypeError(f"n must be int, not {type(n)}")
    
        if n < 1:
            raise ValueError(f"n must be positive int, not {n}")
        
        # First, initialize CPU monitoring for all processes
        if type == "cpu":
            for proc in psutil.process_iter():
                try:
                    proc.cpu_percent()  # Initialize CPU monitoring
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            # Wait a bit for accurate CPU readings
            time.sleep(0.1)
        
        processes = []
        # List of process names to exclude (system processes that report incorrect usage)
        excluded_processes = {
            'System Idle Process',
            'Idle',
            'idle',
            'System',  # Sometimes the main System process also reports weird values
        }
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
            try:
                proc_info = proc.info
                
                # Skip excluded system processes
                if proc_info['name'] in excluded_processes:
                    continue
                    
                # Skip processes with PID 0 (usually system idle)
                if proc_info['pid'] == 0:
                    continue
                
                # Filter out processes with None values and very low usage
                if type == "cpu" and proc_info['cpu_percent'] is not None and proc_info['cpu_percent'] > 0:
                    # Cap CPU usage at reasonable levels (no single process should use more than 100% per core)
                    cpu_percent = min(proc_info['cpu_percent'], 100.0)
                    if cpu_percent > 0.1:  # Only include processes using more than 0.1% CPU
                        proc_info['cpu_percent'] = cpu_percent
                        processes.append(proc_info)
                elif type == "mem" and proc_info['memory_percent'] is not None and proc_info['memory_percent'] > 0:
                    # Add absolute memory usage in MB for better reporting
                    if proc_info['memory_info'] is not None:
                        memory_mb = proc_info['memory_info'].rss / 1024 / 1024  # Convert bytes to MB
                        proc_info['memory_mb'] = memory_mb
                        # Only include processes using at least 1MB of RAM
                        if memory_mb >= 1.0:
                            processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if type == "cpu":
            top_processes = sorted(processes, key=lambda p: p['cpu_percent'] or 0, reverse=True)[:n]
            top_processes_list = []
            for p in top_processes:
                top_processes_list.append({
                    'pid': p['pid'],
                    'name': p['name'],
                    'usage': round(float(p['cpu_percent'] or 0), 2)
                })
            return top_processes_list
        elif type == "mem":
            # Sort by absolute memory usage (MB) for more meaningful results
            top_processes = sorted(processes, key=lambda p: p.get('memory_mb', 0), reverse=True)[:n]
            top_processes_list = []
            for p in top_processes:
                memory_mb = p.get('memory_mb', 0)
                # Format memory usage for display
                if memory_mb >= 1024:  # If >= 1GB, show in GB
                    usage_display = f"{memory_mb / 1024:.1f} GB"
                else:  # Show in MB
                    usage_display = f"{memory_mb:.0f} MB"
                
                top_processes_list.append({
                    'pid': p['pid'],
                    'name': p['name'],
                    'usage': usage_display
                    # Note: Removed usage_mb and usage_percent for cleaner output
                })
            return top_processes_list
        else:
            raise TypeError(f"Type must be cpu or mem, not {type}")
    except Exception as e:
        return {"error": str(e)}

def _cpu_health_score(cpu_usage_dict):
    """
    Calculate CPU health score based on usage percentages.
    
    Args:
        cpu_usage_dict (dict): Dictionary with CPU core usage percentages.
    
    Returns:
        int: Health score from 0 to 100, where 100 is optimal.
    """
    if not cpu_usage_dict:
        return 0
    
    # Average CPU usage across all cores
    average_usage = sum(cpu_usage_dict.values()) / len(cpu_usage_dict)
    
    if average_usage < 50:
        return 100
    elif average_usage < 70:
        return 100 - (average_usage - 50) * 2
    elif average_usage < 85:
        return 60 - (average_usage - 70) * 2
    else:
        return max(0, 30 - (average_usage - 85) * 2)

def _memory_health_score(memory_percent):
    """
    Calculate memory health score based on usage percentage.
    
    Args:
        memory_percent (float): Memory usage percentage (0-100).
    
    Returns:
        int: Health score from 0 to 100, where 100 is optimal.
    """
    if memory_percent < 50:
        return 100
    elif memory_percent < 70:
        return 100 - (memory_percent - 50) * 2
    elif memory_percent < 85:
        return 60 - (memory_percent - 70) * 2
    else:
        return max(0, 30 - (memory_percent - 85) * 2)

def _disk_health_score(disk_usage_percent):
    """
    Calculate disk health score based on usage percentage.
    
    Args:
        disk_usage_percent (float): Disk usage percentage (0-100).
    
    Returns:
        int: Health score from 0 to 100, where 100 is optimal.
    """
    if disk_usage_percent < 60:
        return 100
    elif disk_usage_percent < 80:
        return 100 - (disk_usage_percent - 60) * 2
    elif disk_usage_percent < 95:
        return 60 - (disk_usage_percent - 80) * 3
    else:
        return max(0, 15 - (disk_usage_percent - 95) * 3)

def _temp_health_score(cpu_temp):
    """
    Calculate temperature health score based on CPU temperature.
    
    Args:
        cpu_temp (float): CPU temperature in degrees Celsius.
    
    Returns:
        int: Health score from 0 to 100, where 100 is optimal.
    """
    if cpu_temp < 50:
        return 100
    elif cpu_temp < 70:
        return 100 - (cpu_temp - 50) * 2
    elif cpu_temp < 80:
        return 60 - (cpu_temp - 70) * 4
    else:
        return max(0, 20 - (cpu_temp - 80) * 2)

def _battery_health_score(battery_percent, is_plugged):
    """
    Calculate battery health score based on percentage and charging status.

    Args:
        battery_percent (float): Battery percentage (0-100).
        is_plugged (bool): Whether the device is plugged in.

    Returns:
        int: Health score from 0 to 100, where 100 is optimal.
    """
    if is_plugged:
        return 100 if battery_percent == 100 else 80
    else:
        if battery_percent > 50:
            return 100
        elif battery_percent > 20:
            return 100 - (50 - battery_percent) * 2
        else:
            return 0

def _system_health_score(cliVersion=False):
    try:
        weights = {
            "cpu": 0.3,
            "memory": 0.25,
            "disk": 0.25,
            "temperature": 0.1,
            "battery": 0.1
        }
        
        # Get usage data
        usage = _get_usage(True, True, True, False, True)
        
        # Get CPU usage
        cpu_usage_dict = usage[0] if usage[0] else {}
        
        # Get memory usage
        memory_percent = usage[1]['percent'] if usage[1] else 0
        
        # Get disk usage (space, not I/O speed)
        try:
            disk_usage = psutil.disk_usage('/')  # Linux/Mac
            disk_usage_percent = disk_usage.percent
        except:
            try:
                disk_usage = psutil.disk_usage('C:\\')  # Windows
                disk_usage_percent = disk_usage.percent
            except:
                disk_usage_percent = 0
        
        # Get temperature using platform-specific functions
        cpu_temp = 50  # Default safe temperature
        try:
            operatingSystem = platform.system()
            
            if operatingSystem == "Darwin":  # macOS
                temps = _get_mac_temps()
                if temps and isinstance(temps, dict):
                    # Get CPU temperature from macOS temp data
                    cpu_temp = temps.get('CPU', temps.get('cpu', 50))
                    if isinstance(cpu_temp, str):
                        cpu_temp = float(cpu_temp.replace('°C', '').strip())
                        
            elif operatingSystem == "Linux":  # Linux
                temps = _get_linux_temps()
                if temps and isinstance(temps, dict):
                    # Get CPU temperature from Linux temp data
                    for key, value in temps.items():
                        if 'core' in key.lower() or 'cpu' in key.lower():
                            cpu_temp = value
                            break
                    else:
                        # If no CPU-specific temp, use first available
                        cpu_temp = next(iter(temps.values()), 50)
                        
            elif operatingSystem == "Windows":  # Windows
                temps = _get_windows_temps()
                if temps and isinstance(temps, dict):
                    # Get CPU temperature from Windows temp data
                    cpu_temp = next(iter(temps.values()), 50)
                    
        except Exception as temp_error:
            cpu_temp = 50  # Default safe temperature on error
        
        # Get battery data
        battery_percent = usage[4]['percent'] if usage[4] else 100
        is_plugged = usage[4]['pluggedIn'] if usage[4] else True
        
        # Calculate component scores
        cpu_score = _cpu_health_score(cpu_usage_dict)
        memory_score = _memory_health_score(memory_percent)
        disk_score = _disk_health_score(disk_usage_percent)
        temp_score = _temp_health_score(cpu_temp)
        battery_score = _battery_health_score(battery_percent, is_plugged)
        
        # Calculate weighted total score
        total_score = (
            cpu_score * weights['cpu'] +
            memory_score * weights['memory'] +
            disk_score * weights['disk'] +
            temp_score * weights['temperature'] +
            battery_score * weights['battery']
        )
        
        if not cliVersion:
            return round(total_score, 2)
        else:
            return {
                "cpu": round(cpu_score, 2),
                "memory": round(memory_score, 2),
                "disk": round(disk_score, 2),
                "temperature": round(temp_score, 2),
                "battery": round(battery_score, 2),
                "total": round(total_score, 2)
            }
            
    except Exception as e:
        if cliVersion:
            return {"error": str(e)}
        return 0

def _cpu_benchmark():
    '''
    Get CPU performance with some computational tasks, such as:\n
    - Calculating large Fibonacci numbers\n
    - Calculating large primes\n

    Returns:
     dict: {\n
     "execution_time": time taken to execute (lower is better),\n
     "fibonacci_10000th": fibonacci number computed,\n
     "prime_count": prime number calculated in benchmark,\n
     "score": score calculated (higher is better)\n
     }
    '''
    # start the clock
    start_time = time.time()

    # compute the first 10000 fib numbers
    n = 10000
    count = 0
    a, b = 0, 1
    while count < n:
        count += 1
        a, b = b, a + b
    
    # calculate prime numbers up to 10000
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    prime_count = sum(1 for i in range(2, 10000) if is_prime(i))

    # end the clock
    end_time = time.time()
    time_taken = end_time - start_time
    
    # calculate score (higher is better)
    baseline_time = .05
    score = max(0, (baseline_time / time_taken) * 100)
    
    return {
        "execution_time": round(time_taken, 3),
        "fibonacci_10000th": str(a)[:50] + "..." if len(str(a)) > 50 else str(a),
        "prime_count": prime_count,
        "score": round(score, 1)
    }

def _mem_benchmark():
    '''Benchmark memory allocation and access speed using large lists
    Returns:
     dict: {\n
     "execution_time": time taken to execute the program (lower is better),\n
     "sum_calculated": total sum calculated during the test,\n
     "score": the performance score on your ram (higher is better)\n
     }
    '''

    # start clock
    start_time = time.time()

    large_list = []
    for i in range(1000000):
        large_list.append(i * 2)
    
    total = sum(large_list)

    copied_list = large_list.copy()

    del large_list, copied_list
    gc.collect()

    end_time = time.time()
    time_taken = end_time - start_time

    # calculate score
    baseline = 1.0
    score = max(0, (baseline / time_taken) * 100)

    return {
        "execution_time": round(time_taken, 3),
        "sum_calculated": total,
        "score": round(score, 1)
    }

def _disk_benchmark():
    '''
    Benchmark disk I/O performance by writing and reading a 10MB test file.
    
    Returns:
     dict: {
     "write_speed": Write speed in MB/s,
     "read_speed": Read speed in MB/s, 
     "write_score": Write performance score (higher is better),
     "read_score": Read performance score (higher is better),
     "overall_score": Overall disk performance score (higher is better)
     }
    '''
    
    # create tempfile
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # write test
        start_time = time.time()
        test_data = b"0" * (10 * 1024 * 1024) # 10mb

        with open(temp_path, 'wb') as f:
            f.write(test_data)
            f.flush()
            os.fsync(f.fileno())
        
        write_time = time.time() - start_time

        # read test
        start_time = time.time()
        with open(temp_path, 'rb') as f:
            read_data = f.read()

        read_time = time.time() - start_time

        # calc speed
        file_size_mb = len(test_data) / (1024 * 1024)
        write_speed = file_size_mb / write_time
        read_speed = file_size_mb / read_time

        # scoring (higher is better)
        write_baseline = 100
        read_baseline = 100
        
        write_score = max(0, (write_speed / write_baseline) * 100)
        read_score = max(0, (read_speed / read_baseline) * 100)
        overall_score = (write_score + read_score) / 2

        return {
            "write_speed": round(write_speed, 1),
            "read_speed": round(read_speed, 1),
            "write_score": round(write_score, 1),
            "read_score": round(read_score, 1),
            "overall_score": round(overall_score, 1)
        }

    finally:
        # cleanup
        try:
            os.unlink(temp_path)
        except:
            pass