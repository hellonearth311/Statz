/**
 * Intel GPU Usage Monitor for Windows
 * Uses Intel Graphics Control Library (IGCL) to get GPU utilization and memory usage
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

// Intel Graphics Control Library (IGCL) definitions
typedef enum {
    IGCL_SUCCESS = 0,
    IGCL_ERROR_INVALID_ARGUMENT = 1,
    IGCL_ERROR_NOT_SUPPORTED = 2,
    IGCL_ERROR_NOT_INITIALIZED = 3,
    IGCL_ERROR_DEVICE_NOT_FOUND = 4,
    IGCL_ERROR_UNKNOWN = 5
} igcl_result_t;

typedef struct {
    uint32_t device_id;
    char device_name[256];
    uint32_t vendor_id;
    uint64_t total_memory;
} igcl_device_info_t;

typedef struct {
    uint32_t gpu_utilization;
    uint32_t memory_utilization;
    uint64_t memory_used;
    uint64_t memory_total;
    uint32_t temperature;
    uint32_t power_usage;
} igcl_device_stats_t;

// Forward declarations for IGCL API (dynamically loaded)
typedef igcl_result_t (*igcl_init_t)(void);
typedef igcl_result_t (*igcl_shutdown_t)(void);
typedef igcl_result_t (*igcl_get_device_count_t)(uint32_t* count);
typedef igcl_result_t (*igcl_get_device_info_t)(uint32_t device_index, igcl_device_info_t* info);
typedef igcl_result_t (*igcl_get_device_stats_t)(uint32_t device_index, igcl_device_stats_t* stats);

// Global variables for IGCL API
static HMODULE igcl_lib = NULL;
static igcl_init_t igcl_init = NULL;
static igcl_shutdown_t igcl_shutdown = NULL;
static igcl_get_device_count_t igcl_get_device_count = NULL;
static igcl_get_device_info_t igcl_get_device_info = NULL;
static igcl_get_device_stats_t igcl_get_device_stats = NULL;
static BOOL igcl_initialized = FALSE;

// Performance counter variables (fallback)
static PDH_HQUERY query_handle = NULL;
static PDH_HCOUNTER gpu_util_counter = NULL;
static PDH_HCOUNTER gpu_memory_counter = NULL;
static BOOL perf_counters_initialized = FALSE;

// Load Intel Graphics Control Library (IGCL)
static int load_igcl() {
    // Try to load IGCL library
    const char* possible_paths[] = {
        "C:\\Windows\\System32\\igcl64.dll",
        "C:\\Windows\\SysWOW64\\igcl32.dll",
        "C:\\Program Files\\Intel\\Intel(R) Graphics\\igcl64.dll",
        "C:\\Program Files (x86)\\Intel\\Intel(R) Graphics\\igcl32.dll",
        "igcl64.dll",
        "igcl32.dll"
    };
    
    for (int i = 0; i < 6; i++) {
        igcl_lib = LoadLibraryA(possible_paths[i]);
        if (igcl_lib) break;
    }
    
    if (!igcl_lib) {
        return -1;
    }
    
    // Load function pointers
    igcl_init = (igcl_init_t)GetProcAddress(igcl_lib, "igcl_init");
    igcl_shutdown = (igcl_shutdown_t)GetProcAddress(igcl_lib, "igcl_shutdown");
    igcl_get_device_count = (igcl_get_device_count_t)GetProcAddress(igcl_lib, "igcl_get_device_count");
    igcl_get_device_info = (igcl_get_device_info_t)GetProcAddress(igcl_lib, "igcl_get_device_info");
    igcl_get_device_stats = (igcl_get_device_stats_t)GetProcAddress(igcl_lib, "igcl_get_device_stats");
    
    if (!igcl_init || !igcl_shutdown || !igcl_get_device_count || 
        !igcl_get_device_info || !igcl_get_device_stats) {
        FreeLibrary(igcl_lib);
        igcl_lib = NULL;
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
    
    // Try to add Intel GPU performance counters
    // These paths may vary depending on Intel driver version
    const char* gpu_counter_paths[] = {
        "\\GPU Engine(*)\\Utilization Percentage",
        "\\Intel(R) Graphics\\GPU Utilization",
        "\\GPU Process Memory(*)\\Shared Usage",
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
        "\\Intel(R) Graphics\\Memory Usage"
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

// Unload IGCL API
static void unload_igcl() {
    if (igcl_initialized && igcl_shutdown) {
        igcl_shutdown();
        igcl_initialized = FALSE;
    }
    
    if (igcl_lib) {
        FreeLibrary(igcl_lib);
        igcl_lib = NULL;
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

// Initialize Intel GPU monitoring
int gpu_init() {
    // Try IGCL API first
    if (load_igcl() == 0) {
        if (igcl_init && igcl_init() == IGCL_SUCCESS) {
            igcl_initialized = TRUE;
            printf("Intel IGCL API initialized successfully\n");
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

// Shutdown Intel GPU monitoring
void gpu_shutdown() {
    unload_igcl();
    cleanup_performance_counters();
}

// Get Intel GPU count
int gpu_get_count() {
    if (igcl_initialized && igcl_get_device_count) {
        uint32_t count = 0;
        if (igcl_get_device_count(&count) == IGCL_SUCCESS) {
            return (int)count;
        }
    }
    
    // Fallback: Intel integrated graphics typically shows as 1 GPU
    return 1;
}

// Get GPU utilization using IGCL or performance counters
static int get_gpu_utilization() {
    // Try IGCL first
    if (igcl_initialized && igcl_get_device_stats) {
        igcl_device_stats_t stats;
        if (igcl_get_device_stats(0, &stats) == IGCL_SUCCESS) {
            return (int)stats.gpu_utilization;
        }
    }
    
    // Fallback to performance counters
    return get_gpu_utilization_perf_counter();
}

// Get GPU memory usage using IGCL or performance counters (in bytes)
static unsigned long long get_gpu_memory_usage() {
    // Try IGCL first
    if (igcl_initialized && igcl_get_device_stats) {
        igcl_device_stats_t stats;
        if (igcl_get_device_stats(0, &stats) == IGCL_SUCCESS) {
            return stats.memory_used;
        }
    }
    
    // Fallback to performance counters
    return get_gpu_memory_perf_counter();
}

// Get GPU total memory using IGCL or estimate
static unsigned long long get_gpu_total_memory() {
    // Try IGCL first
    if (igcl_initialized && igcl_get_device_info) {
        igcl_device_info_t info;
        if (igcl_get_device_info(0, &info) == IGCL_SUCCESS) {
            return info.total_memory;
        }
    }
    
    // Fallback: estimate from system memory
    MEMORYSTATUSEX mem_status;
    mem_status.dwLength = sizeof(mem_status);
    GlobalMemoryStatusEx(&mem_status);
    return mem_status.ullTotalPhys / 8; // Estimate Intel GPU gets about 1/8 of system RAM
}

// Get Intel GPU information as JSON string
char* gpu_get_info_json() {
    // Allocate buffer for JSON string
    size_t buffer_size = 1024;
    char* json_buffer = (char*)malloc(buffer_size);
    if (!json_buffer) {
        return NULL;
    }
    
    // Get GPU information
    int gpu_util = get_gpu_utilization();
    unsigned long long memory_used = get_gpu_memory_usage();
    unsigned long long total_mem = get_gpu_total_memory();
    unsigned long long free_mem = total_mem - memory_used;
    
    // Get GPU name
    char gpu_name[256] = "Intel Integrated Graphics";
    
    // Try to get GPU name from IGCL first
    if (igcl_initialized && igcl_get_device_info) {
        igcl_device_info_t info;
        if (igcl_get_device_info(0, &info) == IGCL_SUCCESS) {
            strncpy(gpu_name, info.device_name, sizeof(gpu_name) - 1);
            gpu_name[sizeof(gpu_name) - 1] = '\0';
        }
    } else {
        // Fallback: try to get Intel GPU name from registry
        HKEY hkey;
        if (RegOpenKeyExA(HKEY_LOCAL_MACHINE, 
                          "SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000", 
                          0, KEY_READ, &hkey) == ERROR_SUCCESS) {
            DWORD buffer_size_reg = sizeof(gpu_name);
            RegQueryValueExA(hkey, "DriverDesc", NULL, NULL, (LPBYTE)gpu_name, &buffer_size_reg);
            RegCloseKey(hkey);
        }
    }
    
    // Get additional stats if available via IGCL
    uint32_t temperature = 0;
    float power_usage = 0.0f;
    
    if (igcl_initialized && igcl_get_device_stats) {
        igcl_device_stats_t stats;
        if (igcl_get_device_stats(0, &stats) == IGCL_SUCCESS) {
            temperature = stats.temperature;
            power_usage = stats.power_usage / 1000.0f; // Convert milliwatts to watts
        }
    }
    
    // Create JSON response
    snprintf(json_buffer, buffer_size,
        "{\"gpus\":[{"
        "\"index\":0,"
        "\"name\":\"%s\","
        "\"gpu_utilization\":%d,"
        "\"memory_utilization\":%d,"
        "\"memory_total\":%llu,"
        "\"memory_used\":%llu,"
        "\"memory_free\":%llu,"
        "\"temperature\":%u,"
        "\"power_usage\":%.2f"
        "}]}",
        gpu_name, 
        gpu_util >= 0 ? gpu_util : 0,
        total_mem > 0 ? (int)((memory_used * 100) / total_mem) : 0,
        total_mem,
        memory_used,
        free_mem,
        temperature,
        power_usage);
    
    return json_buffer;
}

// Get simple GPU usage percentage for primary Intel GPU
int gpu_get_usage() {
    return get_gpu_utilization();
}

// Test function - can be called from command line
// Only compile main() if STANDALONE is defined
#ifdef STANDALONE
int main(int argc, char* argv[]) {
    printf("Intel GPU Usage Monitor Test\n");
    printf("============================\n");
    
    if (gpu_init() != 0) {
        printf("Error: Could not initialize Intel GPU monitoring.\n");
        printf("Make sure Intel Graphics drivers are installed.\n");
        return 1;
    }
    
    int count = gpu_get_count();
    printf("Found %d Intel GPU(s)\n\n", count);
    
    if (count > 0) {
        char* json_info = gpu_get_info_json();
        if (json_info) {
            printf("Intel GPU Information (JSON):\n%s\n\n", json_info);
            free(json_info);
        }
        
        int usage = gpu_get_usage();
        printf("Intel GPU Usage: %d%%\n", usage);
    }
    
    gpu_shutdown();
    return 0;
}
#endif
