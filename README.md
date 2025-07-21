# statz
![PyPI - Downloads](https://img.shields.io/pypi/dm/statz) 
![PyPI Version](https://img.shields.io/pypi/v/statz)
![License](https://img.shields.io/github/license/hellonearth311/statz)
![GitHub issues](https://img.shields.io/github/issues/hellonearth311/statz)
![Last Commit](https://img.shields.io/endpoint?url=https://github-last-commit-badge.vercel.app/lastcommit)

**statz** is a cross-platform Python package that fetches **real-time system usage** and **hardware specs** — all wrapped in a simple, clean API.

Works on **macOS**, **Linux**, and **Windows**, and handles OS-specific madness under the hood so you don’t have to.


<img src="img/logo.png" alt="statz logo" style="border-radius: 15px;" width=200>



---

## ✨ Features

- 📊 Get real-time CPU, RAM, and disk usage
- 💻 Fetch detailed system specifications (CPU, RAM, OS, etc.)
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

# Combine multiple components
statz --specs --cpu --ram --disk
statz --usage --cpu --ram --network
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

# Export to file
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
| `--out` | Export to JSON file |
| `--process-count N` | Number of processes to show (default: 5) |
| `--process-type {cpu,mem}` | Sort processes by CPU or memory usage |

### Examples

```bash
# Get CPU and RAM specs in JSON format
statz --specs --cpu --ram --json

# Monitor top 10 memory-intensive processes
statz --processes --process-count 10 --process-type mem

# Get all usage data and export to file
statz --usage --out

# Get system temperatures and CPU usage
statz --temp --usage --cpu

# Get complete system overview
statz --specs --usage --processes --temp

# Get system health score
statz --health

# Check system health with other components
statz --specs --health --cpu --ram

# Launch interactive dashboard for real-time monitoring
statz --dashboard
```
## 🔗 Links
[PyPi Project 🐍](https://pypi.org/project/statz/)

[Github Repository 🧑‍💻](https://github.com/hellonearth311/Statz)

## 📜 Script Usage

**statz** provides a clean Python API for accessing system information programmatically. Here are examples of all available functions:

### Basic System Information

```python
import statz

# Get complete system specifications
specs = statz.get_system_specs()
print(specs)

# Get selective system specifications (improves performance)
specs = statz.get_system_specs(
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
usage = statz.get_hardware_usage()
print(usage)

# Get selective usage data (improves performance)
usage = statz.get_hardware_usage(
    get_cpu=True,     # CPU usage per core
    get_ram=True,     # Memory usage stats
    get_disk=True,    # Disk I/O speeds
    get_network=False, # Network speeds
    get_battery=True   # Battery status
)
```

### Temperature Monitoring

```python
# Get system temperature readings
temps = statz.get_system_temps()
print(temps)

# Returns platform-specific temperature data:
# macOS: {"CPU": 45.2, "GPU": 38.5}
# Linux: {"coretemp-isa-0000": 42.0, "acpi-0": 35.5}
# Windows: {"ThermalZone _TZ.TZ00": 41.3}
```

### Process Monitoring

```python
# Get top 5 processes by CPU usage (default)
top_processes = statz.get_top_n_processes()
print(top_processes)

# Get top 10 processes by CPU usage
top_cpu = statz.get_top_n_processes(n=10, type="cpu")

# Get top 15 processes by memory usage
top_memory = statz.get_top_n_processes(n=15, type="mem")

# Returns: [{"pid": 1234, "name": "chrome", "usage": 15.2}, ...]
```

### System Health Score

```python
# Get simple health score (0-100)
health_score = statz.system_health_score()
print(f"System Health: {health_score}/100")

# Get detailed health breakdown
health_details = statz.system_health_score(cliVersion=True)
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

### Data Export

```python
# Export any function's output to a JSON file
statz.export_into_file(statz.get_system_specs)
statz.export_into_file(statz.get_hardware_usage)
statz.export_into_file(lambda: statz.system_health_score(cliVersion=True))

# Files are saved as: statz_export_YYYY-MM-DD_HH-MM-SS.json
```

### Platform-Specific Notes

```python
import platform

# Check current platform
current_os = platform.system()

if current_os == "Windows":
    # Windows supports all features including GPU, network, and battery specs
    specs = statz.get_system_specs(get_gpu=True, get_network=True, get_battery=True)
    
elif current_os in ["Darwin", "Linux"]:  # macOS or Linux
    # macOS/Linux don't support GPU, network, or battery specs
    specs = statz.get_system_specs(get_gpu=False, get_network=False, get_battery=False)
```

### Error Handling

```python
try:
    # System information functions
    specs = statz.get_system_specs()
    usage = statz.get_hardware_usage()
    temps = statz.get_system_temps()
    processes = statz.get_top_n_processes()
    health = statz.system_health_score()
    
except OSError as e:
    print(f"Unsupported operating system: {e}")
except Exception as e:
    print(f"Error getting system information: {e}")
```


## 📝 Changelog

### [v1.2.0 – System Health Score 💓](https://github.com/hellonearth311/Statz/releases/tag/v1.2.0)
- 🏥 Added system health score functionality
  - Run `statz --health` in the terminal to get a comprehensive system health assessment
  - Call `statz.stats.system_health_score()` programmatically to get a numerical health score (0-100)
  - Use `statz.stats.system_health_score(cliVersion=True)` to get detailed component breakdown
  - Health score evaluates CPU usage, memory usage, disk usage, temperature, and battery status
  - Color-coded output with ratings: Excellent 🟢, Good 🟡, Fair 🟠, Poor 🔴, Critical ⚠️
- 🏷️ Added version flag
  - Run `statz --version` to check the current version of statz
  - Displays version information in standard format

## 📝 Side Note
If you find any errors on Linux, please report them to me with as much detail as possible as I do not have a Linux machine.
