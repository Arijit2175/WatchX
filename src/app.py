from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static, Input
from textual.binding import Binding
from src.stats import get_system_stats
from src.bars import static_bar
from rich.text import Text
import asyncio
import psutil
from collections import deque

class SystemStats(Static):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cpu_history = deque(maxlen=24)
        self.net_history = deque(maxlen=24)

    def _sparkline(self, values):
        if not values:
            return "-"
        bars = "▁▂▃▄▅▆▇█"
        top = max(values)
        if top <= 0:
            return bars[0] * len(values)
        return "".join(bars[min(7, int((value / top) * 7))] for value in values)

    async def on_mount(self):
        self.set_interval(2.0, self.refresh_stats)
        await self.refresh_stats()

    async def refresh_stats(self):
        stats = await asyncio.to_thread(get_system_stats)

        def _fmt_rate(value):
            units = ["B/s", "KB/s", "MB/s", "GB/s"]
            unit_index = 0
            while value >= 1024 and unit_index < len(units) - 1:
                value /= 1024
                unit_index += 1
            return f"{value:.1f} {units[unit_index]}"

        def _fmt_bytes(value):
            units = ["B", "KB", "MB", "GB", "TB"]
            unit_index = 0
            while value >= 1024 and unit_index < len(units) - 1:
                value /= 1024
                unit_index += 1
            return f"{value:.1f} {units[unit_index]}"

        cpu = static_bar(stats['cpu'], "green")
        mem = static_bar(stats['memory']['percent'], "yellow")
        disk = static_bar(stats['disk']['percent'], "magenta")
        net = stats['network']
        net_speed = stats.get('network_speed', {'upload_per_sec': 0.0, 'download_per_sec': 0.0})
        disk_io = stats.get('disk_io', {'read_bytes': 0, 'write_bytes': 0})
        cores = stats.get('cpu_per_core', [])
        gpu = stats.get('gpu', {'name': 'None', 'load': 0, 'memory': 0})

        self.cpu_history.append(float(stats['cpu']))
        net_total_speed = float(net_speed['upload_per_sec']) + float(net_speed['download_per_sec'])
        self.net_history.append(net_total_speed)

        gpu_color = "green" if gpu['load'] < 50 else ("yellow" if gpu['load'] < 80 else "red")
        gpu_bar = static_bar(gpu['load'], gpu_color)
        gpu_text = Text(f"GPU  {gpu['name']}\n", style="bold cyan") + gpu_bar + Text(f"  Mem: {gpu['memory']:.1f}%", style="bold magenta")

        core_chunks = []
        if cores:
            for i in range(0, len(cores), 8):
                chunk = " ".join([f"C{j}:{cores[j]:.0f}%" for j in range(i, min(i + 8, len(cores)))])
                core_chunks.append(chunk)
        core_text = Text("Core CPU:\n" + ("\n".join(core_chunks) if core_chunks else "N/A"), style="bold white")

        cpu_trend = Text(f"CPU Trend: {self._sparkline(list(self.cpu_history))}", style="bright_green")
        net_trend = Text(f"Net Trend: {self._sparkline(list(self.net_history))}", style="bright_blue")

        net_text = Text(
            f"Net: Sent {_fmt_bytes(net['bytes_sent'])} | Recv {_fmt_bytes(net['bytes_recv'])} "
            f"| Up {_fmt_rate(net_speed['upload_per_sec'])} | Down {_fmt_rate(net_speed['download_per_sec'])}",
            style="bold blue"
        )
        disk_io_text = Text(
            f"Disk I/O: Read {_fmt_bytes(disk_io['read_bytes'])} | Write {_fmt_bytes(disk_io['write_bytes'])}",
            style="bold bright_magenta"
        )
        self.update(
            Text("CPU  ", style="bold cyan") + cpu + Text("\n") +
            cpu_trend + Text("\n") +
            core_text + Text("\n") +
            Text("MEM  ", style="bold cyan") + mem + Text("\n") +
            Text("DISK ", style="bold cyan") + disk + Text("\n") +
            disk_io_text + Text("\n") +
            gpu_text + Text("\n") +
            net_text + Text("\n") +
            net_trend
        )

