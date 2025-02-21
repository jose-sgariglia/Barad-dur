import os
import time
import psutil
import logging
from contextlib import contextmanager 

barad_logger = logging.getLogger("barad_logger")

class Monitoring:
    """
    Monitoring class for system monitoring.
    Analyze latency, throughput, CPU and RAM usage.
    """

    def __init__(self, pid=None):
        self.pid = pid if pid is not None else os.getpid()
        self.process = psutil.Process(self.pid)
        self.process.cpu_percent(None)
        self.num_cores = psutil.cpu_count(logical=True)

    def get_cpu_usage(self, interval=None):
        """
        Get the CPU usage of the process.
        """
        raw_cpu_usage = self.process.cpu_percent(interval=interval)
        normalized_cpu_usage = raw_cpu_usage / self.num_cores if self.num_cores else raw_cpu_usage
        return normalized_cpu_usage
    
    def get_ram_usage(self):
        """
        Get the RAM usage of the process.
        """
        return self.process.memory_info().rss / (1024 ** 2)
    
# -----------------------------------------------------------

def monitor_decorator(name_monitoring:str="", interval:float=None):
    """
    Decorator to monitor the CPU and RAM usage of a function.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            name_monitoring_str = f" - {name_monitoring}" if isinstance(name_monitoring, str) else ""

            monitor = Monitoring()
            monitor.get_cpu_usage(interval=interval)
            start_time = time.time()
            
            result = func(*args, **kwargs)
            
            elapsed_time = time.time() - start_time
            cpu_usage = monitor.get_cpu_usage(interval=interval)
            ram_usage = monitor.get_ram_usage()
            
            barad_logger.info(f"[MS{name_monitoring_str}] Elapsed time: {elapsed_time:.2f} seconds")
            barad_logger.info(f"[MS{name_monitoring_str}] CPU usage: {cpu_usage:.2f}%")
            barad_logger.info(f"[MS{name_monitoring_str}] RAM usage: {ram_usage:.2f} MB")
            
            return result
        return wrapper
    return decorator



@contextmanager
def monitor_context(name_monitoring="", interval=None):
    """
    Context manager to monitor the CPU and RAM usage of a block of code.
    """

    name_monitoring_str = f" - {name_monitoring}" if isinstance(name_monitoring, str) else ""

    monitor = Monitoring()
    monitor.get_cpu_usage(interval=interval)
    start_time = time.time()
    
    try:
        yield monitor
    finally:
        elapsed_time = time.time() - start_time
        cpu_usage = monitor.get_cpu_usage(interval=interval)
        ram_usage = monitor.get_ram_usage()
        
        barad_logger.info(f"[MS{name_monitoring_str}] Elapsed time: {elapsed_time:.2f} seconds")
        barad_logger.info(f"[MS{name_monitoring_str}] CPU usage: {cpu_usage:.2f}%")
        barad_logger.info(f"[MS{name_monitoring_str}] RAM usage: {ram_usage:.2f} MB")