-- Professor 1
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('111.111.111-11', 'Ana Silva', TO_DATE('1980-01-15', 'YYYY-MM-DD'), 0, 'PROFESSOR');
INSERT INTO PROFESSOR (CPF, CARGO, RUA, NUMERO, CIDADE, ORGAO_EMISSOR, VALOR, AVALIACAO_DE_ALUNOS)
VALUES ('111.111.111-11', 'Professora de Segurança da Informação', 'Rua Alameda Santos', '123', 'Orgão Emissor da Informação', 'SSP-SP', 1000, 4.5);

-- Professor 2
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('222.222.222-22', 'Carlos Oliveira', TO_DATE('1975-09-23', 'YYYY-MM-DD'), 0, 'PROFESSOR');
INSERT INTO PROFESSOR (CPF, CARGO, RUA, NUMERO, CIDADE, ORGAO_EMISSOR, VALOR, AVALIACAO_DE_ALUNOS)
VALUES ('222.222.222-22', 'Professor de Desenvolvimento de Software', 'Rua Professor Xavier', '456', 'Cidade XYZ', 'Orgão Emissor XYZ', 2000, 4.8);

-- Professor 3
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('333.333.333-33', 'Maria Rodrigues', TO_DATE('1982-06-10', 'YYYY-MM-DD'), 0, 'PROFESSOR');
INSERT INTO PROFESSOR (CPF, CARGO, RUA, NUMERO, CIDADE, ORGAO_EMISSOR, VALOR, AVALIACAO_DE_ALUNOS)
VALUES ('333.333.333-33', 'Professora de Inteligência Artificial', 'Rua Professor Histórico', '789', 'Cidade Histórica', 'Orgão Emissor Histórico', 1500, 4.2);

-- Professor 4
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('444.444.444-44', 'Rafaela Santos', TO_DATE('1978-04-05', 'YYYY-MM-DD'), 0, 'PROFESSOR');
INSERT INTO PROFESSOR (CPF, CARGO, RUA, NUMERO, CIDADE, ORGAO_EMISSOR, VALOR, AVALIACAO_DE_ALUNOS)
VALUES ('444.444.444-44', 'Professora de Redes de Computadores', 'Rua das Artes', '1011', 'Cidade das Artes', 'Orgão Emissor das Artes', 1800, 4.6);

-- Professor 5
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('555.555.555-55', 'Eduardo Souza', TO_DATE('1985-11-19', 'YYYY-MM-DD'), 0, 'PROFESSOR');
INSERT INTO PROFESSOR (CPF, CARGO, RUA, NUMERO, CIDADE, ORGAO_EMISSOR, VALOR, AVALIACAO_DE_ALUNOS)
VALUES ('555.555.555-55', 'Professor de Ciência de Dados', 'Rua do Big Data', '1213', 'Cidade dos Dados', 'Orgão Emissor dos Dados', 2200, 4.9);

-- Professor 6
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('666.666.666-66', 'Juliana Lima', TO_DATE('1983-07-28', 'YYYY-MM-DD'), 0, 'PROFESSOR');
INSERT INTO PROFESSOR (CPF, CARGO, RUA, NUMERO, CIDADE, ORGAO_EMISSOR, VALOR, AVALIACAO_DE_ALUNOS)
VALUES ('666.666.666-66', 'Professora de Engenharia de Software', 'Rua das Equipes', '1415', 'Cidade dos Projetos', 'Orgão Emissor dos Projetos', 1900, 4.3);

-- Professor 7
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('777.777.777-77', 'Fernando Martins', TO_DATE('1976-03-11', 'YYYY-MM-DD'), 0, 'PROFESSOR');
INSERT INTO PROFESSOR (CPF, CARGO, RUA, NUMERO, CIDADE, ORGAO_EMISSOR, VALOR, AVALIACAO_DE_ALUNOS)
VALUES ('777.777.777-77', 'Professor de Sistemas Embarcados', 'Rua da Eletrônica', '1617', 'Cidade dos Circuitos', 'Orgão Emissor dos Circuitos', 2100, 4.7);

-- Professor 8
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('888.888.888-88', 'Mariana Costa', TO_DATE('1981-02-09', 'YYYY-MM-DD'), 1, 'PROFESSOR');
INSERT INTO PROFESSOR (CPF, CARGO, RUA, NUMERO, CIDADE, ORGAO_EMISSOR, VALOR, AVALIACAO_DE_ALUNOS)
VALUES ('888.888.888-88', 'Professora de Cibersegurança', 'Rua da Criptografia', '1819', 'Cidade da Segurança', 'Orgão Emissor da Segurança', 1000, 4.0);

