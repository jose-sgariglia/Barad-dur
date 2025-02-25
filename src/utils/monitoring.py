import os
import time
import json
import redis
import psutil
import logging
from contextlib import contextmanager 

barad_logger = logging.getLogger("barad_logger")

class Monitoring:
    """
    Monitoring class for system monitoring.
    Analyze latency, throughput, CPU and RAM usage.
    """

    def __init__(self, pid=None, host="localhost", port=6379, db=1, database_name="monitoring"):
        self.pid = pid if pid is not None else os.getpid()
        self.process = psutil.Process(self.pid)
        self.process.cpu_percent(None)
        self.num_cores = psutil.cpu_count(logical=True)
        self.dataset_name = database_name
        self.logging_db = redis.StrictRedis(host=host, port=port, db=db)

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
    
    def save_to_db(self, code_area, elapsed_time, cpu_usage, ram_usage):
        """
        Save a monitoring status to the database.
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        data = {
            "timestamp": timestamp,
            "elapsed_time": elapsed_time,
            "cpu_usage": cpu_usage,
            "ram_usage": ram_usage,
            "code_area": code_area
        }
        self.logging_db.rpush(self.dataset_name, json.dumps(data))
        barad_logger.debug(f"Saved record to list '{self.dataset_name}': {data}")



    
# -----------------------------------------------------------

def monitor_decorator(code_area:str="", interval:float=None):
    """
    Decorator to monitor the CPU and RAM usage of a function.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            code_area_ = f"-{code_area}" if isinstance(code_area, str) else ""

            monitor = Monitoring()
            monitor.get_cpu_usage(interval=interval)
            start_time = time.time()
            
            result = func(*args, **kwargs)
            
            elapsed_time = time.time() - start_time
            cpu_usage = monitor.get_cpu_usage(interval=interval)
            ram_usage = monitor.get_ram_usage()
            
            barad_logger.info(f"[MS{code_area_}] Elapsed time: {elapsed_time:.2f} seconds")
            barad_logger.info(f"[MS{code_area_}] CPU usage: {cpu_usage:.2f}%")
            barad_logger.info(f"[MS{code_area_}] RAM usage: {ram_usage:.2f} MB")

            monitor.save_to_db(code_area, elapsed_time, cpu_usage, ram_usage)
            
            return result
        return wrapper
    return decorator



@contextmanager
def monitor_context(code_area="", interval=None):
    """
    Context manager to monitor the CPU and RAM usage of a block of code.
    """

    code_area_ = f"-{code_area}" if isinstance(code_area, str) else ""

    monitor = Monitoring()
    monitor.get_cpu_usage(interval=interval)
    start_time = time.time()
    
    try:
        yield monitor
    finally:
        elapsed_time = time.time() - start_time
        cpu_usage = monitor.get_cpu_usage(interval=interval)
        ram_usage = monitor.get_ram_usage()
        
        barad_logger.info(f"[MS{code_area_}] Elapsed time: {elapsed_time:.2f} seconds")
        barad_logger.info(f"[MS{code_area_}] CPU usage: {cpu_usage:.2f}%")
        barad_logger.info(f"[MS{code_area_}] RAM usage: {ram_usage:.2f} MB")

        monitor.save_to_db(code_area, elapsed_time, cpu_usage, ram_usage)