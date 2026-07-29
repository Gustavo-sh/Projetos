from tunnel import start_tunnel, kill_existing_tunnel
from utils import write_log
from sqlserver import CONN_SQL, CURSOR_SQL, commit
from sync import run_aec, run_santander
from datetime import datetime, time

def main():

    try:
        REBUILDED = False
        write_log("Inciando a ETL D45")

        #start_tunnel()

        CURSOR_SQL.execute("""insert into dbo.Historicos_Procedures values('ETL_Performance_Python_D45', GETDATE(), null, 'Performance Python', 'D45')""")
        write_log("Iniciando disable do indice...")
        CURSOR_SQL.execute("""alter index NonClusteredColumnStore on rby.performance_python DISABLE""")
        write_log("Disable do indice finalizado...")

        write_log("D45 entrando em etapa de execução...")

        run_aec(46)
        run_santander(46)

        write_log("Iniciando rebuild o indice...")
        CURSOR_SQL.execute("""alter index NonClusteredColumnStore on rby.performance_python rebuild""")
        write_log("Rebuild o indice finalizado...")
        REBUILDED = True

        CURSOR_SQL.execute("""update dbo.Historicos_Procedures SET Data_Fim = GETDATE() WHERE Nome = 'ETL_Performance_Python_D45' and cast(data_inicio as date) = cast(getdate() as date) and data_inicio = (select max(data_inicio) from dbo.historicos_Procedures (nolock) where nome = 'ETL_Performance_Python_D45')""")
        commit()

    except Exception as e:
        write_log(f"Erro na ETL: {str(e)}")

    finally:

        try:
            if not REBUILDED:
                write_log("Iniciando rebuild o indice após exception...")
                CURSOR_SQL.execute("""alter index NonClusteredColumnStore on rby.performance_python rebuild""")
                write_log("Rebuild o indice finalizado...")
            CURSOR_SQL.close()
            CONN_SQL.close()
            write_log("Conexão com sqlserver finalizada com sucesso...")
        except:
            pass

        # kill_existing_tunnel()
        # write_log("Tunnel finalizado com sucesso...")
        write_log("ETL D45 finalizada com sucesso.")


if __name__ == "__main__":

    main()