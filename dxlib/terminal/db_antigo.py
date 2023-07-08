"""
pip install oracledb
pip install rich
"""
from enum import Enum

import oracledb

import getpass

from rich.console import Console
from rich.json import JSON


class Commands:
    class GET(Enum):
        TABLE_NAMES = """SELECT table_name FROM user_tables"""
        STUDENTS = """select * from ALUNOS"""

    class CREATE(Enum):
        STUDENTS = """CREATE TABLE ALUNOS (NUSP NUMBER(10) PRIMARY KEY)"""

class Navigation:
    AUTH = 1
    LEAVE = 9
    class PROFESSOR(Enum):
        MENU = 20
        CURSOS = 21
    
    class MONITOR(Enum):
        MENU = 30
        CURSOS = 31
        DISPONIVEIS = 33
    
    class ALUNO(Enum):
        MENU = 40
        CURSOS = 41
        DISPONIVEIS = 43
        CLASSIFICACAO = 44
        NIVEL = 45
        JORNADA = 46

    class MISSOES(Enum):
        CRIAR = 41
        PROFESSOR = 42
        MONITOR = 43
        ALUNO = 44
        DELETAR = 48

    class CURSO(Enum):
        MENU = 60
        SAIR = 61
        CADASTRAR = 62
        INSCREVER_MONITOR = 63
        INSCREVER_ALUNO = 64
        FORUM = 65
        DELETAR = 68
    



class DatabaseManager:
    connection = None

    def connect(self, username, password,
                host="orclgrad1.icmc.usp.br", service_name="pdb_elaine.icmc.usp.br"):
        if not self.connection:
            params = oracledb.ConnectParams(
                host=host, port=1521, service_name=service_name)
            self.connection = oracledb.connect(
                user=username, password=password, params=params)

    def create(self, command: Commands.CREATE, cursor=None):
        if not self.connection:
            raise ConnectionError("Connect to DB!")
        with cursor if cursor else self.connection.cursor() as cursor:
            cursor.execute(command.value)

    def get(self, command: Commands.GET, cursor=None):
        if not self.connection:
            raise ConnectionError("Connect to DB!")
        with cursor if cursor else self.connection.cursor() as cursor:
            return list(cursor.execute(command.value))


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


