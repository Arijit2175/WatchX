import psutil

def get_top_processes(by="cpu", limit=10):
    """Returns a list of top processes sorted by CPU or memory usage."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info
            if by == "cpu" and info['cpu_percent'] is None:
                info['cpu_percent'] = proc.cpu_percent(interval=None)
            processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    key = 'cpu_percent' if by == "cpu" else 'memory_percent'
    processes = sorted(processes, key=lambda p: p.get(key, 0), reverse=True)
    return processes[:limit]

def get_cpu_usage():
    """Returns CPU usage percentage."""
    return psutil.cpu_percent(interval=None)

def get_memory_usage():
    """Returns memory usage stats (total, used, free, percent)."""
    mem = psutil.virtual_memory()
    return {
        'total': mem.total,
        'used': mem.used,
        'free': mem.available,
        'percent': mem.percent
    }

def get_disk_usage():
    """Returns disk usage stats for root (total, used, free, percent)."""
    disk = psutil.disk_usage('/')
    return {
        'total': disk.total,
        'used': disk.used,
        'free': disk.free,
        'percent': disk.percent
    }

def get_network_usage():
    """Returns network I/O stats (bytes sent/received)."""
    net = psutil.net_io_counters()
    return {
        'bytes_sent': net.bytes_sent,
        'bytes_recv': net.bytes_recv
    }

def get_system_stats():
    """Returns all system stats in a dictionary."""
    return {
        'cpu': get_cpu_usage(),
        'memory': get_memory_usage(),
        'disk': get_disk_usage(),
        'network': get_network_usage()
    }