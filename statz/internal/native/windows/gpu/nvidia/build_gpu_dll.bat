@echo off
REM REM Create output directory if it doesn't exist
if not exist "..\..\..\..\bin" mkdir "..\..\..\..\bin"

REM Compile the DLL
echo Compiling gpu_usage.c to nvidia_gpu_monitor.dll...
gcc -shared -fPIC -O2 -Wall ^
    -o ..\..\..\..\bin\nvidia_gpu_monitor.dll ^
    gpu_usage.c ^
    -luser32 -lkernel32

if %errorlevel% equ 0 (
    echo Success! DLL created at: ..\..\..\..\bin\nvidia_gpu_monitor.dll for NVIDIA GPU monitoring DLL
REM Requires GCC (MinGW-w64) to be installed and in PATH

echo Building NVIDIA GPU monitoring DLL...

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
echo Compiling gpu_usage.c to gpu_monitor.dll...
gcc -shared -fPIC -O2 -Wall ^
    -o dist/nvgpu_monitor.dll ^
    gpu_usage.c ^
    -luser32 -lkernel32

if %errorlevel% equ 0 (
    echo Success! DLL created at: dist/gpu_monitor.dll
    echo.
    echo You can now use this DLL from Python with ctypes:
    echo   import ctypes
    echo   dll = ctypes.CDLL('./dist/gpu_monitor.dll'^)
) else (
    echo Error: Compilation failed!
    exit /b 1
)

pause
