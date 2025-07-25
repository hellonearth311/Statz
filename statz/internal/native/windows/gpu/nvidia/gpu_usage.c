/**
 * NVIDIA GPU Usage Monitor for Windows
 * Uses NVIDIA Management Library (NVML) to get GPU utilization and memory usage
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>

// NVML function pointers
typedef enum {
    NVML_SUCCESS = 0,
    NVML_ERROR_UNINITIALIZED = 1,
    NVML_ERROR_INVALID_ARGUMENT = 2,
    NVML_ERROR_NOT_SUPPORTED = 3,
    NVML_ERROR_NO_PERMISSION = 4,
    NVML_ERROR_ALREADY_INITIALIZED = 5,
    NVML_ERROR_NOT_FOUND = 6,
    NVML_ERROR_INSUFFICIENT_SIZE = 7,
    NVML_ERROR_INSUFFICIENT_POWER = 8,
    NVML_ERROR_DRIVER_NOT_LOADED = 9,
    NVML_ERROR_TIMEOUT = 10,
    NVML_ERROR_IRQ_ISSUE = 11,
    NVML_ERROR_LIBRARY_NOT_FOUND = 12,
    NVML_ERROR_FUNCTION_NOT_FOUND = 13,
    NVML_ERROR_CORRUPTED_INFOROM = 14,
    NVML_ERROR_GPU_IS_LOST = 15,
    NVML_ERROR_RESET_REQUIRED = 16,
    NVML_ERROR_OPERATING_SYSTEM = 17,
    NVML_ERROR_LIB_RM_VERSION_MISMATCH = 18,
    NVML_ERROR_IN_USE = 19,
    NVML_ERROR_MEMORY = 20,
    NVML_ERROR_NO_DATA = 21,
    NVML_ERROR_VGPU_ECC_NOT_SUPPORTED = 22,
    NVML_ERROR_INSUFFICIENT_RESOURCES = 23,
    NVML_ERROR_FREQ_NOT_SUPPORTED = 24,
    NVML_ERROR_ARGUMENT_VERSION_MISMATCH = 25,
    NVML_ERROR_DEPRECATED = 26,
    NVML_ERROR_UNKNOWN = 999
} nvmlReturn_t;

typedef struct nvmlDevice_st* nvmlDevice_t;

typedef struct {
    unsigned int gpu;
    unsigned int memory;
} nvmlUtilization_t;

typedef struct {
    unsigned long long total;
    unsigned long long free;
    unsigned long long used;
} nvmlMemory_t;

// NVML function pointers
typedef nvmlReturn_t (*nvmlInit_t)(void);
typedef nvmlReturn_t (*nvmlShutdown_t)(void);
typedef nvmlReturn_t (*nvmlDeviceGetCount_t)(unsigned int*);
typedef nvmlReturn_t (*nvmlDeviceGetHandleByIndex_t)(unsigned int, nvmlDevice_t*);
typedef nvmlReturn_t (*nvmlDeviceGetName_t)(nvmlDevice_t, char*, unsigned int);
typedef nvmlReturn_t (*nvmlDeviceGetUtilizationRates_t)(nvmlDevice_t, nvmlUtilization_t*);
typedef nvmlReturn_t (*nvmlDeviceGetMemoryInfo_t)(nvmlDevice_t, nvmlMemory_t*);
typedef nvmlReturn_t (*nvmlDeviceGetTemperature_t)(nvmlDevice_t, int, unsigned int*);
typedef nvmlReturn_t (*nvmlDeviceGetPowerUsage_t)(nvmlDevice_t, unsigned int*);

// Global variables
static HMODULE nvml_lib = NULL;
static nvmlInit_t nvmlInit = NULL;
static nvmlShutdown_t nvmlShutdown = NULL;
static nvmlDeviceGetCount_t nvmlDeviceGetCount = NULL;
static nvmlDeviceGetHandleByIndex_t nvmlDeviceGetHandleByIndex = NULL;
static nvmlDeviceGetName_t nvmlDeviceGetName = NULL;
static nvmlDeviceGetUtilizationRates_t nvmlDeviceGetUtilizationRates = NULL;
static nvmlDeviceGetMemoryInfo_t nvmlDeviceGetMemoryInfo = NULL;
static nvmlDeviceGetTemperature_t nvmlDeviceGetTemperature = NULL;
static nvmlDeviceGetPowerUsage_t nvmlDeviceGetPowerUsage = NULL;

// Load NVML library and function pointers
static int load_nvml() {
    // Try to load nvml.dll from Program Files
    char nvml_path[MAX_PATH];
    const char* possible_paths[] = {
        "C:\\Program Files\\NVIDIA Corporation\\NVSMI\\nvml.dll",
        "C:\\Windows\\System32\\nvml.dll",
        "nvml.dll"
    };
    
    for (int i = 0; i < 3; i++) {
        nvml_lib = LoadLibraryA(possible_paths[i]);
        if (nvml_lib) break;
    }
    
    if (!nvml_lib) {
        return -1;
    }
    
    // Load function pointers
    nvmlInit = (nvmlInit_t)GetProcAddress(nvml_lib, "nvmlInit_v2");
    if (!nvmlInit) nvmlInit = (nvmlInit_t)GetProcAddress(nvml_lib, "nvmlInit");
    
    nvmlShutdown = (nvmlShutdown_t)GetProcAddress(nvml_lib, "nvmlShutdown");
    nvmlDeviceGetCount = (nvmlDeviceGetCount_t)GetProcAddress(nvml_lib, "nvmlDeviceGetCount_v2");
    if (!nvmlDeviceGetCount) nvmlDeviceGetCount = (nvmlDeviceGetCount_t)GetProcAddress(nvml_lib, "nvmlDeviceGetCount");
    
    nvmlDeviceGetHandleByIndex = (nvmlDeviceGetHandleByIndex_t)GetProcAddress(nvml_lib, "nvmlDeviceGetHandleByIndex_v2");
    if (!nvmlDeviceGetHandleByIndex) nvmlDeviceGetHandleByIndex = (nvmlDeviceGetHandleByIndex_t)GetProcAddress(nvml_lib, "nvmlDeviceGetHandleByIndex");
    
    nvmlDeviceGetName = (nvmlDeviceGetName_t)GetProcAddress(nvml_lib, "nvmlDeviceGetName");
    nvmlDeviceGetUtilizationRates = (nvmlDeviceGetUtilizationRates_t)GetProcAddress(nvml_lib, "nvmlDeviceGetUtilizationRates");
    nvmlDeviceGetMemoryInfo = (nvmlDeviceGetMemoryInfo_t)GetProcAddress(nvml_lib, "nvmlDeviceGetMemoryInfo");
    nvmlDeviceGetTemperature = (nvmlDeviceGetTemperature_t)GetProcAddress(nvml_lib, "nvmlDeviceGetTemperature");
    nvmlDeviceGetPowerUsage = (nvmlDeviceGetPowerUsage_t)GetProcAddress(nvml_lib, "nvmlDeviceGetPowerUsage");
    
    if (!nvmlInit || !nvmlShutdown || !nvmlDeviceGetCount || 
        !nvmlDeviceGetHandleByIndex || !nvmlDeviceGetName || 
        !nvmlDeviceGetUtilizationRates || !nvmlDeviceGetMemoryInfo) {
        FreeLibrary(nvml_lib);
        nvml_lib = NULL;
        return -2;
    }
    
    return 0;
}

// Unload NVML library
static void unload_nvml() {
    if (nvml_lib) {
        FreeLibrary(nvml_lib);
        nvml_lib = NULL;
    }
}

// Initialize NVML
int gpu_init() {
    if (load_nvml() != 0) {
        return -1;
    }
    
    nvmlReturn_t result = nvmlInit();
    if (result != NVML_SUCCESS) {
        unload_nvml();
        return -2;
    }
    
    return 0;
}

// Shutdown NVML
void gpu_shutdown() {
    if (nvml_lib && nvmlShutdown) {
        nvmlShutdown();
    }
    unload_nvml();
}

// Get GPU count
int gpu_get_count() {
    unsigned int device_count = 0;
    nvmlReturn_t result = nvmlDeviceGetCount(&device_count);
    
    if (result != NVML_SUCCESS) {
        return -1;
    }
    
    return (int)device_count;
}

// Get GPU information as JSON string
// Returns allocated string that must be freed by caller
char* gpu_get_info_json() {
    unsigned int device_count = 0;
    nvmlReturn_t result = nvmlDeviceGetCount(&device_count);
    
    if (result != NVML_SUCCESS) {
        return NULL;
    }
    
    // Allocate buffer for JSON string (estimate size)
    size_t buffer_size = 1024 + (device_count * 512);
    char* json_buffer = (char*)malloc(buffer_size);
    if (!json_buffer) {
        return NULL;
    }
    
    strcpy(json_buffer, "{\"gpus\":[");
    
    for (unsigned int i = 0; i < device_count; i++) {
        nvmlDevice_t device;
        result = nvmlDeviceGetHandleByIndex(i, &device);
        if (result != NVML_SUCCESS) {
            continue;
        }
        
        // Get device name
        char name[256];
        result = nvmlDeviceGetName(device, name, sizeof(name));
        if (result != NVML_SUCCESS) {
            strcpy(name, "Unknown GPU");
        }
        
        // Get utilization
        nvmlUtilization_t utilization;
        result = nvmlDeviceGetUtilizationRates(device, &utilization);
        unsigned int gpu_util = (result == NVML_SUCCESS) ? utilization.gpu : 0;
        unsigned int mem_util = (result == NVML_SUCCESS) ? utilization.memory : 0;
        
        // Get memory info
        nvmlMemory_t memory;
        result = nvmlDeviceGetMemoryInfo(device, &memory);
        unsigned long long total_mem = (result == NVML_SUCCESS) ? memory.total : 0;
        unsigned long long used_mem = (result == NVML_SUCCESS) ? memory.used : 0;
        unsigned long long free_mem = (result == NVML_SUCCESS) ? memory.free : 0;
        
        // Get temperature (GPU core)
        unsigned int temperature = 0;
        nvmlDeviceGetTemperature(device, 0, &temperature);  // 0 = NVML_TEMPERATURE_GPU
        
        // Get power usage (in milliwatts)
        unsigned int power = 0;
        nvmlDeviceGetPowerUsage(device, &power);
        
        // Add comma if not first device
        if (i > 0) {
            strcat(json_buffer, ",");
        }
        
        // Append GPU info to JSON
        char gpu_info[512];
        snprintf(gpu_info, sizeof(gpu_info),
            "{\"index\":%u,\"name\": \"%s\",\"gpu_utilization\":%u,\"memory_utilization\":%u,"
            "\"memory_total\":%llu,\"memory_used\":%llu,\"memory_free\":%llu,"
            "\"temperature\":%u,\"power_usage\":%.2f}",
            i, name, gpu_util, mem_util, total_mem, used_mem, free_mem,
            temperature, power / 1000.0);  // Convert milliwatts to watts
        
        strcat(json_buffer, gpu_info);
    }
    
    strcat(json_buffer, "]}");
    
    return json_buffer;
}

// Get simple GPU usage percentage for primary GPU
int gpu_get_usage() {
    nvmlDevice_t device;
    nvmlReturn_t result = nvmlDeviceGetHandleByIndex(0, &device);
    if (result != NVML_SUCCESS) {
        return -1;
    }
    
    nvmlUtilization_t utilization;
    result = nvmlDeviceGetUtilizationRates(device, &utilization);
    if (result != NVML_SUCCESS) {
        return -1;
    }
    
    return (int)utilization.gpu;
}

// Test function - can be called from command line
// Only compile main() if STANDALONE is defined
#ifdef STANDALONE
int main(int argc, char* argv[]) {
    printf("NVIDIA GPU Usage Monitor Test\n");
    printf("=============================\n");
    
    if (gpu_init() != 0) {
        printf("Error: Could not initialize NVML. Make sure NVIDIA drivers are installed.\n");
        return 1;
    }
    
    int count = gpu_get_count();
    printf("Found %d GPU(s)\n\n", count);
    
    if (count > 0) {
        char* json_info = gpu_get_info_json();
        if (json_info) {
            printf("GPU Information (JSON):\n%s\n\n", json_info);
            free(json_info);
        }
        
        int usage = gpu_get_usage();
        if (usage >= 0) {
            printf("Primary GPU Usage: %d%%\n", usage);
        }
    }
    
    gpu_shutdown();
    return 0;
}
#endif