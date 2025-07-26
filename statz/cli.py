from statz import stats
from statz.benchmark import cpu_benchmark, mem_benchmark, disk_benchmark
from statz.temp import get_system_temps
from statz.health import system_health_score
from statz.file import export_into_file
from statz.internet import internet_speed_test
from datetime import date, datetime
from colorama import Fore, Style, init
from .dashboard import run_dashboard
from rich.console import Console
from rich.table import Table
from rich import box

import platform
import json
import argparse

# Import GPU usage function for Windows
try:
    if platform.system() == "Windows":
        from statz.internal._getWindowsInfo import _get_windows_gpu_usage
    else:
        _get_windows_gpu_usage = None
except ImportError:
    _get_windows_gpu_usage = None

def create_export_function_for_specs(args):
    """Create a function that can be used with export_into_file for specs data."""
    if any([args.os, args.cpu, args.gpu, args.ram, args.disk, args.network, args.battery, args.temp, args.processes, args.health, args.benchmark]):
        # Component-specific specs
        def get_specs():
            return get_component_specs(args)
        return get_specs
    else:
        # All specs
        return stats.get_system_specs

def create_export_function_for_usage(args):
    """Create a function that can be used with export_into_file for usage data."""
    if any([args.os, args.cpu, args.gpu, args.ram, args.disk, args.network, args.battery, args.temp, args.processes, args.health, args.benchmark]):
        # Component-specific usage
        def get_usage():
            return get_component_usage(args)
        return get_usage
    else:
        # All usage data
        return stats.get_hardware_usage

def create_export_function_for_processes(args):
    """Create a function that can be used with export_into_file for process data."""
    return lambda: stats.get_top_n_processes(args.process_count, args.process_type)

def create_export_function_for_temps():
    """Create a function that can be used with export_into_file for temperature data."""
    return get_system_temps

def create_export_function_for_health():
    """Create a function that can be used with export_into_file for health data."""
    return lambda: system_health_score(cliVersion=True)

def create_export_function_for_benchmark(args):
    """Create a function that can be used with export_into_file for benchmark data."""
    if any([args.cpu, args.ram, args.disk]):
        # Specific component benchmarks
        def get_benchmarks():
            return get_component_benchmarks(args)
        return get_benchmarks
    else:
        # All benchmarks
        def get_all_benchmarks():
            return {
                "cpu": cpu_benchmark(),
                "memory": mem_benchmark(),
                "disk": disk_benchmark()
            }
        return get_all_benchmarks

def format_value(key, value):
    """Format value with color if it's an error."""
    if isinstance(value, dict) and "error" in value:
        return f"{Fore.RED}{value['error']}{Style.RESET_ALL}"
    elif isinstance(value, str) and "error" in key.lower():
        return f"{Fore.RED}{value}{Style.RESET_ALL}"
    else:
        return value

def format_gpu_data(gpu_data):
    """Format GPU data for display."""
    if isinstance(gpu_data, dict) and "error" in gpu_data:
        return f"{Fore.RED}{gpu_data['error']}{Style.RESET_ALL}"
    elif isinstance(gpu_data, dict):
        # Handle new GPU usage format
        if "nvidia" in gpu_data or "amd" in gpu_data or "intel" in gpu_data:
            formatted_output = []
            formatted_output.append(f"Total GPUs: {gpu_data.get('total_gpus', 0)}")
            
            if gpu_data.get('active_gpus'):
                formatted_output.append(f"Active GPUs: {', '.join(gpu_data['active_gpus'])}")
            
            # Format vendor-specific data
            for vendor in ["nvidia", "amd", "intel"]:
                vendor_data = gpu_data.get(vendor)
                if vendor_data:
                    formatted_output.append(f"\n  {vendor.upper()} GPU:")
                    formatted_output.append(f"    Count: {vendor_data.get('count', 0)}")
                    
                    usage = vendor_data.get('primary_usage', 0)
                    if usage >= 0:
                        # Color code usage
                        if usage >= 90:
                            color = Fore.RED
                        elif usage >= 70:
                            color = Fore.YELLOW
                        else:
                            color = Fore.GREEN
                        formatted_output.append(f"    Usage: {color}{usage}%{Style.RESET_ALL}")
                    
                    # Display detailed info if available
                    detailed = vendor_data.get('detailed_info')
                    if detailed and 'gpus' in detailed:
                        for i, gpu in enumerate(detailed['gpus']):
                            formatted_output.append(f"    GPU {i} Details:")
                            if 'name' in gpu:
                                formatted_output.append(f"      Name: {gpu['name']}")
                            if 'memory_utilization' in gpu:
                                formatted_output.append(f"      Memory Usage: {gpu['memory_utilization']}%")
                            if 'temperature' in gpu and gpu['temperature'] > 0:
                                temp = gpu['temperature']
                                temp_color = Fore.RED if temp > 80 else Fore.YELLOW if temp > 70 else Fore.GREEN
                                formatted_output.append(f"      Temperature: {temp_color}{temp}°C{Style.RESET_ALL}")
                            if 'power_usage' in gpu and gpu['power_usage'] > 0:
                                formatted_output.append(f"      Power: {gpu['power_usage']:.1f}W")
            
            # Handle fallback data
            if gpu_data.get('fallback'):
                formatted_output.append(f"\n  Fallback GPU Info:")
                for gpu in gpu_data['fallback'].get('gpus', []):
                    formatted_output.append(f"    {gpu.get('name', 'Unknown GPU')}")
                    if gpu.get('vram_mb', 0) > 0:
                        formatted_output.append(f"      VRAM: {gpu['vram_mb']} MB")
            
            if gpu_data.get('performance_counter'):
                pc_data = gpu_data['performance_counter']
                usage = pc_data.get('average_usage', 0)
                color = Fore.RED if usage >= 90 else Fore.YELLOW if usage >= 70 else Fore.GREEN
                formatted_output.append(f"\n  Generic GPU Usage: {color}{usage:.1f}%{Style.RESET_ALL}")
            
            return "\n".join(formatted_output)
        else:
            # Handle legacy GPU format (single GPU as dictionary)
            gpu_info = []
            for key, value in gpu_data.items():
                gpu_info.append(f"    {key}: {value}")
            return "  GPU 1:\n" + "\n".join(gpu_info)
    elif isinstance(gpu_data, list):
        if not gpu_data:
            return f"{Fore.RED}No GPU information available{Style.RESET_ALL}"
        # Format each GPU device (legacy format)
        formatted_output = []
        for i, gpu in enumerate(gpu_data):
            if isinstance(gpu, dict):
                gpu_info = f"  GPU {i+1}:"
                for key, value in gpu.items():
                    gpu_info += f"\n    {key}: {value}"
                formatted_output.append(gpu_info)
            else:
                formatted_output.append(f"  GPU {i+1}: {gpu}")
        return "\n".join(formatted_output)
    else:
        return str(gpu_data)

