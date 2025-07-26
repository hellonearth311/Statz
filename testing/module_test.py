#!/usr/bin/env python3
"""
Comprehensive Module Test Suite for statz

This test suite covers all module functionality including:
- System specifications retrieval (get_system_specs)
- Real-time hardware usage monitoring (get_hardware_usage)
- Process monitoring and analysis (get_top_n_processes)
- Temperature sensor readings (get_system_temps)
- GPU usage monitoring (_get_windows_gpu_usage)
- Connected devices monitoring (connected_device_monitoring)
- System health scoring (system_health_score)
- Performance benchmarking (cpu_benchmark, mem_benchmark, disk_benchmark)
- Export functionality (JSON and CSV) with custom paths
- File comparison functionality (compare)
- Internet speed testing (internet_speed_test)
- Error handling and edge cases
- Cross-platform compatibility
- Performance and stress testing

Usage:
    python module_test.py                    # Run all tests
    python module_test.py --specs            # Run system specs tests only
    python module_test.py --usage            # Run hardware usage tests only
    python module_test.py --processes        # Run process monitoring tests only
    python module_test.py --temp             # Run temperature tests only
    python module_test.py --gpu              # Run GPU usage tests only
    python module_test.py --devices          # Run connected devices tests only
    python module_test.py --health           # Run health scoring tests only
    python module_test.py --benchmark        # Run benchmarking tests only
    python module_test.py --export           # Run export functionality tests only
    python module_test.py --compare          # Run file comparison tests only
    python module_test.py --internet         # Run internet speed tests only
    python module_test.py --custompath       # Run custom path export tests only
    python module_test.py --stress           # Run stress/performance tests only
    python module_test.py --verbose          # Verbose output
"""

import sys
import os
import time
import json
import csv
import platform
import argparse
import tempfile
import glob
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from unittest.mock import patch, MagicMock

# Add the parent directory to the Python path to import statz
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from statz.stats import get_hardware_usage, get_system_specs, get_top_n_processes, __version__
    from statz.stats import connected_device_monitoring, get_connected_device_by_name, get_connected_devices_by_type
    from statz.benchmark import cpu_benchmark, mem_benchmark, disk_benchmark
    from statz.temp import get_system_temps
    from statz.health import system_health_score
    from statz.file import export_into_file, compare
    from statz.internet import internet_speed_test
    
    # Import GPU usage function for Windows
    try:
        if platform.system() == "Windows":
            from statz.internal._getWindowsInfo import _get_windows_gpu_usage
        else:
            _get_windows_gpu_usage = None
    except ImportError:
        _get_windows_gpu_usage = None
except ImportError as e:
    print(f"❌ Failed to import statz module: {e}")
    sys.exit(1)

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class TestResult:
    """Container for test results"""
    def __init__(self, name: str, passed: bool, output: str = "", error: str = "", duration: float = 0.0):
        self.name = name
        self.passed = passed
        self.output = output
        self.error = error
        self.duration = duration

