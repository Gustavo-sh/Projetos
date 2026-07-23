from datetime import date
from datetime import timedelta
from decimal import Decimal
import time
from utils import write_log
from sqlserver import CURSOR_SQL, delete_day_aec, delete_day_santander, insert_many, commit, rollback
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

def run_aec(days):

    try:

        CONN_PG = create_connection(os.getenv("HOST_RETORNO"), os.getenv("PORTA_RETORNO"), os.getenv("POSTGRES_DATABASE"), os.getenv("USER_RETORNO"), os.getenv("PASSWORD_RETORNO"))
        #CONN_PG = create_connection(os.getenv("LOCAL_HOST"), os.getenv("LOCAL_PORT"), os.getenv("POSTGRES_DATABASE"), os.getenv("POSTGRES_USER"), os.getenv("POSTGRES_PASSWORD"))
        CURSOR_PG = CONN_PG.cursor()

        for offset in range(days, 0, -1):

            write_log(f"Offset: {offset} - AEC...")
            # if offset == 15:
            #     break

            dia = date.today() - timedelta(days=offset)
            CURSOR_SQL.execute("""delete from rby.performance_python_log where day = ? and type = 'AEC'""", (dia,))
            write_log(f"Dados deletados da rby.performance_python_log para o dia {dia} - AEC...")

            inicio = time.time()
            sync_day_aec(dia, CURSOR_PG)
            fim = time.time()

            write_log(f"{int(fim - inicio)} segundos para processar o dia {dia} - AEC...")

    except Exception as e:
        write_log(str(e))
    
    finally:
        CURSOR_PG.close()
        CONN_PG.close()
        write_log("Conexão com postgre finalizada com sucesso - AEC...")


