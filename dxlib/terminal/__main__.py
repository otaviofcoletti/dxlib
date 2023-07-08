from . import Terminal

terminal = Terminal()

terminal.log('Starting application')
name = terminal.get_input("What is [i]your[/i] [bold red]name[/]? :smiley: ")
terminal.wait(1.2)
terminal.separator(f"Logged in as: [/][blue]{name}[/]")


terminal.print([1, 2, 3])
terminal.print("[blue underline]Looks like a link")
terminal.print("FOO", style="white on blue")

terminal.test()