-- Professor 9
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('999.999.999-99', 'Lucas Oliveira', TO_DATE('1987-05-28', 'YYYY-MM-DD'), 0, 'PROFESSOR');
INSERT INTO PROFESSOR (CPF, CARGO, RUA, NUMERO, CIDADE, ORGAO_EMISSOR, VALOR, AVALIACAO_DE_ALUNOS)
VALUES ('999.999.999-99', 'Professor de Inteligência Artificial', 'Rua da Inovação', '789', 'Cidade Tech', 'Orgão Emissor Tech', 2500, 4.7);

-- Professor 10
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('123.456.789-10', 'Fernanda Santos', TO_DATE('1984-12-01', 'YYYY-MM-DD'), 0, 'PROFESSOR');
INSERT INTO PROFESSOR (CPF, CARGO, RUA, NUMERO, CIDADE, ORGAO_EMISSOR, VALOR, AVALIACAO_DE_ALUNOS)
VALUES ('123.456.789-10', 'Professora de Redes de Computadores', 'Rua dos Protocolos', '1011', 'Cidade da Conexão', 'Orgão Emissor de Redes', 1800, 4.5);

--########################################################################################################################################################

-- Aluno 1
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('111.111.111-12', 'João Silva', TO_DATE('2000-05-10', 'YYYY-MM-DD'), 0, 'ALUNO');
INSERT INTO ALUNO (CPF, NIVEL, SOCIALMENTE_VULNERAVEL)
VALUES ('111.111.111-12', 2, 'SIM');

-- Aluno 2
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('222.222.222-23', 'Mariana Oliveira', TO_DATE('1999-08-22', 'YYYY-MM-DD'), 1, 'ALUNO');
INSERT INTO ALUNO (CPF, NIVEL, SOCIALMENTE_VULNERAVEL)
VALUES ('222.222.222-23', 3, 'NAO');

-- Aluno 3
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('333.333.333-34', 'Pedro Rodrigues', TO_DATE('2001-02-15', 'YYYY-MM-DD'), 0, 'ALUNO');
INSERT INTO ALUNO (CPF, NIVEL, SOCIALMENTE_VULNERAVEL)
VALUES ('333.333.333-34', 1, 'SIM');

-- Aluno 4
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('444.444.444-45', 'Carolina Santos', TO_DATE('2002-11-05', 'YYYY-MM-DD'), 0, 'ALUNO');
INSERT INTO ALUNO (CPF, NIVEL, SOCIALMENTE_VULNERAVEL)
VALUES ('444.444.444-45', 2, 'NAO');

-- Aluno 5
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('555.555.555-56', 'Lucas Oliveira', TO_DATE('2003-07-18', 'YYYY-MM-DD'), 1, 'ALUNO');
INSERT INTO ALUNO (CPF, NIVEL, SOCIALMENTE_VULNERAVEL)
VALUES ('555.555.555-56', 1, 'SIM');

-- Aluno 6
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('666.666.666-67', 'Julia Santos', TO_DATE('2004-03-12', 'YYYY-MM-DD'), 0, 'ALUNO');
INSERT INTO ALUNO (CPF, NIVEL, SOCIALMENTE_VULNERAVEL)
VALUES ('666.666.666-67', 3, 'NAO');

-- Aluno 7
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('777.777.777-78', 'Matheus Lima', TO_DATE('2005-01-25', 'YYYY-MM-DD'), 0, 'ALUNO');
INSERT INTO ALUNO (CPF, NIVEL, SOCIALMENTE_VULNERAVEL)
VALUES ('777.777.777-78', 2, 'SIM');

-- Aluno 8
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('888.888.888-89', 'Beatriz Silva', TO_DATE('2006-09-07', 'YYYY-MM-DD'), 1, 'ALUNO');
INSERT INTO ALUNO (CPF, NIVEL, SOCIALMENTE_VULNERAVEL)
VALUES ('888.888.888-89', 1, 'SIM');

-- Aluno 9
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('999.999.999-90', 'Guilherme Souza', TO_DATE('2007-04-23', 'YYYY-MM-DD'), 0, 'ALUNO');
INSERT INTO ALUNO (CPF, NIVEL, SOCIALMENTE_VULNERAVEL)
VALUES ('999.999.999-90', 3, 'NAO');

-- Aluno 10
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('123.456.789-11', 'Ana Oliveira', TO_DATE('2008-12-08', 'YYYY-MM-DD'), 1, 'ALUNO');
INSERT INTO ALUNO (CPF, NIVEL, SOCIALMENTE_VULNERAVEL)
VALUES ('123.456.789-11', 2, 'SIM');

--########################################################################################################################################################

-- Monitor 1
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('111.111.111-13', 'Lukas Muller', TO_DATE('1998-06-20', 'YYYY-MM-DD'), 0, 'MONITOR');
INSERT INTO MONITOR (CPF, AVALIACAO_DE_ALUNOS)
VALUES ('111.111.111-13', 4);

-- Monitor 2
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('222.222.222-24', 'Anna Schmidt', TO_DATE('1997-09-12', 'YYYY-MM-DD'), 1, 'MONITOR');
INSERT INTO MONITOR (CPF, AVALIACAO_DE_ALUNOS)
VALUES ('222.222.222-24', 3);

-- Monitor 3
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('333.333.333-35', 'Marco Rossi', TO_DATE('1999-03-05', 'YYYY-MM-DD'), 0, 'MONITOR');
INSERT INTO MONITOR (CPF, AVALIACAO_DE_ALUNOS)
VALUES ('333.333.333-35', 5);

-- Monitor 4
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('444.444.444-46', 'Sofia Romano', TO_DATE('1996-12-15', 'YYYY-MM-DD'), 1, 'MONITOR');
INSERT INTO MONITOR (CPF, AVALIACAO_DE_ALUNOS)
VALUES ('444.444.444-46', 4);

-- Monitor 5
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('555.555.555-57', 'Leonardo Esposito', TO_DATE('1998-04-02', 'YYYY-MM-DD'), 0, 'MONITOR');
INSERT INTO MONITOR (CPF, AVALIACAO_DE_ALUNOS)
VALUES ('555.555.555-57', 5);

--########################################################################################################################################################

-- Administrador
INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('000.000.000-00', 'Kenzo Nobre', TO_DATE('2003-07-19', 'YYYY-MM-DD'), 0, 'ADMINISTRADOR');
INSERT INTO ADMINISTRADOR (CPF)
VALUES ('000.000.000-00');

INSERT INTO PESSOA (CPF, NOME, DATA_NASC, PCD, TIPO_USER)
VALUES ('010.101.010-10', 'Mr. Anderson', TO_DATE('1998-07-19', 'YYYY-MM-DD'), 0, 'ADMINISTRADOR');
INSERT INTO ADMINISTRADOR (CPF)
VALUES ('010.101.010-10');

--########################################################################################################################################################

-- Avaliações de Professores
-- Aluno 1 avaliando Professor 1
INSERT INTO AVALIA_PROFESSOR (ALUNO, PROFESSOR, NOTA)
VALUES ('111.111.111-12', '111.111.111-11', 4);

-- Aluno 2 avaliando Professor 2
INSERT INTO AVALIA_PROFESSOR (ALUNO, PROFESSOR, NOTA)
VALUES ('222.222.222-23', '222.222.222-22', 5);

-- Aluno 3 avaliando Professor 3
INSERT INTO AVALIA_PROFESSOR (ALUNO, PROFESSOR, NOTA)
VALUES ('333.333.333-34', '333.333.333-33', 3);

-- Aluno 4 avaliando Professor 4
INSERT INTO AVALIA_PROFESSOR (ALUNO, PROFESSOR, NOTA)
VALUES ('444.444.444-45', '444.444.444-44', 4);

-- Aluno 5 avaliando Professor 5
INSERT INTO AVALIA_PROFESSOR (ALUNO, PROFESSOR, NOTA)
VALUES ('555.555.555-56', '555.555.555-55', 5);

-- Aluno 6 avaliando Professor 6
INSERT INTO AVALIA_PROFESSOR (ALUNO, PROFESSOR, NOTA)
VALUES ('666.666.666-67', '666.666.666-66', 4);

-- Aluno 7 avaliando Professor 7
INSERT INTO AVALIA_PROFESSOR (ALUNO, PROFESSOR, NOTA)
VALUES ('777.777.777-78', '777.777.777-77', 3);

-- Aluno 8 avaliando Professor 8
INSERT INTO AVALIA_PROFESSOR (ALUNO, PROFESSOR, NOTA)
VALUES ('888.888.888-89', '888.888.888-88', 4);

-- Aluno 9 avaliando Professor 9
INSERT INTO AVALIA_PROFESSOR (ALUNO, PROFESSOR, NOTA)
VALUES ('999.999.999-90', '999.999.999-99', 5);

-- Aluno 10 avaliando Professor 10
INSERT INTO AVALIA_PROFESSOR (ALUNO, PROFESSOR, NOTA)
VALUES ('123.456.789-11', '123.456.789-10', 4);

--########################################################################################################################################################

-- Avaliações de Monitores
-- Aluno 1 avaliando Monitor 1
INSERT INTO AVALIA_MONITOR (ALUNO, MONITOR, NOTA)
VALUES ('111.111.111-12', '111.111.111-13', 4);

-- Aluno 2 avaliando Monitor 2
INSERT INTO AVALIA_MONITOR (ALUNO, MONITOR, NOTA)
VALUES ('222.222.222-23', '222.222.222-24', 3);

-- Aluno 3 avaliando Monitor 3
INSERT INTO AVALIA_MONITOR (ALUNO, MONITOR, NOTA)
VALUES ('333.333.333-34', '333.333.333-35', 5);

-- Aluno 4 avaliando Monitor 4
INSERT INTO AVALIA_MONITOR (ALUNO, MONITOR, NOTA)
VALUES ('444.444.444-45', '444.444.444-46', 4);

-- Aluno 5 avaliando Monitor 5
INSERT INTO AVALIA_MONITOR (ALUNO, MONITOR, NOTA)
VALUES ('555.555.555-56', '555.555.555-57', 5);

-- Aluno 6 avaliando Monitor 1
INSERT INTO AVALIA_MONITOR (ALUNO, MONITOR, NOTA)
VALUES ('666.666.666-67', '111.111.111-13', 4);

-- Aluno 7 avaliando Monitor 2
INSERT INTO AVALIA_MONITOR (ALUNO, MONITOR, NOTA)
VALUES ('777.777.777-78', '222.222.222-24', 3);

-- Aluno 8 avaliando Monitor 3
INSERT INTO AVALIA_MONITOR (ALUNO, MONITOR, NOTA)
VALUES ('888.888.888-89', '333.333.333-35', 4);

-- Aluno 9 avaliando Monitor 4
INSERT INTO AVALIA_MONITOR (ALUNO, MONITOR, NOTA)
VALUES ('999.999.999-90', '444.444.444-46', 5);

-- Aluno 10 avaliando Monitor 5
INSERT INTO AVALIA_MONITOR (ALUNO, MONITOR, NOTA)
VALUES ('123.456.789-11', '555.555.555-57', 4);

--########################################################################################################################################################

-- Curso 1
INSERT INTO CURSO (NOME, DESCRICAO, LIMITE_ALUNOS, PROFESSOR, NOME_FORUM)
VALUES ('Informatica1', 'Introdução à Informática', 50, '111.111.111-11', 'ForumInformatica1');

-- Curso 2
INSERT INTO CURSO (NOME, DESCRICAO, LIMITE_ALUNOS, PROFESSOR, NOME_FORUM)
VALUES ('Informatica2', 'Programação em Java', 40, '222.222.222-22', 'ForumInformatica2');

-- Curso 3
INSERT INTO CURSO (NOME, DESCRICAO, LIMITE_ALUNOS, PROFESSOR, NOME_FORUM)
VALUES ('Informatica3', 'Banco de Dados', 30, '333.333.333-33', 'ForumInformatica3');

-- Curso 4
INSERT INTO CURSO (NOME, DESCRICAO, LIMITE_ALUNOS, PROFESSOR, NOME_FORUM)
VALUES ('Informatica4', 'Redes de Computadores', 35, '444.444.444-44', 'ForumInformatica4');

-- Curso 5
INSERT INTO CURSO (NOME, DESCRICAO, LIMITE_ALUNOS, PROFESSOR, NOME_FORUM)
VALUES ('Informatica5', 'Sistemas Operacionais', 25, '555.555.555-55', 'ForumInformatica5');

-- Curso 6
INSERT INTO CURSO (NOME, DESCRICAO, LIMITE_ALUNOS, PROFESSOR, NOME_FORUM)
VALUES ('Informatica6', 'Inteligência Artificial', 20, '666.666.666-66', 'ForumInformatica6');

-- Curso 7
INSERT INTO CURSO (NOME, DESCRICAO, LIMITE_ALUNOS, PROFESSOR, NOME_FORUM)
VALUES ('Informatica7', 'Engenharia de Software', 30, '777.777.777-77', 'ForumInformatica7');

-- Curso 8
INSERT INTO CURSO (NOME, DESCRICAO, LIMITE_ALUNOS, PROFESSOR, NOME_FORUM)
VALUES ('Informatica8', 'Segurança da Informação', 25, '888.888.888-88', 'ForumInformatica8');

-- Curso 9
INSERT INTO CURSO (NOME, DESCRICAO, LIMITE_ALUNOS, PROFESSOR, NOME_FORUM)
VALUES ('Informatica9', 'Desenvolvimento Web', 40, '999.999.999-99', 'ForumInformatica9');

-- Curso 10
INSERT INTO CURSO (NOME, DESCRICAO, LIMITE_ALUNOS, PROFESSOR, NOME_FORUM)
VALUES ('Informatica10', 'Introdução à Inteligência Artificial', 30, '123.456.789-10', 'ForumInformatica10');

--########################################################################################################################################################

-- Inserções na tabela de requisitos

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica1', 'celular');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica1', 'calculadora');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica1', 'computador');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica2', 'computador');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica2', 'IDE (Integrated Development Environment)');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica3', 'computador');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica3', 'SGBD (Sistema Gerenciador de Banco de Dados)');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica4', 'computador');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica4', 'roteador');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica5', 'computador');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica5', 'sistema operacional');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica6', 'computador');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica6', 'algoritmos de IA');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica7', 'computador');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica7', 'ferramentas de desenvolvimento');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica8', 'computador');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica8', 'firewall');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica9', 'computador');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica9', 'HTML/CSS');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica10', 'computador');

INSERT INTO REQUISITOS (CURSO, REQUISITO) 
VALUES ('Informatica10', 'conhecimento básico de programação');

--########################################################################################################################################################

-- Inserções na tabela auxilia
INSERT INTO AUXILIA (MONITOR, CURSO) 
VALUES ('222.222.222-24', 'Informatica10');

INSERT INTO AUXILIA (MONITOR, CURSO) 
VALUES ('333.333.333-35', 'Informatica1');

INSERT INTO AUXILIA (MONITOR, CURSO) 
VALUES ('444.444.444-46', 'Informatica2');

INSERT INTO AUXILIA (MONITOR, CURSO) 
VALUES ('555.555.555-57', 'Informatica3');

INSERT INTO AUXILIA (MONITOR, CURSO) 
VALUES ('111.111.111-13', 'Informatica4');

INSERT INTO AUXILIA (MONITOR, CURSO) 
VALUES ('222.222.222-24', 'Informatica5');

INSERT INTO AUXILIA (MONITOR, CURSO) 
VALUES ('333.333.333-35', 'Informatica6');

INSERT INTO AUXILIA (MONITOR, CURSO) 
VALUES ('444.444.444-46', 'Informatica7');

INSERT INTO AUXILIA (MONITOR, CURSO) 
VALUES ('555.555.555-57', 'Informatica8');

INSERT INTO AUXILIA (MONITOR, CURSO) 
VALUES ('111.111.111-13', 'Informatica9');

--########################################################################################################################################################

--inserções na tabela participa_ranking

INSERT INTO PARTICIPA_RANKING (ALUNO, CURSO, STREAK)
VALUES ('111.111.111-12', 'Informatica1', 2);

INSERT INTO PARTICIPA_RANKING (ALUNO, CURSO, STREAK)
VALUES ('111.111.111-12', 'Informatica2', 3);

INSERT INTO PARTICIPA_RANKING (ALUNO, CURSO, STREAK)
VALUES ('222.222.222-23', 'Informatica1', 3);

INSERT INTO PARTICIPA_RANKING (ALUNO, CURSO, STREAK)
VALUES ('222.222.222-23', 'Informatica2', 2);

--########################################################################################################################################################

-- Inserções na tabela horário ministra

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica1', '08:00');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica2', '09:30');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica3', '10:45');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica4', '13:15');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica5', '14:30');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica6', '15:45');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica7', '17:00');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica8', '18:15');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica9', '19:30');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica10', '20:45');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica1', '10:30');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica5', '13:00');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica5', '15:30');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica5', '18:00');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica5', '09:30');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica5', '11:00');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica6', '14:30');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica9', '16:00');

INSERT INTO HORARIO_MINISTRA (CURSO, HORARIO)
VALUES ('Informatica10', '19:30');

--########################################################################################################################################################

-- Inserções na tabela recurso_ministra
INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica1', 'Computador');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica1', 'Excel');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica1', 'Internet');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica2', 'Computador');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica2', 'Programa de Edição de Imagens');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica2', 'Banco de Dados');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica3', 'Computador');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica3', 'Desenvolvimento Web');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica3', 'Redes de Computadores');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica4', 'Computador');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica4', 'Linguagem de Programação');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica4', 'Sistema Operacional');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica5', 'Computador');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica5', 'Programação em C');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica5', 'Segurança da Informação');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica6', 'Computador');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica6', 'Inteligência Artificial');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica6', 'Banco de Dados Avançado');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica7', 'Computador');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica7', 'Desenvolvimento Mobile');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica7', 'Redes Sem Fio');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica8', 'Computador');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica8', 'Programação Orientada a Objetos');

INSERT INTO RECURSO_MINISTRA (CURSO, RECURSO)
VALUES ('Informatica8', 'Gestão de Projetos de Software');

--########################################################################################################################################################
-- Publicações

-- Publicação por um professor
INSERT INTO PUBLICACAO (PESSOA, EPOCA, CURSO, CONTEUDO, PESSOA_REFERENCIADA, EPOCA_REFERENCIADA, CURSO_REFERENCIADO)
VALUES ('999.999.999-99', TO_DATE('2023-07-03', 'YYYY-MM-DD'), 'Informatica3', 'Hoje teremos uma aula prática sobre SQL. Preparem seus bancos de dados!', NULL, NULL, NULL);

-- Publicação por um aluno
INSERT INTO PUBLICACAO (PESSOA, EPOCA, CURSO, CONTEUDO, PESSOA_REFERENCIADA, EPOCA_REFERENCIADA, CURSO_REFERENCIADO)
VALUES ('111.111.111-12', TO_DATE('2023-07-10', 'YYYY-MM-DD'), 'Informatica4', 'Estou animado para aprender mais sobre redes de computadores!', NULL, NULL, NULL);

-- Publicação por um monitor
INSERT INTO PUBLICACAO (PESSOA, EPOCA, CURSO, CONTEUDO, PESSOA_REFERENCIADA, EPOCA_REFERENCIADA, CURSO_REFERENCIADO)
VALUES ('222.222.222-24', TO_DATE('2023-07-05', 'YYYY-MM-DD'), 'Informatica1', 'Não se esqueçam da monitoria de hoje às 14h!', NULL, NULL, NULL);

-- Publicação com referência a outra pessoa
INSERT INTO PUBLICACAO (PESSOA, EPOCA, CURSO, CONTEUDO, PESSOA_REFERENCIADA, EPOCA_REFERENCIADA, CURSO_REFERENCIADO)
VALUES ('111.111.111-12', TO_DATE('2023-07-06', 'YYYY-MM-DD'), 'Informatica4', 'Parabéns @professor2 pela explicação clara sobre roteadores!', '999.999.999-99', TO_DATE('2023-07-03', 'YYYY-MM-DD'), 'Informatica3');

-- Publicação por um professor
INSERT INTO PUBLICACAO (PESSOA, EPOCA, CURSO, CONTEUDO, PESSOA_REFERENCIADA, EPOCA_REFERENCIADA, CURSO_REFERENCIADO)
VALUES ('222.222.222-24', TO_DATE('2023-07-07', 'YYYY-MM-DD'), 'Informatica2', 'Lembrete: Prova de Java acontecerá na próxima semana. Estudem!', NULL, NULL, NULL);

-- Publicação por um aluno
INSERT INTO PUBLICACAO (PESSOA, EPOCA, CURSO, CONTEUDO, PESSOA_REFERENCIADA, EPOCA_REFERENCIADA, CURSO_REFERENCIADO)
VALUES ('444.444.444-45', TO_DATE('2023-07-08', 'YYYY-MM-DD'), 'Informatica4', 'Compartilhando um ótimo tutorial sobre protocolo TCP/IP. Confiram!', NULL, NULL, NULL);

-- Publicação por um monitor
INSERT INTO PUBLICACAO (PESSOA, EPOCA, CURSO, CONTEUDO, PESSOA_REFERENCIADA, EPOCA_REFERENCIADA, CURSO_REFERENCIADO)
VALUES ('111.111.111-13', TO_DATE('2023-07-09', 'YYYY-MM-DD'), 'Informatica1', 'Monitoria cancelada hoje devido a imprevistos. Desculpem pelo inconveniente.', NULL, NULL, NULL);

-- Publicação com referência a outra pessoa
INSERT INTO PUBLICACAO (PESSOA, EPOCA, CURSO, CONTEUDO, PESSOA_REFERENCIADA, EPOCA_REFERENCIADA, CURSO_REFERENCIADO)
VALUES ('444.444.444-46', TO_DATE('2023-07-10', 'YYYY-MM-DD'), 'Informatica4', 'Parabéns @aluno1 pela conquista da medalha na competição de programação!', '111.111.111-12', TO_DATE('2023-07-10', 'YYYY-MM-DD'), 'Informatica4');

--########################################################################################################################################################
-- JORNADA DE PROGRESSO SÃO OS CURSOS QUE O ALUNO ESTA MATRICULADO

-- Jornada de progresso do Aluno 1
INSERT INTO JORNADA_DE_PROGRESSO (CURSO, ALUNO, NIVEL_DE_APRENDIZADO)
VALUES ('Informatica1', '111.111.111-12', 1);

-- Jornada de progresso do Aluno 2
INSERT INTO JORNADA_DE_PROGRESSO (CURSO, ALUNO, NIVEL_DE_APRENDIZADO)
VALUES ('Informatica2', '222.222.222-23', 2);

-- Jornada de progresso do Aluno 3
INSERT INTO JORNADA_DE_PROGRESSO (CURSO, ALUNO, NIVEL_DE_APRENDIZADO)
VALUES ('Informatica3', '333.333.333-34', 3);

