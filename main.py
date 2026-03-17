from src.stats import get_system_stats
from rich.console import Console
from rich.table import Table

def main():
    stats = get_system_stats()
    console = Console()
    table = Table(title="System Stats", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    table.add_row("CPU Usage (%)", f"{stats['cpu']}")

    mem = stats['memory']
    table.add_row("Memory Used", f"{mem['used'] / (1024**3):.2f} GB / {mem['total'] / (1024**3):.2f} GB ({mem['percent']}%)")

    disk = stats['disk']
    table.add_row("Disk Used", f"{disk['used'] / (1024**3):.2f} GB / {disk['total'] / (1024**3):.2f} GB ({disk['percent']}%)")

    net = stats['network']
    table.add_row("Network Sent", f"{net['bytes_sent'] / (1024**2):.2f} MB")
    table.add_row("Network Received", f"{net['bytes_recv'] / (1024**2):.2f} MB")

    console.print(table)

if __name__ == "__main__":
    main()