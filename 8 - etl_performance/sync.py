from datetime import date
from datetime import timedelta
from decimal import Decimal
import time
from utils import write_log
from sqlserver import CURSOR_SQL, delete_day, insert_many, commit, rollback
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

            write_log(f"Offset: {offset}")
            # if offset == 15:
            #     break

            dia = date.today() - timedelta(days=offset)
            CURSOR_SQL.execute("""delete from rby.performance_python_log where day = ?""", (dia,))
            write_log(f"Dados deletados da rby.performance_log para o dia {dia}...")

            inicio = time.time()
            sync_day_aec(dia, CURSOR_PG)
            fim = time.time()

            write_log(f"{int(fim - inicio)} segundos para processar o dia {dia}...")

    except Exception as e:
        write_log(str(e))
    
    finally:
        CURSOR_PG.close()
        CONN_PG.close()
        write_log("Conexão com postgre finalizada com sucesso...")


def sync_day_aec(dia, cursor_pg):

    CURSOR_SQL.execute("""
                            insert into rby.performance_python_log values
                            (?,getdate(),NULL,NULL)
                            """,(dia,))

    write_log(f"Processando o dia {dia}...")

    # cursor_pg.execute(
    #     """
    #     SELECT
    #         data,
    #         chave_externa,
    #         coalesce(chave_externa_supervisor, 0) AS chave_externa_supervisor,
    #         coalesce(chave_externa_coordenador, 0) AS chave_externa_coordenador,
    #         coalesce(chave_externa_gerente_jr, 0) AS chave_externa_gerente_jr,
    #         coalesce(chave_externa_gerente_pl, 0) AS chave_externa_gerente_pl,
    #         coalesce(chave_externa_gerente_sr, 0) AS chave_externa_gerente_sr,
    #         coalesce(chave_externa_superintendente, 0) AS chave_externa_superintendente,
    #         coalesce(chave_externa_diretor_atendimento, 0) AS chave_externa_diretor_atendimento,
    #         coalesce(chave_externa_diretor, 0) AS chave_externa_diretor,
    #         segmento,
    #         id_grupo,
    #         id_indicador,
    #         nome_indicador,
    #         resultado,
    #         resultado_calculado,
    #         percentual_atingimento,
    #         meta,
    #         ganho,
    #         max_ganho,
    #         fator,
    #         fator_2,
    #         fator_3,
    #         fator_4
    #     FROM "views".performance_view
    #     WHERE data=%s
    #     and nome_nivel_hierarquia IS NOT NULL
    #     and segmento IS NOT NULL
    #     and nome_nivel_hierarquia = '1'
    #     """,
    #     (dia,),
    # )

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
        and nome_nivel_hierarquia IS NOT NULL
        and segmento IS NOT NULL
        and nome_nivel_hierarquia = '1'
        """,
        (dia,),
    )

    try:

        delete_day(dia)

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
                write_log(f"Total de {lines} linhas recebidas do postgre até agora...")

        write_log(f"{lines} linhas inseridas para o dia {dia}...")

        CURSOR_SQL.execute(
            """
            SELECT COUNT(*)
            FROM rby.performance_python
            WHERE data = ?
            """,
            (dia,)
        )

        if CURSOR_SQL.fetchone()[0] != lines:

            raise Exception(
                f"Quantidade de linhas inseridas ({lines}) "
                f"diferente da quantidade de linhas na tabela "
                f"({CURSOR_SQL.fetchone()[0]})"
            )
        
        CURSOR_SQL.execute("""
                            update rby.performance_python_log
                            set end_time = getdate(), lines = ?
                            where day = ?
                            """,(lines,dia,))
        write_log(f"Data fim e linhas atualizado na rby.performance_python_log para o dia {dia}...")
        
        commit()

    except:

        rollback()

        raise