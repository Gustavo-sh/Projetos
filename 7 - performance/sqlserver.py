import pyodbc
from utils import write_log

class SqlServer:

    def __init__(self, config):

        self.conn = pyodbc.connect(config.SQLSERVER_CONNECTION)

        self.conn.autocommit = False

        self.cursor = self.conn.cursor()
        self.cursor.fast_executemany = True

    def delete_day(self, dia):

        write_log(f"Deletando {dia}...")

        while True:

            self.cursor.execute(
                """
                DELETE TOP (10000)
                FROM rby.performance_python
                WHERE data = ?
                """,
                dia
            )

            if self.cursor.rowcount == 0:
                break

        write_log(f"Dia {dia} deletado...")

    def insert_many(self, sql, rows):

        self.cursor.executemany(sql, rows[:])


    def commit(self):

        self.conn.commit()

    def rollback(self):

        self.conn.rollback()