class ProcessTable(DataTable):
    min_page_size = 10
    max_page_size = 100
    page_size = 25
    current_page = 0
    total_count = 0
    total_pages = 1
    sort_by = "cpu"
    sort_desc = True
    current_query = ""
    selected_pid = None
    follow_selected_pid = False

    async def on_click(self, event):
        style_meta = getattr(event.style, 'meta', {}) if hasattr(event.style, 'meta') else {}
        row = style_meta.get('row') if isinstance(style_meta, dict) else None
        if row is not None and 0 <= row < self.row_count:
            self.cursor_coordinate = (row, 0)
            self.selected_pid = str(self.get_row_at(row)[0])
            self.follow_selected_pid = True
            self._refresh_timer.pause()

    def _select_pid_if_present(self, pid):
        for row_index in range(self.row_count):
            if str(self.get_row_at(row_index)[0]) == str(pid):
                self.cursor_coordinate = (row_index, 0)
                self.selected_pid = str(pid)
                return True
        return False
            
    async def on_mount(self):
        self.cursor_type = "row"
        self.add_columns("PID", "Name", "CPU %", "Mem %")
        self._refresh_timer = self.set_interval(3, self.refresh_table)
        await self.refresh_table()

    def _collect_processes(self, query: str):
        results = []
        query = query.lower()
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                name = info.get('name') or ''
                if query and query not in str(info.get('pid', '')) and query not in name.lower():
                    continue
                results.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if self.sort_by == "cpu":
            key_fn = lambda p: p.get('cpu_percent', 0) or 0
        elif self.sort_by == "memory":
            key_fn = lambda p: p.get('memory_percent', 0) or 0
        elif self.sort_by == "name":
            key_fn = lambda p: (p.get('name') or '').lower()
        else:
            key_fn = lambda p: int(p.get('pid') or 0)

        return sorted(results, key=key_fn, reverse=self.sort_desc)

    def get_status_text(self):
        sort_label = {
            "cpu": "CPU%",
            "memory": "Mem%",
            "name": "Name",
            "pid": "PID",
        }.get(self.sort_by, self.sort_by)
        direction = "Desc" if self.sort_desc else "Asc"
        query_label = self.current_query if self.current_query else "None"
        return (
            f"Rows/Page: {self.page_size} | Page {self.current_page + 1}/{self.total_pages} "
            f"| Total {self.total_count} | Sort {sort_label} {direction} | Filter {query_label}"
        )

    async def refresh_table(self, search_query: str | None = None):
        if search_query is not None:
            self.current_query = search_query

        selected_pid = self.selected_pid
        selected_row = self.cursor_row if hasattr(self, 'cursor_row') else 0
        if not self.follow_selected_pid and self.row_count and 0 <= selected_row < self.row_count:
            selected_pid = str(self.get_row_at(selected_row)[0])
            self.selected_pid = selected_pid

        all_procs = await asyncio.to_thread(self._collect_processes, self.current_query)
        self.total_count = len(all_procs)
        self.total_pages = max(1, (self.total_count + self.page_size - 1) // self.page_size)
        self.current_page = min(max(0, self.current_page), self.total_pages - 1)
        start = self.current_page * self.page_size
        end = start + self.page_size
        procs = all_procs[start:end]

        self.clear()
        for proc in procs:
            self.add_row(
                str(proc.get('pid', '')),
                str(proc.get('name', '')),
                f"{proc.get('cpu_percent', 0):.1f}",
                f"{proc.get('memory_percent', 0):.1f}"
            )
        if not self.row_count:
            self.selected_pid = None
            return

        if self.follow_selected_pid and selected_pid and self._select_pid_if_present(selected_pid):
            return

        fallback_row = min(selected_row, self.row_count - 1)
        self.cursor_coordinate = (fallback_row, 0)
        self.selected_pid = str(self.get_row_at(fallback_row)[0])

    async def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.follow_selected_pid = False
            await self.refresh_table()

    async def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.follow_selected_pid = False
            await self.refresh_table()

    async def set_sort(self, sort_by: str):
        if sort_by == self.sort_by:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_by = sort_by
            self.sort_desc = sort_by in {"cpu", "memory"}
        self.current_page = 0
        self.follow_selected_pid = False
        await self.refresh_table()

class WatchXApp(App):
    TITLE = "WatchX"
    CSS_PATH = None
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("k", "kill_process", "Kill"),
        Binding("s", "focus_search", "Search"),
        Binding("[", "prev_page", "Prev Page"),
        Binding("]", "next_page", "Next Page"),
        Binding("1", "sort_cpu", "CPU Sort"),
        Binding("2", "sort_memory", "Mem Sort"),
        Binding("3", "sort_name", "Name Sort"),
        Binding("4", "sort_pid", "PID Sort"),
        Binding("m", "command_palette", "Menu"),
        Binding("r", "refresh", "Refresh", show=False),
        Binding("escape", "clear_search", "Clear Search", show=False),
        Binding("=", "increase_page_size", "More Rows", show=False),
        Binding("-", "decrease_page_size", "Fewer Rows", show=False),
    ]

    async def action_kill_process(self):
        table = self.query_one(ProcessTable)
        pid_str = None
        row_idx = table.cursor_row if hasattr(table, 'cursor_row') else 0
        if table.row_count and 0 <= row_idx < table.row_count:
            pid_str = str(table.get_row_at(row_idx)[0])
            table.selected_pid = pid_str
        elif table.selected_pid:
            pid_str = table.selected_pid

        if not pid_str:
            self.set_footer_text("No process selected.")
            return

        try:
            pid = int(pid_str)
            proc = psutil.Process(pid)
            proc.terminate()
            self.set_footer_text(f"Sent terminate signal to PID {pid}")
        except Exception as e:
            self.set_footer_text(f"Failed to kill PID {pid_str}: {e}")

        # Reset selection state and refresh the table
        table.selected_pid = None
        table.follow_selected_pid = False
        query = self.query_one("#search", Input).value.strip()
        await table.refresh_table(search_query=query)
        if not query:
            table._refresh_timer.resume()
        self.set_status_text(table.get_status_text())

    def on_key(self, event):
        if event.key in {"up", "down", "pageup", "pagedown", "home", "end"}:
            focused = self.focused
            if isinstance(focused, ProcessTable):
                focused.follow_selected_pid = False
                focused._refresh_timer.resume()

    def set_footer_text(self, text):
        footer = self.query(Footer).first()
        if footer:
            footer.text = text

    def set_status_text(self, text):
        status_line = self.query_one("#status_line", Static)
        status_line.update(
            f"Rows: = More / - Fewer | Pages: [ Prev / ] Next | Sort: 1 CPU 2 Memory 3 Name 4 PID | {text}"
        )
            
    def action_focus_search(self):
        self.query_one("#search").focus()

    async def action_clear_search(self):
        search = self.query_one("#search", Input)
        search.value = ""
        table = self.query_one(ProcessTable)
        table.follow_selected_pid = False
        table.current_page = 0
        table._refresh_timer.resume()
        await table.refresh_table(search_query="")
        self.set_status_text(table.get_status_text())
        table.focus()

    async def on_input_changed(self, event: Input.Changed):
        if event.input.id == "search":
            query = event.value.strip()
            table = self.query_one(ProcessTable)
            table.current_page = 0
            if query:
                table._refresh_timer.pause()
            else:
                table._refresh_timer.resume()
            await table.refresh_table(search_query=query)
            self.set_status_text(table.get_status_text())

    async def action_refresh(self):
        await self.query_one(SystemStats).refresh_stats()
        query = self.query_one("#search", Input).value.strip()
        table = self.query_one(ProcessTable)
        await table.refresh_table(search_query=query)
        self.set_status_text(table.get_status_text())

    async def action_increase_page_size(self):
        table = self.query_one(ProcessTable)
        if table.page_size < table.max_page_size:
            table.page_size += 5
            await table.refresh_table()
            self.set_status_text(table.get_status_text())
        else:
            self.set_footer_text(f"Rows/Page already at max ({table.max_page_size})")

    async def action_decrease_page_size(self):
        table = self.query_one(ProcessTable)
        if table.page_size > table.min_page_size:
            table.page_size -= 5
            await table.refresh_table()
            self.set_status_text(table.get_status_text())
        else:
            self.set_footer_text(f"Rows/Page already at min ({table.min_page_size})")

    async def action_next_page(self):
        table = self.query_one(ProcessTable)
        await table.next_page()
        self.set_status_text(table.get_status_text())

    async def action_prev_page(self):
        table = self.query_one(ProcessTable)
        await table.prev_page()
        self.set_status_text(table.get_status_text())

    async def action_sort_cpu(self):
        table = self.query_one(ProcessTable)
        await table.set_sort("cpu")
        self.set_status_text(table.get_status_text())

    async def action_sort_memory(self):
        table = self.query_one(ProcessTable)
        await table.set_sort("memory")
        self.set_status_text(table.get_status_text())

    async def action_sort_name(self):
        table = self.query_one(ProcessTable)
        await table.set_sort("name")
        self.set_status_text(table.get_status_text())

    async def action_sort_pid(self):
        table = self.query_one(ProcessTable)
        await table.set_sort("pid")
        self.set_status_text(table.get_status_text())

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield SystemStats()
        yield Input(placeholder="Search by name or PID... (press s)", id="search")
        yield Static("", id="status_line")
        yield ProcessTable(id="proc_table")
        yield Footer()

    def on_mount(self):
        self.set_focus(self.query_one("#proc_table"))
        table = self.query_one(ProcessTable)
        self.set_status_text(table.get_status_text())

if __name__ == "__main__":
    WatchXApp().run()