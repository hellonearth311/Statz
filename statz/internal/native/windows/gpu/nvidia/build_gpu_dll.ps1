# Build script for NVIDIA GPU monitoring DLL
# Requires GCC (MinGW-w64) to be installed and in PATH

Write-Host "Building NVIDIA GPU monitoring DLL..." -ForegroundColor Green

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
Write-Host "Compiling gpu_usage.c to gpu_monitor.dll..." -ForegroundColor Yellow

$compileArgs = @(
    "-shared",
    "-fPIC", 
    "-O2",
    "-Wall",
    "-o", "dist/gpu_monitor.dll",
    "gpu_usage.c",
    "-luser32",
    "-lkernel32"
)

try {
    & gcc $compileArgs
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Success! DLL created at: dist/gpu_monitor.dll" -ForegroundColor Green
        Write-Host ""
        Write-Host "You can now use this DLL from Python with ctypes:" -ForegroundColor Cyan
        Write-Host "  import ctypes" -ForegroundColor Gray
        Write-Host "  dll = ctypes.CDLL('./dist/gpu_monitor.dll')" -ForegroundColor Gray
        
        # Show file size
        $fileInfo = Get-Item "dist/gpu_monitor.dll"
        Write-Host "DLL size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor Yellow
    } else {
        Write-Host "Error: Compilation failed!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error: Compilation failed with exception: $_" -ForegroundColor Red
    exit 1
}

Read-Host "Press Enter to exit"
