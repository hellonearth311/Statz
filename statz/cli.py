import argparse
from statz import stats
import json

def main():
    parser = argparse.ArgumentParser(description="Get system info with statz.")
    parser.add_argument("--specs", action="store_true", help="Get system specs")
    parser.add_argument("--usage", action="store_true", help="Get system utilization")

    parser.add_argument("--json", action="store_true", help="Output specs/usage as a JSON")

    args = parser.parse_args()

    if args.specs:
        specsOrUsage = stats.get_system_specs()
    elif args.usage:
        specsOrUsage = stats.get_hardware_usage()
    else:
        parser.print_help()
        return

    if args.json:
        if isinstance(specsOrUsage, tuple):
            output = {
                "os": specsOrUsage[0],
                "cpu": specsOrUsage[1],
                "memory": specsOrUsage[2],
                "disk": specsOrUsage[3]
            }
        else:
            output = specsOrUsage
        print(json.dumps(output, indent=2))
    else:
        if isinstance(specsOrUsage, tuple):
            categories = ["OS Info", "CPU Info", "Memory Info", "Disk Info"]
            for i, category_data in enumerate(specsOrUsage):
                print(f"\n{categories[i]}:")
                for k, v in category_data.items():
                    print(f"  {k}: {v}")
        else:
            for k, v in specsOrUsage.items():
                print(f"{k}: {v}")