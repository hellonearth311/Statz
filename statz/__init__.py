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
    get_system_temps,
    get_top_n_processes,
    system_health_score,
    cpu_benchmark,
    mem_benchmark,
    disk_benchmark,
    export_into_file,
    __version__
)

# Public API - all functions available for import
__all__ = [
    # Core system information functions
    "get_system_specs",
    "get_hardware_usage", 
    "get_system_temps",
    
    # Process and system monitoring
    "get_top_n_processes",
    "system_health_score",
    
    # Performance benchmarking
    "cpu_benchmark", 
    "mem_benchmark",
    "disk_benchmark",
    
    # Utility functions
    "export_into_file",
    
    # Module metadata
    "__version__",
    
    # Module reference (for advanced usage)
    "stats"
]

# Version information
__version__ = __version__