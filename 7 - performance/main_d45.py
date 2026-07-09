import config

from tunnel import Tunnel
from postgres import Postgres
from sqlserver import SqlServer
from sync import PerformanceSync
from utils import write_log

def main():

    try:
        write_log("Inciando a ETL D45")

        tunnel = Tunnel()

        tunnel.start()

        write_log("Tunnel aberto, prosseguindo com a D45...")

        pg = Postgres(config)

        sql = SqlServer(config)

        sync = PerformanceSync(
            pg,
            sql,
            config.FETCH_SIZE
        )

        sql.cursor.execute("""insert into dbo.Historicos_Procedures values('ETL_Performance_Python_D45', GETDATE(), null, 'Performance Python', 'D45')""")

        write_log("D45 entrando em etapa de execução...")

        sync.run(46)

        sql.cursor.execute("""update dbo.Historicos_Procedures SET Data_Fim = GETDATE() WHERE Nome = 'ETL_Performance_Python_D45' and cast(data_inicio as date) = cast(getdate() as date) and data_inicio = (select max(data_inicio) from dbo.historicos_Procedures (nolock) where nome = 'ETL_Performance_Python_D45')""")
        sql.commit()
    except Exception as e:
        write_log(f"Erro na ETL: {str(e)}")
    finally:

        try:
            pg.conn.close()
            write_log("Conexão com postgre finalizada com sucesso...")
        except:
            pass

        try:
            sql.conn.close()
            write_log("Conexão com sqlserver finalizada com sucesso...")
        except:
            pass

        tunnel.stop()
        write_log("Tunnel finalizado com sucesso...")

        write_log("ETL D15 finalizada com sucesso.")


if __name__ == "__main__":

    main()