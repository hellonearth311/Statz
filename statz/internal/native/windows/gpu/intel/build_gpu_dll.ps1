# Build script for Intel GPU monitoring DLL
# Requires GCC (MinGW-w64) to be installed and in PATH

Write-Host "Building Intel GPU monitoring DLL..." -ForegroundColor Green

# Check if gcc is available
try {
    $gccVersion = gcc --version 2>$null
    Write-Host "Found GCC: $($gccVersion[0])" -ForegroundColor Cyan
} catch {
    Write-Host "Error: GCC not found in PATH. Please install MinGW-w64 or MSYS2." -ForegroundColor Red
    Write-Host "Download from: https://www.mingw-w64.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create output directory if it doesn't exist
if (!(Test-Path "dist")) {
    New-Item -ItemType Directory -Path "dist" | Out-Null
    Write-Host "Created dist directory" -ForegroundColor Yellow
}

# Compile the DLL
Write-Host "Compiling gpu_usage.c to intel_gpu_monitor.dll..." -ForegroundColor Yellow

$compileArgs = @(
    "-shared",
    "-fPIC", 
    "-O2",
    "-Wall",
    "-o", "dist/intel_gpu_monitor.dll",
    "gpu_usage.c",
    "-luser32",
    "-lkernel32",
    "-lpdh",
    "-ladvapi32"
)

try {
    & gcc $compileArgs
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Success! DLL created at: dist/intel_gpu_monitor.dll" -ForegroundColor Green
        Write-Host ""
        Write-Host "You can now use this DLL from Python with ctypes:" -ForegroundColor Cyan
        Write-Host "  import ctypes" -ForegroundColor Gray
        Write-Host "  dll = ctypes.CDLL('./dist/intel_gpu_monitor.dll')" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Available functions:" -ForegroundColor Cyan
        Write-Host "  - gpu_init() : int" -ForegroundColor Gray
        Write-Host "  - gpu_shutdown() : void" -ForegroundColor Gray
        Write-Host "  - gpu_get_count() : int" -ForegroundColor Gray
        Write-Host "  - gpu_get_usage() : int" -ForegroundColor Gray
        Write-Host "  - gpu_get_info_json() : char*" -ForegroundColor Gray
        
        # Show file size
        $fileInfo = Get-Item "dist/intel_gpu_monitor.dll"
        Write-Host "DLL size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor Yellow
    } else {
        Write-Host "Error: Compilation failed!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error: Compilation failed with exception: $_" -ForegroundColor Red
    exit 1
}

# Also build standalone executable for testing
Write-Host ""
Write-Host "Building standalone test executable..." -ForegroundColor Yellow

$testCompileArgs = @(
    "-DSTANDALONE",
    "-O2",
    "-Wall",
    "-o", "dist/intel_gpu_test.exe",
    "gpu_usage.c",
    "-luser32",
    "-lkernel32", 
    "-lpdh",
    "-ladvapi32"
)

try {
    & gcc $testCompileArgs
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Success! Test executable created at: dist/intel_gpu_test.exe" -ForegroundColor Green
        Write-Host "Run it to test Intel GPU monitoring functionality." -ForegroundColor Cyan
        
        $testFileInfo = Get-Item "dist/intel_gpu_test.exe"
        Write-Host "Test executable size: $([math]::Round($testFileInfo.Length / 1KB, 2)) KB" -ForegroundColor Yellow
    } else {
        Write-Host "Warning: Failed to build test executable." -ForegroundColor Orange
    }
} catch {
    Write-Host "Warning: Failed to build test executable with exception: $_" -ForegroundColor Orange
}

Read-Host "Press Enter to exit"
