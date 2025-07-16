from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn
from time import sleep
from colorama import Fore, init
from ._getUsage import _get_usage
import platform
import psutil
import time

init(autoreset=True)

# Global variables for network monitoring
_last_network_stats = None
_last_network_time = None

def calculate_cpu_average(cpu_usage_dict):
    """Calculate average CPU usage from all cores"""
    if not cpu_usage_dict:
        return 0
    
    # Remove non-numeric keys like 'average' if they exist
    numeric_values = []
    for key, value in cpu_usage_dict.items():
        if isinstance(value, (int, float)):
            numeric_values.append(value)
        elif isinstance(value, str) and value.replace('.', '').replace('%', '').isdigit():
            numeric_values.append(float(value.replace('%', '')))
    
    return sum(numeric_values) / len(numeric_values) if numeric_values else 0

def calculate_ram_percentage(ram_usage):
    """Calculate RAM usage percentage"""
    if isinstance(ram_usage, dict):
        # Try different possible key names from _get_usage()
        total_ram = ram_usage.get('totalRAM') or ram_usage.get('total') or ram_usage.get('totalMemory')
        available_ram = ram_usage.get('availableRAM') or ram_usage.get('available') or ram_usage.get('availableMemory')
        used_ram = ram_usage.get('usedRAM') or ram_usage.get('used') or ram_usage.get('usedMemory')
        
        # Method 1: Use total and available
        if total_ram and available_ram:
            used_ram_calc = total_ram - available_ram
            return (used_ram_calc / total_ram) * 100
        
        # Method 2: Use total and used directly
        elif total_ram and used_ram:
            return (used_ram / total_ram) * 100
        
        # Method 3: Check if there's a direct percentage
        elif 'memoryUsage' in ram_usage:
            usage_str = ram_usage['memoryUsage']
            if isinstance(usage_str, str) and '%' in usage_str:
                return float(usage_str.replace('%', ''))
        
        # Method 4: Fallback to psutil directly
        try:
            memory = psutil.virtual_memory()
            return memory.percent
        except:
            pass
    
    return 0

def calculate_disk_usage():
    """Calculate disk usage percentage"""
    try:
        disk_usage = psutil.disk_usage('/')
        used_percent = (disk_usage.used / disk_usage.total) * 100
        return used_percent, f"{disk_usage.used / (1024**3):.1f}GB / {disk_usage.total / (1024**3):.1f}GB"
    except Exception as e:
        return 0, "Error"

def calculate_network_usage():
    """Calculate network usage (bytes/sec)"""
    global _last_network_stats, _last_network_time
    
    try:
        current_stats = psutil.net_io_counters()
        current_time = time.time()
        
        if _last_network_stats is None or _last_network_time is None:
            _last_network_stats = current_stats
            _last_network_time = current_time
            return 0, "Calculating..."
        
        time_diff = current_time - _last_network_time
        if time_diff <= 0:
            return 0, "Calculating..."
        
        bytes_sent_per_sec = (current_stats.bytes_sent - _last_network_stats.bytes_sent) / time_diff
        bytes_recv_per_sec = (current_stats.bytes_recv - _last_network_stats.bytes_recv) / time_diff
        
        # Update for next calculation
        _last_network_stats = current_stats
        _last_network_time = current_time
        
        # Convert to MB/s for display
        total_mbps = (bytes_sent_per_sec + bytes_recv_per_sec) / (1024 * 1024)
        
        # For visualization, use a reasonable scale (e.g., 10 MB/s = 100%)
        usage_percent = min((total_mbps / 10) * 100, 100)
        
        return usage_percent, f"{total_mbps:.2f} MB/s"
        
    except Exception as e:
        return 0, "Error"

