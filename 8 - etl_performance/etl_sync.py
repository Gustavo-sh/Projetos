from datetime import date
from datetime import timedelta
from decimal import Decimal
import time
from utils import write_log
from sqlserver import CURSOR_SQL, insert_many, commit, rollback, delete_day_indicators_performance
from querys_pg import VIEW_AEC, TABELA_AEC, VIEW_SANTANDER, get_query_pg
from postgre import create_connection
from dotenv import load_dotenv
import os

load_dotenv(r"C:\Users\e.gustavo.santos.GRUPO_A&C\Documents\Projetos\8 - etl_performance\.env")

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

def run_specific_range_performance(range_start, range_end, indicators_pg, indicators_sql, host, port, database, username, password, environ):
    try:
        CONN_PG = create_connection(host, port, database, username, password)
        CURSOR_PG = CONN_PG.cursor()
    except Exception as e:
        write_log(f"Erro ao criar conexão postgre: {str(e)} - {environ}...")
        return

    for offset in range(range_start, 0, -1):
        dia = None
        try:

            dia = date.today() - timedelta(days=offset)

            if offset == range_end-1:
                break

            write_log(f"Offset: {offset} - {environ}...")
            
            inicio = time.time()
            sync_specific_day_performance(dia, CURSOR_PG, indicators_pg, indicators_sql, environ)
            fim = time.time()

            write_log(f"{int(fim - inicio)} segundos para processar o dia {dia} - {environ} ids {indicators_sql or ""}...")
        except Exception as e:
            write_log(f"Erro ({e}) ao processar o dia {dia} - {environ}...")
            CURSOR_SQL.execute("""
            UPDATE dbo.LogReplicacaoRby
            SET DataFim = GETDATE(),
                Erro = ?
            WHERE Data = ?
            AND Objeto = 'rby.performance'
            AND Ambiente = ?
            and DataInicio = (SELECT max(DataInicio) from LogReplicacaoRby where Data = ? AND Objeto = 'rby.performance' AND Ambiente = ?)
            """, (str(e), dia, environ, dia, environ))
            continue

    try:
        CURSOR_PG.close()
        CONN_PG.close()
        write_log(f"Conexão com postgre finalizada com sucesso - {environ}...")
    except:
        pass

def sync_specific_day_performance(dia, cursor_pg, indicators_pg, indicators_sql, environ):

    CURSOR_SQL.execute(f"""INSERT INTO dbo.LogReplicacaoRby (Data, Objeto, DataInicio, DataFim, Linhas, Erro, Ambiente) VALUES (?, 'rby.performance', GETDATE(), NULL, NULL, NULL, ?);""", (dia, environ))

    write_log(f"Processando o dia {dia} - {environ}...")
    
    placeholders_sql = ", ".join("?" for _ in indicators_sql) if indicators_sql else ""

    try:
        if environ == "AEC":
            query = get_query_pg(VIEW_AEC, indicators_pg)
        elif environ == "SANTANDER":
            query = get_query_pg(VIEW_SANTANDER, indicators_pg)
        else:
            raise ValueError(f"Ambiente inválido: {environ}")

        if indicators_pg:
            cursor_pg.execute(
                query,
                (dia, "premium - %santander%", *indicators_pg)
            )
        else:
            cursor_pg.execute(
                query,
                (dia, "premium - %santander%")
            )

        delete_day_indicators_performance(dia, environ, indicators_sql)

        INSERT_SQL = """
            INSERT INTO rby.performance (
            data,
            chave_externa,
            chave_externa_supervisor,
            chave_externa_coordenador,
            chave_externa_gerente_executivo,
            chave_externa_diretor_de_atendimento,
            chave_externa_diretor,
            segmento,
            id_indicador,
            nome_indicador,
            resultado,
            fator,
            resultado_calculado,
            percentual_atingimento,
            meta,
            ganho,
            max_ganho,
            id_grupo,
            chave_externa_gerente_jr,
            chave_externa_gerente_pl,
            chave_externa_gerente_sr,
            fator_2,
            fator_3,
            fator_4
        )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """

        lines = 0

        while True:

            rows = cursor_pg.fetchmany(int(os.getenv("FETCH_SIZE")))

            if not rows:
                break

            rows = normalize(rows)

            insert_many(INSERT_SQL, rows)

            lines += len(rows)

            if lines % 100000 == 0:
                write_log(f"Total de {lines} linhas recebidas do postgre até agora - {environ}...")

        write_log(f"{lines} linhas inseridas para o dia {dia} - {environ}...")

        if environ == "SANTANDER":
            segmento_filter = "segmento LIKE 'premium - %santander%'"
        elif environ == "AEC":
            segmento_filter = "segmento NOT LIKE 'premium - %santander%'"
        else:
            raise ValueError(f"Ambiente inválido: {environ}")

        indicador_filter = (
            f"AND id_indicador IN ({placeholders_sql})"
            if indicators_sql
            else ""
        )

        params = (dia, *indicators_sql) if indicators_sql else (dia,)
        sql_valid = f"""
                    SELECT COUNT(*)
                    FROM rby.performance
                    WHERE data = ?
                    AND {segmento_filter}
                    {indicador_filter}
                    """

        CURSOR_SQL.execute(
            sql_valid,
            params
        )

        count_rows = CURSOR_SQL.fetchone()[0]

        if count_rows != lines:

            raise Exception(
                f"Quantidade de linhas inseridas ({lines}) "
                f"diferente da quantidade de linhas na tabela "
                f"({count_rows})"
            )

        CURSOR_SQL.execute("""
        UPDATE dbo.LogReplicacaoRby
        SET DataFim = GETDATE(),
        Linhas = ?
        WHERE Data = ?
        AND Objeto = 'rby.performance'
        AND Ambiente = ?
        and DataInicio = (SELECT max(DataInicio) from LogReplicacaoRby where Data = ? AND Objeto = 'rby.performance' AND Ambiente = ?)
        """, (lines, dia, environ, dia, environ))
                
        commit()

    except:

        rollback()
        write_log(f"Rollback sql realizado com sucesso - {environ}...")

        raise