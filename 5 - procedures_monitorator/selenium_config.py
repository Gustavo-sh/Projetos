from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip
from utils import logging_msg

def create_webdriver():

    options = Options()
    options.add_argument(r"user-data-dir=C:\chrome-selenium-profile")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 60)
    
    return driver, wait

def send_message_whatsapp(wait, msg):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Campo de mensagem
            msg_box = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div/div/div[3]/div/div[4]/div/footer/div[1]/div/span/div/div/div/div[3]/div[1]/p')))
            pyperclip.copy(msg)
            # Envia mensagem
            msg_box.click()
            msg_box.send_keys(Keys.CONTROL + "v")
            msg_box.send_keys(Keys.ENTER)
            break
        except Exception as e:
            logging_msg(f"Ocorreu um erro ao enviar a mensagem no WhatsApp: {str(e)}")
            if attempt < max_retries - 1:
                logging_msg("Tentando novamente...")
            else:
                logging_msg("Número máximo de tentativas atingido. Não foi possível enviar a mensagem.")

def search_group_whatsapp(wait, group_name):
    try:
        search_box = wait.until(EC.element_to_be_clickable((By.ID, '_r_a_')))
        search_box.click()
        search_box.clear()
        search_box.send_keys(group_name)
        search_box.send_keys(Keys.ENTER)
    except Exception as e:
        logging_msg(f"Ocorreu um erro ao procurar o grupo no WhatsApp: {str(e)}")