def calculate_battery_usage():
    """Calculate battery usage percentage"""
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return 0, "No Battery"
        
        battery_percent = battery.percent
        power_plugged = battery.power_plugged
        
        # For visualization, show actual battery level (higher = more charge)
        usage_percent = battery_percent
        
        status = "Charging" if power_plugged else "Discharging"
        display_text = f"{battery_percent:.1f}% ({status})"
        
        return usage_percent, display_text
        
    except Exception as e:
        return 0, "Error"

def safe_get_usage():
    """Safely get usage data with error handling"""
    try:
        usage_data = _get_usage()
        return usage_data
    except Exception as e:
        print(f"Error getting usage data: {e}")
        return [{"error": "CPU data unavailable"}, {"error": "RAM data unavailable"}]

def make_table():
    """Create the dashboard table with real usage data"""
    table = Table(title=f"🖥️ System Usage Dashboard - {platform.node()}")
    table.add_column("Component", style="cyan", width=12)
    table.add_column("Usage", style="magenta", width=25)
    table.add_column("Visual", style="green", width=30)

    # Get real usage data
    usage_data = safe_get_usage()
    
    components = ["CPU", "RAM", "Disk", "Network", "Battery"]
    
    for component in components:
        usage_value = "N/A"
        visual_bar = "░" * 20
        
        try:
            match component:
                case "CPU":
                    if len(usage_data) > 0 and not "error" in usage_data[0]:
                        cpu_avg = calculate_cpu_average(usage_data[0])
                        usage_value = f"{cpu_avg:.1f}%"
                        # Create visual bar
                        filled_blocks = int(cpu_avg / 5)  # 20 blocks for 100%
                        visual_bar = "█" * filled_blocks + "░" * (20 - filled_blocks)
                    else:
                        usage_value = "Error"
                        
                case "RAM":
                    if len(usage_data) > 1 and not "error" in usage_data[1]:
                        ram_percent = calculate_ram_percentage(usage_data[1])
                        usage_value = f"{ram_percent:.1f}%"
                        # Create visual bar
                        filled_blocks = int(ram_percent / 5)  # 20 blocks for 100%
                        visual_bar = "█" * filled_blocks + "░" * (20 - filled_blocks)
                    else:
                        usage_value = "Error"
                        
                case "Disk":
                    disk_percent, disk_info = calculate_disk_usage()
                    usage_value = f"{disk_percent:.1f}% ({disk_info})"
                    # Create visual bar
                    filled_blocks = int(disk_percent / 5)  # 20 blocks for 100%
                    visual_bar = "█" * filled_blocks + "░" * (20 - filled_blocks)
                    
                case "Network":
                    network_percent, network_info = calculate_network_usage()
                    usage_value = network_info
                    # Create visual bar based on network activity
                    filled_blocks = int(network_percent / 5)  # 20 blocks for 100%
                    visual_bar = "█" * filled_blocks + "░" * (20 - filled_blocks)
                    
                case "Battery":
                    battery_percent, battery_info = calculate_battery_usage()
                    usage_value = battery_info
                    # Create visual bar (showing battery drain, not charge)
                    filled_blocks = int(battery_percent / 5)  # 20 blocks for 100%
                    visual_bar = "█" * filled_blocks + "░" * (20 - filled_blocks)
                    
        except Exception as e:
            usage_value = "Error"
            visual_bar = "░" * 20
            
        table.add_row(component, usage_value, visual_bar)
    
    return table

def run_dashboard(refresh_rate=2):
    """Run dashboard until user stops it with Ctrl+C."""
    print(f"🚀 Starting dashboard with {refresh_rate}s refresh rate...")
    print("Press Ctrl+C to stop")
    
    try:
        with Live(make_table(), refresh_per_second=1/refresh_rate) as live:
            while True:
                sleep(refresh_rate)
                live.update(make_table())
    except KeyboardInterrupt:
        print(Fore.RED + "\n✋ Dashboard stopped by user.")
    except Exception as e:
        print(Fore.RED + f"\n❌ Dashboard error: {e}")

if __name__ == "__main__":
    run_dashboard()