from collections import defaultdict
from connections_db import get_nulls, get_avg_duration, close_connection
from selenium_config import create_webdriver, send_message_whatsapp, search_group_whatsapp
from utils import logging_msg
from datetime import datetime
import time

def main():
    try:
        driver, wait = create_webdriver()
        driver.get("https://web.whatsapp.com/")
        time.sleep(15)
        control_notifications = defaultdict(int)
        search_group_whatsapp(wait, "Robbyson - Avisos")
        send_message_whatsapp(wait, "🖥️ Iniciando monitoramento das procedures.\nAs mensagens serão reenviadas a cada 5 minutos com o status das procedures em execução.")
        now = datetime.now()
        while now < datetime(now.year, now.month, now.day, 12, 0, 0):
            nulls = get_nulls()
            avg_durations = get_avg_duration()
            logging_msg("Nulls e avg_durations obtidos, iniciando análise...")
            for procedure in nulls:
                logging_msg("Nome da procedure: ", procedure.get("nome"))
                logging_msg("Control notifications: ", control_notifications.get(procedure.get("nome"), 0))
                if control_notifications.get(procedure.get("nome"), 0) >= 3:
                    logging_msg(f"Procedure {procedure.get('nome')} atingiu o limite de notificações. Não serão enviadas mais mensagens para este procedimento até que seja finalizado.")
                    continue
                avg_duration = avg_durations.get(procedure.get("nome"))
                if not avg_duration:
                    logging_msg(f"Procedure {procedure.get('nome')} não possui um tempo médio registrado. Gentileza validar as execuções históricas.")
                    #notify_telegram(f"A procedure {procedure.get('nome')} não possui um tempo médio registrado. Gentileza validar as execuções históricas.")
                    send_message_whatsapp(wait, f"⚠️ A procedure {procedure.get('nome')} não possui um tempo médio registrado (últimos 7 dias). Gentileza validar as execuções históricas. ⚠️")
                    control_notifications[procedure.get("nome")] = 3
                    continue
                real_duration = datetime.now() - procedure.get("data_inicio")
                real_duration_minutes = real_duration.total_seconds() / 60
                logging_msg("Real duration e avg duration definidas, iniciando comparação...")
                if real_duration_minutes > avg_duration:
                    control_notifications[procedure.get("nome")] += 1
                    #notify_telegram(f"A procedure {procedure.get('nome')} está demorando mais que o normal. Inicio: {procedure.get('data_inicio')}, Duração atual: {real_duration_minutes}, Duração média: {avg_duration}")
                    send_message_whatsapp(wait, f"⚠️ A procedure {procedure.get('nome')} está demorando mais que o normal.\nInicio: {procedure.get('data_inicio')}\nDuração atual (minutos): {round(real_duration_minutes)}\nDuração média (minutos): {avg_duration}\nNotificação {control_notifications[procedure.get('nome')]} de 3. ⚠️")
            logging_msg(control_notifications)
            time.sleep(300)
            now = datetime.now()
        send_message_whatsapp(wait, "⏰ O monitoramento das procedures foi finalizado. ⏰")
    except Exception as e:
        logging_msg(f"Ocorreu um erro no monitoramento: {str(e)}")
        #notify_telegram(f"Ocorreu um erro no monitoramento: {str(e)}")
        send_message_whatsapp(wait, f"Ocorreu um erro no monitoramento: {str(e)}")
    finally:
        close_connection()
        driver.quit()

if __name__ == "__main__":
    main()