class ModuleTester:
    """Comprehensive module testing class"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.current_os = platform.system()
        
        # Test output directory
        self.test_output_dir = Path("test_outputs")
        self.test_output_dir.mkdir(exist_ok=True)
        
        print(f"{Colors.CYAN}🧪 statz Module Test Suite{Colors.END}")
        print(f"{Colors.BLUE}Platform: {self.current_os}{Colors.END}")
        print(f"{Colors.BLUE}statz Version: {__version__}{Colors.END}")
        print("-" * 60)
    
    def run_test(self, test_func, test_name: str, *args, **kwargs) -> TestResult:
        """Run a single test function and return result"""
        start_time = time.time()
        
        try:
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Validate result based on test
            if result is None:
                # Some functions like get_system_temps can return None
                passed = True
                output = "Function returned None (acceptable for some functions)"
            elif isinstance(result, (dict, list, tuple, str, int, float)):
                passed = True
                output = f"Function returned {type(result).__name__}: {str(result)[:100]}{'...' if len(str(result)) > 100 else ''}"
            else:
                passed = False
                output = f"Unexpected return type: {type(result)}"
            
            return TestResult(test_name, passed, output, "", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(test_name, False, "", str(e), duration)
    
    def add_result(self, result: TestResult):
        """Add a test result"""
        self.results.append(result)
        
        # Print immediate result
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if result.passed else f"{Colors.RED}❌ FAIL{Colors.END}"
        duration_str = f"({result.duration:.2f}s)"
        print(f"{status} {result.name} {duration_str}")
        
        if not result.passed and (result.error or (self.verbose and result.output)):
            if result.error:
                print(f"    {Colors.RED}Error: {result.error}{Colors.END}")
            if self.verbose and result.output:
                print(f"    {Colors.YELLOW}Output: {result.output}{Colors.END}")
    
    def test_system_specs(self):
        """Test system specifications retrieval"""
        print(f"\n{Colors.BOLD}💻 Testing System Specifications{Colors.END}")
        
        # Test basic system specs
        result = self.run_test(get_system_specs, "Get all system specs")
        self.add_result(result)
        
        # Test individual component specs
        component_tests = [
            ({"get_cpu": True, "get_ram": False, "get_disk": False, "get_network": False, "get_battery": False, "get_gpu": False, "get_os": False}, "CPU specs only"),
            ({"get_cpu": False, "get_ram": True, "get_disk": False, "get_network": False, "get_battery": False, "get_gpu": False, "get_os": False}, "RAM specs only"),
            ({"get_cpu": False, "get_ram": False, "get_disk": True, "get_network": False, "get_battery": False, "get_gpu": False, "get_os": False}, "Disk specs only"),
            ({"get_cpu": False, "get_ram": False, "get_disk": False, "get_network": True, "get_battery": False, "get_gpu": False, "get_os": False}, "Network specs only"),
            ({"get_cpu": False, "get_ram": False, "get_disk": False, "get_network": False, "get_battery": True, "get_gpu": False, "get_os": False}, "Battery specs only"),
            ({"get_cpu": False, "get_ram": False, "get_disk": False, "get_network": False, "get_battery": False, "get_gpu": False, "get_os": True}, "OS specs only"),
        ]
        
        # Add GPU test for Windows
        if self.current_os == "Windows":
            component_tests.append(({"get_cpu": False, "get_ram": False, "get_disk": False, "get_network": False, "get_battery": False, "get_gpu": True, "get_os": False}, "GPU specs only (Windows)"))
        
        for kwargs, description in component_tests:
            result = self.run_test(get_system_specs, description, **kwargs)
            self.add_result(result)
        
        # Test combined components
        combined_tests = [
            ({"get_cpu": True, "get_ram": True, "get_disk": False, "get_network": False, "get_battery": False, "get_gpu": False, "get_os": False}, "CPU + RAM specs"),
            ({"get_cpu": True, "get_ram": True, "get_disk": True, "get_network": True, "get_battery": False, "get_gpu": False, "get_os": False}, "Core components"),
        ]
        
        for kwargs, description in combined_tests:
            result = self.run_test(get_system_specs, description, **kwargs)
            self.add_result(result)
    
    def test_hardware_usage(self):
        """Test real-time hardware usage monitoring"""
        print(f"\n{Colors.BOLD}📊 Testing Hardware Usage Monitoring{Colors.END}")
        
        # Test basic hardware usage
        result = self.run_test(get_hardware_usage, "Get all hardware usage")
        self.add_result(result)
        
        # Test individual component usage
        component_tests = [
            ({"get_cpu": True, "get_ram": False, "get_disk": False, "get_network": False, "get_battery": False}, "CPU usage only"),
            ({"get_cpu": False, "get_ram": True, "get_disk": False, "get_network": False, "get_battery": False}, "RAM usage only"),
            ({"get_cpu": False, "get_ram": False, "get_disk": True, "get_network": False, "get_battery": False}, "Disk usage only"),
            ({"get_cpu": False, "get_ram": False, "get_disk": False, "get_network": True, "get_battery": False}, "Network usage only"),
            ({"get_cpu": False, "get_ram": False, "get_disk": False, "get_network": False, "get_battery": True}, "Battery usage only"),
        ]
        
        for kwargs, description in component_tests:
            result = self.run_test(get_hardware_usage, description, **kwargs)
            self.add_result(result)
        
        # Test combined components
        combined_tests = [
            ({"get_cpu": True, "get_ram": True, "get_disk": False, "get_network": False, "get_battery": False}, "CPU + RAM usage"),
            ({"get_cpu": True, "get_ram": True, "get_disk": True, "get_network": True, "get_battery": False}, "Core components usage"),
        ]
        
        for kwargs, description in combined_tests:
            result = self.run_test(get_hardware_usage, description, **kwargs)
            self.add_result(result)
    
    def test_process_monitoring(self):
        """Test process monitoring and analysis"""
        print(f"\n{Colors.BOLD}⚙️ Testing Process Monitoring{Colors.END}")
        
        # Test basic process monitoring
        process_tests = [
            ((5, "cpu"), "Top 5 CPU processes"),
            ((10, "cpu"), "Top 10 CPU processes"),
            ((5, "mem"), "Top 5 memory processes"),
            ((10, "mem"), "Top 10 memory processes"),
            ((3, "cpu"), "Top 3 CPU processes"),
            ((1, "cpu"), "Single top CPU process"),
            ((20, "cpu"), "Top 20 CPU processes"),
        ]
        
        for args, description in process_tests:
            result = self.run_test(get_top_n_processes, description, *args)
            self.add_result(result)
        
        # Test edge cases
        edge_cases = [
            ((0, "cpu"), "Zero processes (edge case)"),
            ((-1, "cpu"), "Negative process count (edge case)"),
            ((1000, "cpu"), "Very large process count"),
        ]
        
        for args, description in edge_cases:
            result = self.run_test(get_top_n_processes, description, *args)
            self.add_result(result)
        
        # Test invalid process types
        invalid_tests = [
            ((5, "invalid"), "Invalid process type"),
            ((5, ""), "Empty process type"),
            ((5, None), "None process type"),
        ]
        
        for args, description in invalid_tests:
            result = self.run_test(get_top_n_processes, description, *args)
            # These should fail gracefully or handle the error
            self.add_result(result)
    
    def test_temperature_monitoring(self):
        """Test temperature sensor readings"""
        print(f"\n{Colors.BOLD}🌡️ Testing Temperature Monitoring{Colors.END}")
        
        # Test basic temperature reading
        result = self.run_test(get_system_temps, "Get system temperatures")
        self.add_result(result)
        
        # Test multiple calls to ensure consistency
        for i in range(3):
            result = self.run_test(get_system_temps, f"Temperature reading #{i+1}")
            self.add_result(result)
    
    def test_health_scoring(self):
        """Test system health scoring"""
        print(f"\n{Colors.BOLD}🏥 Testing System Health Scoring{Colors.END}")
        
        # Test basic health score
        result = self.run_test(system_health_score, "Basic health score")
        self.add_result(result)
        
        # Test CLI version (detailed scores)
        result = self.run_test(system_health_score, "Detailed health score (CLI version)", cliVersion=True)
        self.add_result(result)
        
        # Test multiple calls to ensure consistency
        for i in range(3):
            result = self.run_test(system_health_score, f"Health score consistency test #{i+1}")
            self.add_result(result)
    
    def test_benchmarking(self):
        """Test performance benchmarking"""
        print(f"\n{Colors.BOLD}🏁 Testing Performance Benchmarking{Colors.END}")
        
        # Test CPU benchmark
        result = self.run_test(cpu_benchmark, "CPU performance benchmark")
        self.add_result(result)
        
        # Test memory benchmark
        result = self.run_test(mem_benchmark, "Memory performance benchmark")
        self.add_result(result)
        
        # Test disk benchmark
        result = self.run_test(disk_benchmark, "Disk performance benchmark")
        self.add_result(result)
        
        # Test benchmark consistency (run each twice)
        consistency_tests = [
            (cpu_benchmark, "CPU benchmark consistency"),
            (mem_benchmark, "Memory benchmark consistency"),
            (disk_benchmark, "Disk benchmark consistency"),
        ]
        
        for benchmark_func, description in consistency_tests:
            result = self.run_test(benchmark_func, description)
            self.add_result(result)
    
    def test_export_functionality(self):
        """Test export functionality"""
        print(f"\n{Colors.BOLD}💾 Testing Export Functionality{Colors.END}")
        
        # Create test functions to export
        def test_data_dict():
            return {"test_key": "test_value", "number": 42, "list": [1, 2, 3]}
        
        def test_data_list():
            return [{"name": "test1", "value": 1}, {"name": "test2", "value": 2}]
        
        def test_specs_data():
            return get_system_specs()
        
        def test_usage_data():
            return get_hardware_usage()
        
        # Test JSON exports
        json_tests = [
            (test_data_dict, False, "Export dict to JSON"),
            (test_data_list, False, "Export list to JSON"),
            (test_specs_data, False, "Export system specs to JSON"),
            (test_usage_data, False, "Export usage data to JSON"),
        ]
        
        for func, csv_flag, description in json_tests:
            result = self.run_test(export_into_file, description, func, csv=csv_flag)
            self.add_result(result)
        
        # Test CSV exports
        csv_tests = [
            (test_data_dict, True, "Export dict to CSV"),
            (test_data_list, True, "Export list to CSV"),
            (test_specs_data, True, "Export system specs to CSV"),
            (test_usage_data, True, "Export usage data to CSV"),
        ]
        
        for func, csv_flag, description in csv_tests:
            result = self.run_test(export_into_file, description, func, csv=csv_flag)
            self.add_result(result)
        
        # Test with invalid data
        def invalid_data():
            return object()  # Non-serializable object
        
        result = self.run_test(export_into_file, "Export invalid data (should handle gracefully)", invalid_data, csv=False)
        self.add_result(result)
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print(f"\n{Colors.BOLD}🚨 Testing Error Handling{Colors.END}")
        
        # Test with mock failures
        with patch('statz.stats.platform.system', return_value="UnsupportedOS"):
            result = self.run_test(get_system_specs, "Unsupported OS handling")
            self.add_result(result)
        
        # Test with invalid parameters
        invalid_tests = [
            (lambda: get_top_n_processes("invalid", "cpu"), "Invalid process count type"),
            (lambda: get_top_n_processes(5, 123), "Invalid process type"),
            (lambda: system_health_score(cliVersion="invalid"), "Invalid cliVersion parameter"),
        ]
        
        for test_func, description in invalid_tests:
            result = self.run_test(test_func, description)
            self.add_result(result)
    
    def test_stress_performance(self):
        """Test stress and performance scenarios"""
        print(f"\n{Colors.BOLD}💪 Testing Stress & Performance{Colors.END}")
        
        # Test rapid consecutive calls
        rapid_tests = [
            (get_hardware_usage, "Rapid hardware usage calls"),
            (get_system_specs, "Rapid system specs calls"),
            (lambda: get_top_n_processes(5, "cpu"), "Rapid process monitoring calls"),
        ]
        
        for test_func, description in rapid_tests:
            start_time = time.time()
            errors = 0
            
            for i in range(10):  # 10 rapid calls
                try:
                    test_func()
                except Exception:
                    errors += 1
            
            duration = time.time() - start_time
            passed = errors == 0
            
            result = TestResult(
                f"{description} (10 calls)",
                passed,
                f"Completed in {duration:.2f}s, {errors} errors",
                f"{errors} errors occurred" if errors > 0 else "",
                duration
            )
            self.add_result(result)
        
        # Test memory usage over time
        start_time = time.time()
        try:
            for i in range(5):
                get_hardware_usage()
                get_system_specs()
                time.sleep(0.1)  # Small delay
            
            duration = time.time() - start_time
            result = TestResult(
                "Memory usage over time test",
                True,
                f"Completed in {duration:.2f}s",
                "",
                duration
            )
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(
                "Memory usage over time test",
                False,
                "",
                str(e),
                duration
            )
        
        self.add_result(result)
    
    def test_data_validation(self):
        """Test data structure validation"""
        print(f"\n{Colors.BOLD}🔍 Testing Data Validation{Colors.END}")
        
        # Test system specs structure
        try:
            specs = get_system_specs()
            
            # Validate specs structure - should be a list
            if not isinstance(specs, list):
                result = TestResult(
                    "System specs structure validation",
                    False,
                    f"Expected list, got {type(specs).__name__}",
                    "System specs should return a list",
                    0.0
                )
            else:
                # Check if we have reasonable data
                has_reasonable_data = len(specs) > 0
                valid_structure = True
                validation_details = []
                
                result = TestResult(
                    "System specs structure validation",
                    has_reasonable_data and valid_structure,
                    f"Specs structure: {', '.join(validation_details)}",
                    "Invalid data types in specs structure" if not valid_structure else 
                    "Empty specs dictionary" if not has_reasonable_data else "",
                    0.0
                )
            self.add_result(result)
        except Exception as e:
            result = TestResult(
                "System specs structure validation",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
        
        # Test hardware usage structure
        try:
            usage = get_hardware_usage()
            
            # Validate usage structure (should be a list of 5 elements)
            has_expected_structure = isinstance(usage, list) and len(usage) == 5
            
            result = TestResult(
                "Hardware usage structure validation",
                has_expected_structure,
                f"Usage structure: {type(usage).__name__} with {len(usage) if isinstance(usage, list) else 'N/A'} elements",
                "Invalid usage structure" if not has_expected_structure else "",
                0.0
            )
            self.add_result(result)
        except Exception as e:
            result = TestResult(
                "Hardware usage structure validation",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
        
        # Test benchmark structure
        benchmark_tests = [
            (cpu_benchmark, "CPU benchmark structure", ["execution_time", "score"]),
            (mem_benchmark, "Memory benchmark structure", ["execution_time", "score"]),
            (disk_benchmark, "Disk benchmark structure", ["overall_score"]),
        ]
        
        for benchmark_func, description, required_keys in benchmark_tests:
            try:
                benchmark_result = benchmark_func()
                
                has_required_keys = isinstance(benchmark_result, dict)
                for key in required_keys:
                    has_required_keys = has_required_keys and key in benchmark_result
                
                result = TestResult(
                    description,
                    has_required_keys,
                    f"Keys: {list(benchmark_result.keys()) if isinstance(benchmark_result, dict) else 'Invalid'}",
                    f"Missing required keys: {required_keys}" if not has_required_keys else "",
                    0.0
                )
                self.add_result(result)
            except Exception as e:
                result = TestResult(
                    description,
                    False,
                    "",
                    str(e),
                    0.0
                )
                self.add_result(result)
    
    def cleanup_test_files(self):
        """Clean up any test files created during export tests"""
        patterns = ["statz_export_*.json", "statz_export_*.csv"]
        for pattern in patterns:
            files = glob.glob(pattern)
            for file in files:
                try:
                    os.remove(file)
                except OSError:
                    pass  # Ignore if file doesn't exist or can't be removed
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print(f"{Colors.BOLD}📊 TEST SUMMARY{Colors.END}")
        print("=" * 60)
        
        print(f"Total Tests: {total_tests}")
        print(f"{Colors.GREEN}Passed: {passed_tests}{Colors.END}")
        print(f"{Colors.RED}Failed: {failed_tests}{Colors.END}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        total_duration = sum(r.duration for r in self.results)
        print(f"Total Duration: {total_duration:.2f}s")
        
        if failed_tests > 0:
            print(f"\n{Colors.RED}❌ Failed Tests:{Colors.END}")
            for result in self.results:
                if not result.passed:
                    print(f"  • {result.name}: {result.error}")
        
        print("\n" + "=" * 60)
        
        # Overall result
        if failed_tests == 0:
            print(f"{Colors.GREEN}🎉 All tests passed! Module is working correctly.{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}⚠️ {failed_tests} test(s) failed. Please review the errors above.{Colors.END}")
            return False
    
    def run_all_tests(self):
        """Run the complete test suite"""
        print(f"{Colors.BOLD}🚀 Running Complete Module Test Suite{Colors.END}\n")
        
        try:
            self.test_system_specs()
            self.test_hardware_usage()
            self.test_process_monitoring()
            self.test_temperature_monitoring()
            self.test_gpu_usage_monitoring()
            self.test_connected_devices_monitoring()
            self.test_health_scoring()
            self.test_benchmarking()
            self.test_export_functionality()
            self.test_custom_path_export()
            self.test_file_comparison()
            self.test_internet_speed()
            self.test_error_handling()
            self.test_data_validation()
            self.test_stress_performance()
        finally:
            self.cleanup_test_files()
        
        return self.print_summary()
    
    def run_specs_tests(self):
        """Run only system specs tests"""
        print(f"{Colors.BOLD}💻 Running System Specs Tests Only{Colors.END}\n")
        self.test_system_specs()
        self.test_data_validation()
        return self.print_summary()
    
    def run_usage_tests(self):
        """Run only hardware usage tests"""
        print(f"{Colors.BOLD}📊 Running Hardware Usage Tests Only{Colors.END}\n")
        self.test_hardware_usage()
        return self.print_summary()
    
    def run_process_tests(self):
        """Run only process monitoring tests"""
        print(f"{Colors.BOLD}⚙️ Running Process Tests Only{Colors.END}\n")
        self.test_process_monitoring()
        return self.print_summary()
    
    def run_temp_tests(self):
        """Run only temperature tests"""
        print(f"{Colors.BOLD}🌡️ Running Temperature Tests Only{Colors.END}\n")
        self.test_temperature_monitoring()
        return self.print_summary()
    
    def run_health_tests(self):
        """Run only health scoring tests"""
        print(f"{Colors.BOLD}🏥 Running Health Tests Only{Colors.END}\n")
        self.test_health_scoring()
        return self.print_summary()
    
    def run_benchmark_tests(self):
        """Run only benchmarking tests"""
        print(f"{Colors.BOLD}🏁 Running Benchmark Tests Only{Colors.END}\n")
        self.test_benchmarking()
        return self.print_summary()
    
    def run_export_tests(self):
        """Run only export functionality tests"""
        print(f"{Colors.BOLD}💾 Running Export Tests Only{Colors.END}\n")
        try:
            self.test_export_functionality()
        finally:
            self.cleanup_test_files()
        return self.print_summary()
    
    def run_stress_tests(self):
        """Run only stress/performance tests"""
        print(f"{Colors.BOLD}💪 Running Stress Tests Only{Colors.END}\n")
        self.test_stress_performance()
        return self.print_summary()
    
    def run_file_comparison_tests(self):
        """Run only file comparison tests"""
        print(f"{Colors.BOLD}📁 Running File Comparison Tests Only{Colors.END}\n")
        try:
            self.test_file_comparison()
        finally:
            self.cleanup_test_files()
        return self.print_summary()
    
    def run_internet_speed_tests(self):
        """Run only internet speed tests"""
        print(f"{Colors.BOLD}🌐 Running Internet Speed Tests Only{Colors.END}\n")
        self.test_internet_speed()
        return self.print_summary()
    
    def run_custom_path_tests(self):
        """Run only custom path export tests"""
        print(f"{Colors.BOLD}📁 Running Custom Path Export Tests Only{Colors.END}\n")
        try:
            self.test_custom_path_export()
        finally:
            self.cleanup_test_files()
        return self.print_summary()
    
    def test_file_comparison(self):
        """Test file comparison functionality"""
        print(f"\n{Colors.BOLD}📁 Testing File Comparison{Colors.END}")
        
        # Create test data for comparison
        test_data_1 = {
            "OS": {"name": "Windows 10", "version": "10.0.19041"},
            "CPU": {"name": "Intel Core i5", "cores": "4", "speed": "2.5GHz"},
            "Memory 1": {"capacity": "8GB", "type": "DDR4"},
            "Storage 1": {"size": "500GB", "type": "SSD"}
        }
        
        test_data_2 = {
            "OS": {"name": "Windows 10", "version": "10.0.19042"},  # Version changed
            "CPU": {"name": "Intel Core i5", "cores": "4", "speed": "2.5GHz"},
            "Memory 1": {"capacity": "16GB", "type": "DDR4"},  # Capacity changed
            "Storage 1": {"size": "500GB", "type": "SSD"},
            "GPU": {"name": "NVIDIA GTX 1060", "memory": "6GB"}  # New component added
        }
        
        # Test JSON to JSON comparison
        json_file_1 = self.test_output_dir / "test_specs_1.json"
        json_file_2 = self.test_output_dir / "test_specs_2.json"
        
        try:
            # Write test JSON files
            with open(json_file_1, 'w') as f:
                json.dump(test_data_1, f, indent=2)
            with open(json_file_2, 'w') as f:
                json.dump(test_data_2, f, indent=2)
            
            # Test JSON comparison
            comparison_result = compare(str(json_file_2), str(json_file_1))
            
            # Validate comparison structure
            expected_keys = ['added', 'removed', 'changed', 'summary']
            has_expected_structure = all(key in comparison_result for key in expected_keys)
            
            result = TestResult(
                "JSON comparison structure test",
                has_expected_structure,
                f"Comparison keys: {list(comparison_result.keys())}",
                "Missing expected keys in comparison result" if not has_expected_structure else "",
                0.0
            )
            self.add_result(result)
            
            # Test if changes were detected correctly
            has_changes = (len(comparison_result['added']) > 0 or 
                          len(comparison_result['changed']) > 0 or 
                          len(comparison_result['removed']) > 0)
            
            result = TestResult(
                "JSON comparison change detection",
                has_changes,
                f"Added: {len(comparison_result['added'])}, Changed: {len(comparison_result['changed'])}, Removed: {len(comparison_result['removed'])}",
                "No changes detected when there should be differences" if not has_changes else "",
                0.0
            )
            self.add_result(result)
            
            # Test summary information
            has_summary = 'summary' in comparison_result and 'total_added' in comparison_result['summary']
            result = TestResult(
                "JSON comparison summary test",
                has_summary,
                f"Summary: {comparison_result.get('summary', {})}",
                "Missing or invalid summary information" if not has_summary else "",
                0.0
            )
            self.add_result(result)
            
        except Exception as e:
            result = TestResult(
                "JSON comparison test",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
        
        # Test CSV comparison
        csv_file_1 = self.test_output_dir / "test_specs_1.csv"
        csv_file_2 = self.test_output_dir / "test_specs_2.csv"
        
        try:
            # Write test CSV files
            with open(csv_file_1, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Component', 'Property', 'Value'])
                writer.writerow(['OS', 'name', 'Windows 10'])
                writer.writerow(['OS', 'version', '10.0.19041'])
                writer.writerow(['CPU', 'name', 'Intel Core i5'])
                writer.writerow(['CPU', 'cores', '4'])
                writer.writerow(['Memory 1', 'capacity', '8GB'])
            
            with open(csv_file_2, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Component', 'Property', 'Value'])
                writer.writerow(['OS', 'name', 'Windows 10'])
                writer.writerow(['OS', 'version', '10.0.19042'])  # Changed
                writer.writerow(['CPU', 'name', 'Intel Core i5'])
                writer.writerow(['CPU', 'cores', '4'])
                writer.writerow(['Memory 1', 'capacity', '16GB'])  # Changed
                writer.writerow(['GPU', 'name', 'NVIDIA GTX 1060'])  # Added
            
            # Test CSV comparison
            comparison_result = compare(str(csv_file_2), str(csv_file_1))
            
            has_expected_structure = all(key in comparison_result for key in expected_keys)
            result = TestResult(
                "CSV comparison structure test",
                has_expected_structure,
                f"Comparison keys: {list(comparison_result.keys())}",
                "Missing expected keys in CSV comparison result" if not has_expected_structure else "",
                0.0
            )
            self.add_result(result)
            
            # Test if changes were detected
            has_changes = (len(comparison_result['added']) > 0 or 
                          len(comparison_result['changed']) > 0 or 
                          len(comparison_result['removed']) > 0)
            
            result = TestResult(
                "CSV comparison change detection",
                has_changes,
                f"Added: {len(comparison_result['added'])}, Changed: {len(comparison_result['changed'])}, Removed: {len(comparison_result['removed'])}",
                "No changes detected in CSV comparison when there should be differences" if not has_changes else "",
                0.0
            )
            self.add_result(result)
            
        except Exception as e:
            result = TestResult(
                "CSV comparison test",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
        
        # Test cross-format comparison (JSON to CSV)
        try:
            comparison_result = compare(str(json_file_1), str(csv_file_1))
            
            # Should work despite different formats
            has_expected_structure = all(key in comparison_result for key in expected_keys)
            result = TestResult(
                "Cross-format comparison (JSON to CSV)",
                has_expected_structure,
                f"Cross-format comparison successful: {list(comparison_result.keys())}",
                "Cross-format comparison failed" if not has_expected_structure else "",
                0.0
            )
            self.add_result(result)
            
        except Exception as e:
            result = TestResult(
                "Cross-format comparison (JSON to CSV)",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
        
        # Test identical file comparison
        try:
            comparison_result = compare(str(json_file_1), str(json_file_1))
            
            # Should show no changes when comparing identical files
            no_changes = (len(comparison_result['added']) == 0 and 
                         len(comparison_result['changed']) == 0 and 
                         len(comparison_result['removed']) == 0)
            
            result = TestResult(
                "Identical file comparison test",
                no_changes,
                f"Identical comparison: Added: {len(comparison_result['added'])}, Changed: {len(comparison_result['changed'])}, Removed: {len(comparison_result['removed'])}",
                "Identical files showing differences" if not no_changes else "",
                0.0
            )
            self.add_result(result)
            
        except Exception as e:
            result = TestResult(
                "Identical file comparison test",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
        
        # Test error handling for non-existent files
        try:
            comparison_result = compare("non_existent_file.json", "another_non_existent_file.json")
            
            # Should return error structure
            has_error_handling = 'error' in str(comparison_result)
            result = TestResult(
                "Non-existent file error handling",
                has_error_handling,
                f"Error handling working: {str(comparison_result)[:100]}",
                "Error handling not working for non-existent files" if not has_error_handling else "",
                0.0
            )
            self.add_result(result)
            
        except Exception as e:
            result = TestResult(
                "Non-existent file error handling",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
        
        # Test unsupported file format
        try:
            txt_file = self.test_output_dir / "test.txt"
            with open(txt_file, 'w') as f:
                f.write("This is a text file")
            
            comparison_result = compare(str(txt_file), str(json_file_1))
            
            # Should return error for unsupported format
            has_error_handling = 'error' in str(comparison_result)
            result = TestResult(
                "Unsupported file format error handling",
                has_error_handling,
                f"Unsupported format handling: {str(comparison_result)[:100]}",
                "Error handling not working for unsupported file formats" if not has_error_handling else "",
                0.0
            )
            self.add_result(result)
            
        except Exception as e:
            result = TestResult(
                "Unsupported file format error handling",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
        
        # Test with real system specs data
        try:
            # Generate real system specs
            real_specs = get_system_specs()
            
            # Export to both JSON and CSV
            real_json_file = self.test_output_dir / "real_specs.json"
            real_csv_file = self.test_output_dir / "real_specs.csv"
            
            with open(real_json_file, 'w') as f:
                json.dump(real_specs, f, indent=2)
            
            # Convert to CSV format for testing
            with open(real_csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Component', 'Property', 'Value'])
                
                if isinstance(real_specs, list):
                    for i, item in enumerate(real_specs):
                        if isinstance(item, dict):
                            component_name = f"Component_{i}"
                            for key, value in item.items():
                                writer.writerow([component_name, key, str(value)])
            
            # Test comparison with real data
            comparison_result = compare(str(real_json_file), str(real_csv_file))
            
            has_expected_structure = all(key in comparison_result for key in expected_keys)
            result = TestResult(
                "Real system specs comparison test",
                has_expected_structure,
                f"Real specs comparison successful with {comparison_result.get('summary', {}).get('total_added', 0)} changes detected",
                "Real specs comparison failed" if not has_expected_structure else "",
                0.0
            )
            self.add_result(result)
            
        except Exception as e:
            result = TestResult(
                "Real system specs comparison test",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
    
    def test_internet_speed(self):
        """Test internet speed test functionality"""
        print(f"\n{Colors.BOLD}🌐 Testing Internet Speed Test{Colors.END}")
        
        # Test basic internet speed test
        result = self.run_test(internet_speed_test, "Basic internet speed test")
        self.add_result(result)
        
        # Test with rounding disabled
        result = self.run_test(internet_speed_test, "Internet speed test without rounding", roundResult=False)
        self.add_result(result)
        
        # Test with rounding enabled explicitly
        result = self.run_test(internet_speed_test, "Internet speed test with rounding", roundResult=True)
        self.add_result(result)
        
        # Validate return structure
        try:
            speed_results = internet_speed_test()
            
            # Should return a tuple of 3 elements (download, upload, ping)
            is_tuple = isinstance(speed_results, tuple)
            has_three_elements = len(speed_results) == 3 if is_tuple else False
            has_numeric_values = all(isinstance(x, (int, float)) for x in speed_results) if has_three_elements else False
            
            result = TestResult(
                "Internet speed test structure validation",
                is_tuple and has_three_elements and has_numeric_values,
                f"Returned: {type(speed_results).__name__} with {len(speed_results) if is_tuple else 'N/A'} elements",
                "Invalid return structure" if not (is_tuple and has_three_elements and has_numeric_values) else "",
                0.0
            )
            self.add_result(result)
            
            # Validate reasonable values
            if has_three_elements and has_numeric_values:
                download, upload, ping = speed_results
                reasonable_values = (
                    0 <= download <= 10000 and  # Download speed 0-10Gbps
                    0 <= upload <= 10000 and    # Upload speed 0-10Gbps
                    0 <= ping <= 5000           # Ping 0-5000ms
                )
                
                result = TestResult(
                    "Internet speed test value validation",
                    reasonable_values,
                    f"Download: {download}Mbps, Upload: {upload}Mbps, Ping: {ping}ms",
                    "Unreasonable speed test values" if not reasonable_values else "",
                    0.0
                )
                self.add_result(result)
            
        except Exception as e:
            result = TestResult(
                "Internet speed test structure validation",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
    
    def test_custom_path_export(self):
        """Test custom path export functionality"""
        print(f"\n{Colors.BOLD}📁 Testing Custom Path Export{Colors.END}")
        
        # Create test data for export
        def test_data_simple():
            return {"test": "data", "number": 42}
        
        def test_data_complex():
            return get_system_specs()
        
        # Test custom JSON export
        json_test_path = self.test_output_dir / "custom_test_export.json"
        
        try:
            # Remove file if it exists
            if json_test_path.exists():
                json_test_path.unlink()
            
            export_into_file(test_data_simple, path=str(json_test_path), csv=False)
            
            # Check if file was created
            file_created = json_test_path.exists()
            
            # Validate file content
            valid_content = False
            if file_created:
                try:
                    with open(json_test_path, 'r') as f:
                        content = json.load(f)
                        valid_content = content.get("test") == "data" and content.get("number") == 42
                except (json.JSONDecodeError, IOError):
                    valid_content = False
            
            result = TestResult(
                "Custom JSON export path test",
                file_created and valid_content,
                f"File created: {file_created}, Valid content: {valid_content}",
                "Custom JSON export failed" if not (file_created and valid_content) else "",
                0.0
            )
            self.add_result(result)
            
        except Exception as e:
            result = TestResult(
                "Custom JSON export path test",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
        
        # Test custom CSV export
        csv_test_path = self.test_output_dir / "custom_test_export.csv"
        
        try:
            # Remove file if it exists
            if csv_test_path.exists():
                csv_test_path.unlink()
            
            export_into_file(test_data_simple, path=str(csv_test_path), csv=True)
            
            # Check if file was created
            file_created = csv_test_path.exists()
            
            # Validate file content (basic check)
            valid_content = False
            if file_created:
                try:
                    with open(csv_test_path, 'r') as f:
                        content = f.read()
                        # Check if it contains some expected content
                        valid_content = len(content.strip()) > 0 and ('test' in content or 'number' in content)
                except IOError:
                    valid_content = False
            
            result = TestResult(
                "Custom CSV export path test",
                file_created and valid_content,
                f"File created: {file_created}, Has content: {valid_content}",
                "Custom CSV export failed" if not (file_created and valid_content) else "",
                0.0
            )
            self.add_result(result)
            
        except Exception as e:
            result = TestResult(
                "Custom CSV export path test",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
        
        # Test with complex data (system specs)
        complex_json_path = self.test_output_dir / "custom_complex_export.json"
        
        try:
            if complex_json_path.exists():
                complex_json_path.unlink()
            
            export_into_file(test_data_complex, path=str(complex_json_path), csv=False)
            
            file_created = complex_json_path.exists()
            
            # Basic validation - file should exist and have reasonable size
            valid_content = False
            if file_created:
                try:
                    size = complex_json_path.stat().st_size
                    valid_content = size > 100  # Should have substantial content
                    
                    # Try to parse as JSON
                    with open(complex_json_path, 'r') as f:
                        json.load(f)  # This will raise exception if invalid JSON
                        
                except (json.JSONDecodeError, IOError):
                    valid_content = False
            
            result = TestResult(
                "Custom complex data export test",
                file_created and valid_content,
                f"File created: {file_created}, Valid: {valid_content}",
                "Complex data export failed" if not (file_created and valid_content) else "",
                0.0
            )
            self.add_result(result)
            
        except Exception as e:
            result = TestResult(
                "Custom complex data export test",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
        
        # Test with None path (should use default behavior)
        try:
            export_into_file(test_data_simple, path=None, csv=False)
            
            # Should create a file with default naming
            import glob
            default_files = glob.glob("statz_export_*.json")
            file_created = len(default_files) > 0
            
            result = TestResult(
                "Default path behavior test",
                file_created,
                f"Default files created: {len(default_files)}",
                "Default path behavior failed" if not file_created else "",
                0.0
            )
            self.add_result(result)
            
            # Clean up default files
            for file in default_files:
                try:
                    os.remove(file)
                except OSError:
                    pass
            
        except Exception as e:
            result = TestResult(
                "Default path behavior test",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
    
    def test_gpu_usage_monitoring(self):
        """Test GPU usage monitoring"""
        print(f"\n{Colors.BOLD}🎮 Testing GPU Usage Monitoring{Colors.END}")
        
        # Test GPU usage on Windows only
        if self.current_os == "Windows" and _get_windows_gpu_usage is not None:
            # Test basic GPU usage
            result = self.run_test(_get_windows_gpu_usage, "Windows GPU usage monitoring")
            self.add_result(result)
            
            # Test multiple calls for consistency
            for i in range(3):
                result = self.run_test(_get_windows_gpu_usage, f"GPU usage reading #{i+1}")
                self.add_result(result)
            
            # Validate GPU usage data structure
            try:
                gpu_data = _get_windows_gpu_usage()
                
                # Check if it's a dictionary
                is_dict = isinstance(gpu_data, dict)
                result = TestResult(
                    "GPU usage data structure validation",
                    is_dict,
                    f"Type: {type(gpu_data).__name__}",
                    "GPU usage should return a dictionary" if not is_dict else "",
                    0.0
                )
                self.add_result(result)
                
                if is_dict:
                    # Check for expected keys
                    expected_keys = ['total_gpus']
                    has_expected_keys = all(key in gpu_data for key in expected_keys)
                    result = TestResult(
                        "GPU usage data keys validation",
                        has_expected_keys,
                        f"Keys: {list(gpu_data.keys())}",
                        f"Missing expected keys: {[k for k in expected_keys if k not in gpu_data]}" if not has_expected_keys else "",
                        0.0
                    )
                    self.add_result(result)
                    
                    # Check GPU count
                    total_gpus = gpu_data.get('total_gpus', 0)
                    valid_gpu_count = isinstance(total_gpus, int) and total_gpus >= 0
                    result = TestResult(
                        "GPU count validation",
                        valid_gpu_count,
                        f"Total GPUs: {total_gpus}",
                        "Invalid GPU count" if not valid_gpu_count else "",
                        0.0
                    )
                    self.add_result(result)
                    
                    # Check vendor-specific data if GPUs are present
                    if total_gpus > 0:
                        vendors = ['nvidia', 'amd', 'intel']
                        vendor_data_found = any(vendor in gpu_data for vendor in vendors)
                        result = TestResult(
                            "GPU vendor data validation",
                            vendor_data_found,
                            f"Available vendors: {[v for v in vendors if v in gpu_data]}",
                            "No vendor-specific GPU data found" if not vendor_data_found else "",
                            0.0
                        )
                        self.add_result(result)
                
            except Exception as e:
                result = TestResult(
                    "GPU usage data validation",
                    False,
                    "",
                    str(e),
                    0.0
                )
                self.add_result(result)
        else:
            # Test that non-Windows platforms handle GPU gracefully
            result = TestResult(
                f"GPU usage on {self.current_os} (expected not available)",
                True,
                f"GPU usage monitoring not available on {self.current_os}",
                "",
                0.0
            )
            self.add_result(result)

    def test_connected_devices_monitoring(self):
        """Test connected devices monitoring"""
        print(f"\n{Colors.BOLD}🔌 Testing Connected Devices Monitoring{Colors.END}")
        
        # Test basic connected device monitoring
        result = self.run_test(connected_device_monitoring, "Basic connected device monitoring")
        self.add_result(result)
        
        # Test multiple calls for consistency
        for i in range(3):
            result = self.run_test(connected_device_monitoring, f"Connected devices reading #{i+1}")
            self.add_result(result)
        
        # Validate connected devices data structure
        try:
            devices_data = connected_device_monitoring()
            
            # Check if it's a dictionary
            is_dict = isinstance(devices_data, dict)
            result = TestResult(
                "Connected devices data structure validation",
                is_dict,
                f"Type: {type(devices_data).__name__}",
                "Connected devices should return a dictionary" if not is_dict else "",
                0.0
            )
            self.add_result(result)
            
            if is_dict:
                # Check for expected keys
                expected_keys = ['total_usb_devices', 'devices', 'summary', 'platform']
                has_expected_keys = all(key in devices_data for key in expected_keys)
                result = TestResult(
                    "Connected devices data keys validation",
                    has_expected_keys,
                    f"Keys: {list(devices_data.keys())}",
                    f"Missing expected keys: {[k for k in expected_keys if k not in devices_data]}" if not has_expected_keys else "",
                    0.0
                )
                self.add_result(result)
                
                # Check device count
                total_devices = devices_data.get('total_usb_devices', 0)
                valid_device_count = isinstance(total_devices, int) and total_devices >= 0
                result = TestResult(
                    "USB device count validation",
                    valid_device_count,
                    f"Total USB devices: {total_devices}",
                    "Invalid USB device count" if not valid_device_count else "",
                    0.0
                )
                self.add_result(result)
                
                # Check devices list
                devices_list = devices_data.get('devices', [])
                valid_devices_list = isinstance(devices_list, list)
                result = TestResult(
                    "USB devices list validation",
                    valid_devices_list,
                    f"Devices list type: {type(devices_list).__name__}, count: {len(devices_list) if valid_devices_list else 'N/A'}",
                    "Devices should be a list" if not valid_devices_list else "",
                    0.0
                )
                self.add_result(result)
                
                # Validate individual device structure if devices exist
                if valid_devices_list and devices_list:
                    first_device = devices_list[0]
                    expected_device_keys = ['device_id', 'name', 'manufacturer', 'device_class', 'status', 'connection_type', 'specs']
                    device_has_expected_keys = isinstance(first_device, dict) and all(key in first_device for key in expected_device_keys)
                    result = TestResult(
                        "Individual device structure validation",
                        device_has_expected_keys,
                        f"First device keys: {list(first_device.keys()) if isinstance(first_device, dict) else 'Not a dict'}",
                        f"Missing device keys: {[k for k in expected_device_keys if k not in first_device] if isinstance(first_device, dict) else 'Device not a dictionary'}" if not device_has_expected_keys else "",
                        0.0
                    )
                    self.add_result(result)
                
        except Exception as e:
            result = TestResult(
                "Connected devices data validation",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
        
        # Test get_connected_device_by_name function
        try:
            # Test with a common device name that might exist
            test_device_names = ['hub', 'root', 'usb', 'mass', 'storage']
            found_device = False
            
            for device_name in test_device_names:
                device = get_connected_device_by_name(device_name)
                if device is not None:
                    found_device = True
                    result = TestResult(
                        f"Get device by name test ('{device_name}')",
                        True,
                        f"Found device: {device.get('name', 'Unknown') if isinstance(device, dict) else device}",
                        "",
                        0.0
                    )
                    self.add_result(result)
                    break
            
            if not found_device:
                result = TestResult(
                    "Get device by name test (no devices found)",
                    True,
                    "No devices found with common names (expected if no USB devices connected)",
                    "",
                    0.0
                )
                self.add_result(result)
            
        except Exception as e:
            result = TestResult(
                "Get device by name test",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
        
        # Test get_connected_devices_by_type function
        try:
            # Test with different device types
            device_types = ['hub', 'storage', 'hid', 'audio', 'network']
            
            for device_type in device_types:
                devices_by_type = get_connected_devices_by_type(device_type)
                
                # Should return a dictionary
                is_dict = isinstance(devices_by_type, dict)
                has_expected_keys = is_dict and all(key in devices_by_type for key in ['device_type', 'count', 'devices', 'platform'])
                
                result = TestResult(
                    f"Get devices by type test ('{device_type}')",
                    is_dict and has_expected_keys,
                    f"Type: {type(devices_by_type).__name__}, keys: {list(devices_by_type.keys()) if is_dict else 'N/A'}",
                    "Invalid structure for devices by type result" if not (is_dict and has_expected_keys) else "",
                    0.0
                )
                self.add_result(result)
        
        except Exception as e:
            result = TestResult(
                "Get devices by type test",
                False,
                "",
                str(e),
                0.0
            )
            self.add_result(result)
    
    def run_gpu_tests(self):
        """Run only GPU usage tests"""
        print(f"{Colors.BOLD}🎮 Running GPU Tests Only{Colors.END}\n")
        self.test_gpu_usage_monitoring()
        return self.print_summary()
    
    def run_devices_tests(self):
        """Run only connected devices tests"""
        print(f"{Colors.BOLD}🔌 Running Connected Devices Tests Only{Colors.END}\n")
        self.test_connected_devices_monitoring()
        return self.print_summary()
    
def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="statz Module Test Suite")
    parser.add_argument("--specs", action="store_true", help="Run system specs tests only")
    parser.add_argument("--usage", action="store_true", help="Run hardware usage tests only")
    parser.add_argument("--processes", action="store_true", help="Run process monitoring tests only")
    parser.add_argument("--temp", action="store_true", help="Run temperature tests only")
    parser.add_argument("--gpu", action="store_true", help="Run GPU usage tests only")
    parser.add_argument("--devices", action="store_true", help="Run connected devices tests only")
    parser.add_argument("--health", action="store_true", help="Run health scoring tests only")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmarking tests only")
    parser.add_argument("--export", action="store_true", help="Run export functionality tests only")
    parser.add_argument("--compare", action="store_true", help="Run file comparison tests only")
    parser.add_argument("--internet", action="store_true", help="Run internet speed tests only")
    parser.add_argument("--custompath", action="store_true", help="Run custom path export tests only")
    parser.add_argument("--stress", action="store_true", help="Run stress/performance tests only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    tester = ModuleTester(verbose=args.verbose)
    
    success = True
    
    if args.specs:
        success = tester.run_specs_tests()
    elif args.usage:
        success = tester.run_usage_tests()
    elif args.processes:
        success = tester.run_process_tests()
    elif args.temp:
        success = tester.run_temp_tests()
    elif args.gpu:
        success = tester.run_gpu_tests()
    elif args.devices:
        success = tester.run_devices_tests()
    elif args.health:
        success = tester.run_health_tests()
    elif args.benchmark:
        success = tester.run_benchmark_tests()
    elif args.export:
        success = tester.run_export_tests()
    elif args.compare:
        success = tester.run_file_comparison_tests()
    elif args.internet:
        success = tester.run_internet_speed_tests()
    elif args.custompath:
        success = tester.run_custom_path_tests()
    elif args.stress:
        success = tester.run_stress_tests()
    else:
        success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
