-- Faremos abaixo uma consulta implementando a divisão de algebra relacional
-- Encontraremos os nomes dos alunos fizeram todas as missões de um curso


SELECT P.NOME 
FROM PESSOA P 
JOIN  
(SELECT A.CPF
FROM ALUNO A WHERE NOT EXISTS (
    (SELECT M.NOME, M.CURSO
    FROM MISSAO M
    WHERE M.CURSO = 'Informatica1')
    MINUS
    (SELECT F.MISSAO, F.CURSO
    FROM FAZ F
    WHERE F.ALUNO = A.CPF)
)) X ON P.CPF = X.CPF


-- Faremos aqui uma consulta para contar quantas missões fez cada aluno, em cada curso que está matriculado
SELECT P.NOME, F.CURSO, MISSOES_FEITAS
FROM PESSOA P 
JOIN ( 
SELECT A.CPF, F.CURSO, COUNT(*) AS MISSOES_FEITAS 
FROM ALUNO A
JOIN FAZ F ON (F.ALUNO = A.CPF)
GROUP BY A.CPF, F.CURSO ) ON P.CPF = A.CPF


-- Faremos aqui uma consulta para saber quais cursos tem professores com as médias mais altas de avaliação, 
-- juntamente com o monitor com a melhor avaliação do curso do professor


SELECT C.NOME, P.NOME, P.AVALIACAO_DE_ALUNOS, P2.NOME, M.AVALIACAO_DE_ALUNOS 
FROM PESSOA P
JOIN CURSO C ON (C.PROFESSOR = P.CPF)
JOIN (SELECT M.CPF, P.NOME
FROM PESSOA P2
JOIN AUXILIA A ON (P2.CPF = A.MONITOR)
JOIN MONITOR M ON (P2.CPF = M.CPF)
GROUP BY A.CURSO
HAVING MAX(M.AVALIACAO_DE_ALUNOS)) ON A.CURSO = C.NOME
ORDER BY P.AVALIACAO_DE_ALUNOS

