import psutil

def monitor_resources(interval=1):
    cpu_usage = psutil.cpu_percent(interval=interval)
    memory_usage = psutil.virtual_memory().percent
    return cpu_usage, memory_usage
