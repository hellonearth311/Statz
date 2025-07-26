# statz
![PyPI - Downloads](https://img.shields.io/pypi/dm/statz) 
![PyPI Version](https://img.shields.io/pypi/v/statz)
![License](https://img.shields.io/github/license/hellonearth311/statz)
![GitHub issues](https://img.shields.io/github/issues/hellonearth311/statz)
![Last Commit](https://img.shields.io/endpoint?url=https://github-last-commit-badge.vercel.app/lastcommit)
![Lines of Code](https://raw.githubusercontent.com/hellonearth311/Statz/refs/heads/badges/loc-badge.svg)


**statz** is a cross-platform Python package that fetches **real-time system usage** and **hardware specs** — all wrapped in a simple, clean API.

Works on **macOS**, **Linux**, and **Windows**, and handles OS-specific madness under the hood so you don’t have to.


<img src="https://raw.githubusercontent.com/hellonearth311/Statz/refs/heads/main/img/logo.png" alt="statz logo" width=200>



---

## ✨ Features

- 📊 Get real-time CPU, RAM, and disk usage
- 💻 Fetch detailed system specifications (CPU, RAM, OS, etc.)
- 🏁 Run comprehensive performance benchmarks (CPU, memory, disk)
- 📋 Beautiful table output with Rich formatting
- 📊 CSV export for all data types (specs, usage, processes, benchmarks)
- 🏥 System health scoring and monitoring
- 🌡️ Temperature sensor readings (when available)
- 📈 Top process monitoring with filtering options
- 🧠 Automatically handles platform-specific logic
- 🧼 Super clean API — just a few functions, no fluff

---

## 📦 Installation

```bash
pip install statz
```

---

## 💻 CLI Usage

**statz** comes with a powerful command-line interface that lets you get system information right from your terminal.

### Basic Usage

```bash
# Get all system specs
statz --specs

# Get all system usage
statz --usage

# Get top processes
statz --processes

# Get temperature readings
statz --temp

# Get system health score
statz --health

# Run system performance benchmarks
statz --benchmark

# Check version
statz --version

# Launch live dashboard
statz --dashboard
```

### Live Dashboard

The live dashboard provides real-time monitoring of your system with an interactive interface:

```bash
# Launch the dashboard
statz --dashboard
```

The dashboard displays:
- 📊 Real-time CPU usage per core
- 🧠 Memory usage and availability
- 💾 Disk I/O speeds
- 🌐 Network upload/download speeds
- 🔋 Battery status (if available)
- 🌡️ Temperature readings (if available)

Press `Ctrl+C` to exit the dashboard.
```

### Component-Specific Information

You can get information for specific components using these flags:

```bash
# Individual components
statz --specs --cpu        # CPU specifications
statz --specs --ram        # RAM information
statz --specs --disk       # Disk/storage info
statz --specs --gpu        # GPU information (Windows only)
statz --specs --network    # Network adapter info
statz --specs --battery    # Battery information
statz --specs --os         # Operating system info

# Component benchmarks
statz --benchmark --cpu    # CPU performance benchmark
statz --benchmark --ram    # Memory performance benchmark
statz --benchmark --disk   # Disk performance benchmark

# Combine multiple components
statz --specs --cpu --ram --disk
statz --usage --cpu --ram --network
statz --benchmark --cpu --ram --disk
```

### Process Monitoring

```bash
# Get top 5 processes by CPU usage (default)
statz --processes

# Get top 10 processes by CPU usage
statz --processes --process-count 10

# Get top 5 processes by memory usage
statz --processes --process-type mem

# Get top 15 processes by memory usage
statz --processes --process-count 15 --process-type mem
```

### Output Formats

```bash
# JSON output
statz --specs --json
statz --usage --cpu --ram --json

# Table output (formatted tables)
statz --specs --table
statz --usage --cpu --ram --table
statz --processes --table
statz --benchmark --table

# CSV export
statz --specs --csv
statz --usage --csv
statz --processes --csv
statz --benchmark --csv

# Export to JSON file
statz --specs --out
statz --usage --processes --out
```

### Available Flags

| Flag | Description |
|------|-------------|
| `--specs` | Get system specifications |
| `--usage` | Get real-time system usage |
| `--processes` | Get top processes information |
| `--temp` | Get temperature readings |
| `--health` | Get system health score |
| `--benchmark` | Run system performance benchmarks |
| `--dashboard` | Launch live monitoring dashboard |
| `--version` | Show statz version |
| `--os` | Operating system information |
| `--cpu` | CPU information |
| `--gpu` | GPU information (Windows only) |
| `--ram` | RAM/memory information |
| `--disk` | Disk/storage information |
| `--network` | Network adapter information |
| `--battery` | Battery information |
| `--json` | Output in JSON format |
| `--table` | Output in formatted table format |
| `--csv` | Export to CSV file |
| `--out` | Export to JSON file |
| `--path {path}`| Specify the path of file export/deletion |
| `--process-count N` | Number of processes to show (default: 5) |
| `--process-type {cpu,mem}` | Sort processes by CPU or memory usage |
| `--internetspeedtest` | Run an internet speed test |
| `--compare`| Compare 2 files (you need to run --path1 and --path2 for this to work) |
| `--path1`| Path 1 for the compare parameter |
| `--path2`| Path 2 for the compare parameter |
| `--securedelete` | Delete a file by repeatedly overwriting it with random data, then deleting it. |


### Examples

```bash
# Get CPU and RAM specs in JSON format
statz --specs --cpu --ram --json

# Get CPU and RAM specs in table format
statz --specs --cpu --ram --table

# Monitor top 10 memory-intensive processes
statz --processes --process-count 10 --process-type mem

# Export all usage data to CSV
statz --usage --csv

# Export system specs to JSON file
statz --specs --out

# Export system specs to JSON file with custom path specs.json
statz --specs --out --path specs.json

# Get system temperatures and CPU usage in table format
statz --temp --usage --cpu --table

# Run comprehensive system benchmark
statz --benchmark

# Run specific component benchmarks
statz --benchmark --cpu --ram

# Get complete system overview
statz --specs --usage --processes --temp

# Get system health score
statz --health

# Check system health with other components in table format
statz --specs --health --cpu --ram --table

# Export benchmark results to CSV
statz --benchmark --csv

# Launch interactive dashboard for real-time monitoring
statz --dashboard

# Test internet speed
statz --internetspeedtest

# Compare 2 files (note that the 2 file types MUST match)
statz --compare --path1 path/to/specsorusage1.json or csv --path2 path/to/specsorusage2.json or csv

# Securely delete a file
statz --securedelete --path specs.json
```
## 🔗 Links
[PyPi Project 🐍](https://pypi.org/project/statz/)

[Github Repository 🧑‍💻](https://github.com/hellonearth311/Statz)

## 📜 Script Usage

**statz** provides a clean Python API for accessing system information programmatically. Here are examples of all available functions:

### Basic System Information

```python
import statz.stats as stats

# Get complete system specifications
specs = stats.get_system_specs()
print(specs)

# Get selective system specifications (improves performance)
specs = stats.get_system_specs(
    get_os=True,     # Operating system info
    get_cpu=True,    # CPU specifications
    get_gpu=False,   # GPU info (Windows only)
    get_ram=True,    # RAM specifications
    get_disk=True,   # Disk/storage info
    get_network=False, # Network adapters (Windows only)
    get_battery=False  # Battery info (Windows only)
)
```

### Real-Time Usage Data

```python
# Get all hardware usage data
usage = stats.get_hardware_usage()
print(usage)

# Get selective usage data (improves performance)
usage = stats.get_hardware_usage(
    get_cpu=True,     # CPU usage per core
    get_ram=True,     # Memory usage stats
    get_disk=True,    # Disk I/O speeds
    get_network=False, # Network speeds
    get_battery=True   # Battery status
)
```

### Temperature Monitoring

```python
import statz.temp as temp

# Get system temperature readings
temps = temp.get_system_temps()
print(temps)

# Returns platform-specific temperature data:
# macOS: {"CPU": 45.2, "GPU": 38.5}
# Linux: {"coretemp-isa-0000": 42.0, "acpi-0": 35.5}
# Windows: {"ThermalZone _TZ.TZ00": 41.3}
```

### Process Monitoring

```python
# Get top 5 processes by CPU usage (default)
top_processes = stats.get_top_n_processes()
print(top_processes)

# Get top 10 processes by CPU usage
top_cpu = stats.get_top_n_processes(n=10, type="cpu")

# Get top 15 processes by memory usage
top_memory = stats.get_top_n_processes(n=15, type="mem")

# Returns: [{"pid": 1234, "name": "chrome", "usage": 15.2}, ...]
```

### System Health Score

```python
import statz.health as health

# Get simple health score (0-100)
health_score = health.system_health_score()
print(f"System Health: {health_score}/100")

# Get detailed health breakdown
health_details = health.system_health_score(cliVersion=True)
print(health_details)
# Returns: {
#   "cpu": 85.2,
#   "memory": 76.8,
#   "disk": 64.1,
#   "temperature": 70.5,
#   "battery": 100.0,
#   "total": 78.4
# }
```

### Performance Benchmarking

```python
import statz.benchmark as benchmark

# Run CPU performance benchmark
cpu_bench = benchmark.cpu_benchmark()
print(cpu_bench)
# Returns: {"execution_time": 0.025, "fibonacci_10000th": "...", "prime_count": 1229, "score": 750.2}

# Run memory performance benchmark
mem_bench = benchmark.mem_benchmark()
print(mem_bench)
# Returns: {"execution_time": 0.15, "sum_calculated": 999999000000, "score": 666.7}

# Run disk performance benchmark
disk_bench = benchmark.disk_benchmark()
print(disk_bench)
# Returns: {"write_speed": 450.2, "read_speed": 380.1, "write_score": 450.2, "read_score": 380.1, "overall_score": 415.15}
```

### Data Export & File Operations

```python
import statz.file as file

# Export any function's output to a JSON file
file.export_into_file(stats.get_system_specs)
file.export_into_file(stats.get_hardware_usage)
file.export_into_file(lambda: health.system_health_score(cliVersion=True))

# Export to CSV format
file.export_into_file(stats.get_system_specs, csv=True)
file.export_into_file(stats.get_hardware_usage, csv=True)
file.export_into_file(stats.get_top_n_processes, csv=True)

# Export with function parameters
file.export_into_file(stats.get_top_n_processes, csv=True, params=(True, [10, "cpu"]))
file.export_into_file(benchmark.cpu_benchmark, csv=False)

# Securely delete a file
file.secure_delete("path/to/file")
```

### File Comparison

```python
import statz.file as file

# Compare two system spec files to see what changed
differences = file.compare(
    "statz_export_2025-01-23_10-30-15.json",  # Current specs
    "statz_export_2025-01-20_10-30-15.csv"    # Baseline specs
)

print(differences)
# Returns: {
#   "added": {"GPU.newProperty": "new_value"},
#   "removed": {"CPU.oldProperty": "old_value"}, 
#   "changed": {"RAM.capacity": {"from": "8192", "to": "16384"}},
#   "summary": {
#     "total_added": 1,
#     "total_removed": 1, 
#     "total_changed": 1,
#     "current_file": "statz_export_2025-01-23_10-30-15.json",
#     "baseline_file": "statz_export_2025-01-20_10-30-15.csv"
#   }
# }

# Supports cross-format comparison (JSON vs CSV, CSV vs JSON)
json_vs_csv = file.compare("specs.json", "baseline.csv")
csv_vs_json = file.compare("current.csv", "baseline.json")
```

### Platform-Specific Notes

```python
import platform
import statz.stats as stats

# Check current platform
current_os = platform.system()

if current_os == "Windows":
    # Windows supports all features including GPU, network, and battery specs
    specs = stats.get_system_specs(get_gpu=True, get_network=True, get_battery=True)
    
elif current_os in ["Darwin", "Linux"]:  # macOS or Linux
    # macOS/Linux don't support GPU, network, or battery specs
    specs = stats.get_system_specs(get_gpu=False, get_network=False, get_battery=False)
```

### Error Handling

```python
import statz.stats as stats
import statz.temp as temp
import statz.benchmark as benchmark
import statz.health as health
import statz.file as file

try:
    # System information functions
    specs = stats.get_system_specs()
    usage = stats.get_hardware_usage()
    temps = temp.get_system_temps()
    processes = stats.get_top_n_processes()
    health_score = health.system_health_score()
    
    # Performance benchmarks
    cpu_bench = benchmark.cpu_benchmark()
    mem_bench = benchmark.mem_benchmark()
    disk_bench = benchmark.disk_benchmark()
    
    # File operations
    file.export_into_file(stats.get_system_specs, csv=True)
    differences = file.compare("current.json", "baseline.csv")
    
except OSError as e:
    print(f"Unsupported operating system: {e}")
except Exception as e:
    print(f"Error getting system information: {e}")
```
### Internet Testing
```python
from statz.internet import internet_speed_test

results = internet_speed_test()

print(f"Download Speed (Mbps): {results[0]}, Upload Speed (Mbps): {results[1]}, Ping (ms): {results[2]}")
```

### Connected Device Monitoring
```python
from statz.stats import connected_device_monitoring

devices = connected_device_monitoring()
print(devices)
```

### Port Scanning
```python
from statz.network import scan_open_ports

ports = scan_open_ports()
print(ports)
```

## 📝 Changelog

### [v2.4.0 – Secure Delete and Port Scanner ✂️](https://github.com/hellonearth311/Statz/releases/tag/v2.4.0)

### 🔒 Port Scanner
- You can now scan specified ports on a certain host to see if they are open.
 - Example Usage: ```network.scan_open_ports(starting_port, ending_port, host_ip)```

### 📁 Secure Delete
- You can now securely delete files. It will overwrite it with random data **5** times and then rename it to something random, before deleting it.
 - Example CLI Usage: ```statz --securedelete --path specs.json```
 - Example API Usage: ```file.secure_delete(specs.json)```

### ✂️ Removed GPU Usage
- GPU usage has been removed from the app due to it being extremely buggy and unreliable. Sorry.


## 📝 Side Note
If you find any errors on Linux, please report them to me with as much detail as possible as I do not have a Linux machine.