-- Jornada de progresso do Aluno 4
INSERT INTO JORNADA_DE_PROGRESSO (CURSO, ALUNO, NIVEL_DE_APRENDIZADO)
VALUES ('Informatica4', '444.444.444-45', 1);

-- Jornada de progresso do Aluno 5
INSERT INTO JORNADA_DE_PROGRESSO (CURSO, ALUNO, NIVEL_DE_APRENDIZADO)
VALUES ('Informatica5', '555.555.555-56', 2);

-- Jornada de progresso do Aluno 6 no curso Informatica1
INSERT INTO JORNADA_DE_PROGRESSO (CURSO, ALUNO, NIVEL_DE_APRENDIZADO)
VALUES ('Informatica1', '666.666.666-67', 3);

-- Jornada de progresso do Aluno 7 no curso Informatica1
INSERT INTO JORNADA_DE_PROGRESSO (CURSO, ALUNO, NIVEL_DE_APRENDIZADO)
VALUES ('Informatica1', '777.777.777-78', 1);

-- Jornada de progresso do Aluno 8 no curso Informatica1
INSERT INTO JORNADA_DE_PROGRESSO (CURSO, ALUNO, NIVEL_DE_APRENDIZADO)
VALUES ('Informatica1', '888.888.888-89', 2);

-- Jornada de progresso do Aluno 9 no curso Informatica1
INSERT INTO JORNADA_DE_PROGRESSO (CURSO, ALUNO, NIVEL_DE_APRENDIZADO)
VALUES ('Informatica1', '999.999.999-90', 1);

-- Jornada de progresso do Aluno 10 no curso Informatica2
INSERT INTO JORNADA_DE_PROGRESSO (CURSO, ALUNO, NIVEL_DE_APRENDIZADO)
VALUES ('Informatica2', '123.456.789-11', 3);

--########################################################################################################################################################

-- Missão 1
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica1', 'Missao1', 'Conceitos básicos de informática', 100, 'Fácil', '2h');

-- Missão 2
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica2', 'Missao2', 'Programação em Java avançada', 150, 'Médio', '3h');

-- Missão 3
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica3', 'Missao3', 'Projeto de banco de dados', 200, 'Difícil', '4h');

-- Missão 4
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica4', 'Missao4', 'Configuração de redes de computadores', 120, 'Médio', '2h');

-- Missão 5
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica5', 'Missao5', 'Gerenciamento de sistemas operacionais', 180, 'Médio', '3h');

-- Missão 6
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica6', 'Missao6', 'Aplicações práticas de inteligência artificial', 250, 'Difícil', '4h');

-- Missão 7
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica7', 'Missao7', 'Desenvolvimento de software em equipe', 180, 'Médio', '3h');

-- Missão 8
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica8', 'Missao8', 'Práticas de segurança da informação', 200, 'Difícil', '4h');

-- Missão 9
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica9', 'Missao9', 'Desenvolvimento de websites dinâmicos', 150, 'Médio', '3h');

-- Missão 10
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica10', 'Missao10', 'Integração de IA em projetos reais', 250, 'Difícil', '4h');

-- Missão 2 do curso Informatica1
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica1', 'Missao2', 'Conceitos básicos de computação', 120, 'Fácil', '1h');

-- Missão 3 do curso Informatica1
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica1', 'Missao3', 'Uso básico de sistemas operacionais', 150, 'Médio', '2h');

-- Missão 4 do curso Informatica1
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica1', 'Missao4', 'Introdução à programação', 180, 'Médio', '2h');

-- Missão 5 do curso Informatica1
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica1', 'Missao5', 'Prática de algoritmos', 200, 'Médio', '3h');

-- Missão 1 do curso Informatica2
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica2', 'Missao1', 'Programação orientada a objetos', 150, 'Médio', '2h');

-- Missão 3 do curso Informatica2
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica2', 'Missao3', 'Banco de dados relacional', 200, 'Médio', '3h');

-- Missão 4 do curso Informatica2
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica2', 'Missao4', 'Desenvolvimento web', 220, 'Médio', '3h');

-- Missão 5 do curso Informatica2
INSERT INTO MISSAO (CURSO, NOME, DESCRICAO, EXPERIENCIA, DIFICULDADE, DURACAO)
VALUES ('Informatica2', 'Missao5', 'Princípios de design de software', 250, 'Médio', '2h');

--########################################################################################################################################################

