import GPUtil
import psutil
import time

_last_net = None
_last_net_ts = None

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

def get_gpu_usage():
    """Returns GPU usage stats (load, memory, name) or 0 if no GPU found."""
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return {'name': 'None', 'load': 0, 'memory': 0}
        gpu = gpus[0]
        return {
            'name': gpu.name,
            'load': gpu.load * 100,  
            'memory': gpu.memoryUtil * 100  
        }
    except Exception:
        return {'name': 'None', 'load': 0, 'memory': 0}

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

def get_network_speed():
    """Returns upload/download speed in bytes per second."""
    global _last_net, _last_net_ts
    now = time.time()
    net = psutil.net_io_counters()

    if _last_net is None or _last_net_ts is None:
        _last_net = net
        _last_net_ts = now
        return {'upload_per_sec': 0.0, 'download_per_sec': 0.0}

    elapsed = max(now - _last_net_ts, 1e-6)
    upload_speed = max(0.0, (net.bytes_sent - _last_net.bytes_sent) / elapsed)
    download_speed = max(0.0, (net.bytes_recv - _last_net.bytes_recv) / elapsed)

    _last_net = net
    _last_net_ts = now

    return {
        'upload_per_sec': upload_speed,
        'download_per_sec': download_speed,
    }

def get_disk_io_stats():
    """Returns cumulative disk read/write bytes."""
    io = psutil.disk_io_counters()
    if io is None:
        return {'read_bytes': 0, 'write_bytes': 0}
    return {
        'read_bytes': io.read_bytes,
        'write_bytes': io.write_bytes,
    }

def get_per_core_cpu_usage():
    """Returns per-core CPU usage percentages."""
    return psutil.cpu_percent(interval=None, percpu=True)

def get_system_stats():
    """Returns all system stats in a dictionary."""
    return {
        'cpu': get_cpu_usage(),
        'cpu_per_core': get_per_core_cpu_usage(),
        'memory': get_memory_usage(),
        'disk': get_disk_usage(),
        'disk_io': get_disk_io_stats(),
        'network': get_network_usage(),
        'network_speed': get_network_speed(),
        'gpu': get_gpu_usage()
    }