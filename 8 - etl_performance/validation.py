from postgre import create_connection
import os
from utils import write_log
from datetime import timedelta
from datetime import date
from sqlserver import CONN_SQL, CURSOR_SQL, commit 

def validation_aec():
    try:
        #CONN_PG = create_connection(os.getenv("HOST_RETORNO"), os.getenv("PORTA_RETORNO"), os.getenv("POSTGRES_DATABASE"), os.getenv("USER_RETORNO"), os.getenv("PASSWORD_RETORNO"))
        CONN_PG = create_connection(os.getenv("LOCAL_HOST"),os.getenv("LOCAL_PORT"),os.getenv("POSTGRES_DATABASE"),os.getenv("POSTGRES_USER"),os.getenv("POSTGRES_PASSWORD"))
        CURSOR_PG = CONN_PG.cursor()
    except Exception as e:
        write_log(f"Erro ao criar conexão postgre: {str(e)} - AEC...")
        return

    QUERY_AEC = """
    select
        data,
        count(1) as linhas
    FROM "views".performance_view
    where data = %s
    and id_indicador = 34
    and segmento not ilike %s
    group by data, id_indicador
    """

    write_log("Iniciando Validation AeC -60...")

    try:

        for offset in range(60, 0, -1):
            dia = None
            try:
                write_log(f"Offset Validation: {offset} - AEC...")

                dia = date.today() - timedelta(days=offset)

                CURSOR_PG.execute(QUERY_AEC, (dia,'premium - %santander%',))

                result = CURSOR_PG.fetchone()

                if result:
                    data, linhas = result
                else:
                    continue

                CURSOR_SQL.execute("insert into rby.performance_validation values (?, ?, ?)", (data, linhas, 'GERAL'))

            except Exception as e:
                write_log(f"Erro ({e}) ao processar o dia {dia} - AEC...")

    finally:
        commit()
        CURSOR_PG.close()
        CONN_PG.close()

        

def validation_santander():
    try:
        CONN_PG = create_connection(os.getenv("HOST_RETORNO_SANTANDER"), os.getenv("PORTA_RETORNO_SANTANDER"), os.getenv("POSTGRES_DATABASE"), os.getenv("USER_RETORNO_SANTANDER"), os.getenv("PASSWORD_RETORNO_SANTANDER"))
        CURSOR_PG = CONN_PG.cursor()
    except Exception as e:
        write_log(f"Erro ao criar conexão postgre: {str(e)} - Santander...")
        return

    QUERY_SANTANDER = """
    select
        data,
        count(1) as linhas
    FROM public.performance
    where data = %s
    and id_indicador = -5
    and segmento ilike %s
    group by data, id_indicador
    """

    write_log("Iniciando Validation Santander -60...")

    try: 

        for offset in range(60, 0, -1):
            dia = None
            try:
                write_log(f"Offset Validation: {offset} - Santander...")

                dia = date.today() - timedelta(days=offset)

                CURSOR_PG.execute(QUERY_SANTANDER, (dia,'premium - %santander%',))

                result = CURSOR_PG.fetchone()

                if result:
                    data, linhas = result
                else:
                    continue

                CURSOR_SQL.execute("insert into rby.performance_validation values (?, ?, ?)", (data, linhas, 'SANTANDER'))

            except Exception as e:
                write_log(f"Erro ({e}) ao processar o dia {dia} - Santander...")

    finally:
        commit()
        CURSOR_PG.close()
        CONN_PG.close()

def exec_validation():
    try:
        CURSOR_SQL.execute("""insert into dbo.Historicos_Procedures values('Validation_Performance_Python', GETDATE(), null, 'Validation Performance', 'D60')""")
        CURSOR_SQL.execute("truncate table rby.performance_validation")
        commit()
        try:
            validation_aec()
        except Exception as e:
            write_log(f"Erro na validation AeC: {str(e)}")
        try:
            validation_santander()
        except Exception as e:
            write_log(f"Erro na validation Santander: {str(e)}")
        write_log("Validation finalizada.")
        CURSOR_SQL.execute("""update dbo.Historicos_Procedures SET Data_Fim = GETDATE() WHERE Nome = 'Validation_Performance_Python' and cast(data_inicio as date) = cast(getdate() as date) and data_inicio = (select max(data_inicio) from dbo.historicos_Procedures (nolock) where nome = 'Validation_Performance_Python')""")
        commit()
    finally:
        CURSOR_SQL.close()
        CONN_SQL.close()

if __name__ == "__main__":
    exec_validation()