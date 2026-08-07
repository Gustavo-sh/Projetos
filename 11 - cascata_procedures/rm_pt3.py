import pyodbc
from utils import write_log

CONNECTION_STRING = "Driver={ODBC Driver 18 for SQL Server};Server=primno4;Database=Robbyson;Trusted_Connection=yes;TrustServerCertificate=yes;"

try:
    with pyodbc.connect(CONNECTION_STRING) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT @@SPID")
        spid = cursor.fetchone()[0]
        write_log(f"Executando Robbyson Matriz parte 3 (SPID: {spid})...")
        cursor.execute(f"EXEC exec sp_ins_Robbyson_Matriz_pt3")
        write_log(f"Procedure Robbyson Matriz parte 3 finalizada...")
        conn.commit()
except Exception as e:
    write_log(str(e))