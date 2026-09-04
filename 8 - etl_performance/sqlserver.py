import pyodbc
from utils import write_log
from dotenv import load_dotenv
import os

load_dotenv(r"C:\Users\e.gustavo.santos.GRUPO_A&C\Documents\Projetos\8 - etl_performance\.env")

SQLSERVER_CONNECTION = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=primno4;"
    "DATABASE=robbyson;"
    "Trusted_Connection=yes;"
    "Encrypt=no;"
)

CONN_SQL = pyodbc.connect(SQLSERVER_CONNECTION)
CONN_SQL.autocommit = False
CURSOR_SQL = CONN_SQL.cursor()
CURSOR_SQL.fast_executemany = True

def delete_day_indicators_performance(dia, environ, indicators):

    str_like = ""
    if environ == "AEC":
        str_like = "segmento not like 'premium - %santander%'"
    elif environ == "SANTANDER":
        str_like = "segmento like 'premium - %santander%'"

    sql = f"""
        DELETE TOP (10000)
        FROM rby.performance
        WHERE data = ?
        and {str_like}
        """

    if indicators:
        placeholders = ", ".join("?" for _ in indicators)
        sql += f"and id_indicador in ({placeholders})"
    
    write_log(f"Deletando {dia} para {environ}...")

    lines = 0

    params = (dia, *indicators) if indicators else (dia,)

    while True:

        CURSOR_SQL.execute(sql,
            params
        )

        rowcount = CURSOR_SQL.rowcount
        lines += rowcount

        if rowcount == 0:
            break

    write_log(f"Dia {dia} deletado ({lines} linhas) para {environ} (ids {indicators})...")


def delete_day_indicators_notificacao(dia, environ):

    str_like = ""
    if environ == "AEC":
        str_like = "segmento not like 'premium - %santander%'"
    elif environ == "SANTANDER":
        str_like = "segmento like 'premium - %santander%'"

    sql = f"""
        DELETE TOP (10000)
        FROM rby.notificacao_compacta_python      
        WHERE data = ?
        and {str_like}
        """
    
    write_log(f"NOTIF - Deletando {dia} para {environ}...")

    lines = 0

    params = (dia,)

    while True:

        CURSOR_SQL.execute(sql,
            params
        )

        rowcount = CURSOR_SQL.rowcount
        lines += rowcount

        if rowcount == 0:
            break

    write_log(f"NOTIF - Dia {dia} deletado ({lines} linhas) para {environ}...")


def insert_many(sql, rows, many=True):

    if not many:
        CURSOR_SQL.fast_executemany = False

    CURSOR_SQL.executemany(sql, rows[:])


def commit():

    CONN_SQL.commit()

def rollback():

    CONN_SQL.rollback()