def format_health_data(health_data):
    """Format health score data for display with colors."""
    if isinstance(health_data, dict) and "error" in health_data:
        return f"{Fore.RED}{health_data['error']}{Style.RESET_ALL}"
    elif isinstance(health_data, dict):
        formatted_output = []
        
        # Format total score with color
        total_score = health_data.get('total', 0)
        if total_score >= 90:
            color = Fore.GREEN
            rating = "Excellent 🟢"
        elif total_score >= 75:
            color = Fore.YELLOW
            rating = "Good 🟡"
        elif total_score >= 60:
            color = Fore.YELLOW
            rating = "Fair 🟠"
        elif total_score >= 40:
            color = Fore.RED
            rating = "Poor 🔴"
        else:
            color = Fore.RED
            rating = "Critical ⚠️"
        
        formatted_output.append(f"  {color}Overall Score: {total_score}/100 ({rating}){Style.RESET_ALL}")
        formatted_output.append("")
        formatted_output.append("  Component Breakdown:")
        
        # Format individual component scores
        components = {
            'cpu': 'CPU',
            'memory': 'Memory', 
            'disk': 'Disk',
            'temperature': 'Temperature',
            'battery': 'Battery'
        }
        
        for key, label in components.items():
            if key in health_data:
                score = health_data[key]
                if score >= 80:
                    comp_color = Fore.GREEN
                elif score >= 60:
                    comp_color = Fore.YELLOW
                else:
                    comp_color = Fore.RED
                formatted_output.append(f"    {comp_color}{label}: {score}/100{Style.RESET_ALL}")
        
        return "\n".join(formatted_output)
    else:
        return str(health_data)

def format_benchmark_data(benchmark_data):
    """Format benchmark data for display with colors."""
    if isinstance(benchmark_data, dict) and "error" in benchmark_data:
        return f"{Fore.RED}{benchmark_data['error']}{Style.RESET_ALL}"
    elif isinstance(benchmark_data, dict):
        formatted_output = []
        
        for component, data in benchmark_data.items():
            if isinstance(data, dict):
                # Format component header
                formatted_output.append(f"\n  {component.upper()} Benchmark:")
                
                # Color code scores
                score = data.get('score', 0)
                if score >= 200:
                    color = Fore.GREEN
                    rating = "Excellent 🚀"
                elif score >= 150:
                    color = Fore.GREEN
                    rating = "Very Good 🟢"
                elif score >= 100:
                    color = Fore.YELLOW
                    rating = "Good 🟡"
                elif score >= 75:
                    color = Fore.YELLOW
                    rating = "Fair 🟠"
                else:
                    color = Fore.RED
                    rating = "Poor 🔴"
                
                # Display results
                for key, value in data.items():
                    if key == 'score':
                        formatted_output.append(f"    {color}{key}: {value} ({rating}){Style.RESET_ALL}")
                    else:
                        formatted_output.append(f"    {key}: {value}")
        
        return "\n".join(formatted_output)
    else:
        return str(benchmark_data)

def get_component_benchmarks(args):
    """Run benchmarks for specific components."""
    result = {}
    
    if args.cpu:
        print("Running CPU benchmark...")
        try:
            result["cpu"] = cpu_benchmark()
        except Exception as e:
            result["cpu"] = {"error": f"CPU benchmark failed: {str(e)}"}
    
    if args.ram:
        print("Running memory benchmark...")
        try:
            result["memory"] = mem_benchmark()
        except Exception as e:
            result["memory"] = {"error": f"Memory benchmark failed: {str(e)}"}
    
    if args.disk:
        print("Running disk benchmark...")
        try:
            result["disk"] = disk_benchmark()
        except Exception as e:
            result["disk"] = {"error": f"Disk benchmark failed: {str(e)}"}
    
    return result

