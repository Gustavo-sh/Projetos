from tunnel import start_tunnel, kill_existing_tunnel
from utils import write_log
from sqlserver import CONN_SQL, CURSOR_SQL, commit
from etl_sync import run_specific_range_performance, run_specific_range_notificacao
from validation import exec_validation
import os
import sys


ETLS = {
    "PD15": {
        "range_start": 16,
        "procedures": [
            "dbo.sp_Ins_matriz",
            "dbo.sp_Ins_bussola_d15",
            "dbo.sp_ins_bussola_semanal",
            "dbo.SP_Ins_Resultado_Consolidado_D15",
            "dbo.sp_ins_rel1",
            "dbo.sp_ins_rel2",
            "dbo.sp_ins_rel3",
            "dbo.Sp_Ins_ReincidenciaDeGrupos",
            "dbo.sp_Ins_IGD",
            "dbo.sp_ins_indice_evolucao",
            "rlt.Sp_Ins_CheckPoint_D10",
            "dbo.SP_Ins_Gamification_D15",
            "dbo.sp_ins_gamificationperformance_D15",
            "dbo.sp_ins_grupos_rh_processo",
            "dbo.sp_Ins_RV_D15",
            "rby.sp_Ins_PerformanceFoto"
        ]
    },

    "PD45": {
        "range_start": 46,
        "procedures": [
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
    },

    "PDVAR": {
        "range_start": 1,
        "procedures": [
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
    },

    "ND15": {
        "range_start": 16
    },

    "ND45": {
        "range_start": 46
    }
}


def executar_procedures(procedures):

    if not procedures:
        return

    try:
        CONN_SQL.autocommit = True
        cursor = CONN_SQL.cursor()

        for procedure in procedures:
            write_log(f"Iniciando chamada da {procedure}...")

            cursor.execute(f"EXEC {procedure}")

            write_log(f"{procedure} finalizada...")

    except Exception as e:
        write_log(f"Erro na execução das procedures: {str(e)}")

    finally:
        try:
            cursor.close()
        except:
            pass


def executar_etl(tipo_etl):

    nomes = {"PD15": "Performance", "PD45": "Performance", "PDVAR": "Performance", "ND15": "Notificação", "ND45": "Notificação"}
    nome = nomes.get(tipo_etl)

    config = ETLS[tipo_etl]

    nome_etl = f"ETL_{nome}_Python_{tipo_etl}"

    try:
        write_log(f"Iniciando a ETL {tipo_etl}")

        CURSOR_SQL.execute("""
            INSERT INTO dbo.Historicos_Procedures
            VALUES (?, GETDATE(), NULL, ?, ?)
        """, nome_etl, nome, tipo_etl)

        write_log(f"{tipo_etl} entrando em etapa de execução...")

        if tipo_etl in ("ND15", "ND45"):

            # AEC
            run_specific_range_notificacao(
                config["range_start"],
                0,
                os.getenv("HOST_RETORNO"),
                os.getenv("PORTA_RETORNO"),
                os.getenv("POSTGRES_DATABASE"),
                os.getenv("USER_RETORNO"),
                os.getenv("PASSWORD_RETORNO"),
                "AEC"
            )

            # SANTANDER
            run_specific_range_notificacao(
                config["range_start"],
                0,
                os.getenv("HOST_RETORNO_SANTANDER"),
                os.getenv("PORTA_RETORNO_SANTANDER"),
                os.getenv("POSTGRES_DATABASE"),
                os.getenv("USER_RETORNO_SANTANDER"),
                os.getenv("PASSWORD_RETORNO_SANTANDER"),
                "SANTANDER"
            )

        elif tipo_etl in ("PD15", "PD45"):

            # AEC
            run_specific_range_performance(
                config["range_start"],
                0,
                None,
                None,
                os.getenv("HOST_RETORNO"),
                os.getenv("PORTA_RETORNO"),
                os.getenv("POSTGRES_DATABASE"),
                os.getenv("USER_RETORNO"),
                os.getenv("PASSWORD_RETORNO"),
                "AEC"
            )

            # SANTANDER
            run_specific_range_performance(
                config["range_start"],
                0,
                None,
                None,
                os.getenv("HOST_RETORNO_SANTANDER"),
                os.getenv("PORTA_RETORNO_SANTANDER"),
                os.getenv("POSTGRES_DATABASE"),
                os.getenv("USER_RETORNO_SANTANDER"),
                os.getenv("PASSWORD_RETORNO_SANTANDER"),
                "SANTANDER"
            )

        elif tipo_etl in ("PDVAR"):
                        
            # AEC
            run_specific_range_performance(
                config["range_start"],
                0,
                [10, 34, 217], # indicadores para consultar no postgre
                [10, 34, 217], # indicadores para consultar e deletar no sql
                os.getenv("HOST_RETORNO"),
                os.getenv("PORTA_RETORNO"),
                os.getenv("POSTGRES_DATABASE"),
                os.getenv("USER_RETORNO"),
                os.getenv("PASSWORD_RETORNO"),
                "AEC"
            )

            # SANTANDER
            run_specific_range_performance(
                config["range_start"],
                0,
                [10, -5, 217], # indicadores para consultar no postgre
                [10, 34, 217], # indicadores para consultar e deletar no sql
                os.getenv("HOST_RETORNO_SANTANDER"),
                os.getenv("PORTA_RETORNO_SANTANDER"),
                os.getenv("POSTGRES_DATABASE"),
                os.getenv("USER_RETORNO_SANTANDER"),
                os.getenv("PASSWORD_RETORNO_SANTANDER"),
                "SANTANDER"
            )

        CURSOR_SQL.execute("""
            UPDATE dbo.Historicos_Procedures
            SET Data_Fim = GETDATE()
            WHERE Nome = ?
              AND CAST(data_inicio AS date) = CAST(GETDATE() AS date)
              AND data_inicio = (
                  SELECT MAX(data_inicio)
                  FROM dbo.historicos_Procedures (NOLOCK)
                  WHERE nome = ?
              )
        """, nome_etl, nome_etl)

        commit()

        executar_procedures(config.get("procedures"))

        if tipo_etl in ("PD15", "PD45"):
            exec_validation()

    except Exception as e:
        write_log(f"Erro na ETL {tipo_etl}: {str(e)}")
        raise

    finally:
        try:
            CURSOR_SQL.close()
            CONN_SQL.close()
            write_log("Conexão com sqlserver finalizada com sucesso...")
        except:
            pass

        write_log(f"ETL {tipo_etl} finalizada com sucesso.")



def main():

    if len(sys.argv) != 2:
        raise ValueError("Informe a ETL: PD15, ND15, PD45, ND45 ou PDVAR")

    tipo_etl = sys.argv[1].upper()

    if tipo_etl not in ETLS:
        raise ValueError(f"ETL inválida: {tipo_etl}")

    executar_etl(tipo_etl)


if __name__ == "__main__":
    main()