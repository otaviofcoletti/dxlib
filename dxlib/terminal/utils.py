"""
pip install oracledb
pip install rich
"""
import oracledb

from rich.console import Console
from rich.json import JSON


class DatabaseManager:
    connection = None

    def connect(self, username, password,
                host="orclgrad1.icmc.usp.br", service_name="pdb_elaine.icmc.usp.br"):
        if not self.connection:
            params = oracledb.ConnectParams(
                host=host, port=1521, service_name=service_name)
            self.connection = oracledb.connect(
                user=username, password=password, params=params)

    def create(self, command, cursor=None):
        if not self.connection:
            raise ConnectionError("Connect to DB!")
        with cursor if cursor else self.connection.cursor() as cursor:
            cursor.execute(command.value)

    def get(self, command, cursor=None):
        if not self.connection:
            raise ConnectionError("Connect to DB!")
        with cursor if cursor else self.connection.cursor() as cursor:
            return list(cursor.execute(command.value))

    def create_schema(self):
        with open("sql/create_schema.sql") as file:
            sql = file.read()

        create = sql.split(";")
        print(create)
        print(self.connection)


class Terminal:
    def __init__(self):
        self.console = Console()

    def print(self, *args, **kwargs):
        self.console.print(*args, **kwargs)

    def wait(self, msg, func, *args, **kwargs):
        with self.console.status(msg):
            func(*args, **kwargs)

    def log(self, msg=None, json=None):
        if msg:
            self.console.log(msg)
        else:
            self.console.log(JSON(json))

    def get_input(self, prompt):
        return self.console.input(prompt)

    def header(self, title, color="red"):
        self.console.rule(f"[bold {color}]{title}")

    def clear(self):
        self.console.clear()


class Menu:
    def __init__(self, name, identifier, paths: list = None, calls: list[dict] = None,
                 text="Selecione uma opção para continuar:"):
        self.name = name
        self.identifier = identifier
        self.paths = [] if not paths else paths
        self.calls = [] if not calls else calls
        self.text = text

    def select(self, index):
        if index < 0:
            raise IndexError("Invalid option")
        else:
            return self.paths[index]

    def call(self, index, *args, **kwargs):
        if index >= len(self.calls):
            raise IndexError("Invalid option")
        else:
            return self.calls[index]["method"](*args, **kwargs)


class Navigation:
    terminal = None

    def __init__(self, starting_menu: Menu, terminal: Terminal):
        self.current_menu = starting_menu
        self.previous_menus = []
        self.terminal = terminal

    def display(self, output=None):
        self.terminal.clear()
        self.terminal.header(f"Menu: { self.current_menu.name}\n")

        if self.previous_menus:
            self.terminal.print(f"0 - Retornar ao Menu anterior. \n")

        for idx, path in enumerate(self.current_menu.paths):
            self.terminal.print(f"{idx + 1} - {path.identifier}")

        for idx, call in enumerate(self.current_menu.calls):
            self.terminal.print(f"{len(self.current_menu.paths) + idx + 1} - {call['name']}")

        self.terminal.print(f"{len(self.current_menu.paths) + len(self.current_menu.calls) + 1} - Sair \n")

        if output:
            self.terminal.log(json=output)

    def listen(self):
        while True:
            option = int(self.terminal.get_input(self.current_menu.text + "\n"))

            if option == (len(self.current_menu.paths) + len(self.current_menu.calls)) + 1:
                raise SystemExit

            if option == 0 and self.previous_menus:
                self.current_menu = self.previous_menus.pop()
                break

            option -= 1

            try:
                if option < len(self.current_menu.paths):
                    selected_menu = self.current_menu.select(option)
                    self.enter_menu(selected_menu)
                    break

                else:
                    try:
                        call = self.current_menu.calls[option - len(self.current_menu.paths)]
                        args = call.get("args", None)

                        if args:
                            args = self.terminal.get_input(f"Insira os argumentos: {args}\n")
                            output = self.current_menu.call(option - len(self.current_menu.paths), args.split(" "))
                        else:
                            output = self.current_menu.call(option - len(self.current_menu.paths))
                        return output
                    except ValueError as params:
                        self.terminal.print(f"Para a opção {option}, use os parâmetros no formato correto: {params}")

            except IndexError:
                self.terminal.print("Opção inválida, por favor insira um número entre 0 e {}".format(
                    len(self.current_menu.paths) + len(self.current_menu.calls) + 1
                ))

    def enter_menu(self, menu):
        self.previous_menus.append(self.current_menu)
        self.current_menu = menu
