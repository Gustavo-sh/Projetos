from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
from utils import resource_path, notify
from datetime import datetime

def generate_session_key(driver):
    sessionkey = driver.execute_script("""
    return JSON.parse(sessionStorage.getItem('SessionKey'))
    """)
    notify(":: Session key obtida do session storage :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    deslig_proxy = resource_path("desligar_proxy.bat")
    subprocess.run(deslig_proxy, shell=True)

    notify(":: Proxy desligado :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    return sessionkey

def get_session_key(username, password):
    notify(":: Obtendo session key :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    driver = webdriver.Edge()
    wait_4m = WebDriverWait(driver, 240)
    wait_30s = WebDriverWait(driver, 30)

    driver.get("https://aec.robbyson.com/administracao/#/login/")

    try:
        wait_30s.until(EC.presence_of_element_located((By.XPATH, "/html/body/nav/div/ul/li/a/div[1]"))).click()
        notify(":: Usuario logado, gerando session key :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return generate_session_key(driver)
    except:
        pass

    usuario = wait_4m.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[3]/div/div/div/div[2]/div[2]/div/input[1]"))).send_keys(username)
    notify(":: Usuário preenchido :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    driver.find_element(By.XPATH, "/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[3]/div/div/div/div[4]/div/div/div/div/input").click()
    notify(":: Senha preenchida :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    senha = wait_4m.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[3]/div/div[2]/input"))).send_keys(password)
    driver.find_element(By.XPATH, "/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[5]/div/div/div/div/input").click()
    wait_4m.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/form/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[3]/div[2]/div/div/div[2]/input"))).send_keys(Keys.ENTER)

    wait_4m.until(EC.presence_of_element_located((By.XPATH, "/html/body/nav/div/ul/li/a/div[1]"))).click()

    return generate_session_key(driver)