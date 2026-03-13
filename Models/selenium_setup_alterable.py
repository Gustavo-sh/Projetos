from asyncio import wait
import shutil
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyodbc
import keyring

def start_driver():
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def main_func(driver, wait, resultados): 
    senha = keyring.get_password("orbi", "e.gustavo.santos") # se futuramente precisar alterar o login, alterar aqui também
    for row in resultados:
        driver.get("https://pegasus/Orbi/modulo-administrativo/gerenciamento-perfis-concessao") # get orbi
        wait.until(EC.element_to_be_clickable((By.ID, "Login"))).send_keys("e.gustavo.santos" + Keys.TAB + senha + Keys.TAB + Keys.ENTER) # login e senha / se futuramente precisar alterar o login, alterar aqui também
        wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div[2]/button[3]"))).click() # aceitar cookies
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div[1]/div[2]/div/div/div[2]/div/table/thead/tr[2]/th[4]/input"))).send_keys(row[1]) # pesquisar relatorio
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div[2]/div[2]/div/div/div[1]/div[1]/div/label/select"))).send_keys(Keys.ENTER + Keys.ARROW_DOWN + Keys.ENTER) # selecionar 40 itens por pagina
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div[2]/div[2]/div/div/div[2]/div/table/thead/tr[2]/th[4]/input"))).send_keys(row[2]) # pesquisar cargo
        time.sleep(5) # aguardar carregamento
        elemento_down = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div[2]/div[2]/div/div/div[3]/div[2]/div/ul/li[2]/a"))) # localizar elemento paginação
        driver.execute_script("arguments[0].scrollIntoView();", elemento_down) # rolar para baixo
        itens_paginas = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "li"))) # define todos os elementos de paginação
        total_paginas = int(itens_paginas[-2].find_element(By.TAG_NAME, "a").text) # define o total de páginas
        elemento_up = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div[1]/div[2]/div/div/div[1]/div[1]/div/label/select"))) # localizar elemento no topo
        driver.execute_script("arguments[0].scrollIntoView(true);", elemento_up) # rolar para o topo
        itens_flags = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "select-checkbox"))) # define todos os checkbox (incluindo o do relatorio no inicio)
        for i in range(total_paginas):
            for item in itens_flags:
                driver.execute_script("arguments[0].scrollIntoView();", item) # rolar para o checkbox
                item.click()
                if item == itens_flags[-1] and total_paginas > 1: # se for o ultimo checkbox e tiver mais de uma pagina
                    #wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[3]/div/input"))).click() # associar perfil
                    #wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div/div/div[3]/button"))).click() # entendi
                    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div[2]/div[2]/div/div/div[3]/div[2]/div/ul/li[9]/a"))).click() # proxima pagina
                    driver.execute_script("arguments[0].scrollIntoView(true);", elemento_up)
                    div_especifica = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div[2]/div[2]/div/div/div[2]/div"))) # div que contem os checkbox de cr
                    itens_flags = div_especifica.find_elements(By.CLASS_NAME, "select-checkbox") # atualizar a lista de checkbox
                    time.sleep(1)
                    break
                time.sleep(1)
        print(f"Finalizado para{row[1]} - {row[2]}")

def conexao_bd():
    conn = pyodbc.connect(
    "Driver={SQL Server};"
    "Server=primno4;"  
    "Database=Robbyson;"
    "Trusted_Connection=yes;"  
    )

    cur = conn.cursor()
    cur.execute("select * from acessos_orbi")
    resultados = cur.fetchall()
    cur.close()
    conn.close()

    del resultados[0]
    return resultados

if __name__ == "__main__":

    # keyring.set_password("orbi", "coloque seu login aqui", "coloque sua senha aqui") # se futuramente precisar alterar o login e senha, alterar nas linhas 25 e 28 tambem. Apos isso, descomentar as proximas 3 linhas e rodar o script uma vez
    # time.sleep(5)
    # exit()

    resultados = conexao_bd()

    chromedriver = os.path.expanduser(r'~\.cache\selenium\chromedriver\win64')
    if os.path.exists(chromedriver):
        if len(os.listdir(chromedriver)) >= 2:
            shutil.rmtree(chromedriver+"\\")
    driver = start_driver()
    wait = WebDriverWait(driver, 90)
    main_func(driver, wait, resultados)