def get_component_specs(args):
    """Get specs for specific components based on OS and requested components."""
    current_os = platform.system()
    
    # Get all system specs first
    if current_os == "Windows":
        all_specs = stats.get_system_specs()
        # Windows returns: os_data, cpu_data, gpu_data_list, ram_data_list, storage_data_list, network_data, battery_data
        result = {}
        
        if args.os:
            result["os"] = all_specs[0] if all_specs[0] else {"system": current_os, "platform": platform.platform()}
        if args.cpu:
            result["cpu"] = all_specs[1]
        if args.gpu:
            if all_specs[2]:
                result["gpu"] = all_specs[2]
            else:
                result["gpu"] = {"error": "GPU information not available on this system"}
        if args.ram:
            result["ram"] = all_specs[3]
        if args.disk:
            result["disk"] = all_specs[4]
        if args.network:
            if all_specs[5]:
                result["network"] = all_specs[5]
            else:
                result["network"] = {"error": "Network information not available on this system"}
        if args.battery:
            if all_specs[6]:
                result["battery"] = all_specs[6]
            else:
                result["battery"] = {"error": "Battery information not available on this system"}
        if args.temp:
            try:
                temp_data = get_system_temps()
                if temp_data:
                    result["temperature"] = temp_data
                else:
                    result["temperature"] = {"error": "Temperature information not available on this system"}
            except Exception as e:
                result["temperature"] = {"error": f"Temperature reading failed: {str(e)}"}
        if args.processes:
            try:
                process_data = stats.get_top_n_processes(args.process_count, args.process_type)
                if process_data:
                    result["processes"] = process_data
                else:
                    result["processes"] = {"error": "Process information not available on this system"}
            except Exception as e:
                result["processes"] = {"error": f"Process monitoring failed: {str(e)}"}
        if args.health:
            try:
                health_data = system_health_score(cliVersion=True)
                if health_data:
                    result["health"] = health_data
                else:
                    result["health"] = {"error": "Health score calculation failed"}
            except Exception as e:
                result["health"] = {"error": f"Health score calculation failed: {str(e)}"}
        if args.benchmark:
            try:
                benchmark_data = get_component_benchmarks(args)
                if benchmark_data:
                    result["benchmark"] = benchmark_data
                else:
                    result["benchmark"] = {"error": "Benchmark failed"}
            except Exception as e:
                result["benchmark"] = {"error": f"Benchmark failed: {str(e)}"}
                
    else:
        # macOS and Linux return: os_info, cpu_info, mem_info, disk_info
        all_specs = stats.get_system_specs()
        result = {}
        
        if args.os:
            result["os"] = all_specs[0]
        if args.cpu:
            result["cpu"] = all_specs[1]
        if args.gpu:
            result["gpu"] = {"error": f"GPU information not available on {current_os}"}
        if args.ram:
            result["ram"] = all_specs[2]
        if args.disk:
            result["disk"] = all_specs[3]
        if args.network:
            result["network"] = {"error": f"Network specs not available on {current_os}"}
        if args.battery:
            result["battery"] = {"error": f"Battery specs not available on {current_os}"}
        if args.temp:
            try:
                temp_data = get_system_temps()
                if temp_data:
                    result["temperature"] = temp_data
                else:
                    result["temperature"] = {"error": "Temperature information not available on this system"}
            except Exception as e:
                result["temperature"] = {"error": f"Temperature reading failed: {str(e)}"}
        if args.processes:
            try:
                process_data = stats.get_top_n_processes(args.process_count, args.process_type)
                if process_data:
                    result["processes"] = process_data
                else:
                    result["processes"] = {"error": "Process information not available on this system"}
            except Exception as e:
                result["processes"] = {"error": f"Process monitoring failed: {str(e)}"}
        if args.health:
            try:
                health_data = system_health_score(cliVersion=True)
                if health_data:
                    result["health"] = health_data
                else:
                    result["health"] = {"error": "Health score calculation failed"}
            except Exception as e:
                result["health"] = {"error": f"Health score calculation failed: {str(e)}"}
        if args.benchmark:
            try:
                benchmark_data = get_component_benchmarks(args)
                if benchmark_data:
                    result["benchmark"] = benchmark_data
                else:
                    result["benchmark"] = {"error": "Benchmark failed"}
            except Exception as e:
                result["benchmark"] = {"error": f"Benchmark failed: {str(e)}"}
    
    return result

def get_component_usage(args):
    """Get usage for specific components based on OS and requested components."""
    current_os = platform.system()

    # Get all usage data first
    try:
        all_usage = stats.get_hardware_usage(
            get_cpu=args.cpu,
            get_ram=args.ram,
            get_disk=args.disk,
            get_network=args.network,
            get_battery=args.battery
        )
        # Returns: [cpu_usage, ram_usage, disk_usages, network_usage, battery_usage]
        result = {}

        if args.os:
            result["os"] = {"system": current_os, "platform": platform.platform()}
        if args.cpu:
            result["cpu"] = all_usage[0]
        if args.gpu:
            # Add GPU usage functionality
            if current_os == "Windows" and _get_windows_gpu_usage:
                try:
                    gpu_usage = _get_windows_gpu_usage()
                    result["gpu"] = gpu_usage
                except Exception as e:
                    result["gpu"] = {"error": f"GPU usage monitoring failed: {str(e)}"}
            else:
                result["gpu"] = {"error": f"GPU usage monitoring not available on {current_os}"}
        if args.ram:
            result["ram"] = all_usage[1]
        if args.disk:
            result["disk"] = all_usage[2]
        if args.network:
            result["network"] = all_usage[3]
        if args.battery:
            result["battery"] = all_usage[4]
        if args.temp:
            try:
                temp_data = get_system_temps()
                if temp_data:
                    result["temperature"] = temp_data
                else:
                    result["temperature"] = {"error": "Temperature information not available on this system"}
            except Exception as e:
                result["temperature"] = {"error": f"Temperature reading failed: {str(e)}"}
        if args.processes:
            try:
                process_data = stats.get_top_n_processes(args.process_count, args.process_type)
                if process_data:
                    result["processes"] = process_data
                else:
                    result["processes"] = {"error": "Process information not available on this system"}
            except Exception as e:
                result["processes"] = {"error": f"Process monitoring failed: {str(e)}"}
        if args.health:
            try:
                health_data = system_health_score(cliVersion=True)
                if health_data:
                    result["health"] = health_data
                else:
                    result["health"] = {"error": "Health score calculation failed"}
            except Exception as e:
                result["health"] = {"error": f"Health score calculation failed: {str(e)}"}
        if args.benchmark:
            try:
                benchmark_data = get_component_benchmarks(args)
                if benchmark_data:
                    result["benchmark"] = benchmark_data
                else:
                    result["benchmark"] = {"error": "Benchmark failed"}
            except Exception as e:
                result["benchmark"] = {"error": f"Benchmark failed: {str(e)}"}

    except Exception as e:
        result = {"error": f"Usage data not available on {current_os}: {str(e)}"}

    return result

def format_table_data(data, title="System Information"):
    """Format data into a Rich table for display."""
    console = Console()
    table = Table(title=title, box=box.ROUNDED, title_style="bold cyan")
    table.add_column("Property", style="bold blue", no_wrap=True)
    table.add_column("Value", style="green")
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                # Handle nested dictionaries (like error messages)
                if "error" in value:
                    table.add_row(key, f"[red]{value['error']}[/red]")
                else:
                    # Flatten nested dict
                    for sub_key, sub_value in value.items():
                        table.add_row(f"{key} - {sub_key}", str(sub_value))
            elif isinstance(value, list):
                # Handle lists - show each item in detail
                if value:  # Check if list is not empty
                    # Determine appropriate label based on title or data type
                    if "process" in title.lower():
                        item_label = "Process"
                    elif "gpu" in title.lower():
                        item_label = "GPU"
                    elif "disk" in title.lower() or "storage" in title.lower():
                        item_label = "Drive"
                    elif "memory" in title.lower() or "ram" in title.lower():
                        item_label = "Module"
                    elif "network" in title.lower():
                        item_label = "Interface"
                    else:
                        item_label = "Device"
                    
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            # Show each dictionary item as separate rows
                            table.add_row(f"{key} {i+1}", "")  # Header row
                            for sub_key, sub_value in item.items():
                                table.add_row(f"  {sub_key}", str(sub_value))
                        else:
                            table.add_row(f"{key} {i+1}", str(item))
                else:
                    table.add_row(key, "[yellow]No data available[/yellow]")
            else:
                # Handle simple values
                if "error" in str(value).lower():
                    table.add_row(key, f"[red]{value}[/red]")
                else:
                    table.add_row(key, str(value))
    elif isinstance(data, list):
        # Handle case where data itself is a list
        # Determine appropriate label based on title
        if "process" in title.lower():
            item_label = "Process"
        elif "gpu" in title.lower():
            item_label = "GPU"
        elif "disk" in title.lower() or "storage" in title.lower():
            item_label = "Drive"
        elif "memory" in title.lower() or "ram" in title.lower():
            item_label = "Module"
        elif "network" in title.lower():
            item_label = "Interface"
        else:
            item_label = "Item"
            
        for i, item in enumerate(data):
            if isinstance(item, dict):
                table.add_row(f"{item_label} {i+1}", "")  # Header row
                for sub_key, sub_value in item.items():
                    table.add_row(f"  {sub_key}", str(sub_value))
            else:
                table.add_row(f"{item_label} {i+1}", str(item))
    else:
        table.add_row("Data", str(data))
    
    return table

