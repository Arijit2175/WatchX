import psutil

def get_cpu_usage():
    """Returns CPU usage percentage."""
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    """Returns memory usage stats (total, used, free, percent)."""
    mem = psutil.virtual_memory()
    return {
        'total': mem.total,
        'used': mem.used,
        'free': mem.available,
        'percent': mem.percent
    }

