from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Vertical
from src.stats import get_system_stats, get_top_processes
from src.bars import static_bar
from rich.text import Text
import asyncio

class SystemStats(Static):
    def on_mount(self):
        self.set_interval(0.3, self.refresh_stats)
        self.refresh_stats()

    def refresh_stats(self):
        stats = get_system_stats()
        cpu = static_bar(stats['cpu'], "green")
        mem = static_bar(stats['memory']['percent'], "yellow")
        disk = static_bar(stats['disk']['percent'], "magenta")
        net = stats['network']
        gpu = stats.get('gpu', {'name': 'None', 'load': 0, 'memory': 0})
        gpu_color = "green" if gpu['load'] < 50 else ("yellow" if gpu['load'] < 80 else "red")
        gpu_bar = static_bar(gpu['load'], gpu_color)
        gpu_text = Text(f"GPU  {gpu['name']}\n", style="bold cyan") + gpu_bar + Text(f"  Mem: {gpu['memory']:.1f}%", style="bold magenta")
        net_text = Text(f"Net: Sent {net['bytes_sent'] // (1024**2)} MB | Recv {net['bytes_recv'] // (1024**2)} MB", style="bold blue")
        self.update(
            Text("CPU  ", style="bold cyan") + cpu + Text("\n") +
            Text("MEM  ", style="bold cyan") + mem + Text("\n") +
            Text("DISK ", style="bold cyan") + disk + Text("\n") +
            gpu_text + Text("\n") +
            net_text
        )

class ProcessTable(DataTable):
    def on_mount(self):
        self.cursor_type = "row"
        self.add_columns("PID", "Name", "CPU %", "Mem %")
        self.set_interval(1, self.refresh_table)
        self.refresh_table()

    def refresh_table(self):
        selected_row = self.cursor_row if hasattr(self, 'cursor_row') else 0
        self.clear()
        procs = get_top_processes(by="cpu", limit=10)
        for proc in procs:
            self.add_row(
                str(proc.get('pid', '')),
                str(proc.get('name', '')),
                f"{proc.get('cpu_percent', 0):.1f}",
                f"{proc.get('memory_percent', 0):.1f}"
            )
        if self.row_count:
            self.cursor_coordinate = (min(selected_row, self.row_count - 1), 0)

class WatchXApp(App):
    TITLE = "WatchX"
    CSS_PATH = None
    BINDINGS = [ ("q", "quit", "Quit"), ("r", "refresh", "Refresh Now") ]
    def action_refresh(self):
        self.query_one(SystemStats).refresh_stats()
        self.query_one(ProcessTable).refresh_table()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield SystemStats()
        yield ProcessTable(id="proc_table")
        yield Footer()

    def on_mount(self):
        self.set_focus(self.query_one("#proc_table"))

if __name__ == "__main__":
    WatchXApp().run()