def format_component_tables(component_data):
    """Format component-specific data into multiple tables."""
    console = Console()
    
    for component, data in component_data.items():
        title = f"{component.upper()} Information"
        
        # Handle special cases
        if component.lower() == "health":
            table = format_health_table(data)
        elif component.lower() in ["cpu", "memory", "disk"] and isinstance(data, dict) and "score" in data:
            # This is benchmark data for a specific component
            benchmark_data = {component: data}
            table = format_benchmark_table(benchmark_data)
        elif component.lower() == "benchmark":
            table = format_benchmark_table(data)
        elif component.lower() == "processes":
            table = format_processes_table(data)
        elif component.lower() == "gpu" and isinstance(data, list):
            table = format_gpu_table(data)
        else:
            table = format_table_data(data, title)
        
        console.print(table)
        console.print()  # Add spacing between tables

def format_health_table(health_data):
    """Format health score data into a table."""
    table = Table(title="System Health Score", box=box.ROUNDED, title_style="bold cyan")
    table.add_column("Component", style="bold blue", no_wrap=True)
    table.add_column("Score", style="green")
    table.add_column("Status", style="yellow")
    
    if isinstance(health_data, dict):
        if "error" in health_data:
            table.add_row("Error", f"[red]{health_data['error']}[/red]", "")
        else:
            for component, score in health_data.items():
                if component != "overall_score":
                    # Color code the score
                    if score >= 85:
                        color = "green"
                        status = "Excellent 🚀"
                    elif score >= 70:
                        color = "green"
                        status = "Good 🟢"
                    elif score >= 55:
                        color = "yellow"
                        status = "Fair 🟡"
                    else:
                        color = "red"
                        status = "Poor 🔴"
                    
                    table.add_row(component.replace('_', ' ').title(), f"[{color}]{score}[/{color}]", status)
            
            # Add overall score if present
            if "overall_score" in health_data:
                overall = health_data["overall_score"]
                if overall >= 85:
                    color = "green"
                    status = "Excellent 🚀"
                elif overall >= 70:
                    color = "green"
                    status = "Good 🟢"
                elif overall >= 55:
                    color = "yellow"
                    status = "Fair 🟡"
                else:
                    color = "red"
                    status = "Poor 🔴"
                
                table.add_row("[bold]Overall Score[/bold]", f"[{color}]{overall}[/{color}]", f"[bold]{status}[/bold]")
    
    return table

def format_benchmark_table(benchmark_data):
    """Format benchmark data into a table."""
    table = Table(title="System Benchmark Results", box=box.ROUNDED, title_style="bold cyan")
    table.add_column("Component", style="bold blue", no_wrap=True)
    table.add_column("Metric", style="blue")
    table.add_column("Value", style="green")
    table.add_column("Rating", style="yellow")
    
    if isinstance(benchmark_data, dict):
        if "error" in benchmark_data:
            table.add_row("Error", "", f"[red]{benchmark_data['error']}[/red]", "")
        else:
            for component, data in benchmark_data.items():
                if isinstance(data, dict):
                    if "error" in data:
                        table.add_row(component.upper(), "Error", f"[red]{data['error']}[/red]", "")
                    else:
                        first_row = True
                        for metric, value in data.items():
                            if metric == 'score':
                                # Color code scores
                                score = value
                                if score >= 200:
                                    color = "green"
                                    rating = "Excellent 🚀"
                                elif score >= 150:
                                    color = "green"
                                    rating = "Very Good 🟢"
                                elif score >= 100:
                                    color = "yellow"
                                    rating = "Good 🟡"
                                elif score >= 75:
                                    color = "yellow"
                                    rating = "Fair 🟠"
                                else:
                                    color = "red"
                                    rating = "Poor 🔴"
                                
                                table.add_row(
                                    component.upper() if first_row else "",
                                    metric.replace('_', ' ').title(),
                                    f"[{color}]{value}[/{color}]",
                                    rating
                                )
                            else:
                                table.add_row(
                                    component.upper() if first_row else "",
                                    metric.replace('_', ' ').title(),
                                    str(value),
                                    ""
                                )
                            first_row = False
    
    return table

def format_processes_table(process_data):
    """Format process data into a table."""
    table = Table(title="Top Processes", box=box.ROUNDED, title_style="bold cyan")
    table.add_column("PID", style="bold blue")
    table.add_column("Name", style="green")
    table.add_column("Usage", style="yellow")
    
    if isinstance(process_data, list):
        for process in process_data:
            if isinstance(process, dict):
                usage = process.get('usage', 0)
                # Check if usage is already formatted (string) or needs formatting (number)
                if isinstance(usage, str):
                    # Already formatted (memory usage)
                    usage_display = usage
                else:
                    # Numeric (CPU usage percentage)
                    usage_display = f"{usage:.1f}%"
                
                table.add_row(
                    str(process.get('pid', 'N/A')),
                    process.get('name', 'N/A'),
                    usage_display
                )
    elif isinstance(process_data, dict) and "error" in process_data:
        table.add_row("Error", f"[red]{process_data['error']}[/red]", "")
    
    return table

