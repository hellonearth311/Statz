# statz

**statz** is a cross-platform Python package that fetches **real-time system usage** and **hardware specs** — all wrapped in a simple, clean API.

Works on **macOS**, **Linux**, and **Windows**, and handles OS-specific madness under the hood so you don’t have to.

<img src="img/logo.png" alt="drawing" width="200"/>


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

## �️ CLI Usage

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
```

---
[PyPi Project 🐍](https://pypi.org/project/statz/)

[Github Repository 🧑‍💻](https://github.com/hellonearth311/Statz)

## 📝 Changelog

### v0.4.1 – Bug Squashing and Windows Compatibility
- Fixed CLI Bugs 🐞
  - I have fixed the CLI bugs that some users are reporting
- Added OS information to Windows 🪟
  - You can now get OS information on Windows!
## 📝 Side Note
If you find any errors on Linux, please report them to me with as much detail as possible as I do not have a Linux machine.
