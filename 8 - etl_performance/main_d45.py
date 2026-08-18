from tunnel import start_tunnel, kill_existing_tunnel
from utils import write_log
from sqlserver import CONN_SQL, CURSOR_SQL, commit
from etl_sync import run_specific_range
import os

def main():

    PROCEDURES = [
        "dbo.sp_Ins_matriz",
        "dbo.SPR_Voucher_Quantidade",
        "dbo.sp_ins_bussola_d45",
        "dbo.sp_Ins_bussola_semanal_D45",
        "dbo.SP_Ins_Resultado_Consolidado_D45",
        "dbo.sp_ins_rel11",
        "dbo.sp_ins_rel2",
        "dbo.sp_ins_rel31",
        "dbo.Sp_Ins_ReincidenciaDeGrupos",
        "dbo.sp_ins_indice_evolucao",
        "rlt.Sp_Ins_CheckPoint_D45",
        "dbo.SP_Ins_Gamification_D45",
        "dbo.sp_ins_gamificationperformance_D45",
        "dbo.sp_ins_grupos_rh_processo",
        "dbo.sp_Ins_RV",
        "rby.sp_Ins_PerformanceFoto"
    ]

    try:
        write_log("Inciando a ETL D45")

        #start_tunnel()

        CURSOR_SQL.execute("""insert into dbo.Historicos_Procedures values('ETL_Performance_Python_D45', GETDATE(), null, 'Performance', 'D45')""")

        write_log("D45 entrando em etapa de execução...")

        run_specific_range(46,                                       # range start
                            0,                                       # range end
                            None,                           # indicadores para consultar postgre
                            None,                           # indicadores para consultar e deletar sql
                            os.getenv("HOST_RETORNO"),
                            os.getenv("PORTA_RETORNO"), 
                            os.getenv("POSTGRES_DATABASE"), 
                            os.getenv("USER_RETORNO"), 
                            os.getenv("PASSWORD_RETORNO"), 
                            "AEC"                                      # ambiente ("AEC" OU "SANTANDER")
                            )
        run_specific_range(46,                                       # range start
                            0,                                       # range end
                            None,                           # indicadores para consultar postgre
                            None,                           # indicadores para consultar e deletar sql
                            os.getenv("HOST_RETORNO_SANTANDER"), 
                            os.getenv("PORTA_RETORNO_SANTANDER"), 
                            os.getenv("POSTGRES_DATABASE"), 
                            os.getenv("USER_RETORNO_SANTANDER"), 
                            os.getenv("PASSWORD_RETORNO_SANTANDER"), 
                            "SANTANDER"                              # ambiente ("AEC" OU "SANTANDER")
                            )

        CURSOR_SQL.execute("""update dbo.Historicos_Procedures SET Data_Fim = GETDATE() WHERE Nome = 'ETL_Performance_Python_D45' and cast(data_inicio as date) = cast(getdate() as date) and data_inicio = (select max(data_inicio) from dbo.historicos_Procedures (nolock) where nome = 'ETL_Performance_Python_D45')""")
        commit()
        try:
            CONN_SQL.autocommit = True
            cursor = CONN_SQL.cursor()
            for procedure in PROCEDURES:
                write_log(f"Iniciando chamada da {procedure}...")
                cursor.execute(f"""exec {procedure}""")
                write_log(f"{procedure} finalizada...")
        except Exception as e:
            write_log(f"Erro na execução das procedures: {str(e)}")
        finally:
            try:
                cursor.close()
            except:
                pass

    except Exception as e:
            write_log(f"Erro na ETL: {str(e)}")

    finally:

        try:
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