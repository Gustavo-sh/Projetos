from collections import defaultdict
from connections_db import get_nulls, get_avg_duration, close_connection
from selenium_config import create_webdriver, send_message_whatsapp, search_group_whatsapp
from whatsapp_config import notify_whatsapp
from utils import logging_msg
from datetime import datetime
import time

def main():
    try:
        # driver, wait = create_webdriver()
        # driver.get("https://web.whatsapp.com/")
        # time.sleep(15)
        control_notifications = defaultdict(int)
        # search_group_whatsapp(wait, "Robbyson - Avisos")
        notify_whatsapp("🖥️ Iniciando monitoramento das procedures.\nAs mensagens serão reenviadas a cada 5 minutos com o status das procedures em execução.")
        now = datetime.now()
        while now < datetime(now.year, now.month, now.day, 18, 0, 0):
            nulls = get_nulls()
            avg_durations = get_avg_duration()
            logging_msg("Nulls e avg_durations obtidos, iniciando análise...")
            for procedure in nulls:
                if control_notifications.get(procedure.get("nome"), 0) >= 3:
                    logging_msg(f"Procedure {procedure.get('nome')} atingiu o limite de notificações. Não serão enviadas mais mensagens para este procedimento até que seja finalizado.")
                    continue
                avg_duration = avg_durations.get(procedure.get("nome"))
                if not avg_duration and avg_duration != 0:
                    logging_msg(f"Procedure {procedure.get('nome')} não possui um tempo médio registrado. Gentileza validar as execuções históricas.")
                    notify_whatsapp(f"⚠️ A procedure {procedure.get('nome')} não possui um tempo médio registrado (últimos 7 dias). Gentileza validar as execuções históricas. ⚠️")
                    control_notifications[procedure.get("nome")] = 3
                    continue
                real_duration = datetime.now() - procedure.get("data_inicio")
                real_duration_minutes = real_duration.total_seconds() / 60
                logging_msg("Real duration e avg duration definidas, iniciando comparação...")
                if real_duration_minutes > avg_duration:
                    control_notifications[procedure.get("nome")] += 1
                    notify_whatsapp(f"⚠️ A procedure {procedure.get('nome')} está demorando mais que o normal.\nInicio: {procedure.get('data_inicio')}\nDuração atual (minutos): {round(real_duration_minutes)}\nDuração média (minutos): {avg_duration}\nNotificação {control_notifications[procedure.get('nome')]} de 3. ⚠️")
            time.sleep(300)
            now = datetime.now()
        notify_whatsapp("⏰ O monitoramento das procedures foi finalizado. ⏰")
    except Exception as e:
        logging_msg(f"Ocorreu um erro no monitoramento: {str(e)}")
        try:
            notify_whatsapp(f"Ocorreu um erro no monitoramento: {str(e)}")
        except:
            pass
    finally:
        close_connection()
        # try:
        #     driver.quit()
        # except Exception as e:
        #     logging_msg(f"Ocorreu um erro ao fechar o driver: {str(e)}")

if __name__ == "__main__":
    main()