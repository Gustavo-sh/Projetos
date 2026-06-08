import pyodbc

CONNECTION_STRING = "Driver={SQL Server};Server=primno4;Database=Robbyson;Trusted_Connection=yes;"
CONN = pyodbc.connect(CONNECTION_STRING)

nulls = """
select
       nome,
       data_inicio,
       data_fim
from Historicos_Procedures (nolock)
where cast(Data_Inicio as date) >= cast(getdate() as date)
and data_fim is null
"""

avg_duration = """
select 
    nome,
    avg(datediff(n, data_inicio, data_fim))
from Historicos_Procedures (nolock)
where data_inicio between cast(getdate()-7 as date) and cast(getdate()-1 as date)
group by nome
"""

def get_nulls():
    
    cur = CONN.cursor()
    cur.execute(nulls)
    resultados = [{"nome": row[0], "data_inicio": row[1], "data_fim": row[2]} for row in cur.fetchall()]
    cur.close()
    return resultados

def get_avg_duration():
    cur = CONN.cursor()
    cur.execute(avg_duration)
    resultados = {row[0]: row[1] for row in cur.fetchall()}
    cur.close()
    return resultados

def close_connection():
    CONN.close()