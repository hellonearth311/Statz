'''
Benchmarking module for CPU, memory, and disk performance.'''

from .internal._crossPlatform import _cpu_benchmark, _mem_benchmark, _disk_benchmark

def cpu_benchmark():
    '''
    Get CPU performance with some computational tasks, such as:\n
    - Calculating large Fibonacci numbers\n
    - Calculating large primes\n

    Returns:
     dict: {\n
     "execution_time": time taken to execute (lower is better),\n
     "fibonacci_10000th": fibonacci number computed,\n
     "prime_count": prime number calculated in benchmark,\n
     "score": score calculated (higher is better)\n
     }
     '''
    
    return _cpu_benchmark()

def mem_benchmark():
    '''Benchmark memory allocation and access speed using large lists
    Returns:
     dict: {\n
     "execution_time": time taken to execute the program (lower is better),\n
     "sum_calculated": total sum calculated during the test,\n
     "score": the performance score on your ram (higher is better)\n
     }
    '''

    return _mem_benchmark()

def disk_benchmark():
    '''
    Benchmark disk I/O performance by writing and reading a 10MB test file.
    
    Returns:
     dict: {
     "write_speed": Write speed in MB/s,
     "read_speed": Read speed in MB/s, 
     "write_score": Write performance score (higher is better),
     "read_score": Read performance score (higher is better),
     "overall_score": Overall disk performance score (higher is better)
     }
    '''

    return _disk_benchmark()