def sync_day_aec(dia, cursor_pg):

    CURSOR_SQL.execute("""
                            insert into rby.performance_python_log values
                            (?,getdate(),NULL,NULL,'AEC')
                            """,(dia,))

    write_log(f"Processando o dia {dia} - AEC...")

    cursor_pg.execute(
        """
        SELECT
            data,
            chave_externa,
            COALESCE(chave_externa_supervisor, 0) AS chave_externa_supervisor,
            COALESCE(chave_externa_coordenador, 0) AS chave_externa_coordenador,
            COALESCE(chave_externa_superintendente, 0) AS chave_externa_gerente_executivo,
            COALESCE(chave_externa_diretor_de_atendimento, 0) AS chave_externa_diretor_de_atendimento,
            --COALESCE(chave_externa_diretor_atendimento, 0) AS chave_externa_diretor_de_atendimento,
            COALESCE(chave_externa_diretor, 0) AS chave_externa_diretor,
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
            COALESCE(chave_externa_gerente_jr, 0) AS chave_externa_gerente_jr,
            COALESCE(chave_externa_gerente_pl, 0) AS chave_externa_gerente_pl,
            COALESCE(chave_externa_gerente_sr, 0) AS chave_externa_gerente_sr,
            fator_2,
            fator_3,
            fator_4
        FROM public.performance_view
        --FROM "views".performance_view
        WHERE data=%s
        and id_indicador <> 86
        and nome_nivel_hierarquia = '1'
        and segmento not ilike %s
        """,
        (dia,"premium - %santander%"),
    )

    try:

        delete_day_aec(dia)

        INSERT_SQL = """
            INSERT INTO rby.performance_python (
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
                write_log(f"Total de {lines} linhas recebidas do postgre até agora - AEC...")

        write_log(f"{lines} linhas inseridas para o dia {dia} - AEC...")

        CURSOR_SQL.execute(
            """
            SELECT COUNT(*)
            FROM rby.performance_python
            WHERE data = ?
            and segmento not like '%santander%'
            """,
            (dia,)
        )

        count_rows = CURSOR_SQL.fetchone()[0]

        if count_rows != lines:

            raise Exception(
                f"Quantidade de linhas inseridas ({lines}) "
                f"diferente da quantidade de linhas na tabela "
                f"({count_rows})"
            )
        
        CURSOR_SQL.execute("""
                            update rby.performance_python_log
                            set end_time = getdate(), lines = ?
                            where day = ? and type = 'AEC'
                            """,(lines,dia,))
        write_log(f"Data fim e linhas atualizado na rby.performance_python_log para o dia {dia} - AEC...")
        
        commit()

    except:

        rollback()
        write_log("Rollback sql realizado com sucesso - AEC...")

        raise






def run_santander(days):

    try:

        CONN_PG = create_connection(os.getenv("HOST_RETORNO_SANTANDER"), os.getenv("PORTA_RETORNO_SANTANDER"), os.getenv("POSTGRES_DATABASE"), os.getenv("USER_RETORNO_SANTANDER"), os.getenv("PASSWORD_RETORNO_SANTANDER"))
        CURSOR_PG = CONN_PG.cursor()

        for offset in range(days, 0, -1):

            write_log(f"Offset: {offset} - SANTANDER...")
            # if offset == 15:
            #     break

            dia = date.today() - timedelta(days=offset)
            CURSOR_SQL.execute("""delete from rby.performance_python_log where day = ? and type = 'SANTANDER'""", (dia,))
            write_log(f"Dados deletados da rby.performance_python_log para o dia {dia} - SANTANDER...")

            inicio = time.time()
            sync_day_santander(dia, CURSOR_PG)
            fim = time.time()

            write_log(f"{int(fim - inicio)} segundos para processar o dia {dia} - SANTANDER...")

    except Exception as e:
        write_log(str(e))
    
    finally:
        CURSOR_PG.close()
        CONN_PG.close()
        write_log("Conexão com postgre finalizada com sucesso - SANTANDER...")


def sync_day_santander(dia, cursor_pg):

    CURSOR_SQL.execute("""
                            insert into rby.performance_python_log values
                            (?,getdate(),NULL,NULL,'SANTANDER')
                            """,(dia,))

    write_log(f"Processando o dia {dia} - SANTANDER...")

    cursor_pg.execute(
        """
        SELECT
            data,
            chave_externa::int,
            COALESCE(REPLACE(chave_externa_supervisor, 'SEM INFORMAÇÃO', '0'), '0')::int AS chave_externa_supervisor,
            COALESCE(REPLACE(chave_externa_coordenador, 'SEM INFORMAÇÃO', '0'), '0')::int AS chave_externa_coordenador,
            COALESCE(REPLACE(chave_externa_superintendente, 'SEM INFORMAÇÃO', '0'), '0')::int AS chave_externa_gerente_executivo,
            COALESCE(REPLACE(chave_externa_diretor_de_atendimento, 'SEM INFORMAÇÃO', '0'), '0')::int AS chave_externa_diretor_de_atendimento,
            COALESCE(REPLACE(chave_externa_diretor, 'SEM INFORMAÇÃO', '0'), '0')::int AS chave_externa_diretor,
            segmento,
            id_indicador::int,
            nome_indicador,
            REPLACE(resultado, ',', '.')::float as resultado,
            REPLACE(fator, ',', '.')::float as fator,
            REPLACE(resultado_calculado, ',', '.')::float as resultado_calculado,
            REPLACE(percentual_atingimento, ',', '.')::float as percentual_atingimento,
            REPLACE(meta, ',', '.')::float as meta,
            ganho::int,
            max_ganho::int,
            id_grupo::int,
            COALESCE(REPLACE(chave_externa_gerente_jr, 'SEM INFORMAÇÃO', '0'), '0')::int AS chave_externa_gerente_jr,
            COALESCE(REPLACE(chave_externa_gerente_pl, 'SEM INFORMAÇÃO', '0'), '0')::int AS chave_externa_gerente_pl,
            COALESCE(REPLACE(chave_externa_gerente_sr, 'SEM INFORMAÇÃO', '0'), '0')::int AS chave_externa_gerente_sr,
            REPLACE(fator_2, ',', '.')::float as fator_2,
            REPLACE(fator_3, ',', '.')::float as fator_3,
            REPLACE(fator_4, ',', '.')::float as fator_4
        FROM public.performance
        WHERE data=%s
        and id_indicador <> -1
        and nome_nivel_hierarquia = 'OPERACIONAL'
        and segmento ilike %s
        """,
        (dia,"premium - %santander%"),
    )

    try:

        delete_day_santander(dia)

        INSERT_SQL = """
            INSERT INTO rby.performance_python (
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
                write_log(f"Total de {lines} linhas recebidas do postgre até agora - SANTANDER...")

        write_log(f"{lines} linhas inseridas para o dia {dia} - SANTANDER...")

        CURSOR_SQL.execute(
            """
            SELECT COUNT(*)
            FROM rby.performance_python
            WHERE data = ?
            AND segmento like '%santander%'
            """,
            (dia,)
        )

        count_rows = CURSOR_SQL.fetchone()[0]

        if count_rows != lines:

            raise Exception(
                f"Quantidade de linhas inseridas ({lines}) "
                f"diferente da quantidade de linhas na tabela "
                f"({count_rows})"
            )
        
        CURSOR_SQL.execute("""
                            update rby.performance_python_log
                            set end_time = getdate(), lines = ?
                            where day = ? and type = 'SANTANDER'
                            """,(lines,dia,))
        write_log(f"Data fim e linhas atualizado na rby.performance_python_log para o dia {dia} - SANTANDER...")
        
        commit()

    except:

        rollback()
        write_log("Rollback sql realizado com sucesso - SANTANDER...")

        raise