def format_gpu_table(gpu_data):
    """Format GPU data into a table."""
    table = Table(title="GPU Information", box=box.ROUNDED, title_style="bold cyan")
    table.add_column("GPU", style="bold blue")
    table.add_column("Property", style="blue")
    table.add_column("Value", style="green")
    
    if isinstance(gpu_data, dict):
        if "error" in gpu_data:
            table.add_row("Error", "", f"[red]{gpu_data['error']}[/red]")
        elif "nvidia" in gpu_data or "amd" in gpu_data or "intel" in gpu_data:
            # Handle new GPU usage format
            table.add_row("Total GPUs", "", str(gpu_data.get('total_gpus', 0)))
            
            if gpu_data.get('active_gpus'):
                table.add_row("Active GPUs", "", ", ".join(gpu_data['active_gpus']))
            
            # Add vendor-specific information
            for vendor in ["nvidia", "amd", "intel"]:
                vendor_data = gpu_data.get(vendor)
                if vendor_data:
                    vendor_name = vendor.upper()
                    first_row = True
                    
                    table.add_row(vendor_name if first_row else "", "Count", str(vendor_data.get('count', 0)))
                    first_row = False
                    
                    usage = vendor_data.get('primary_usage', -1)
                    if usage >= 0:
                        # Color code usage
                        if usage >= 90:
                            usage_color = "red"
                        elif usage >= 70:
                            usage_color = "yellow"
                        else:
                            usage_color = "green"
                        table.add_row("", "Usage", f"[{usage_color}]{usage}%[/{usage_color}]")
                    
                    # Add detailed info if available
                    detailed = vendor_data.get('detailed_info')
                    if detailed and 'gpus' in detailed:
                        for i, gpu in enumerate(detailed['gpus']):
                            gpu_name = f"{vendor_name} GPU {i}"
                            if 'name' in gpu:
                                table.add_row(gpu_name if i == 0 else "", "Name", gpu['name'])
                            if 'memory_utilization' in gpu:
                                table.add_row("", "Memory Usage", f"{gpu['memory_utilization']}%")
                            if 'temperature' in gpu and gpu['temperature'] > 0:
                                temp = gpu['temperature']
                                temp_color = "red" if temp > 80 else "yellow" if temp > 70 else "green"
                                table.add_row("", "Temperature", f"[{temp_color}]{temp}°C[/{temp_color}]")
                            if 'power_usage' in gpu and gpu['power_usage'] > 0:
                                table.add_row("", "Power Usage", f"{gpu['power_usage']:.1f}W")
            
            # Handle fallback data
            if gpu_data.get('fallback'):
                table.add_row("Fallback Info", "", "")
                for i, gpu in enumerate(gpu_data['fallback'].get('gpus', [])):
                    table.add_row(f"GPU {i+1}", "Name", gpu.get('name', 'Unknown GPU'))
                    if gpu.get('vram_mb', 0) > 0:
                        table.add_row("", "VRAM", f"{gpu['vram_mb']} MB")
            
            if gpu_data.get('performance_counter'):
                pc_data = gpu_data['performance_counter']
                usage = pc_data.get('average_usage', 0)
                usage_color = "red" if usage >= 90 else "yellow" if usage >= 70 else "green"
                table.add_row("Generic GPU", "Usage", f"[{usage_color}]{usage:.1f}%[/{usage_color}]")
        else:
            # Handle legacy single GPU format
            for key, value in gpu_data.items():
                table.add_row("GPU 1", key.replace('_', ' ').title(), str(value))
    elif isinstance(gpu_data, list):
        # Handle legacy list format
        for i, gpu in enumerate(gpu_data):
            if isinstance(gpu, dict):
                first_row = True
                for key, value in gpu.items():
                    table.add_row(
                        f"GPU {i+1}" if first_row else "",
                        key.replace('_', ' ').title(),
                        str(value)
                    )
                    first_row = False
    
    return table

def format_full_system_table(specs_data):
    """Format full system specs into organized tables."""
    console = Console()
    
    if isinstance(specs_data, (tuple, list)):
        if len(specs_data) == 4:
            # macOS/Linux format
            categories = [
                ("OS Information", specs_data[0]),
                ("CPU Information", specs_data[1]), 
                ("Memory Information", specs_data[2]),
                ("Disk Information", specs_data[3])
            ]
        elif len(specs_data) == 5:
            # Usage format
            categories = [
                ("CPU Usage", specs_data[0]),
                ("Memory Usage", specs_data[1]),
                ("Disk Usage", specs_data[2]),
                ("Network Usage", specs_data[3]),
                ("Battery Usage", specs_data[4])
            ]
        elif len(specs_data) == 7:
            # Windows format (new with OS info)
            categories = [
                ("OS Information", specs_data[0]),
                ("CPU Information", specs_data[1]),
                ("GPU Information", specs_data[2]),
                ("Memory Information", specs_data[3]),
                ("Disk Information", specs_data[4]),
                ("Network Information", specs_data[5]),
                ("Battery Information", specs_data[6])
            ]
        else:
            # Fallback
            categories = [(f"Category {i+1}", data) for i, data in enumerate(specs_data)]
        
        for title, data in categories:
            if title == "GPU Information" and isinstance(data, list):
                table = format_gpu_table(data)
            else:
                table = format_table_data(data, title)
            console.print(table)
            console.print()  # Add spacing between tables

