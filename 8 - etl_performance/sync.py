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
    except Exception as e:
        write_log(f"Erro ao criar conexão postgre: {str(e)} - AEC...")
        return

    for offset in range(days, 0, -1):
        dia = None
        try:
            write_log(f"Offset: {offset} - AEC...")

            dia = date.today() - timedelta(days=offset)

            # if offset == 2:
            #     raise Exception("Erro teste aec")
            #     break
            
            CURSOR_SQL.execute("""delete from rby.performance_python_log where day = ? and type = 'AEC'""", (dia,))
            write_log(f"Dados deletados da rby.performance_python_log para o dia {dia} - AEC...")

            inicio = time.time()
            sync_day_aec(dia, CURSOR_PG)
            fim = time.time()

            write_log(f"{int(fim - inicio)} segundos para processar o dia {dia} - AEC...")
        except Exception as e:
            write_log(f"Erro ({e}) ao processar o dia {dia} - AEC...")
            CURSOR_SQL.execute("""
            UPDATE dbo.LogReplicacaoRby
            SET DataFim = GETDATE(),
                Erro = ?
            WHERE Data = ?
            AND Objeto = 'rby.performance'
            AND Ambiente = 'AEC'
            and DataInicio = (SELECT max(DataInicio) from LogReplicacaoRby where Data = ? AND Objeto = 'rby.performance' AND Ambiente = 'AEC')
            """, (str(e), dia, dia))
            continue

    try:
        CURSOR_PG.close()
        CONN_PG.close()
        write_log("Conexão com postgre finalizada com sucesso - AEC...")
    except:
        pass


def sync_day_aec(dia, cursor_pg):

    CURSOR_SQL.execute(f"""INSERT INTO dbo.LogReplicacaoRby (Data, Objeto, DataInicio, DataFim, Linhas, Erro, Ambiente) VALUES ('{dia}', 'rby.performance', GETDATE(), NULL, NULL, NULL, 'AEC');""")

    CURSOR_SQL.execute("""
                            insert into rby.performance_python_log values
                            (?,getdate(),NULL,NULL,'AEC')
                            """,(dia,))

    write_log(f"Processando o dia {dia} - AEC...")

    # if dia == date.today() - timedelta(days=1):
    #     raise Exception("Erro teste aec")

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
            UPPER(segmento) as segmento,
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
                write_log(f"Total de {lines} linhas recebidas do postgre até agora - AEC...")

        write_log(f"{lines} linhas inseridas para o dia {dia} - AEC...")

        CURSOR_SQL.execute(
            """
            SELECT COUNT(*)
            FROM rby.performance
            WHERE data = ?
            and segmento not like 'premium - %santander%'
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
        UPDATE dbo.LogReplicacaoRby
        SET DataFim = GETDATE(),
        Linhas = ?
        WHERE Data = ?
        AND Objeto = 'rby.performance'
        AND Ambiente = 'AEC'
        and DataInicio = (SELECT max(DataInicio) from LogReplicacaoRby where Data = ? AND Objeto = 'rby.performance' AND Ambiente = 'AEC')
        """, (lines, dia, dia))
        
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
    except Exception as e:
        write_log(F"Erro ao criar conexão postgre: {str(e)} - SANTANDER...")
        return

    for offset in range(days, 0, -1):
        try:
            write_log(f"Offset: {offset} - SANTANDER...")
            
            dia = date.today() - timedelta(days=offset)

            # if offset == 2:
            #     raise Exception("Erro teste santander")
            #     break
            
            CURSOR_SQL.execute("""delete from rby.performance_python_log where day = ? and type = 'SANTANDER'""", (dia,))
            write_log(f"Dados deletados da rby.performance_python_log para o dia {dia} - SANTANDER...")

            inicio = time.time()
            sync_day_santander(dia, CURSOR_PG)
            fim = time.time()

            write_log(f"{int(fim - inicio)} segundos para processar o dia {dia} - SANTANDER...")
        except Exception as e:
            write_log(f"Erro ({e}) ao processar o dia {dia} - SANTANDER...")
            CURSOR_SQL.execute("""
            UPDATE dbo.LogReplicacaoRby
            SET DataFim = GETDATE(),
                Erro = ?
            WHERE Data = ?
            AND Objeto = 'rby.performance'
            AND Ambiente = 'SANTANDER'
            and DataInicio = (SELECT max(DataInicio) from LogReplicacaoRby where Data = ? AND Objeto = 'rby.performance' AND Ambiente = 'SANTANDER')
            """, (str(e), dia, dia))
            continue

    try:
        CURSOR_PG.close()
        CONN_PG.close()
        write_log("Conexão com postgre finalizada com sucesso - SANTANDER...")
    except:
        pass


def sync_day_santander(dia, cursor_pg):

    CURSOR_SQL.execute(f"""INSERT INTO dbo.LogReplicacaoRby (Data, Objeto, DataInicio, DataFim, Linhas, Erro, Ambiente) VALUES ('{dia}', 'rby.performance', GETDATE(), NULL, NULL, NULL, 'SANTANDER');""")

    CURSOR_SQL.execute("""
                            insert into rby.performance_python_log values
                            (?,getdate(),NULL,NULL,'SANTANDER')
                            """,(dia,))

    write_log(f"Processando o dia {dia} - SANTANDER...")

    # if dia == date.today() - timedelta(days=1):
    #     raise Exception("Erro teste santander")

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
            UPPER(segmento) as segmento,
            (CASE WHEN id_indicador = -5 THEN 34 WHEN id_indicador = -1 THEN 86 ELSE id_indicador END)::int as id_indicador,
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
                write_log(f"Total de {lines} linhas recebidas do postgre até agora - SANTANDER...")

        write_log(f"{lines} linhas inseridas para o dia {dia} - SANTANDER...")

        CURSOR_SQL.execute(
            """
            SELECT COUNT(*)
            FROM rby.performance
            WHERE data = ?
            AND segmento like 'premium - %santander%'
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
        UPDATE dbo.LogReplicacaoRby
        SET DataFim = GETDATE(),
        Linhas = ?
        WHERE Data = ?
        AND Objeto = 'rby.performance'
        AND Ambiente = 'SANTANDER'
        and DataInicio = (SELECT max(DataInicio) from LogReplicacaoRby where Data = ? AND Objeto = 'rby.performance' AND Ambiente = 'SANTANDER')
        """, (lines, dia, dia))
        
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