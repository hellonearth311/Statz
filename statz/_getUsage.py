import psutil
import time

def _get_usage():
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
    try:
        # cpu usage
        psutil.cpu_percent(percpu=True)
        time.sleep(0.1)
        cpu_usage_list = psutil.cpu_percent(percpu=True)

        cpu_usage = {}
        for i, core in enumerate(cpu_usage_list, 1):
            cpu_usage[f"core{i}"] = core
    except:
        cpu_usage = None
    try:
        # ram usage
        ram = psutil.virtual_memory()

        ram_usage = {
            "total": round(ram.total / (1024 ** 2), 1),
            "used": round(ram.used / (1024 ** 2), 1),
            "free": round(ram.available / (1024 ** 2), 1),
            "percent": ram.percent
        }
    except:
        ram_usage = None

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
    except:
        disk_usages = None

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
    except:
        network_usage = None

    try:
        # battery stats
        battery = psutil.sensors_battery()
        battery_usage = {
            "percent": battery.percent,
            "pluggedIn": battery.power_plugged,
            "timeLeftMins": battery.secsleft // 60 if battery.secsleft != psutil.POWER_TIME_UNLIMITED else 2147483640
        }
    except:
        battery_usage = None

    return [cpu_usage, ram_usage, disk_usages, network_usage, battery_usage]