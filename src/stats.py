import psutil

def get_cpu_usage():
    """Returns CPU usage percentage."""
    return psutil.cpu_percent(interval=1)

