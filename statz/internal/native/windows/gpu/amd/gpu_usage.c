/**
 * AMD GPU Usage Monitor for Windows
 * Uses AMD GPU Services (AGS) library to get GPU utilization and memory usage
 * Also falls back to Windows Performance Counters for basic metrics
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <windows.h>
#include <pdh.h>
#include <pdhmsg.h>

#ifdef _MSC_VER
#pragma comment(lib, "pdh.lib")
#endif

// AMD GPU Services (AGS) library definitions
typedef enum {
    AGS_SUCCESS = 0,
    AGS_FAILURE = -1,
    AGS_INVALID_ARGS = -2,
    AGS_OUT_OF_MEMORY = -3,
    AGS_MISSING_D3D_DLL = -4,
    AGS_LEGACY_DRIVER = -5,
    AGS_NO_AMD_DRIVER_INSTALLED = -6,
    AGS_EXTENSION_NOT_SUPPORTED = -7,
    AGS_ADL_FAILURE = -8,
    AGS_DX_FAILURE = -9
} AGSReturnCode;

typedef struct {
    int adapterIndex;
    int vendorId;
    int deviceId;
    int revisionId;
    char adapterString[256];
    int numCUs;                     // Number of compute units
    int numWGPs;                    // Number of work group processors
    int numROPs;                    // Number of render output units
    long long localMemoryInBytes;   // Local memory in bytes
    long long sharedMemoryInBytes;  // Shared memory in bytes
    int memoryBandwidth;            // Memory bandwidth in GB/s
    float teraFlops;                // Peak teraflops
} AGSDeviceInfo;

typedef struct {
    float gpuUsagePercent;
    float memoryUsagePercent;
    long long memoryUsedInBytes;
    float temperatureInC;
    float fanSpeedPercent;
    float engineClockInMHz;
    float memoryClockInMHz;
    float powerUsageInWatts;
} AGSGPUUsage;

typedef struct {
    int numDevices;
    AGSDeviceInfo* devices;
} AGSGPUInfo;

typedef void* AGSContext;

// Forward declarations for AGS API (dynamically loaded)
typedef AGSReturnCode (*agsInitialize_t)(int agsVersion, const void* config, AGSContext** context, AGSGPUInfo* gpuInfo);
typedef AGSReturnCode (*agsDeInitialize_t)(AGSContext* context);
typedef AGSReturnCode (*agsGetGPUMemoryUsage_t)(AGSContext* context, int deviceIndex, AGSGPUUsage* usage);
typedef AGSReturnCode (*agsGetVersionNumber_t)(void);

// Global variables for AGS API
static HMODULE ags_lib = NULL;
static agsInitialize_t agsInitialize = NULL;
static agsDeInitialize_t agsDeInitialize = NULL;
static agsGetGPUMemoryUsage_t agsGetGPUMemoryUsage = NULL;
static agsGetVersionNumber_t agsGetVersionNumber = NULL;
static AGSContext* ags_context = NULL;
static AGSGPUInfo gpu_info = {0};
static BOOL ags_initialized = FALSE;

// Performance counter variables (fallback)
static PDH_HQUERY query_handle = NULL;
static PDH_HCOUNTER gpu_util_counter = NULL;
static PDH_HCOUNTER gpu_memory_counter = NULL;
static BOOL perf_counters_initialized = FALSE;

// Load AMD GPU Services (AGS) library
static int load_ags() {
    // Try to load AGS library
    const char* possible_paths[] = {
        "C:\\Program Files\\AMD\\ags_lib\\lib\\amd_ags_x64.dll",
        "C:\\Program Files (x86)\\AMD\\ags_lib\\lib\\amd_ags_x86.dll",
        "C:\\Windows\\System32\\amd_ags_x64.dll",
        "C:\\Windows\\SysWOW64\\amd_ags_x86.dll",
        "amd_ags_x64.dll",
        "amd_ags_x86.dll"
    };
    
    for (int i = 0; i < 6; i++) {
        ags_lib = LoadLibraryA(possible_paths[i]);
        if (ags_lib) break;
    }
    
    if (!ags_lib) {
        return -1;
    }
    
    // Load function pointers
    agsInitialize = (agsInitialize_t)GetProcAddress(ags_lib, "agsInitialize");
    agsDeInitialize = (agsDeInitialize_t)GetProcAddress(ags_lib, "agsDeInitialize");
    agsGetGPUMemoryUsage = (agsGetGPUMemoryUsage_t)GetProcAddress(ags_lib, "agsGetGPUMemoryUsage");
    agsGetVersionNumber = (agsGetVersionNumber_t)GetProcAddress(ags_lib, "agsGetVersionNumber");
    
    if (!agsInitialize || !agsDeInitialize) {
        FreeLibrary(ags_lib);
        ags_lib = NULL;
        return -2;
    }
    
    return 0;
}

// Initialize performance counters as fallback
static int init_performance_counters() {
    PDH_STATUS status;
    
    // Create query
    status = PdhOpenQueryA(NULL, 0, &query_handle);
    if (status != ERROR_SUCCESS) {
        return -1;
    }
    
    // Try to add AMD GPU performance counters
    // These paths may vary depending on AMD driver version
    const char* gpu_counter_paths[] = {
        "\\GPU Engine(*)\\Utilization Percentage",
        "\\AMD Graphics\\GPU Utilization",
        "\\GPU Process Memory(*)\\Dedicated Usage",
        "\\GPU Engine(engtype_3D)\\Utilization Percentage"
    };
    
    BOOL found_counter = FALSE;
    for (int i = 0; i < 4; i++) {
        status = PdhAddCounterA(query_handle, gpu_counter_paths[i], 0, &gpu_util_counter);
        if (status == ERROR_SUCCESS) {
            found_counter = TRUE;
            break;
        }
    }
    
    // Try to add GPU memory counter
    const char* memory_counter_paths[] = {
        "\\GPU Process Memory(*)\\Dedicated Usage",
        "\\GPU Process Memory(*)\\Shared Usage",
        "\\AMD Graphics\\Memory Usage"
    };
    
    for (int i = 0; i < 3; i++) {
        status = PdhAddCounterA(query_handle, memory_counter_paths[i], 0, &gpu_memory_counter);
        if (status == ERROR_SUCCESS) {
            break;
        }
    }
    
    if (!found_counter) {
        PdhCloseQuery(query_handle);
        query_handle = NULL;
        return -2;
    }
    
    // Collect initial sample
    PdhCollectQueryData(query_handle);
    Sleep(100); // Wait a bit for first sample
    
    perf_counters_initialized = TRUE;
    return 0;
}

// Unload AGS API
static void unload_ags() {
    if (ags_initialized && ags_context && agsDeInitialize) {
        agsDeInitialize(ags_context);
        ags_context = NULL;
        ags_initialized = FALSE;
    }
    
    if (ags_lib) {
        FreeLibrary(ags_lib);
        ags_lib = NULL;
    }
}

// Cleanup performance counters
static void cleanup_performance_counters() {
    if (query_handle) {
        PdhCloseQuery(query_handle);
        query_handle = NULL;
    }
    perf_counters_initialized = FALSE;
}

// Get GPU utilization using performance counters (fallback)
static int get_gpu_utilization_perf_counter() {
    if (!perf_counters_initialized || !query_handle) {
        return -1;
    }
    
    PDH_STATUS status = PdhCollectQueryData(query_handle);
    if (status != ERROR_SUCCESS) {
        return -1;
    }
    
    if (gpu_util_counter) {
        PDH_FMT_COUNTERVALUE counter_value;
        status = PdhGetFormattedCounterValue(gpu_util_counter, PDH_FMT_DOUBLE, NULL, &counter_value);
        if (status == ERROR_SUCCESS && counter_value.CStatus == PDH_CSTATUS_VALID_DATA) {
            return (int)counter_value.doubleValue;
        }
    }
    
    return 0; // Return 0 if we can't get the value
}

// Get GPU memory usage using performance counters (in bytes, fallback)
static unsigned long long get_gpu_memory_perf_counter() {
    if (!perf_counters_initialized || !query_handle) {
        return 0;
    }
    
    if (gpu_memory_counter) {
        PDH_FMT_COUNTERVALUE counter_value;
        PDH_STATUS status = PdhGetFormattedCounterValue(gpu_memory_counter, PDH_FMT_LARGE, NULL, &counter_value);
        if (status == ERROR_SUCCESS && counter_value.CStatus == PDH_CSTATUS_VALID_DATA) {
            return (unsigned long long)counter_value.largeValue;
        }
    }
    
    return 0;
}

// Initialize AMD GPU monitoring
int gpu_init() {
    // Try AGS API first
    if (load_ags() == 0) {
        if (agsInitialize && agsInitialize(5, NULL, &ags_context, &gpu_info) == AGS_SUCCESS) {
            ags_initialized = TRUE;
            printf("AMD AGS API initialized successfully\n");
            return 0;
        }
    }
    
    // Fallback to performance counters
    if (init_performance_counters() == 0) {
        printf("Performance counters initialized successfully\n");
        return 0;
    }
    
    return -1;
}

// Shutdown AMD GPU monitoring
void gpu_shutdown() {
    unload_ags();
    cleanup_performance_counters();
}

// Get AMD GPU count
int gpu_get_count() {
    if (ags_initialized) {
        return gpu_info.numDevices;
    }
    
    // Fallback: assume 1 AMD GPU
    return 1;
}

// Get GPU utilization using AGS or performance counters
static int get_gpu_utilization(int device_index) {
    // Try AGS first
    if (ags_initialized && agsGetGPUMemoryUsage) {
        AGSGPUUsage usage;
        if (agsGetGPUMemoryUsage(ags_context, device_index, &usage) == AGS_SUCCESS) {
            return (int)usage.gpuUsagePercent;
        }
    }
    
    // Fallback to performance counters
    return get_gpu_utilization_perf_counter();
}

// Get GPU memory usage using AGS or performance counters (in bytes)
static unsigned long long get_gpu_memory_usage(int device_index) {
    // Try AGS first
    if (ags_initialized && agsGetGPUMemoryUsage) {
        AGSGPUUsage usage;
        if (agsGetGPUMemoryUsage(ags_context, device_index, &usage) == AGS_SUCCESS) {
            return usage.memoryUsedInBytes;
        }
    }
    
    // Fallback to performance counters
    return get_gpu_memory_perf_counter();
}

// Get AMD GPU information as JSON string
char* gpu_get_info_json() {
    int device_count = gpu_get_count();
    if (device_count <= 0) {
        return NULL;
    }
    
    // Allocate buffer for JSON string (estimate size)
    size_t buffer_size = 1024 + (device_count * 1024);
    char* json_buffer = (char*)malloc(buffer_size);
    if (!json_buffer) {
        return NULL;
    }
    
    strcpy(json_buffer, "{\"gpus\":[");
    
    for (int i = 0; i < device_count; i++) {
        // Get device information
        char gpu_name[256] = "AMD Graphics Card";
        unsigned long long total_mem = 0;
        unsigned long long used_mem = get_gpu_memory_usage(i);
        int gpu_util = get_gpu_utilization(i);
        float temperature = 0.0f;
        float power_usage = 0.0f;
        
        // Try to get detailed info from AGS
        if (ags_initialized && i < gpu_info.numDevices) {
            strncpy(gpu_name, gpu_info.devices[i].adapterString, sizeof(gpu_name) - 1);
            gpu_name[sizeof(gpu_name) - 1] = '\0';
            total_mem = gpu_info.devices[i].localMemoryInBytes;
            
            // Get additional stats if available
            if (agsGetGPUMemoryUsage) {
                AGSGPUUsage usage;
                if (agsGetGPUMemoryUsage(ags_context, i, &usage) == AGS_SUCCESS) {
                    temperature = usage.temperatureInC;
                    power_usage = usage.powerUsageInWatts;
                }
            }
        } else {
            // Fallback: try to get AMD GPU name from registry
            HKEY hkey;
            if (RegOpenKeyExA(HKEY_LOCAL_MACHINE, 
                              "SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000", 
                              0, KEY_READ, &hkey) == ERROR_SUCCESS) {
                DWORD buffer_size_reg = sizeof(gpu_name);
                RegQueryValueExA(hkey, "DriverDesc", NULL, NULL, (LPBYTE)gpu_name, &buffer_size_reg);
                RegCloseKey(hkey);
            }
            
            // Estimate memory for fallback
            total_mem = 8ULL * 1024 * 1024 * 1024; // Assume 8GB for fallback
        }
        
        unsigned long long free_mem = (total_mem > used_mem) ? (total_mem - used_mem) : 0;
        
        // Add comma if not first device
        if (i > 0) {
            strcat(json_buffer, ",");
        }
        
        // Append GPU info to JSON
        char gpu_info_str[1024];
        snprintf(gpu_info_str, sizeof(gpu_info_str),
            "{\"index\":%d,\"name\":\"%s\",\"gpu_utilization\":%d,\"memory_utilization\":%d,"
            "\"memory_total\":%llu,\"memory_used\":%llu,\"memory_free\":%llu,"
            "\"temperature\":%.1f,\"power_usage\":%.2f}",
            i, gpu_name, 
            gpu_util >= 0 ? gpu_util : 0,
            total_mem > 0 ? (int)((used_mem * 100) / total_mem) : 0,
            total_mem, used_mem, free_mem,
            temperature, power_usage);
        
        strcat(json_buffer, gpu_info_str);
    }
    
    strcat(json_buffer, "]}");
    
    return json_buffer;
}

// Get simple GPU usage percentage for primary AMD GPU
int gpu_get_usage() {
    return get_gpu_utilization(0);
}

// Test function - can be called from command line
// Only compile main() if STANDALONE is defined
#ifdef STANDALONE
int main(int argc, char* argv[]) {
    printf("AMD GPU Usage Monitor Test\n");
    printf("==========================\n");
    
    if (gpu_init() != 0) {
        printf("Error: Could not initialize AMD GPU monitoring.\n");
        printf("Make sure AMD drivers are installed.\n");
        return 1;
    }
    
    int count = gpu_get_count();
    printf("Found %d AMD GPU(s)\n\n", count);
    
    if (count > 0) {
        char* json_info = gpu_get_info_json();
        if (json_info) {
            printf("AMD GPU Information (JSON):\n%s\n\n", json_info);
            free(json_info);
        }
        
        int usage = gpu_get_usage();
        printf("AMD GPU Usage: %d%%\n", usage);
    }
    
    gpu_shutdown();
    return 0;
}
#endif
