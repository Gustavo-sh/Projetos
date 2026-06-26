import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openpyxl
from datetime import datetime
from selenium.common.exceptions import InvalidElementStateException

def start_driver():
    options = Options()
    options.add_argument("--start-maximized")
    prefs = {"download.prompt_for_download": False}
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=options)

def viradas(driver, wait):
    path = r'C:\Users\e.gustavo.santos\Downloads/VIRADAS PELO ROBO.xlsx' # ATENÇÃO!! MUDAR O PATH PARA O CORRESPONDENTE ANTES DE USAR
    wb = openpyxl.load_workbook(path)
    BASE = wb['BASE']
    index_viradas = int(input("Digite de qual linha o programa deve começar a executar (apenas o número da linha, cabeçalho não conta): ")) # geralmente 2

    driver.get(r"https://pegasus/Rekrut/Candidato")
    wait.until(EC.presence_of_element_located((By.ID, "Login"))).send_keys("e.gustavo.santos" + Keys.TAB + "GUS*963,*963," + Keys.ENTER)
    
    while True:
        cpf = str(BASE[f'A{index_viradas}'].value)
        sessao = str(BASE[f'B{index_viradas}'].value)
        tomador = str(BASE[f'C{index_viradas}'].value)
        funcao = str(BASE[f'D{index_viradas}'].value)
        cr = str(BASE[f'E{index_viradas}'].value)
        salario = str(BASE[f'F{index_viradas}'].value)
        dt_admissao = str(BASE[f'G{index_viradas}'].value)
        jornada = str(BASE[f'H{index_viradas}'].value)
        ht_inicial = str(BASE[f'I{index_viradas}'].value)
        ht_final = str(BASE[f'J{index_viradas}'].value)
        hd_inicial = str(BASE[f'K{index_viradas}'].value)
        hd_final = str(BASE[f'L{index_viradas}'].value)
        labore = str(BASE[f'M{index_viradas}'].value)

        if BASE[f'A{index_viradas}'].value == None:
            wb.save(path)
            return "Viradas finalizadas."
        
        dt_modified = datetime.strptime(dt_admissao, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y") # modifica a data para o formato "dd/mm/aaaa"

        driver.get(r"https://pegasus/Rekrut/Candidato")

        wait.until(EC.presence_of_element_located((By.ID, "Cpf"))).send_keys(cpf + Keys.ENTER)
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div[1]/table/tbody/tr/td[4]/a"))).click() # clica em alterar os dados
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div[1]/ul/li[2]/a"))).click() # vai para a aba "jornada"
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div[2]/form/table/tbody/tr[1]/td[2]/select"))).send_keys(Keys.ENTER + jornada + Keys.ENTER)
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div[2]/form/table/tbody/tr[2]/td[2]/input[1]"))).send_keys(ht_inicial + ht_final + hd_inicial + hd_final + Keys.ENTER + labore + Keys.ENTER)
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div[2]/form/table/tbody/tr[5]/td/input"))).click() # salva as informações em "jornada"

        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div[1]/ul/li[3]/ul/li/a"))).click() #vai para a aba "geral"
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div[2]/form/table/tbody/tr[1]/td[2]/select"))).send_keys(Keys.ENTER + "3 - AEC CENTRO DE CONTATOS S/A" + Keys.ENTER) # define a coligada
        
        driver.find_element(By.ID, "Sessao").clear()
        time.sleep(1.5)
        driver.find_element(By.ID, "Sessao").send_keys(sessao)
        time.sleep(1.5)
        driver.find_element(By.ID, "Sessao").send_keys(Keys.DOWN)
        time.sleep(1.5)
        driver.find_element(By.ID, "Sessao").send_keys(Keys.ENTER)

        driver.find_element(By.ID, "Tomador").clear()
        time.sleep(1.5)
        driver.find_element(By.ID, "Tomador").send_keys(tomador)
        time.sleep(1.5)
        driver.find_element(By.ID, "Tomador").send_keys(Keys.DOWN)
        time.sleep(1.5)
        driver.find_element(By.ID, "Tomador").send_keys(Keys.ENTER)

        driver.find_element(By.ID, "Funcao").clear()
        time.sleep(1.5)
        driver.find_element(By.ID, "Funcao").send_keys(funcao)
        time.sleep(1.5)
        driver.find_element(By.ID, "Funcao").send_keys(Keys.DOWN)
        time.sleep(1.5)
        driver.find_element(By.ID, "Funcao").send_keys(Keys.ENTER)

        driver.find_element(By.ID, "CentroResultado").clear()
        time.sleep(1.5)
        driver.find_element(By.ID, "CentroResultado").send_keys(cr)
        time.sleep(1.5)
        driver.find_element(By.ID, "CentroResultado").send_keys(Keys.DOWN)
        time.sleep(1.5)
        driver.find_element(By.ID, "CentroResultado").send_keys(Keys.ENTER)

        driver.find_element(By.ID, "Salario").clear()
        driver.find_element(By.ID, "Salario").send_keys(salario)

        try:
            driver.find_element(By.ID, "DataAdmissao").clear()
            driver.find_element(By.ID, "DataAdmissao").send_keys(dt_modified)
        except InvalidElementStateException:
            print(f"Virada do agente na linha {index_viradas} já efetuada")
            BASE[f'N{index_viradas}'] = 'Virada já estava feita.'
            index_viradas += 1
            continue
    
        driver.find_element(By.ID, "botaosalvar").click() # salva as modificações na aba "geral"

        driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div[1]/ul/li[1]/a").click() # volta para a aba de "identificacao"

        wait.until(EC.presence_of_element_located((By.ID, "SituacaoCandidato"))).send_keys(Keys.ENTER + "Em Admissão" + Keys.ENTER) # muda o status para "em admissao"

        driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div[2]/form/table/tbody/tr[11]/td/input").click() # salva as modifiações na aba "identificacao"
        
        mensagem = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/ul/li/div/div/span")))

        BASE[f'N{index_viradas}'] = mensagem.text
        print(mensagem)
        print(BASE[f'N{index_viradas}'].value)
        wb.save(path)

        index_viradas += 1
        print(index_viradas)

        time.sleep(2)

driver = start_driver()
wait = WebDriverWait(driver, 90)

result = viradas(driver, wait)
print(result)