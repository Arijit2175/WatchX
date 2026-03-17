from src.stats import get_system_stats
from src.bars import static_bar
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
import time

def build_dashboard():
    stats = get_system_stats()
    cpu_bar = static_bar(stats['cpu'], "green")
    cpu_panel = Panel(
        Text("CPU Usage\n", style="bold cyan") + cpu_bar,
        title="[bold cyan]CPU Usage",
        border_style="green"
    )
    mem = stats['memory']
    mem_bar = static_bar(mem['percent'], "yellow")
    mem_text = Text(
        f"Used: {mem['used'] / (1024**3):.2f} GB / {mem['total'] / (1024**3):.2f} GB\n"
        f"Free: {mem['free'] / (1024**3):.2f} GB",
        style="bold yellow"
    )
    mem_panel = Panel(
        Text("Memory\n", style="bold cyan") + mem_bar + Text("\n") + mem_text,
        title="[bold cyan]Memory",
        border_style="yellow"
    )
    disk = stats['disk']
    disk_bar = static_bar(disk['percent'], "magenta")
    disk_text = Text(
        f"Used: {disk['used'] / (1024**3):.2f} GB / {disk['total'] / (1024**3):.2f} GB\n"
        f"Free: {disk['free'] / (1024**3):.2f} GB",
        style="bold magenta"
    )
    disk_panel = Panel(
        Text("Disk\n", style="bold cyan") + disk_bar + Text("\n") + disk_text,
        title="[bold cyan]Disk",
        border_style="magenta"
    )
    net = stats['network']
    net_text = Text(
        f"Sent: {net['bytes_sent'] / (1024**2):.2f} MB\n"
        f"Received: {net['bytes_recv'] / (1024**2):.2f} MB",
        style="bold blue"
    )
    net_panel = Panel(net_text, title="[bold cyan]Network", border_style="blue")
    layout = Layout()
    layout.split_column(
        Layout(name="upper", ratio=2),
        Layout(name="lower", ratio=1)
    )
    layout["upper"].split_row(
        Layout(cpu_panel, name="cpu"),
        Layout(mem_panel, name="mem"),
        Layout(disk_panel, name="disk")
    )
    layout["lower"].update(net_panel)
    return layout

def run_live_dashboard():
    console = Console()
    with Live(build_dashboard(), console=console, refresh_per_second=2, screen=True) as live:
        try:
            while True:
                live.update(build_dashboard())
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass