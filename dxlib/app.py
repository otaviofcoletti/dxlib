import getpass

import time

from db.utils import DatabaseManager, Menu, Navigation
from db.sql.queries import GET_USERS, GET_MISSIONS, GET_TABLES
from db.sql.create import CREATE_COURSE

from terminal import Terminal


class App:
    db = None
    terminal = None
    nav = None
    running = False

    def login(self):
        self.db = DatabaseManager()
        self.terminal = Terminal()

        username = self.terminal.get_input("Qual o username?\n")
        password = getpass.getpass('Senha: ')

        self.terminal.wait(
            "Connectando...", self.db.connect, username, password)

        self.terminal.clear()
        self.terminal.header("Bem vindo: " + username, color="blue")

        if self.db.get(GET_TABLES()) is None:
            self.db.create_schema()

        time.sleep(1.4)

    def exit(self):
        self.running = False

    def interactive(self, running=True):
        self.running = running

        self.nav = Navigation(
            starting_menu=self.menu_home(),
            terminal=self.terminal
        )

        while self.running:
            self.nav.display()
            try:
                self.nav.listen()
            except SystemExit:
                self.terminal.print("Txau txau...")
                self.exit()

    def __init__(self):
        self.login()
        self.interactive()


if __name__ == "__main__":
    App()