class App:
    db = None
    terminal = None
    running = False
    menu = 1

    def login(self):
        self.db = DatabaseManager()
        self.terminal = Terminal()

        username = self.terminal.get_input("Qual o username?\n")
        password = getpass.getpass('Senha: ')

        self.terminal.wait(
            "Connectando...", self.db.connect, username, password)

        self.terminal.header("Bem vindo: " + username, color="blue")

    def manage_menus(self):
        Nav = Navigation()

        if self.menu == Nav.AUTH:
            self.CPF = self.terminal.get_input("Identifique-se pelo CPF:")
            tipo = self.db.connection.cursor().execute(f"SELECT TIPO FROM PESSOA WHERE CPF = {self.CPF};")
            tipo = str(tipo)
            self.terminal.print(tipo)
            self.menu = Nav.PROFESSOR.MENU if tipo == "PROFESSOR" else 0
            self.menu = Nav.MONITOR.MENU if tipo == "MONITOR" else 0
            self.menu = Nav.ALUNO.MENU if tipo == "ALUNO" else 0
            # else self.terminal.print("CPF não encontrado")
            if self.menu == 0:
                raise Exception("Tipo de pessoa inconsistente")
            return 
        
        #Professor
        elif self.menu == Nav.PROFESSOR.MENU:
            self.terminal.print("""
                    1 - Seus Cursos
                    2 - Cadastrar novo curso
                    3 - Fechar
                    """)
            command = self.terminal.get_input("Escolha uma das opções...\n")
            if int(command) == 1:
                self.menu == Nav.PROFESSOR.CURSOS
            elif int(command) == 2:
                self.menu = Nav.CURSO.CADASTRAR
            elif int(command) == 3:
                self.menu = Nav.LEAVE
            return

        elif self.menu == Nav.PROFESSOR.CURSOS:
            #self.terminal.log(self.db.get(Commands.GET.CURSOS(PROF = CPF))) Select curso.* where professor = CPF
            self.terminal.print("""
                    1 - Finalizar curso
                    2 - Ver missões
                    3 - Ver fórum
                    4 - Voltar
                    5 - Fechar
                    """)
            command = self.terminal.get_input("Escolha uma das opções...\n")
            if int(command) == 1:
                self.menu == Nav.CURSO.DELETAR
            elif int(command) == 2:
                self.menu = Nav.MISSOES.PROFESSOR
            elif int(command) == 3:
                self.menu = Nav.CURSO.FORUM
            elif int(command) == 4:
                self.menu = Nav.PROFESSOR.MENU
            elif int(command) == 5:
                self.menu = Nav.LEAVE
            return

        elif self.menu == Nav.MISSOES.PROFESSOR:
            curso_selecionado = self.terminal.get_input("Digite o nome do curso escolhido\n")
            #self.terminal.log(self.db.get(Commands.GET.MISSOES(NOME = curso))) Select curso.* where professor = CPF
            self.terminal.print("""
                    1 - Criar Missão
                    2 - Excluir Missão
                    3 - Voltar
                    4 - Fechar
                    """)
            command = self.terminal.get_input("Escolha uma das opções...\n")
            if int(command) == 1:
                self.menu == Nav.MISSOES.CRIAR
            elif int(command) == 2:
                self.menu = Nav.MISSOES.DELETAR
            elif int(command) == 4:
                self.menu = Nav.PROFESSOR.CURSOS
            elif int(command) == 5:
                self.menu = Nav.LEAVE
            return

        #Funções
        elif self.menu == Nav.CURSO.CADASTRAR:
            nome = self.terminal.get_input("nome descr limite prof  nome_forum\n")
            descr = self.terminal.get_input("nome descr limite prof nome_forum\n")
            limite = int(self.terminal.get_input("nome descr limite prof nome_forum\n"))
            nome_forum = self.terminal.get_input("nome descr limite prof nome_forum\n")
            values = f"(${nome}, ${nome}, ${nome}, ${nome}, ${nome}, )" #TTEEEEEEEEEEEERRRRRRRRRRMMMMMMMMMIIIIIINNNNNNAAAAAAAARRRRRRRRR

        #Monitores
        elif self.menu == Nav.MONITOR.MENU:
            self.terminal.print("""
                    1 - Seus Cursos
                    2 - Inscrever
                    3 - Fechar
                    """)
            command = self.terminal.get_input("Escolha uma das opções...\n")
            if int(command) == 1:
                self.menu == Nav.MONITOR.CURSOS
            elif int(command) == 2:
                self.menu = Nav.MONITOR.DISPONIVEIS
            elif int(command) == 3:
                self.menu = Nav.LEAVE
            return 

        elif self.menu == Nav.MONITOR.CURSOS:
            #self.terminal.log(self.db.get(Commands.GET.CURSOS(PROF = CPF))) Select curso.* where professor = CPF
            self.terminal.print("""
                    1 - Sair de curso
                    2 - Ver missões
                    3 - Ver fórum
                    4 - Voltar 
                    5 - Fechar
                    """)
            command = self.terminal.get_input("Escolha uma das opções...\n")
            if int(command) == 1:
                self.menu == Nav.CURSO.SAIR
            elif int(command) == 2:
                self.menu = Nav.MISSOES.MONITOR
            elif int(command) == 3:
                self.menu = Nav.CURSO.FORUM
            elif int(command) == 4:
                self.menu = Nav.MONITOR.MENU
            elif int(command) == 5:
                self.menu = Nav.LEAVE
            return

        elif self.menu == Nav.MONITOR.DISPONIVEIS:
            #self.terminal.log(self.db.get(Commands.GET.CURSOS(total_monitores < 2 AND Monitor != CPF))) Select curso.* where professor = CPF
            self.terminal.print("""
                    1 - Entrar em Curso
                    2 - Voltar 
                    3 - Fechar
                    """)
            command = self.terminal.get_input("Escolha uma das opções...\n")
            if int(command) == 1:
                self.menu == Nav.CURSO.INSCREVER_MONITOR
            elif int(command) == 2:
                self.menu = Nav.MONITOR.MENU
            elif int(command) == 3:
                self.menu = Nav.LEAVE
            return


        #Aluno
        elif self.menu == Nav.ALUNO.MENU:
            #self.terminal.log(self.db.get(Commands.GET.Alunos(cpf = CPF))) Select alunos.* where cpf = CPF
            self.terminal.print("""
                    1 - Seus Cursos
                    2 - Inscrever
                    3 - Fechar
                    """)
            command = self.terminal.get_input("Escolha uma das opções...\n")
            if int(command) == 1:
                self.menu == Nav.ALUNO.CURSOS
            elif int(command) == 2:
                self.menu = Nav.ALUNO.DISPONIVEIS
            elif int(command) == 3:
                self.menu = Nav.LEAVE
            else:
                self.terminal.print("Opção inválida")
            return 

        elif self.menu == Nav.ALUNO.CURSOS:
            #self.terminal.log(self.db.get(Commands.GET.CURSOS(Aluno = CPF))) Select curso.* where aluno = CPF
            self.terminal.print("""
                    1 - Sair do curso
                    2 - Ver Missões
                    3 - Classificação
                    4 - Jornada
                    5 - Voltar 
                    6 - Fechar
                    """)
            command = self.terminal.get_input("Escolha uma das opções...\n")
            if int(command) == 1:
                self.menu == Nav.CURSO.SAIR
            elif int(command) == 2:
                self.menu = Nav.MISSOES.ALUNO
            elif int(command) == 3:
                self.menu = Nav.ALUNO.CLASSIFICACAO
            elif int(command) == 4:
                self.menu = Nav.ALUNO.JORNADA
            elif int(command) == 5:
                self.menu = Nav.ALUNO.MENU
            elif int(command) == 6:
                self.menu = Nav.LEAVE
            else:
                self.terminal.print("Opção inválida")
            return 

        elif self.menu == Nav.ALUNO.CLASSIFICACAO:
            curso = self.terminal.get_input("Digite o nome do curso que quer a classificação\n")
            #self.terminal.log(self.db.get(Commands.GET.Ranking(Aluno = CPF))) Select ranking from ranking where curso = curso
            #mostrar bonitinho a classificacao
            self.terminal.print("""
                    1 - Voltar 
                    2 - Fechar
                    """)
            command = self.terminal.get_input("Escolha uma das opções...\n")
            if int(command) == 1:
                self.menu = Nav.ALUNO.CURSOS
            elif int(command) == 2:
                self.menu = Nav.LEAVE
            else:
                self.terminal.print("Opção inválida")
            return 
        
        elif self.menu == Nav.ALUNO.JORNADA:
            curso = self.terminal.get_input("Digite o nome do curso que quer a Jornada\n")
            #self.terminal.log(self.db.get(Commands.GET.Jornada(Aluno = CPF AND Curso = curso))) Select Jornada.nível from Jornada where curso = curso
            #mostrar bonitinho a jornada preenchida até o menos nível-1 e vazia do nível pra cima
            self.terminal.print("""
                    1 - Voltar 
                    2 - Fechar
                    """)
            command = self.terminal.get_input("Escolha uma das opções...\n")
            if int(command) == 1:
                self.menu = Nav.ALUNO.CURSOS
            elif int(command) == 2:
                self.menu = Nav.LEAVE
            else:
                self.terminal.print("Opção inválida")
            return 

        elif self.menu == Nav.MISSOES.ALUNO:
            curso = self.terminal.get_input("Digite o nome do curso que quer as Missões\n")
            #self.terminal.log(self.db.get(Commands.GET.Missoes(Curso = curso))) Select Missions from Missoes where curso = curso
            #mostrar bonitinho a jornada
            self.terminal.print("""
                    1 - Voltar 
                    2 - Fechar
                    """)
            command = self.terminal.get_input("Escolha uma das opções...\n")
            if int(command) == 1:
                self.menu = Nav.ALUNO.CURSOS
            elif int(command) == 2:
                self.menu = Nav.LEAVE
            else:
                self.terminal.print("Opção inválida")
            return 

        elif self.menu == Nav.ALUNO.DISPONIVEIS:
            #self.terminal.log(self.db.get(Commands.GET.CURSOS(total_ALUNO < limite AND CPF not in curso como aluno))) Select curso.* where professor = CPF
            self.terminal.print("""
                    1 - Entrar em Curso
                    2 - Voltar 
                    3 - Fechar
                    """)
            command = self.terminal.get_input("Escolha uma das opções...\n")
            if int(command) == 1:
                self.menu == Nav.CURSO.INSCREVER_ALUNO
            elif int(command) == 2:
                self.menu = Nav.ALUNO.MENU
            elif int(command) == 3:
                self.menu = Nav.LEAVE
            else:
                self.terminal.print("Opção inválida")
            return

        elif self.menu == Nav.CURSO.INSCREVER_ALUNO:
            curso = self.terminal.get_input("Digite o nome do curso que quer as Missões\n")
            #insert 
            self.terminal.print("""
                    1 - Voltar 
                    2 - Fechar
                    """)
            command = self.terminal.get_input("Escolha uma das opções...\n")
            if int(command) == 1:
                self.menu = Nav.ALUNO.MENU
            elif int(command) == 2:
                self.menu = Nav.LEAVE
            else:
                self.terminal.print("Opção inválida")
            return


    def interactive(self, running=True):
        self.running = running

        while self.running:
            while True:
                
                
                    self.manage_menus()
                
                    self.terminal.print("500, Internal Server Error")

    def __init__(self):
        self.login()
        self.interactive()


if __name__ == "__main__":
    App()
