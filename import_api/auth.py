from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
import subprocess
from utils import resource_path, notify
from datetime import datetime
import json

def generate_session_key(driver):
    try:

        sessionkey = driver.execute_script("""
        return JSON.parse(sessionStorage.getItem('SessionKey'))
        """)

        notify(":: Session key obtida do session storage :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        with open("config_session.json", "w") as f:
            json.dump({"sessionKey": sessionkey}, f)

        notify(":: Sessionkey salva no json ::")

        try:
            driver.quit()
        except:
            pass

        return sessionkey

    except Exception as e:
        notify(":: Erro ao obter session key :: " + str(e))
    finally:
        deslig_proxy = resource_path("desligar_proxy.bat")
        subprocess.run(deslig_proxy, shell=True)

        notify(":: Proxy desligado :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        try:
            driver.quit()
        except:
            pass

def get_session_key(username, password):
    notify(":: Obtendo session key :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Edge(options=options)
    wait_4m = WebDriverWait(driver, 240)

    driver.get("https://aec.robbyson.com/administracao/#/login/")

    try:
        wait_4m.until(EC.presence_of_element_located((By.XPATH, "/html/body/nav/div/ul/li/a/div[1]"))).click()
        notify(":: Usuario logado, gerando session key :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return generate_session_key(driver)
    except:
        pass

    wait_4m.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[3]/div/div/div/div[2]/div[2]/div/input[1]"))).send_keys(username) # usuario
    notify(":: Usuário preenchido :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 
    driver.find_element(By.XPATH, "/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[3]/div/div/div/div[4]/div/div/div/div/input").click() # avançar
    wait_4m.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[3]/div/div[2]/input"))).send_keys(password) # senha
    notify(":: Senha preenchida :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    driver.find_element(By.XPATH, "/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[5]/div/div/div/div/input").click() # avançar
    wait_4m.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/form/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[3]/div[2]/div/div/div[2]/input"))).send_keys(Keys.ENTER) # avançar

    wait_4m.until(EC.presence_of_element_located((By.XPATH, "/html/body/nav/div/ul/li/a/div[1]"))).click() # sessao

    return generate_session_key(driver)