import argparse
import random
import time
from typing import Optional

from rich.align import Align
from rich.columns import Columns
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from src.app import WatchXApp

try:
    from pyfiglet import Figlet
except ImportError:
    Figlet = None


console = Console()


WATCHX_ASCII_FALLBACK = r"""
██╗    ██╗ █████╗ ████████╗ ██████╗██╗  ██╗██╗  ██╗
██║    ██║██╔══██╗╚══██╔══╝██╔════╝██║  ██║╚██╗██╔╝
██║ █╗ ██║███████║   ██║   ██║     ███████║ ╚███╔╝
██║███╗██║██╔══██║   ██║   ██║     ██╔══██║ ██╔██╗
╚███╔███╔╝██║  ██║   ██║   ╚██████╗██║  ██║██╔╝ ██╗
 ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝
"""


def _render_watchx_ascii() -> str:
    if Figlet is not None:
        try:
            return Figlet(font="sub-zero", width=200).renderText("WATCHX")
        except Exception:
            pass
    return WATCHX_ASCII_FALLBACK


WATCHX_ASCII = _render_watchx_ascii()


def _glitch_title_to_digits(ascii_text: str) -> str:
    return "".join(
        random.choice("0123456789") if ch not in {" ", "\n"} else ch
        for ch in ascii_text
    )


def _blank_title_shape(ascii_text: str) -> str:
    return "".join(" " if ch != "\n" else "\n" for ch in ascii_text)


def _build_landing(title_mode: str = "normal", command_buffer: str = "", frame: int = 0):
    if title_mode == "blank":
        title_text = _blank_title_shape(WATCHX_ASCII)
    elif title_mode == "digits":
        title_text = _glitch_title_to_digits(WATCHX_ASCII)
    else:
        title_text = WATCHX_ASCII

    title = Text(title_text, style="bold cyan")
    subtitle = Text("Terminal Command Center", style="bold magenta")
    byline = Text("Live System Insights", style="bright_black")
    cursor = "▌" if frame % 2 == 0 else " "

    left = Panel(
        Group(
            Align.center(title),
            Align.center(subtitle),
            Align.center(byline),
        ),
        title="WatchX",
        border_style="cyan",
    )

    commands = Text.from_markup(
        "\n".join(
            [
                "[bold yellow]Commands[/bold yellow]",
                "[green]start[/green] / [green]run[/green]  Launch monitor",
                "[green]help[/green]               Command guide",
                "[green]about[/green]              Project info",
                "[green]clear[/green]              Redraw screen",
                "[green]quit[/green]               Exit launcher",
            ]
        )
    )
    prompt = Text(f"watchx> {command_buffer}{cursor}", style="bold cyan")

    right = Panel(
        Group(
            commands,
            Text("\n"),
            Text("\n"),
            Text("Input", style="bold magenta"),
            prompt,
        ),
        title="Console",
        border_style="bright_blue",
    )

    return Columns(
        [left, right],
        equal=False,
        expand=True,
    )


def _show_landing() -> None:
    console.print(_build_landing("normal", "", 0))


def _read_char_nonblocking() -> Optional[str]:
    try:
        import msvcrt

        if not msvcrt.kbhit():
            return None

        char = msvcrt.getwch()
        if char in {"\r", "\n"}:
            return "ENTER"
        if char == "\x08":
            return "BACKSPACE"
        if char in {"\x00", "\xe0"}:
            msvcrt.getwch()
            return None
        if char == "\x03":
            raise KeyboardInterrupt
        return char
    except ImportError:
        return None


def _animated_command_input(start_frame: int = 0, fps: int = 12) -> tuple[str, int]:
    sequence = (["normal"] * 8) + (["digits"] * 6) + (["blank"] * 3) + (["digits"] * 4) + (["normal"] * 7)
    frame = start_frame
    command_buffer = ""

    with Live(console=console, refresh_per_second=fps, screen=False) as live:
        while True:
            mode = sequence[frame % len(sequence)]
            live.update(_build_landing(mode, command_buffer, frame))
            frame += 1

            key = _read_char_nonblocking()
            if key is None:
                time.sleep(1 / fps)
                continue

            if key == "ENTER":
                return command_buffer.strip().lower(), frame

            if key == "BACKSPACE":
                command_buffer = command_buffer[:-1]
                continue

            if key.isprintable():
                command_buffer += key


def _show_help() -> None:
    help_text = Text.from_markup(
        "\n".join(
            [
                "[bold cyan]WatchX Commands[/bold cyan]",
                "[green]start[/green] / [green]run[/green]     Launch system monitor",
                "[green]help[/green]              Show this command guide",
                "[green]about[/green]             Show project info",
                "[green]clear[/green]             Clear terminal and redraw landing",
                "[green]quit[/green] / [green]exit[/green]     Exit WatchX launcher",
            ]
        )
    )
    console.print(Panel(help_text, title="Usage", border_style="cyan"))


def _show_about() -> None:
    about_text = Text.from_markup(
        "[bold]WatchX[/bold]\n"
        "Modern terminal system monitor with live metrics, process control, and multi-pane UI.\n"
        "Use this launcher as a command shell, similar to CLI assistants."
    )
    console.print(Panel(about_text, title="About", border_style="magenta"))


def _run_shell() -> None:
    frame = 0
    try:
        import msvcrt  # noqa: F401
        windows_nonblocking = True
    except ImportError:
        windows_nonblocking = False

    while True:
        if windows_nonblocking:
            try:
                command, frame = _animated_command_input(frame)
            except KeyboardInterrupt:
                console.print("\n[bold yellow]Exiting WatchX launcher. Bye![/bold yellow]")
                break
        else:
            if frame == 0:
                _show_landing()
            command = Prompt.ask("[bold cyan]watchx>[/bold cyan]").strip().lower()

        if command in {"start", "run", "monitor"}:
            console.print("[bold green]Launching WatchX monitor...[/bold green]")
            try:
                WatchXApp().run()
            except Exception as exc:
                console.print(f"[bold red]Monitor failed:[/bold red] {exc}")
            continue

        if command in {"help", "?"}:
            _show_help()
            continue

        if command == "about":
            _show_about()
            continue

        if command == "clear":
            console.clear()
            continue

        if command in {"quit", "exit"}:
            console.print("[bold yellow]Exiting WatchX launcher. Bye![/bold yellow]")
            break

        if not command:
            continue

        console.print(
            "[red]Unknown command.[/red] Try [bold]help[/bold] or type [bold]start[/bold] to launch monitor."
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="WatchX launcher")
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Launch monitor directly without launcher shell",
    )
    args = parser.parse_args()

    if args.direct:
        WatchXApp().run()
    else:
        _run_shell()


if __name__ == "__main__":
    main()