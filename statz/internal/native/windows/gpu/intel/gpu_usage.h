/**
 * Intel GPU Usage Monitor Header
 * Header file for Intel GPU monitoring functions
 */

#ifndef INTEL_GPU_USAGE_H
#define INTEL_GPU_USAGE_H

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Initialize Intel GPU monitoring system
 * @return 0 on success, negative on error
 */
int gpu_init(void);

/**
 * Shutdown Intel GPU monitoring system
 */
void gpu_shutdown(void);

/**
 * Get the number of Intel GPUs
 * @return Number of Intel GPUs found, or -1 on error
 */
int gpu_get_count(void);

/**
 * Get detailed GPU information as JSON string
 * @return Allocated JSON string (must be freed by caller), or NULL on error
 */
char* gpu_get_info_json(void);

/**
 * Get simple GPU usage percentage for primary Intel GPU
 * @return GPU usage percentage (0-100), or -1 on error
 */
int gpu_get_usage(void);

#ifdef __cplusplus
}
#endif

#endif // INTEL_GPU_USAGE_H
