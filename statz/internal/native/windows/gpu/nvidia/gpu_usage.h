/**
 * NVIDIA GPU Usage Monitor Header
 * Header file for NVIDIA GPU monitoring functions using NVML
 */

#ifndef NVIDIA_GPU_USAGE_H
#define NVIDIA_GPU_USAGE_H

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Initialize NVIDIA GPU monitoring system (NVML)
 * @return 0 on success, negative on error
 *         -1: Could not load NVML library
 *         -2: NVML initialization failed
 */
int gpu_init(void);

/**
 * Shutdown NVIDIA GPU monitoring system
 */
void gpu_shutdown(void);

/**
 * Get the number of NVIDIA GPUs
 * @return Number of NVIDIA GPUs found, or -1 on error
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
 *       "name": "GeForce RTX 4090",
 *       "gpu_utilization": 85,
 *       "memory_utilization": 75,
 *       "memory_total": 24564498432,
 *       "memory_used": 18423373824,
 *       "memory_free": 6141124608,
 *       "temperature": 72,
 *       "power_usage": 350.5
 *     }
 *   ]
 * }
 */
char* gpu_get_info_json(void);

/**
 * Get simple GPU usage percentage for primary NVIDIA GPU
 * @return GPU usage percentage (0-100), or -1 on error
 */
int gpu_get_usage(void);

#ifdef __cplusplus
}
#endif

#endif // NVIDIA_GPU_USAGE_H