-- Aluno 1, Curso Informatica1, Missões
INSERT INTO JORNADA_CONTEM_MISSAO (CURSO_JORNADA, ALUNO_JORNADA, CURSO_MISSAO, NOME_MISSAO, FINALIZADA)
VALUES ('Informatica1', '111.111.111-12', 'Informatica1', 'Missao1', 1);

INSERT INTO JORNADA_CONTEM_MISSAO (CURSO_JORNADA, ALUNO_JORNADA, CURSO_MISSAO, NOME_MISSAO, FINALIZADA)
VALUES ('Informatica1', '111.111.111-12', 'Informatica1', 'Missao2', 0);

INSERT INTO JORNADA_CONTEM_MISSAO (CURSO_JORNADA, ALUNO_JORNADA, CURSO_MISSAO, NOME_MISSAO, FINALIZADA)
VALUES ('Informatica1', '111.111.111-12', 'Informatica1', 'Missao3', 0);

-- Aluno 2, Curso Informatica2, Missões
INSERT INTO JORNADA_CONTEM_MISSAO (CURSO_JORNADA, ALUNO_JORNADA, CURSO_MISSAO, NOME_MISSAO, FINALIZADA)
VALUES ('Informatica2', '222.222.222-23', 'Informatica2', 'Missao1', 0);

INSERT INTO JORNADA_CONTEM_MISSAO (CURSO_JORNADA, ALUNO_JORNADA, CURSO_MISSAO, NOME_MISSAO, FINALIZADA)
VALUES ('Informatica2', '222.222.222-23', 'Informatica2', 'Missao2', 0);

INSERT INTO JORNADA_CONTEM_MISSAO (CURSO_JORNADA, ALUNO_JORNADA, CURSO_MISSAO, NOME_MISSAO, FINALIZADA)
VALUES ('Informatica2', '222.222.222-23', 'Informatica2', 'Missao3', 0);

--########################################################################################################################################################
--FAZ SAO AS MISSOES REALIZADAS DOS ALUNOS DE UM CURSO

-- Aluno 1 faz as missões do curso Informatica1
INSERT INTO FAZ (ALUNO, CURSO, MISSAO, EPOCA)
VALUES ('111.111.111-12', 'Informatica1', 'Missao2', TO_DATE('2008-12-08', 'YYYY-MM-DD'));

INSERT INTO FAZ (ALUNO, CURSO, MISSAO, EPOCA)
VALUES ('111.111.111-12', 'Informatica1', 'Missao3', TO_DATE('2008-12-09', 'YYYY-MM-DD'));

-- Aluno 1 faz as missões do curso Informatica2
INSERT INTO FAZ (ALUNO, CURSO, MISSAO, EPOCA)
VALUES ('111.111.111-12', 'Informatica2', 'Missao1', TO_DATE('2008-12-10', 'YYYY-MM-DD'));

INSERT INTO FAZ (ALUNO, CURSO, MISSAO, EPOCA)
VALUES ('111.111.111-12', 'Informatica2', 'Missao2', TO_DATE('2008-12-11', 'YYYY-MM-DD'));

INSERT INTO FAZ (ALUNO, CURSO, MISSAO, EPOCA)
VALUES ('111.111.111-12', 'Informatica2', 'Missao3', TO_DATE('2008-12-12', 'YYYY-MM-DD'));

-- Aluno 2 faz as missões do curso Informatica1
INSERT INTO FAZ (ALUNO, CURSO, MISSAO, EPOCA)
VALUES ('222.222.222-23', 'Informatica1', 'Missao1', TO_DATE('2008-12-01', 'YYYY-MM-DD'));

INSERT INTO FAZ (ALUNO, CURSO, MISSAO, EPOCA)
VALUES ('222.222.222-23', 'Informatica1', 'Missao2', TO_DATE('2008-12-02', 'YYYY-MM-DD'));

INSERT INTO FAZ (ALUNO, CURSO, MISSAO, EPOCA)
VALUES ('222.222.222-23', 'Informatica1', 'Missao3', TO_DATE('2008-12-03', 'YYYY-MM-DD'));

-- Aluno 2 faz as missões do curso Informatica2
INSERT INTO FAZ (ALUNO, CURSO, MISSAO, EPOCA)
VALUES ('222.222.222-23', 'Informatica2', 'Missao1', TO_DATE('2008-12-01', 'YYYY-MM-DD'));

INSERT INTO FAZ (ALUNO, CURSO, MISSAO, EPOCA)
VALUES ('222.222.222-23', 'Informatica2', 'Missao2', TO_DATE('2008-12-04', 'YYYY-MM-DD'));

INSERT INTO FAZ (ALUNO, CURSO, MISSAO, EPOCA)
VALUES ('222.222.222-23', 'Informatica2', 'Missao3', TO_DATE('2008-12-05', 'YYYY-MM-DD'));

--########################################################################################################################################################