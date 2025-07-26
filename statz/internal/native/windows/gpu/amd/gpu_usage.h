/**
 * AMD GPU Usage Monitor Header
 * Header file for AMD GPU monitoring functions using AGS library
 */

#ifndef AMD_GPU_USAGE_H
#define AMD_GPU_USAGE_H

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Initialize AMD GPU monitoring system (AGS)
 * @return 0 on success, negative on error
 *         -1: Could not load AGS library or initialize
 */
int gpu_init(void);

/**
 * Shutdown AMD GPU monitoring system
 */
void gpu_shutdown(void);

/**
 * Get the number of AMD GPUs
 * @return Number of AMD GPUs found, or -1 on error
 */
int gpu_get_count(void);

/**
 * Get detailed GPU information as JSON string
 * @return Allocated JSON string (must be freed by caller), or NULL on error
 * 
 * JSON format:
 * {
 *   "gpus": [
 *     {
 *       "index": 0,
 *       "name": "AMD Radeon RX 7900 XTX",
 *       "gpu_utilization": 85,
 *       "memory_utilization": 75,
 *       "memory_total": 24564498432,
 *       "memory_used": 18423373824,
 *       "memory_free": 6141124608,
 *       "temperature": 72.5,
 *       "power_usage": 350.75
 *     }
 *   ]
 * }
 */
char* gpu_get_info_json(void);

/**
 * Get simple GPU usage percentage for primary AMD GPU
 * @return GPU usage percentage (0-100), or -1 on error
 */
int gpu_get_usage(void);

#ifdef __cplusplus
}
#endif

#endif // AMD_GPU_USAGE_H
