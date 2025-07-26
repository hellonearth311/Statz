@echo off
REM Build script for Intel GPU monitoring DLL
REM Requires GCC (MinGW-w64) to be installed and in PATH

echo Building Intel GPU monitoring DLL...

REM Check if gcc is available
gcc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: GCC not found in PATH. Please install MinGW-w64 or MSYS2.
    echo Download from: https://www.mingw-w64.org/downloads/
    pause
    exit /b 1
)

REM Create output directory if it doesn't exist
if not exist "dist" mkdir dist

REM Compile the DLL
echo Compiling gpu_usage.c to intel_gpu_monitor.dll...
gcc -shared -fPIC -O2 -Wall ^
    -o dist/intel_gpu_monitor.dll ^
    gpu_usage.c ^
    -luser32 -lkernel32 -lpdh -ladvapi32

if %errorlevel% equ 0 (
    echo Success! DLL created at: dist/intel_gpu_monitor.dll
    echo.
    echo You can now use this DLL from Python with ctypes:
    echo   import ctypes
    echo   dll = ctypes.CDLL('./dist/intel_gpu_monitor.dll'^)
    echo.
    echo Available functions:
    echo   - gpu_init(^) : int
    echo   - gpu_shutdown(^) : void
    echo   - gpu_get_count(^) : int
    echo   - gpu_get_usage(^) : int
    echo   - gpu_get_info_json(^) : char*
) else (
    echo Error: Compilation failed!
    exit /b 1
)

REM Also build standalone executable for testing
echo.
echo Building standalone test executable...
gcc -DSTANDALONE -O2 -Wall ^
    -o dist/intel_gpu_test.exe ^
    gpu_usage.c ^
    -luser32 -lkernel32 -lpdh -ladvapi32

if %errorlevel% equ 0 (
    echo Success! Test executable created at: dist/intel_gpu_test.exe
    echo Run it to test Intel GPU monitoring functionality.
) else (
    echo Warning: Failed to build test executable.
)

pause
