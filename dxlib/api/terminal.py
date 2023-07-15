from rich.console import Console


class Terminal:
    def __init__(self):
        self.console = Console()

    def print(self, message):
        self.console.print(message)

    def input(self, message):
        return self.console.input(message)

    def clear(self):
        self.console.clear()
