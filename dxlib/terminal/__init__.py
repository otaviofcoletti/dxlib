import time

from rich.console import Console
from rich.json import JSON
from rich.align import Align
from rich.text import Text
from rich.panel import Panel


class Terminal:
    def __init__(self):
        self.console = Console()

    def print(self, *args, **kwargs):
        self.console.print(*args, **kwargs)

    def wait(self, delay):
        with self.console.status("Loading..."):
            time.sleep(delay)

    def log(self, msg=None, json=None):
        if msg:
            self.console.log(msg)
        else:
            self.console.log(JSON(json))

    def get_input(self, prompt):
        return self.console.input(prompt)

    def separator(self, name):
        self.console.rule(f"[bold red]{name}")

    def test(self):
        with self.console.screen(style="bold white on red") as screen:
            for count in range(5, 0, -1):
                text = Align.center(
                    Text.from_markup(f"[blink]Don't Panic![/blink]\n{count}", justify="center"),
                    vertical="middle",
                )
                screen.update(Panel(text))
                time.sleep(1)