def main():
    # Initialize colorama
    init()
    
    parser = argparse.ArgumentParser(description="Get system info with statz.")
    parser.add_argument("--specs", action="store_true", help="Get system specs")
    parser.add_argument("--usage", action="store_true", help="Get system utilization")
    parser.add_argument("--processes", action="store_true", help="Get top processes")

    parser.add_argument("--os", action="store_true", help="Get OS specs/usage")
    parser.add_argument("--cpu", action="store_true", help="Get CPU specs/usage")
    parser.add_argument("--gpu", action="store_true", help="Get GPU specs/usage")
    parser.add_argument("--ram", action="store_true", help="Get RAM specs/usage")
    parser.add_argument("--disk", action="store_true", help="Get disk specs/usage")
    parser.add_argument("--network", action="store_true", help="Get network specs/usage")
    parser.add_argument("--battery", action="store_true", help="Get battery specs/usage")
    parser.add_argument("--temp", action="store_true", help="Get temperature readings")
    parser.add_argument("--health", action="store_true", help="Get system health score")
    parser.add_argument("--benchmark", action="store_true", help="Run system performance benchmark")
    parser.add_argument("--internetspeedtest", action="store_true", help="Run an internet speed test and get the upload/download speed as well as ping")

    parser.add_argument("--json", action="store_true", help="Output specs/usage as a JSON")
    parser.add_argument("--out", action="store_true", help="Write specs/usage into a JSON file")
    parser.add_argument("--csv", action="store_true", help="Write specs/usage into a CSV file")
    parser.add_argument("--table", action="store_true", help="Output specs/usage as a table")
    parser.add_argument("--path", type=str, help="Specify custom export path (works with --out and --csv)")

    parser.add_argument("--process-count", type=int, default=5, help="Number of top processes to show (default: 5)")
    parser.add_argument("--process-type", choices=["cpu", "mem"], default="cpu", help="Sort processes by CPU or memory usage (default: cpu)")

    parser.add_argument("--dashboard", action="store_true", help="Create a live dashboard")

    parser.add_argument("--version", action="version", version=f"%(prog)s {stats.__version__}", help="Show the version of statz")

    args = parser.parse_args()

    # Check if any component flags are used
    component_flags = [args.os, args.cpu, args.gpu, args.ram, args.disk, args.network, args.battery, args.temp, args.processes, args.health, args.benchmark]
    any_component_requested = any(component_flags)

    # Determine what data to retrieve
    if args.benchmark and not args.specs and not args.usage and not args.temp and not args.processes and not args.health and not args.internetspeedtest:
        # Handle standalone benchmark command
        if any([args.cpu, args.ram, args.disk]):
            # Run specific component benchmarks
            print("Starting component benchmarks...")
            specsOrUsage = get_component_benchmarks(args)
        else:
            # Run all benchmarks if no specific components requested
            print("Starting comprehensive system benchmark...")
            try:
                specsOrUsage = {
                    "cpu": stats.cpu_benchmark(),
                    "memory": stats.mem_benchmark(),
                    "disk": stats.disk_benchmark()
                }
            except Exception as e:
                specsOrUsage = {"benchmark": {"error": f"Benchmark failed: {str(e)}"}}
    elif args.health and not args.specs and not args.usage and not args.temp and not args.processes and not args.internetspeedtest:
        # Handle standalone health score command
        try:
            specsOrUsage = {"health": stats.system_health_score(cliVersion=True)}
            if not specsOrUsage["health"]:
                specsOrUsage["health"] = {"error": "Health score calculation failed"}
        except Exception as e:
            specsOrUsage = {"health": {"error": f"Health score calculation failed: {str(e)}"}}
    elif args.temp and not args.specs and not args.usage and not args.processes:
        # Handle standalone temperature command
        try:
            specsOrUsage = {"temperature": get_system_temps()}
            if not specsOrUsage["temperature"]:
                specsOrUsage["temperature"] = {"error": "Temperature information not available on this system"}
        except Exception as e:
            specsOrUsage = {"temperature": {"error": f"Temperature reading failed: {str(e)}"}}
    elif args.processes and not args.specs and not args.usage and not args.temp and not args.dashboard and not args.internetspeedtest:
        # Handle standalone processes command
        try:
            specsOrUsage = {"processes": stats.get_top_n_processes(args.process_count, args.process_type)}
            if not specsOrUsage["processes"]:
                specsOrUsage["processes"] = {"error": "Process information not available on this system"}
        except Exception as e:
            specsOrUsage = {"processes": {"error": f"Process monitoring failed: {str(e)}"}}
    elif args.specs:
        if any_component_requested:
            # Get specific component specs
            specsOrUsage = get_component_specs(args)
        else:
            # Get all specs
            specsOrUsage = stats.get_system_specs()
    elif args.usage:
        if any_component_requested:
            # Get specific component usage
            specsOrUsage = get_component_usage(args)
        else:
            # Get all usage
            specsOrUsage = stats.get_hardware_usage()
    elif args.dashboard and not args.specs and not args.usage and not args.temp and not args.processes and not args.internetspeedtest:
        try:
            run_dashboard()
            return
        except Exception as e:
            print(f"{Fore.RED} Error starting dashboard: {e}{Style.RESET_ALL}")
            return
    elif args.internetspeedtest and not args.specs and not args.usage and not args.temp and not args.processes and not args.dashboard:
        try:
            print("Running internet speed test...")

            results = internet_speed_test()

            print("Test Successful! Results:")

            print(f"    Download Speed: {results[0]} Mbps")
            print(f"    Upload Speed: {results[1]} Mbps")
            print(f"    Ping: {results[2]} ms")
            return

        except Exception as e:
            print(f"{Fore.RED} Error running internet speed test: {e}{Style.RESET_ALL}")
            return
    else:
        parser.print_help()
        return

    if args.json:
        if isinstance(specsOrUsage, tuple):
            # Handle tuple format (full system specs)
            if len(specsOrUsage) == 4:
                # macOS/Linux format
                output = {
                    "os": specsOrUsage[0],
                    "cpu": specsOrUsage[1],
                    "memory": specsOrUsage[2],
                    "disk": specsOrUsage[3]
                }
            elif len(specsOrUsage) == 5:
                # Usage format
                output = {
                    "cpu": specsOrUsage[0],
                    "memory": specsOrUsage[1],
                    "disk": specsOrUsage[2],
                    "network": specsOrUsage[3],
                    "battery": specsOrUsage[4]
                }
            elif len(specsOrUsage) == 6:
                # Windows format (old)
                output = {
                    "cpu": specsOrUsage[0],
                    "gpu": specsOrUsage[1],
                    "memory": specsOrUsage[2],
                    "disk": specsOrUsage[3],
                    "network": specsOrUsage[4],
                    "battery": specsOrUsage[5]
                }
            elif len(specsOrUsage) == 7:
                # Windows format (new with OS info)
                output = {
                    "os": specsOrUsage[0],
                    "cpu": specsOrUsage[1],
                    "gpu": specsOrUsage[2],
                    "memory": specsOrUsage[3],
                    "disk": specsOrUsage[4],
                    "network": specsOrUsage[5],
                    "battery": specsOrUsage[6]
                }
            else:
                output = specsOrUsage
        else:
            # Handle dictionary format (component-specific data)
            output = specsOrUsage
        print(json.dumps(output, indent=2))
    elif args.out:
        if args.path:
            print(f"exporting specs/usage into a JSON file at: {args.path}")
        else:
            print("exporting specs/usage into a file...")
        
        # Use custom path if provided, otherwise use default naming
        if args.path:
            # Ensure the path has .json extension
            if not args.path.endswith('.json'):
                path_to_export = f"{args.path}.json"
            else:
                path_to_export = args.path
        else:
            # Default naming
            time = datetime.now().strftime("%H-%M-%S")
            path_to_export = f"statz_export_{date.today()}_{time}.json"
        
        try:
            with open(path_to_export, "x") as f:
                if isinstance(specsOrUsage, tuple):
                    # Handle tuple format (full system specs)
                    if len(specsOrUsage) == 4:
                        # macOS/Linux format
                        output = {
                            "os": specsOrUsage[0],
                            "cpu": specsOrUsage[1],
                            "memory": specsOrUsage[2],
                            "disk": specsOrUsage[3]
                        }
                    elif len(specsOrUsage) == 5:
                        # Usage format
                        output = {
                            "cpu": specsOrUsage[0],
                            "memory": specsOrUsage[1],
                            "disk": specsOrUsage[2],
                            "network": specsOrUsage[3],
                            "battery": specsOrUsage[4]
                        }
                    elif len(specsOrUsage) == 6:
                        # Windows format (old)
                        output = {
                            "cpu": specsOrUsage[0],
                            "gpu": specsOrUsage[1],
                            "memory": specsOrUsage[2],
                            "disk": specsOrUsage[3],
                            "network": specsOrUsage[4],
                            "battery": specsOrUsage[5]
                        }
                    elif len(specsOrUsage) == 7:
                        # Windows format (new with OS info)
                        output = {
                            "os": specsOrUsage[0],
                            "cpu": specsOrUsage[1],
                            "gpu": specsOrUsage[2],
                            "memory": specsOrUsage[3],
                            "disk": specsOrUsage[4],
                            "network": specsOrUsage[5],
                            "battery": specsOrUsage[6]
                        }
                    else:
                        output = specsOrUsage
                    f.write(json.dumps(output, indent=2))
                else:
                    # Handle dictionary format (component-specific data)
                    output = specsOrUsage
                    f.write(json.dumps(output, indent=2))

            print(f"export complete! File saved to: {path_to_export}")
        except FileExistsError:
            print(f"{Fore.RED}Error: File '{path_to_export}' already exists. Please choose a different path or remove the existing file.{Style.RESET_ALL}")
        except PermissionError:
            print(f"{Fore.RED}Error: Permission denied when writing to '{path_to_export}'. Please check file permissions or choose a different path.{Style.RESET_ALL}")
        except OSError as e:
            print(f"{Fore.RED}Error: Could not write to '{path_to_export}': {str(e)}{Style.RESET_ALL}")
    elif args.csv:
        if args.path:
            print(f"exporting specs/usage into a CSV file at: {args.path}")
        else:
            print("exporting specs/usage into a CSV file...")
        
        # Determine which export function to use based on the command
        if args.benchmark and not args.specs and not args.usage and not args.temp and not args.processes and not args.health:
            # Standalone benchmark command
            export_func = create_export_function_for_benchmark(args)
        elif args.health and not args.specs and not args.usage and not args.temp and not args.processes:
            # Standalone health command
            export_func = create_export_function_for_health()
        elif args.temp and not args.specs and not args.usage and not args.processes:
            # Standalone temperature command
            export_func = create_export_function_for_temps()
        elif args.processes and not args.specs and not args.usage and not args.temp:
            # Standalone processes command
            export_func = create_export_function_for_processes(args)
        elif args.specs:
            # Specs command
            export_func = create_export_function_for_specs(args)
        elif args.usage:
            # Usage command
            export_func = create_export_function_for_usage(args)
        else:
            # Fallback - create a lambda function that returns the current data
            export_func = lambda: specsOrUsage
        
        # Use the stats export function for CSV
        # Use custom path if provided
        custom_path = None
        if args.path:
            # Ensure the path has .csv extension for CSV export
            if not args.path.endswith('.csv'):
                custom_path = f"{args.path}.csv"
            else:
                custom_path = args.path
        
        try:
            export_into_file(export_func, path=custom_path, csv=True, params=(False, None))
        except Exception as e:
            print(f"{Fore.RED}Error during CSV export: {str(e)}{Style.RESET_ALL}")
    elif args.table:
        # Handle table output format
        if isinstance(specsOrUsage, (tuple, list)):
            # Handle tuple/list format (full system specs)
            format_full_system_table(specsOrUsage)
        else:
            # Handle dictionary format (component-specific data)
            format_component_tables(specsOrUsage)

    else:
        if isinstance(specsOrUsage, (tuple, list)):
            # Handle tuple format (full system specs)
            if len(specsOrUsage) == 4:
                # macOS/Linux format
                categories = ["OS Info", "CPU Info", "Memory Info", "Disk Info"]
                for i, category_data in enumerate(specsOrUsage):
                    print(f"\n{categories[i]}:")
                    for k, v in category_data.items():
                        formatted_value = format_value(k, v)
                        print(f"  {k}: {formatted_value}")
            elif len(specsOrUsage) == 5:
                # Usage format
                categories = ["CPU Usage", "Memory Usage", "Disk Usage", "Network Usage", "Battery Usage"]
                for i, category_data in enumerate(specsOrUsage):
                    print(f"\n{categories[i]}:")
                    if isinstance(category_data, dict):
                        for k, v in category_data.items():
                            formatted_value = format_value(k, v)
                            print(f"  {k}: {formatted_value}")
                    elif isinstance(category_data, list):
                        # Determine appropriate label based on category
                        if "usage" in categories[i].lower():
                            item_label = "Device"  # For usage data, keep "Device"
                        elif "memory" in categories[i].lower() or "ram" in categories[i].lower():
                            item_label = "Module"
                        elif "disk" in categories[i].lower():
                            item_label = "Drive"
                        elif "gpu" in categories[i].lower():
                            item_label = "GPU"
                        elif "network" in categories[i].lower():
                            item_label = "Interface"
                        else:
                            item_label = "Device"
                        
                        for j, item in enumerate(category_data):
                            print(f"  {item_label} {j+1}: {item}")
                    else:
                        print(f"  {category_data}")
            elif len(specsOrUsage) == 6:
                # Windows format (old)
                categories = ["CPU Info", "GPU Info", "Memory Info", "Disk Info", "Network Info", "Battery Info"]
                for i, category_data in enumerate(specsOrUsage):
                    print(f"\n{categories[i]}:")
                    if i == 1:  # GPU Info index
                        formatted_gpu = format_gpu_data(category_data)
                        print(formatted_gpu)
                    elif isinstance(category_data, dict):
                        for k, v in category_data.items():
                            formatted_value = format_value(k, v)
                            print(f"  {k}: {formatted_value}")
                    elif isinstance(category_data, list):
                        # Determine appropriate label based on category for Windows format (old)
                        if "memory" in categories[i].lower() or "ram" in categories[i].lower():
                            item_label = "Module"
                        elif "disk" in categories[i].lower():
                            item_label = "Drive"
                        elif "gpu" in categories[i].lower():
                            item_label = "GPU"
                        elif "network" in categories[i].lower():
                            item_label = "Interface"
                        else:
                            item_label = "Device"
                        
                        for j, item in enumerate(category_data):
                            if isinstance(item, dict):
                                print(f"  {item_label} {j+1}:")
                                for k, v in item.items():
                                    print(f"    {k}: {v}")
                            else:
                                print(f"  {item_label} {j+1}: {item}")
                    else:
                        print(f"  {category_data}")
            elif len(specsOrUsage) == 7:
                # Windows format (new with OS info)
                categories = ["OS Info", "CPU Info", "GPU Info", "Memory Info", "Disk Info", "Network Info", "Battery Info"]
                for i, category_data in enumerate(specsOrUsage):
                    print(f"\n{categories[i]}:")
                    if i == 2:  # GPU Info index
                        formatted_gpu = format_gpu_data(category_data)
                        print(formatted_gpu)
                    elif isinstance(category_data, dict):
                        for k, v in category_data.items():
                            formatted_value = format_value(k, v)
                            print(f"  {k}: {formatted_value}")
                    elif isinstance(category_data, list):
                        # Determine appropriate label based on category for Windows format (new)
                        if "memory" in categories[i].lower() or "ram" in categories[i].lower():
                            item_label = "Module"
                        elif "disk" in categories[i].lower():
                            item_label = "Drive"
                        elif "gpu" in categories[i].lower():
                            item_label = "GPU"
                        elif "network" in categories[i].lower():
                            item_label = "Interface"
                        else:
                            item_label = "Device"
                        
                        for j, item in enumerate(category_data):
                            if isinstance(item, dict):
                                print(f"  {item_label} {j+1}:")
                                for k, v in item.items():
                                    print(f"    {k}: {v}")
                            else:
                                print(f"  {item_label} {j+1}: {item}")
                    else:
                        print(f"  {category_data}")
        elif isinstance(specsOrUsage, dict):
            # Handle dictionary format (component-specific data)
            for component, data in specsOrUsage.items():
                print(f"\n{component.upper()} Info:")
                if component.lower() == "gpu":
                    formatted_gpu = format_gpu_data(data)
                    print(formatted_gpu)
                elif component.lower() == "health":
                    formatted_health = format_health_data(data)
                    print(formatted_health)
                elif component.lower() == "benchmark":
                    formatted_benchmark = format_benchmark_data(data)
                    print(formatted_benchmark)
                elif isinstance(data, dict):
                    for k, v in data.items():
                        formatted_value = format_value(k, v)
                        print(f"  {k}: {formatted_value}")
                elif isinstance(data, list):
                    # Determine appropriate label based on component type
                    if component.lower() == "processes":
                        item_label = "Process"
                    elif component.lower() == "gpu":
                        item_label = "GPU"
                    elif component.lower() in ["disk", "storage"]:
                        item_label = "Drive"
                    elif component.lower() in ["memory", "ram"]:
                        item_label = "Module"
                    elif component.lower() == "network":
                        item_label = "Interface"
                    else:
                        item_label = "Device"
                    
                    for j, item in enumerate(data):
                        if isinstance(item, dict):
                            print(f"  {item_label} {j+1}:")
                            for k, v in item.items():
                                print(f"    {k}: {v}")
                        else:
                            print(f"  {item_label} {j+1}: {item}")
                else:
                    formatted_value = format_value("data", data)
                    print(f"  {formatted_value}")
        else:
            # Handle other data types (fallback)
            print("System Information:")
            if hasattr(specsOrUsage, '__iter__') and not isinstance(specsOrUsage, (str, dict)):
                # Handle other iterable types like lists
                for i, item in enumerate(specsOrUsage):
                    print(f"  Item {i+1}: {item}")
            else:
                # Handle single values or unknown types
                print(f"  {specsOrUsage}")

