import pyodbc
from datetime import datetime, timedelta
import os
import sys

d = 91
connection_string1 = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=primno;DATABASE=db_qualidade;Trusted_Connection=yes;"
connection_string2 = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=primno4;DATABASE=Robbyson;Trusted_Connection=yes;"
LOG_FILE = f"C:\\Users\\danilo.cabral\\Desktop\\Logs\\replica_cyf_d{d}_{datetime.now().date()}.log"

def log(msg):
    timestamp = f"[{datetime.now()}] {msg}"

    # console
    print(timestamp)

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    # arquivo
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(timestamp + "\n")


def get_connection(conn_str):
    return pyodbc.connect(conn_str,  timeout=600)


def get_data(data_fim):
    with get_connection(connection_string1) as conn:
        cursor = conn.cursor()
        log("Consultando dados no banco da qualidade...")

        query = """
        SET NOCOUNT ON;

        DECLARE @data_fim DATE = ?;

        CREATE TABLE #monitorias1(
            num_monitoria bigint,
            data_monitoria date,
            matricula int,
            matricula_supervisor int,
            data_feedback date,
            perfil_monitoria nvarchar(255),
            pontos_realizados tinyint,
            campo_feedback tinyint
        );

        WHILE @data_fim <= GETDATE()
        BEGIN
            INSERT INTO #monitorias1
            SELECT DISTINCT
                num_monitoria,
                data_monitoria,
                matricula,
                CASE 
                    WHEN perfil_monitoria LIKE '%operaç%' THEN matricula_monitor
                    ELSE matricula_supervisor
                END,
                data_feedback,
                perfil_monitoria,
                pontos_realizados,
                LEN(CAST(comentario_feedback AS VARCHAR(1)))
            FROM db_qualidade.dbo.vw_ccm_aec_monitoria_cyf (NOLOCK)
            WHERE
                (data_monitoria >= @data_fim AND data_monitoria < DATEADD(DAY,1,@data_fim))
                AND valido = 1
                AND (perfil_monitoria LIKE '%operaç%' OR perfil_monitoria LIKE '%monitor de qualidade%')
                AND LEN(matricula) BETWEEN 4 AND 6;

            SET @data_fim = DATEADD(DAY, 1, @data_fim);
        END;

        SELECT 
            data_monitoria,
            matricula,
            matricula_supervisor,
            data_feedback,
            num_monitoria,
            perfil_monitoria,
            campo_feedback,
            pontos_realizados
        FROM (
            SELECT *,
                ROW_NUMBER() OVER (PARTITION BY num_monitoria ORDER BY data_monitoria DESC) AS valida
            FROM #monitorias1
        ) t
        WHERE valida = 1;

        DROP TABLE #monitorias1;
        """

        try:
            cursor.execute(query, data_fim)
        except pyodbc.OperationalError as e:
            log("Consulta cancelada por timeout (10 min).")
            return []

        if cursor.description is None:
            log("Nenhum resultado retornado do banco da qualidade.")
            return []

        rows = cursor.fetchall()
        log(f"{len(rows)} linhas retornadas do banco da qualidade.")
        return rows


def bulk_insert(cursor, rows, batch_size=10000):
    if not rows:
        log("Nenhum dado para inserir.")
        return

    insert_query = """
    INSERT INTO [Robbyson].[dbo].[monitoria_cyf] with (tablockx) (
        data_monitoria,
        matricula,
        matricula_supervisor,
        data_feedback,
        num_monitoria,
        perfil_monitoria,
        campo_feedback,
        pontos_realizados
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    total = len(rows)
    log(f"Iniciando insert de {total} linhas na tabela monitoria_cyf...")
    cursor.fast_executemany = True

    for i in range(0, total, batch_size):
        batch = rows[i:i + batch_size]

        try:
            cursor.executemany(insert_query, batch)

            log(f"Lote inserido: {i + len(batch)}/{total}")

        except Exception as e:
            log(f"Erro no lote {i}: {e}")
            raise  

    log("Insert finalizado.")


def main():
    log(f"Iniciando d{d}...")

    try:
        with get_connection(connection_string2) as conn2:
            conn2.autocommit = False 
            cursor2 = conn2.cursor()

            cursor2.execute(f"""
                INSERT INTO dbo.historicos_Procedures (Nome, Data_Inicio, Tabela, Ordem)
                VALUES ('Replica_CYF_Python', GETDATE(), 'monitoria_cyf','D{d}')
            """)
            conn2.commit()

            with get_connection(connection_string1) as conn1:
                log("Transação iniciada...")
                cursor1 = conn1.cursor()
                cursor1.execute("""
                    SELECT MAX(data_monitoria)
                    FROM DB_QUALIDADE.dbo.VW_CCM_AEC_MONITORIA_CYF (nolock)
                """)
                data_fim = cursor1.fetchone()[0]

                if data_fim is None:
                    log("Data máxima não encontrada. Abortando.")
                    return

                data_fim = data_fim - timedelta(days=d)
                log(f"Data corte obtida: {data_fim}")

            max_retries = 5
            for attempt in range(max_retries):
                rows = get_data(data_fim)

                if rows and len(rows) > 0:
                    break

                log(f"Tentativa {attempt + 1} falhou, tentando novamente...")
            else:
                log("Falha após múltiplas tentativas. Abortando processo.")
                return

            try:
                all_rows_deleted = 0

                while True:
                    cursor2.execute("""
                        DELETE TOP (5000)
                        FROM [Robbyson].[dbo].[monitoria_cyf] with (tablockx)
                        WHERE data_monitoria >= ?
                    """, data_fim)

                    rows_deleted = cursor2.rowcount
                    all_rows_deleted += rows_deleted

                    if rows_deleted == 0:
                        break

                log(f"{all_rows_deleted} deletadas da tabela monitoria_cyf...")

                bulk_insert(cursor2, rows)

                conn2.commit() 
                log("Transação concluída com sucesso.")

            except Exception as e:
                conn2.rollback()
                log(f"Erro na transação, rollback executado: {e}")
                return

    except Exception as e:
        log(f"Erro geral: {e}")

    finally:
        try:
            with get_connection(connection_string2) as conn2:
                cursor2 = conn2.cursor()
                cursor2.execute("""
                    UPDATE dbo.historicos_Procedures
                    SET Data_fim = GETDATE()
                    WHERE nome = 'Replica_CYF_Python'
                      AND data_fim IS NULL
                      AND data_inicio = (
                          SELECT MAX(data_inicio)
                          FROM dbo.historicos_Procedures
                          WHERE nome = 'Replica_CYF_Python'
                      )
                """)
                conn2.commit()

                log("Histórico atualizado.")
        except Exception as e:
            log(f"Erro ao atualizar histórico: {e}")

    log("Finalizado.")


if __name__ == "__main__":
    main()