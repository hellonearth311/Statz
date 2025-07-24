"""
statz - Cross-platform system information and monitoring library.

A comprehensive Python library for retrieving system specifications, 
hardware usage statistics, process information, temperature readings,
health scores, and performance benchmarks across Windows, macOS, and Linux.

Key Features:
- System specifications (CPU, GPU, RAM, disk, network, battery)
- Real-time hardware usage monitoring
- Process monitoring and analysis
- Temperature sensor readings
- System health scoring
- Performance benchmarking
- Export functionality (JSON and CSV)

Example Usage:
    import statz
    
    # Get all system specs
    specs = statz.get_system_specs()
    
    # Get current hardware usage
    usage = statz.get_hardware_usage()
    
    # Get top processes
    processes = statz.get_top_n_processes(10, "cpu")
    
    # Run system health check
    health = statz.system_health_score()
"""

from . import stats
from .stats import (
    get_system_specs,
    get_hardware_usage, 
    get_top_n_processes,
    __version__
)

from .temp import get_system_temps
from .health import system_health_score
from .benchmark import cpu_benchmark, mem_benchmark, disk_benchmark
from .file import export_into_file, compare
from .internet import internet_speed_test

__all__ = [
    "get_system_specs",
    "get_hardware_usage", 
    "get_system_temps",
    "get_top_n_processes",
    "system_health_score",
    "cpu_benchmark", 
    "mem_benchmark",
    "disk_benchmark",
    "export_into_file",
    "compare",
    "__version__",
    "stats",
    "internet_speed_test"
]

# Version information
__version__ = __version__