'''System health monitoring module for cross-platform systems.
This module provides a unified interface to calculate system health scores based on various hardware metrics.'''

from .internal._crossPlatform import _system_health_score

def system_health_score(cliVersion=False):
    '''
    Calculate a system health score based on various hardware metrics.
    
    This function evaluates the health of the system by calculating scores for CPU, memory, disk,
    temperature, battery (if available), and network usage. Each metric contributes to a total score
    that reflects the overall health of the system.

    Args:
        cliVersion (bool, optional): If True, returns a dictionary with individual scores for each metric.
                                     If False, returns a single health score. Defaults to False.
    
    Returns:
        float: A health score between 0 and 100, where 100 indicates optimal health.\n
        OR\n
        dict: If cliVersion is True, returns a dictionary with individual scores for each metric.\n
        OR\n
        exception: If any metric calculation fails.\n
    
    Raises:
        Exception: If any metric calculation fails.
    '''

    return _system_health_score(cliVersion)
