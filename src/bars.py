from rich.text import Text

def static_bar(percentage, color):
    bar_length = 20
    filled_length = int(bar_length * percentage // 100)
    bar = ("█ " * filled_length) + ("  " * (bar_length - filled_length))
    bar = bar.rstrip()
    return Text.from_markup(f"[{color}]{bar}[/{color}] {percentage:.1f}%")