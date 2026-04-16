from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyperclip
from connections_db import query_results
from utils import mount_message

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
    destinatario = "Elvis Oliveira"

    # Procura o grupo
    search_box = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/div/div[3]/div/div[4]/div/div[1]/div/div/div/div/div/div/div[2]/input')))
    search_box.click()
    search_box.send_keys(destinatario)
    time.sleep(3)
    search_box.send_keys(Keys.ENTER)

    # Campo de mensagem
    msg_box = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/div/div[3]/div/div[5]/div/footer/div[1]/div/span/div/div/div/div[3]/div[1]/p')))

    results = query_results()
    msg = mount_message(results)

    # Envia mensagem
    pyperclip.copy(msg)

    msg_box.click()
    msg_box.send_keys(Keys.CONTROL, 'v')
    msg_box.send_keys(Keys.ENTER)

    time.sleep(5)

    print("Mensagem enviada com sucesso!")

    driver.quit()

if __name__ == "__main__":
    main()