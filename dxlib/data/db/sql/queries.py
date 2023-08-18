def GET_TABLES():
    return """
    SELECT table_name FROM user_tables;
    """


def GET_USERS():
    return """
    SELECT P.NOME FROM PESSOA P 
    JOIN  
    (SELECT A.CPF FROM ALUNO A WHERE NOT EXISTS (
        (SELECT M.NOME, M.CURSO FROM MISSAO M
            WHERE M.CURSO = 'Informatica1')
            MINUS
            (SELECT F.MISSAO, F.CURSO FROM FAZ F
            WHERE F.ALUNO = A.CPF)
        )
    ) 
    X ON P.CPF = X.CPF
    """


def GET_MISSIONS():
    return """
    SELECT P.NOME, F.CURSO, MISSOES_FEITAS FROM PESSOA P 
    JOIN 
    (SELECT A.CPF, F.CURSO, COUNT(*) AS MISSOES_FEITAS FROM ALUNO A
        JOIN FAZ F ON (F.ALUNO = A.CPF)
        GROUP BY A.CPF, F.CURSO 
    ) 
    ON P.CPF = A.CPF
    """
