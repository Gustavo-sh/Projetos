import pyodbc

CONNECTION_STRING = "Driver={SQL Server};Server=primno4;Database=Robbyson;Trusted_Connection=yes;"

query = """
select id_indicador, indicador_nome from rby.indicador (nolock)
"""

def get_indicadores():
    conn = pyodbc.connect(CONNECTION_STRING)
    cur = conn.cursor()
    cur.execute(query)
    resultados = [{"id_indicador": r[0], "indicador_nome": r[1]} for r in cur.fetchall()]
    cur.close()
    conn.close()

    return resultados