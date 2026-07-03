from datetime import date
from datetime import timedelta
from decimal import Decimal
import time

class PerformanceSync:

    @staticmethod
    def normalize(rows):

        result = []

        for row in rows:

            nova = []

            for value in row:

                if isinstance(value, Decimal):

                    nova.append(float(value))

                elif isinstance(value, date):

                    nova.append(value.isoformat())

                else:

                    nova.append(value)

            result.append(tuple(nova))

        return result

    def __init__(self, pg, sql, fetch_size):

        self.pg = pg

        self.sql = sql

        self.fetch_size = fetch_size

    def run(self, days):

        for offset in range(days, 0, -1):

            dia = date.today() - timedelta(days=offset)

            inicio = time.time()
            self.sync_day(dia)
            fim = time.time()

            print(f"{int(fim - inicio)} segundos para processar o dia {dia}...")

    def sync_day(self, dia):

        print(f"processando o dia {dia}...")

        cursor = self.pg.cursor()

        cursor.execute(
            """
            SELECT
                data,
                nome_nivel_hierarquia::int AS nome_nivel_hierarquia,
                chave_externa,
                coalesce(chave_externa_supervisor, 0) AS chave_externa_supervisor,
                coalesce(chave_externa_coordenador, 0) AS chave_externa_coordenador,
                coalesce(chave_externa_gerente_jr, 0) AS chave_externa_gerente_jr,
                coalesce(chave_externa_gerente_pl, 0) AS chave_externa_gerente_pl,
                coalesce(chave_externa_gerente_sr, 0) AS chave_externa_gerente_sr,
                coalesce(chave_externa_superintendente, 0) AS chave_externa_superintendente,
                coalesce(chave_externa_diretor_atendimento, 0) AS chave_externa_diretor_atendimento,
                coalesce(chave_externa_diretor, 0) AS chave_externa_diretor,
                segmento,
                id_grupo,
                id_indicador,
                nome_indicador,
                resultado,
                resultado_calculado,
                percentual_atingimento,
                meta,
                ganho,
                max_ganho,
                fator,
                fator_2,
                fator_3,
                fator_4
            FROM "views".performance_view
            WHERE data=%s
            and nome_nivel_hierarquia IS NOT NULL
            and segmento IS NOT NULL
            """,
            (dia,),
        )

        try:

            self.sql.delete_day(dia)

            INSERT_SQL = """
                INSERT INTO rby.performance_python (
                    data,
                    nome_nivel_hierarquia,
                    chave_externa,
                    chave_externa_supervisor,
                    chave_externa_coordenador,
                    chave_externa_gerente_jr,
                    chave_externa_gerente_pl,
                    chave_externa_gerente_sr,
                    chave_externa_superintendente,
                    chave_externa_diretor_atendimento,
                    chave_externa_diretor,
                    segmento,
                    id_grupo,
                    id_indicador,
                    nome_indicador,
                    resultado,
                    resultado_calculado,
                    percentual_atingimento,
                    meta,
                    ganho,
                    max_ganho,
                    fator,
                    fator_2,
                    fator_3,
                    fator_4
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """

            lines = 0

            while True:

                rows = cursor.fetchmany(self.fetch_size)

                if not rows:
                    break

                rows = PerformanceSync.normalize(rows)

                self.sql.insert_many(INSERT_SQL, rows)

                lines += len(rows)

            print(f"{lines} linhas inseridas para o dia {dia}...")

            self.sql.commit()

            self.sql.cursor.execute(
                """
                SELECT COUNT(*)
                FROM rby.performance_python
                WHERE data = ?
                """,
                (dia,)
            )

            if self.sql.cursor.fetchone()[0] != lines:

                raise Exception(
                    f"Quantidade de linhas inseridas ({lines}) "
                    f"diferente da quantidade de linhas na tabela "
                    f"({self.sql.cursor.fetchone()[0]})"
                )

        except:

            self.sql.rollback()

            raise

        finally:

            cursor.close()