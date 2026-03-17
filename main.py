from src.stats import get_system_stats

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.table import Table

def main():
    stats = get_system_stats()
    console = Console()

    cpu_panel = Panel(
        Text(f"{stats['cpu']}%", style="bold green"),
        title="[bold cyan]CPU Usage",
        border_style="green"
    )

    mem = stats['memory']
    mem_text = Text(
        f"Used: {mem['used'] / (1024**3):.2f} GB\n"
        f"Total: {mem['total'] / (1024**3):.2f} GB\n"
        f"Free: {mem['free'] / (1024**3):.2f} GB\n"
        f"Percent: {mem['percent']}%",
        style="bold yellow"
    )
    mem_panel = Panel(mem_text, title="[bold cyan]Memory", border_style="yellow")

    disk = stats['disk']
    disk_text = Text(
        f"Used: {disk['used'] / (1024**3):.2f} GB\n"
        f"Total: {disk['total'] / (1024**3):.2f} GB\n"
        f"Free: {disk['free'] / (1024**3):.2f} GB\n"
        f"Percent: {disk['percent']}%",
        style="bold magenta"
    )
    disk_panel = Panel(disk_text, title="[bold cyan]Disk", border_style="magenta")

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

    console.print(layout)

if __name__ == "__main__":
    main()