from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyperclip
from connections_db import query_results, get_diretores, close_connection
from utils import mount_message, mount_message_director

def main():

    options = Options()

    # Caminho do perfil do Chrome (ajuste para seu usuário)
    options.add_argument(r"user-data-dir=C:\chrome-selenium-profile")
    options.add_argument("--window-size=1920,1080")
    #options.add_argument("--headless")
    options.add_argument(r"user-data-dir=C:\chrome-selenium-profile")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 240)
    driver.get("https://web.whatsapp.com/")
    destinatario = "."

    diretores = get_diretores()

    mapping_groups = {"ANA PAULA GONCALVES ROCHA": ".",
               "FAGNER EUSTAQUIO ANDRADE SILVA": ".",
               "GISELE DE CASTRO MARQUES": ".",
               "JAIME FERREIRA DE MACEDO MOURA": "."}

    for diretor in diretores:
        destinatario = mapping_groups.get(diretor, ".")

        # Procura o grupo
        search_box = wait.until(EC.element_to_be_clickable((By.ID, '_r_a_')))
        search_box.click()
        search_box.clear()
        search_box.send_keys(destinatario)
        time.sleep(3)
        search_box.send_keys(Keys.ENTER)

        # Campo de mensagem
        msg_box = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div/div/div[3]/div/div[4]/div/footer/div[1]/div/span/div/div/div/div[3]/div[1]/p')))

        
        results = query_results(diretor=diretor)
        msg = mount_message_director(results, diretor)

        time.sleep(5)

        # Envia mensagem
        pyperclip.copy(msg)

        msg_box.click()
        msg_box.send_keys(Keys.CONTROL, 'v')
        msg_box.send_keys(Keys.ENTER)

        time.sleep(2)

        print("Mensagem do diretor " + diretor + " enviada com sucesso para " + destinatario + "!")

    try:
        driver.quit()
        close_connection()
    except:
        pass

if __name__ == "__main__":
    main()