#!/usr/bin/env python3
"""
Comprehensive CLI Test Suite for statz

This test suite covers all CLI functionality including:
- Basic commands (specs, usage, processes, temp, health, benchmark, internetspeedtest)
- Component-specific flags (cpu, ram, disk, gpu, network, battery, os)
- Output formats (json, table, csv, out)
- Custom path export functionality
- Process monitoring options
- Internet speed testing
- Error handling and edge cases
- Cross-platform compatibility

Usage:
    python cli_test.py                    # Run all tests
    python cli_test.py --basic            # Run basic functionality tests only
    python cli_test.py --output           # Run output format tests only
    python cli_test.py --components       # Run component-specific tests only
    python cli_test.py --processes        # Run process monitoring tests only
    python cli_test.py --benchmarks       # Run benchmark tests only
    python cli_test.py --dashboard        # Test dashboard (interactive)
    python cli_test.py --internet         # Run internet speed test only
    python cli_test.py --custompath       # Run custom path export tests only
    python cli_test.py --verbose          # Verbose output
"""

import subprocess
import sys
import os
import json
import csv
import time
import platform
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional

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

class CLITester:
    """Comprehensive CLI testing class"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.current_os = platform.system()
        
        # Determine the correct Python command and statz module path
        self.python_cmd = self._get_python_command()
        self.statz_cmd = [self.python_cmd, "-m", "statz"]
        
        # Test output directory
        self.test_output_dir = Path("test_outputs")
        self.test_output_dir.mkdir(exist_ok=True)
        
        print(f"{Colors.CYAN}🧪 statz CLI Test Suite{Colors.END}")
        print(f"{Colors.BLUE}Platform: {self.current_os}{Colors.END}")
        print(f"{Colors.BLUE}Python Command: {' '.join(self.statz_cmd)}{Colors.END}")
        print("-" * 60)
    
    def _get_python_command(self) -> str:
        """Determine the correct Python command to use"""
        # Try to use the virtual environment if available
        venv_python = Path("../.venv/Scripts/python.exe")  # Windows
        if not venv_python.exists():
            venv_python = Path("../.venv/bin/python")  # Unix-like
        
        if venv_python.exists():
            return str(venv_python.resolve())
        else:
            return sys.executable
    
    def _filter_harmless_warnings(self, stderr: str) -> str:
        """Filter out harmless Python warnings that shouldn't count as errors"""
        if not stderr:
            return stderr
        
        # List of harmless warning patterns to filter out
        harmless_patterns = [
            "Could not find platform independent libraries <prefix>",
            "Consider setting $PYTHONHOME to <prefix>[:<exec_prefix>]",
            "Python path configuration:",
        ]
        
        # Split stderr into lines and filter out harmless warnings
        lines = stderr.split('\n')
        filtered_lines = []
        
        for line in lines:
            is_harmless = False
            for pattern in harmless_patterns:
                if pattern in line:
                    is_harmless = True
                    break
            
            if not is_harmless:
                filtered_lines.append(line)
        
        # Join back and strip empty lines at the end
        filtered_stderr = '\n'.join(filtered_lines).strip()
        return filtered_stderr
    
    def run_command(self, args: List[str], timeout: int = 30) -> Tuple[bool, str, str, float]:
        """Run a statz command and return success, stdout, stderr, duration"""
        cmd = self.statz_cmd + args
        start_time = time.time()
        
        try:
            if self.verbose:
                print(f"{Colors.YELLOW}Running: {' '.join(cmd)}{Colors.END}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=".."  # Run from the statz package directory
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            # Filter out harmless Python warnings from stderr
            filtered_stderr = self._filter_harmless_warnings(result.stderr)
            
            return success, result.stdout, filtered_stderr, duration
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return False, "", f"Command timed out after {timeout}s", duration
        except Exception as e:
            duration = time.time() - start_time
            return False, "", f"Exception: {str(e)}", duration
    
    def add_result(self, name: str, passed: bool, output: str = "", error: str = "", duration: float = 0.0):
        """Add a test result"""
        result = TestResult(name, passed, output, error, duration)
        self.results.append(result)
        
        # Print immediate result
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
        duration_str = f"({duration:.2f}s)"
        print(f"{status} {name} {duration_str}")
        
        if not passed and (error or (self.verbose and output)):
            print(f"  {Colors.RED}Error: {error}{Colors.END}")
            if self.verbose and output:
                print(f"  {Colors.YELLOW}Output: {output[:200]}...{Colors.END}")
    
    def test_basic_commands(self):
        """Test basic CLI commands"""
        print(f"\n{Colors.BOLD}🔧 Testing Basic Commands{Colors.END}")
        
        basic_tests = [
            (["--help"], "Help command"),
            (["--version"], "Version command"),
            (["--specs"], "System specifications"),
            (["--usage"], "System usage"),
            (["--processes"], "Process monitoring"),
            (["--temp"], "Temperature readings"),
            (["--health"], "System health score"),
            (["--benchmark"], "Performance benchmark"),
        ]
        
        for args, description in basic_tests:
            success, output, error, duration = self.run_command(args)
            self.add_result(description, success, output, error, duration)
    
    def test_component_flags(self):
        """Test component-specific flags"""
        print(f"\n{Colors.BOLD}🔩 Testing Component Flags{Colors.END}")
        
        # Test specs with individual components
        component_tests = [
            (["--specs", "--cpu"], "CPU specifications"),
            (["--specs", "--ram"], "RAM specifications"),
            (["--specs", "--disk"], "Disk specifications"),
            (["--specs", "--os"], "OS specifications"),
            (["--usage", "--cpu"], "CPU usage"),
            (["--usage", "--ram"], "RAM usage"),
            (["--usage", "--disk"], "Disk usage"),
            (["--usage", "--network"], "Network usage"),
        ]
        
        # Add platform-specific tests
        if self.current_os == "Windows":
            component_tests.extend([
                (["--specs", "--gpu"], "GPU specifications (Windows)"),
                (["--specs", "--network"], "Network specifications (Windows)"),
                (["--specs", "--battery"], "Battery specifications (Windows)"),
                (["--usage", "--gpu"], "GPU usage (Windows)"),
                (["--usage", "--battery"], "Battery usage (Windows)"),
            ])
        else:
            # Test GPU flag on non-Windows (should handle gracefully)
            component_tests.extend([
                (["--specs", "--gpu"], f"GPU specifications ({self.current_os} - should show unavailable)"),
                (["--usage", "--gpu"], f"GPU usage ({self.current_os} - should show unavailable)"),
            ])
        
        # Test combined components
        component_tests.extend([
            (["--specs", "--cpu", "--ram", "--disk"], "Combined specs (CPU+RAM+Disk)"),
            (["--usage", "--cpu", "--ram", "--network"], "Combined usage (CPU+RAM+Network)"),
            (["--benchmark", "--cpu", "--ram"], "Combined benchmarks (CPU+RAM)"),
        ])
        
        for args, description in component_tests:
            success, output, error, duration = self.run_command(args)
            self.add_result(description, success, output, error, duration)
    
    def test_output_formats(self):
        """Test different output formats"""
        print(f"\n{Colors.BOLD}📄 Testing Output Formats{Colors.END}")
        
        output_tests = [
            (["--specs", "--json"], "JSON output format"),
            (["--usage", "--json"], "Usage JSON output"),
            (["--specs", "--table"], "Table output format"),
            (["--usage", "--table"], "Usage table output"),
            (["--processes", "--table"], "Process table output"),
            (["--benchmark", "--table"], "Benchmark table output"),
            (["--health", "--table"], "Health table output"),
        ]
        
        for args, description in output_tests:
            success, output, error, duration = self.run_command(args)
            
            # Additional validation for JSON output
            if "--json" in args and success:
                try:
                    json.loads(output)
                    json_valid = True
                except json.JSONDecodeError:
                    json_valid = False
                    error += " (Invalid JSON output)"
                    success = False
            
            self.add_result(description, success, output, error, duration)
    
    def test_export_functionality(self):
        """Test file export functionality"""
        print(f"\n{Colors.BOLD}💾 Testing Export Functionality{Colors.END}")
        
        export_tests = [
            (["--specs", "--out"], "JSON file export"),
            (["--usage", "--csv"], "CSV file export"),
            (["--processes", "--csv"], "Process CSV export"),
            (["--benchmark", "--csv"], "Benchmark CSV export"),
            (["--specs", "--cpu", "--ram", "--csv"], "Component CSV export"),
        ]
        
        for args, description in export_tests:
            # Clean up any existing export files first
            self._cleanup_export_files()
            
            success, output, error, duration = self.run_command(args)
            
            # Check if export file was created
            if success:
                export_created = self._check_export_files_created(args)
                if not export_created:
                    success = False
                    error += " (Export file not created)"
            
            self.add_result(description, success, output, error, duration)
    
    def test_process_monitoring(self):
        """Test process monitoring options"""
        print(f"\n{Colors.BOLD}⚙️  Testing Process Monitoring{Colors.END}")
        
        process_tests = [
            (["--processes"], "Default process monitoring"),
            (["--processes", "--process-count", "10"], "Custom process count"),
            (["--processes", "--process-type", "cpu"], "CPU-sorted processes"),
            (["--processes", "--process-type", "mem"], "Memory-sorted processes"),
            (["--processes", "--process-count", "15", "--process-type", "mem"], "Combined process options"),
            (["--processes", "--table"], "Process table format"),
            (["--processes", "--json"], "Process JSON format"),
        ]
        
        for args, description in process_tests:
            success, output, error, duration = self.run_command(args)
            self.add_result(description, success, output, error, duration)
    
    def test_benchmark_functionality(self):
        """Test benchmark functionality"""
        print(f"\n{Colors.BOLD}🏁 Testing Benchmark Functionality{Colors.END}")
        
        benchmark_tests = [
            (["--benchmark"], "Full system benchmark"),
            (["--benchmark", "--cpu"], "CPU benchmark only"),
            (["--benchmark", "--ram"], "RAM benchmark only"),
            (["--benchmark", "--disk"], "Disk benchmark only"),
            (["--benchmark", "--cpu", "--ram"], "CPU+RAM benchmark"),
            (["--benchmark", "--table"], "Benchmark table output"),
            (["--benchmark", "--json"], "Benchmark JSON output"),
        ]
        
        for args, description in benchmark_tests:
            # Benchmarks can take longer
            success, output, error, duration = self.run_command(args, timeout=60)
            self.add_result(description, success, output, error, duration)
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print(f"\n{Colors.BOLD}🚨 Testing Error Handling{Colors.END}")
        
        error_tests = [
            (["--invalid-flag"], "Invalid flag handling"),
            (["--process-count", "abc"], "Invalid process count"),
            (["--process-type", "invalid"], "Invalid process type"),
            (["--process-count", "-5"], "Negative process count"),
            (["--specs", "--usage", "--processes"], "Conflicting commands"),
        ]
        
        for args, description in error_tests:
            success, output, error, duration = self.run_command(args)
            # For error tests, we expect them to fail gracefully
            handled_gracefully = not success and ("error" in error.lower() or "usage:" in output.lower())
            self.add_result(description, handled_gracefully, output, error, duration)
    
    def test_comprehensive_scenarios(self):
        """Test realistic usage scenarios"""
        print(f"\n{Colors.BOLD}🎯 Testing Comprehensive Scenarios{Colors.END}")
        
        scenario_tests = [
            (["--specs", "--usage", "--processes", "--temp"], "Complete system overview"),
            (["--specs", "--health", "--cpu", "--ram", "--table"], "Health monitoring scenario"),
            (["--usage", "--cpu", "--ram", "--network", "--json"], "Resource monitoring JSON"),
            (["--benchmark", "--cpu", "--ram", "--csv"], "Performance testing with export"),
            (["--processes", "--process-count", "20", "--process-type", "mem", "--table"], "Memory analysis scenario"),
        ]
        
        for args, description in scenario_tests:
            success, output, error, duration = self.run_command(args, timeout=45)
            self.add_result(description, success, output, error, duration)
    
    def test_internet_speed(self):
        """Test internet speed test functionality"""
        print(f"\n{Colors.BOLD}🌐 Testing Internet Speed Test{Colors.END}")
        
        # Note: Internet speed tests require network connectivity and can be slow
        speed_tests = [
            (["--internetspeedtest"], "Basic internet speed test"),
            (["--internetspeedtest", "--json"], "Internet speed test JSON output"),
            (["--internetspeedtest", "--table"], "Internet speed test table output"),
        ]
        
        for args, description in speed_tests:
            print(f"{Colors.YELLOW}Note: {description} may take 30-60 seconds...{Colors.END}")
            # Internet speed tests can take much longer
            success, output, error, duration = self.run_command(args, timeout=120)
            
            # Additional validation for speed test output
            if success and output:
                # Check if output contains expected speed test results
                has_download = "download" in output.lower()
                has_upload = "upload" in output.lower()
                has_ping = "ping" in output.lower()
                
                if not (has_download and has_upload and has_ping):
                    success = False
                    error += " (Missing expected speed test results)"
            
            self.add_result(description, success, output, error, duration)
    
    def test_compare_functionality(self):
        """Test file comparison functionality"""
        print(f"\n{Colors.BOLD}🔄 Testing File Comparison{Colors.END}")
        
        # First, create some test files to compare
        test_file1 = "test_compare_file1.json"
        test_file2 = "test_compare_file2.json"
        test_file3 = "test_compare_identical.json"
        
        # Clean up any existing test files
        for file in [test_file1, test_file2, test_file3]:
            try:
                os.remove(f"../{file}")
            except FileNotFoundError:
                pass
        
        # Create test data files
        test_data1 = {
            "cpu": {"name": "Intel Core i7", "cores": 8, "speed": 3.4},
            "memory": {"total": 16, "available": 8},
            "disk": {"total": 500, "free": 200}
        }
        
        test_data2 = {
            "cpu": {"name": "Intel Core i7", "cores": 8, "speed": 3.6},  # Changed speed
            "memory": {"total": 32, "available": 16},  # Changed memory
            "disk": {"total": 500, "free": 150},  # Changed free space
            "gpu": {"name": "NVIDIA RTX 4080"}  # Added GPU
        }
        
        test_data3 = test_data1.copy()  # Identical to test_data1
        
        try:
            # Create test files
            with open(f"../{test_file1}", 'w') as f:
                json.dump(test_data1, f, indent=2)
            with open(f"../{test_file2}", 'w') as f:
                json.dump(test_data2, f, indent=2)
            with open(f"../{test_file3}", 'w') as f:
                json.dump(test_data3, f, indent=2)
            
            compare_tests = [
                # Test compare with missing arguments
                (["--compare"], "Compare without paths (should fail)"),
                (["--compare", "--path1", test_file1], "Compare with only one path (should fail)"),
                
                # Test valid comparisons
                (["--compare", "--path1", test_file1, "--path2", test_file2], "Compare different files"),
                (["--compare", "--path1", test_file1, "--path2", test_file3], "Compare identical files"),
                (["--compare", "--path1", test_file1, "--path2", test_file2, "--json"], "Compare with JSON output"),
                
                # Test with non-existent files
                (["--compare", "--path1", "nonexistent1.json", "--path2", "nonexistent2.json"], "Compare non-existent files (should fail gracefully)"),
                (["--compare", "--path1", test_file1, "--path2", "nonexistent.json"], "Compare existing vs non-existent file"),
            ]
            
            for args, description in compare_tests:
                success, output, error, duration = self.run_command(args)
                
                # Special handling for expected failures
                if "should fail" in description:
                    # These should fail gracefully with error messages
                    expected_failure = not success and (
                        "error" in error.lower() or 
                        "error" in output.lower() or
                        "required" in output.lower()
                    )
                    self.add_result(description, expected_failure, output, error, duration)
                elif "identical files" in description and success:
                    # Check if output indicates files are identical
                    identical_detected = (
                        "identical" in output.lower() or 
                        "no differences" in output.lower() or
                        '"total_added": 0' in output
                    )
                    self.add_result(description, identical_detected, output, error, duration)
                elif "different files" in description and success:
                    # Check if output shows differences
                    differences_detected = (
                        "added" in output.lower() or 
                        "changed" in output.lower() or 
                        "difference" in output.lower() or
                        '"total_added":' in output or
                        '"total_changed":' in output
                    )
                    self.add_result(description, differences_detected, output, error, duration)
                else:
                    self.add_result(description, success, output, error, duration)
        
        finally:
            # Clean up test files
            for file in [test_file1, test_file2, test_file3]:
                try:
                    os.remove(f"../{file}")
                except FileNotFoundError:
                    pass
    
    def test_gpu_functionality(self):
        """Test GPU-specific functionality"""
        print(f"\n{Colors.BOLD}🎮 Testing GPU Functionality{Colors.END}")
        
        gpu_tests = [
            (["--usage", "--gpu"], "GPU usage monitoring"),
            (["--usage", "--gpu", "--json"], "GPU usage JSON output"),
            (["--usage", "--gpu", "--table"], "GPU usage table output"),
            (["--specs", "--gpu"], "GPU specifications"),
            (["--specs", "--gpu", "--json"], "GPU specs JSON output"),
            (["--specs", "--gpu", "--table"], "GPU specs table output"),
            (["--usage", "--cpu", "--gpu", "--ram"], "Combined usage with GPU"),
            (["--specs", "--cpu", "--gpu", "--ram"], "Combined specs with GPU"),
        ]
        
        for args, description in gpu_tests:
            success, output, error, duration = self.run_command(args)
            
            # Special validation for GPU tests
            if success and output:
                # On Windows, should show GPU info or proper error
                # On other platforms, should show "not available" message
                if self.current_os == "Windows":
                    # Should either show GPU data or indicate no GPU found
                    valid_output = (
                        "gpu" in output.lower() or 
                        "nvidia" in output.lower() or 
                        "amd" in output.lower() or 
                        "intel" in output.lower() or
                        "not available" in output.lower() or
                        "not found" in output.lower()
                    )
                else:
                    # Should indicate GPU monitoring not available on this platform
                    valid_output = (
                        "not available" in output.lower() or
                        "not supported" in output.lower() or
                        f"{self.current_os.lower()}" in output.lower()
                    )
                
                if not valid_output:
                    success = False
                    error += " (GPU output doesn't contain expected information)"
            
            self.add_result(description, success, output, error, duration)
    
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
            print(f"\n{Colors.RED}❌ FAILED TESTS:{Colors.END}")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.name}")
                    if result.error:
                        print(f"    Error: {result.error}")
        
        print("\n" + "=" * 60)
        
        # Overall result
        if failed_tests == 0:
            print(f"{Colors.GREEN}🎉 ALL TESTS PASSED!{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}💥 {failed_tests} TEST(S) FAILED{Colors.END}")
            return False
    
    def run_all_tests(self):
        """Run the complete test suite"""
        print(f"{Colors.BOLD}🚀 Running Complete CLI Test Suite{Colors.END}\n")
        
        self.test_basic_commands()
        self.test_component_flags()
        self.test_gpu_functionality()
        self.test_output_formats()
        self.test_export_functionality()
        self.test_custom_path_export()
        self.test_compare_functionality()
        self.test_process_monitoring()
        self.test_benchmark_functionality()
        self.test_error_handling()
        self.test_comprehensive_scenarios()
        
        return self.print_summary()
    
    def run_basic_tests(self):
        """Run only basic functionality tests"""
        print(f"{Colors.BOLD}🔧 Running Basic Tests Only{Colors.END}\n")
        self.test_basic_commands()
        return self.print_summary()
    
    def run_output_tests(self):
        """Run only output format tests"""
        print(f"{Colors.BOLD}📄 Running Output Format Tests Only{Colors.END}\n")
        self.test_output_formats()
        self.test_export_functionality()
        return self.print_summary()
    
    def run_component_tests(self):
        """Run only component-specific tests"""
        print(f"{Colors.BOLD}🔩 Running Component Tests Only{Colors.END}\n")
        self.test_component_flags()
        return self.print_summary()
    
    def run_process_tests(self):
        """Run only process monitoring tests"""
        print(f"{Colors.BOLD}⚙️ Running Process Tests Only{Colors.END}\n")
        self.test_process_monitoring()
        return self.print_summary()
    
    def run_benchmark_tests(self):
        """Run only benchmark tests"""
        print(f"{Colors.BOLD}🏁 Running Benchmark Tests Only{Colors.END}\n")
        self.test_benchmark_functionality()
        return self.print_summary()
    
    def run_dashboard_test(self):
        """Run only dashboard test"""
        print(f"{Colors.BOLD}📊 Running Dashboard Test Only{Colors.END}\n")
        self.test_dashboard()
        return self.print_summary()
    
    def run_internet_speed_test(self):
        """Run only internet speed test"""
        print(f"{Colors.BOLD}🌐 Running Internet Speed Test Only{Colors.END}\n")
        self.test_internet_speed()
        return self.print_summary()
    
    def run_custom_path_tests(self):
        """Run only custom path export tests"""
        print(f"{Colors.BOLD}📁 Running Custom Path Tests Only{Colors.END}\n")
        self.test_custom_path_export()
        return self.print_summary()
    
    def run_gpu_tests(self):
        """Run only GPU functionality tests"""
        print(f"{Colors.BOLD}🎮 Running GPU Tests Only{Colors.END}\n")
        self.test_gpu_functionality()
        return self.print_summary()
    
    def run_compare_tests(self):
        """Run only file comparison tests"""
        print(f"{Colors.BOLD}🔄 Running Compare Tests Only{Colors.END}\n")
        self.test_compare_functionality()
        return self.print_summary()

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="statz CLI Test Suite")
    parser.add_argument("--basic", action="store_true", help="Run basic functionality tests only")
    parser.add_argument("--output", action="store_true", help="Run output format tests only")
    parser.add_argument("--components", action="store_true", help="Run component-specific tests only")
    parser.add_argument("--gpu", action="store_true", help="Run GPU functionality tests only")
    parser.add_argument("--compare", action="store_true", help="Run file comparison tests only")
    parser.add_argument("--processes", action="store_true", help="Run process monitoring tests only")
    parser.add_argument("--benchmarks", action="store_true", help="Run benchmark tests only")
    parser.add_argument("--dashboard", action="store_true", help="Test dashboard (interactive)")
    parser.add_argument("--internet", action="store_true", help="Run internet speed test only")
    parser.add_argument("--custompath", action="store_true", help="Run custom path export tests only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    tester = CLITester(verbose=args.verbose)
    
    success = True
    
    if args.basic:
        success = tester.run_basic_tests()
    elif args.output:
        success = tester.run_output_tests()
    elif args.components:
        success = tester.run_component_tests()
    elif args.gpu:
        success = tester.run_gpu_tests()
    elif args.compare:
        success = tester.run_compare_tests()
    elif args.processes:
        success = tester.run_process_tests()
    elif args.benchmarks:
        success = tester.run_benchmark_tests()
    elif args.dashboard:
        success = tester.run_dashboard_test()
    elif args.internet:
        success = tester.run_internet_speed_test()
    elif args.custompath:
        success = tester.run_custom_path_tests()
    else:
        success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