def create_export_function_for_specs(args):
    """Create a function that can be used with export_into_file for specs data."""
    if any([args.os, args.cpu, args.gpu, args.ram, args.disk, args.network, args.battery, args.temp, args.processes, args.health, args.benchmark]):
        # Component-specific specs
        def get_specs():
            return get_component_specs(args)
        return get_specs
    else:
        # All specs
        return stats.get_system_specs

def create_export_function_for_usage(args):
    """Create a function that can be used with export_into_file for usage data."""
    if any([args.os, args.cpu, args.gpu, args.ram, args.disk, args.network, args.battery, args.temp, args.processes, args.health, args.benchmark]):
        # Component-specific usage
        def get_usage():
            return get_component_usage(args)
        return get_usage
    else:
        # All usage data
        return stats.get_hardware_usage

def create_export_function_for_processes(args):
    """Create a function that can be used with export_into_file for process data."""
    return lambda: stats.get_top_n_processes(args.process_count, args.process_type)

def create_export_function_for_temps():
    """Create a function that can be used with export_into_file for temperature data."""
    return get_system_temps

def create_export_function_for_health():
    """Create a function that can be used with export_into_file for health data."""
    return lambda: stats.system_health_score(cliVersion=True)

def create_export_function_for_benchmark(args):
    """Create a function that can be used with export_into_file for benchmark data."""
    if any([args.cpu, args.ram, args.disk]):
        # Specific component benchmarks
        def get_benchmarks():
            return get_component_benchmarks(args)
        return get_benchmarks
    else:
        # All benchmarks
        def get_all_benchmarks():
            return {
                "cpu": stats.cpu_benchmark(),
                "memory": stats.mem_benchmark(), 
                "disk": stats.disk_benchmark()
            }
        return get_all_benchmarks
