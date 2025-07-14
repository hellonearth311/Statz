from statz import stats
from datetime import date, datetime
from colorama import Fore, Style, init

import platform
import json
import argparse

def format_value(key, value):
    """Format value with color if it's an error."""
    if isinstance(value, dict) and "error" in value:
        return f"{Fore.RED}{value['error']}{Style.RESET_ALL}"
    elif isinstance(value, str) and "error" in key.lower():
        return f"{Fore.RED}{value}{Style.RESET_ALL}"
    else:
        return value

def get_component_specs(args):
    """Get specs for specific components based on OS and requested components."""
    current_os = platform.system()
    
    # Get all system specs first
    if current_os == "Windows":
        all_specs = stats.get_system_specs()
        # Windows returns: cpu_data, gpu_data_list, ram_data_list, storage_data_list, network_data, battery_data
        result = {}
        
        if args.os:
            result["os"] = {"system": current_os, "platform": platform.platform()}
        if args.cpu:
            result["cpu"] = all_specs[0]
        if args.gpu:
            if all_specs[1]:
                result["gpu"] = all_specs[1]
            else:
                result["gpu"] = {"error": "GPU information not available on this system"}
        if args.ram:
            result["ram"] = all_specs[2]
        if args.disk:
            result["disk"] = all_specs[3]
        if args.network:
            if all_specs[4]:
                result["network"] = all_specs[4]
            else:
                result["network"] = {"error": "Network information not available on this system"}
        if args.battery:
            if all_specs[5]:
                result["battery"] = all_specs[5]
            else:
                result["battery"] = {"error": "Battery information not available on this system"}
                
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
    
    return result

def get_component_usage(args):
    """Get usage for specific components based on OS and requested components."""
    current_os = platform.system()
    
    # Get all usage data first
    try:
        all_usage = stats.get_hardware_usage()
        # Returns: cpu_usage, ram_usage, disk_usages, network_usage, battery_usage
        result = {}
        
        if args.os:
            result["os"] = {"system": current_os, "platform": platform.platform()}
        if args.cpu:
            result["cpu"] = all_usage[0]
        if args.gpu:
            result["gpu"] = {"error": "GPU usage not supported due to lack of Python bindings for AMD and Intel GPUs"}
        if args.ram:
            result["ram"] = all_usage[1]
        if args.disk:
            result["disk"] = all_usage[2]
        if args.network:
            result["network"] = all_usage[3]
        if args.battery:
            result["battery"] = all_usage[4]
            
    except Exception as e:
        result = {"error": f"Usage data not available on {current_os}: {str(e)}"}
    
    return result

def main():
    # Initialize colorama
    init()
    
    parser = argparse.ArgumentParser(description="Get system info with statz.")
    parser.add_argument("--specs", action="store_true", help="Get system specs")
    parser.add_argument("--usage", action="store_true", help="Get system utilization")

    parser.add_argument("--os", action="store_true", help="Get OS specs/usage")
    parser.add_argument("--cpu", action="store_true", help="Get CPU specs/usage")
    parser.add_argument("--gpu", action="store_true", help="Get GPU specs/usage")
    parser.add_argument("--ram", action="store_true", help="Get RAM specs/usage")
    parser.add_argument("--disk", action="store_true", help="Get disk specs/usage")
    parser.add_argument("--network", action="store_true", help="Get network specs/usage")
    parser.add_argument("--battery", action="store_true", help="Get battery specs/usage")

    parser.add_argument("--json", action="store_true", help="Output specs/usage as a JSON")
    parser.add_argument("--out", action="store_true", help="Write specs/usage into a JSON file")

    args = parser.parse_args()

    # Check if any component flags are used
    component_flags = [args.os, args.cpu, args.gpu, args.ram, args.disk, args.network, args.battery]
    any_component_requested = any(component_flags)

    # Determine what data to retrieve
    if args.specs:
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
                # Windows format
                output = {
                    "cpu": specsOrUsage[0],
                    "gpu": specsOrUsage[1],
                    "memory": specsOrUsage[2],
                    "disk": specsOrUsage[3],
                    "network": specsOrUsage[4],
                    "battery": specsOrUsage[5]
                }
            else:
                output = specsOrUsage
        else:
            # Handle dictionary format (component-specific data)
            output = specsOrUsage
        print(json.dumps(output, indent=2))
    elif args.out:
        print("exporting specs/usage into a file...")
        
        time = datetime.now().strftime("%H:%M:%S")
        path_to_export = f"statz_export_{date.today()}_{time}.json"
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
                    # Windows format
                    output = {
                        "cpu": specsOrUsage[0],
                        "gpu": specsOrUsage[1],
                        "memory": specsOrUsage[2],
                        "disk": specsOrUsage[3],
                        "network": specsOrUsage[4],
                        "battery": specsOrUsage[5]
                    }
                else:
                    output = specsOrUsage
                f.write(json.dumps(output, indent=2))
            else:
                # Handle dictionary format (component-specific data)
                output = specsOrUsage
                f.write(json.dumps(output, indent=2))

        print("export complete!")
    else:
        if isinstance(specsOrUsage, tuple):
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
                        for j, item in enumerate(category_data):
                            print(f"  Device {j+1}: {item}")
                    else:
                        print(f"  {category_data}")
            elif len(specsOrUsage) == 6:
                # Windows format
                categories = ["CPU Info", "GPU Info", "Memory Info", "Disk Info", "Network Info", "Battery Info"]
                for i, category_data in enumerate(specsOrUsage):
                    print(f"\n{categories[i]}:")
                    if isinstance(category_data, dict):
                        for k, v in category_data.items():
                            formatted_value = format_value(k, v)
                            print(f"  {k}: {formatted_value}")
                    elif isinstance(category_data, list):
                        for j, item in enumerate(category_data):
                            print(f"  Device {j+1}: {item}")
                    else:
                        print(f"  {category_data}")
        else:
            # Handle dictionary format (component-specific data)
            for component, data in specsOrUsage.items():
                print(f"\n{component.upper()} Info:")
                if isinstance(data, dict):
                    for k, v in data.items():
                        formatted_value = format_value(k, v)
                        print(f"  {k}: {formatted_value}")
                elif isinstance(data, list):
                    for j, item in enumerate(data):
                        print(f"  Device {j+1}: {item}")
                else:
                    formatted_value = format_value("data", data)
                    print(f"  {formatted_value}")
