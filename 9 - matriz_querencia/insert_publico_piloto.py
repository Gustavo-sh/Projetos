import pyodbc
from datetime import datetime
from telegram_config import notify_telegram

CONNECTION_STRING = "Driver={ODBC Driver 18 for SQL Server};Server=primno4;Database=RobbysonMatriz;Trusted_Connection=yes;TrustServerCertificate=yes;"

def insert_publico_piloto():
    with pyodbc.connect(CONNECTION_STRING, autocommit=True) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            insert into publico_piloto_sistema_matriz
            select distinct atributo, '', '', '', cast(getdate() as date) as data
            from sistema_matriz (nolock) sm
            where 
                (
                atributo like '% quinto %' or atributo like '% vivo %' or atributo like '% claro %' or atributo like '% net %'
                or atributo like '% porto %' or atributo like '% bradesc%' or atributo like '% casas bahia %' or atributo like '% stellantis %'
                or atributo like '% light %' or atributo like '% shopee %' or atributo like '% livelo %' or atributo like '% leapmotor %'
                ) 
            and periodo = dateadd(d, 1, eomonth(getdate(), -1))
            and not exists (
                select 1 from publico_piloto_sistema_matriz pp (nolock)
                where pp.atributo = sm.atributo
            )
        """)
        conn.commit()
        cursor.close()
    notify_telegram(f"✅ Matriz Querência - Publico Piloto foi atualizado com sucesso!")

if __name__ == "__main__":
    insert_publico_piloto()