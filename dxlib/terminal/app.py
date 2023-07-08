import getpass

import time

from utils import DatabaseManager, Terminal, Menu, Navigation
from sql.queries import GET_USERS, GET_MISSIONS, GET_TABLES
from sql.create import CREATE_COURSE


class AcessoAluno:
    @classmethod
    def menu_perfil(cls, CPF):
        home = Menu(name="Minha Pagina", identifier="Retornar ao Menu inicial",
                    paths=[
                        cls.menu_cursos(CPF),
                        cls.menu_missoes(CPF)
                    ])
        return home

    @classmethod
    def menu_cursos(cls, CPF):
        return Menu(name="Meus Cursos", identifier="Acessar cursos nos quais está matriculado")

    @classmethod
    def menu_missoes(cls, CPF):
        return Menu(name="Minhas Missoes", identifier="Missões nas quais está participando")


class AcessoProfessor:
    @classmethod
    def menu_perfil(cls, CPF):
        home = Menu(name="Minha Pagina", identifier="Retornar ao Menu inicial",
                    paths=[
                        cls.menu_cursos(CPF),
                    ],
                    calls=[
                        {"name": "Cadastrar novo curso", "method": cls.cadastrar_curso,
                         "args": "<NOME_CURSO>"}
                    ]
                    )
        return home

    @classmethod
    def menu_cursos(cls, CPF):
        return Menu(name="Meus Cursos", identifier="Acessar cursos que você ministra")

    @classmethod
    def cadastrar_curso(cls, NOME_CURSO):
        # App.db.create(CREATE_COURSE(NOME_CURSO))
        return f"Curso cadastrado com sucesso"


class AcessoAdmin:
    @classmethod
    def menu_perfil(cls, CPF):
        home = Menu(name="Minha Pagina", identifier="Retornar ao Menu inicial",
                    paths=[
                        cls.menu_cursos(CPF),
                        cls.menu_missoes(CPF)
                    ])
        return home

    @classmethod
    def menu_cursos(cls, CPF):
        return Menu(name="Meus Cursos", identifier="Acessar seus cursos")

    @classmethod
    def menu_missoes(cls, CPF):
        return Menu(name="Minhas Missoes", identifier="Acessar minhas missoes")


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

    def menu_home(self):
        home = Menu(name="Menu inicial", identifier="Retornar ao Menu inicial",
                    calls=[
                        {"name": "Acessar como professor", "method": self.acesso_professor, "args": "<CPF>"},
                        {"name": "Acessar como aluno", "method": self.acesso_aluno, "args": "<CPF>"},
                        {"name": "Acessar como administrador", "method": self.acesso_admin, "args": "<CPF>"}
                    ])
        return home

    def acesso_professor(self, CPF):
        # acessar banco e verificar se existe ?
        # self.db.get(GET_USERS())

        self.nav.enter_menu(AcessoProfessor.menu_perfil(CPF))

    def acesso_aluno(self, CPF):
        self.nav.enter_menu(AcessoAluno.menu_perfil(CPF))

    def acesso_admin(self, CPF):
        self.nav.enter_menu(AcessoAdmin.menu_perfil(CPF))

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
