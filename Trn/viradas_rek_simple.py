import threading
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import openpyxl
from datetime import datetime
from selenium.common.exceptions import InvalidElementStateException
import customtkinter as ctk
import json
from tkinter import filedialog

sys.stdout.reconfigure(encoding='utf-8')

def start_driver():
    options = Options()
    options.add_argument("--start-maximized")
    prefs = {"download.prompt_for_download": False}
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=options)

def viradas(driver, wait, login, pw, line, pathr):
    folderCD = os.path.expanduser(r'~\.cache\selenium\chromedriver\win64')
    if os.path.exists(folderCD):
        archivesFolder = os.listdir(folderCD)
        if len(archivesFolder) >= 2:
            return print(fr"Favor remover chromedriver de versao antiga da pasta para que o programa funcione. Pasta: C:\Users\SEU USUARIO\.cache\selenium\chromedriver\win64")
    path = pathr
    wb = openpyxl.load_workbook(path)
    BASE = wb['BASE']
    index_viradas = int(line)

    driver.get(r"https://pegasus/Rekrut/Candidato")
    print(":: Abrindo a página do Rekrut")
    wait.until(EC.presence_of_element_located((By.ID, "Login"))).send_keys(login + Keys.TAB + pw + Keys.ENTER)
    
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

        if salario[4] != ",":
            return "Salário foi preenchido errado, favor verificar a planilha e executar o programa novamente."
        
        print(f"Verificação do salário ok, o quinto caracter é '{salario[4]}'.")

        if BASE[f'A{index_viradas}'].value == None:
            wb.save(path)
            return ":: Viradas finalizadas."
        
        dt_modified = datetime.strptime(dt_admissao, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y") # modifica a data para o formato "dd/mm/aaaa"

        driver.get(r"https://pegasus/Rekrut/Candidato")

        wait.until(EC.element_to_be_clickable((By.ID, "Cpf"))).send_keys(cpf + Keys.ENTER)
        time.sleep(10)
        mensagemm = wait.until(EC.element_to_be_clickable((By.XPATH, "//*/text()[normalize-space(.)='Alterar']/parent::*")))
        print(mensagemm.text)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*/text()[normalize-space(.)='Alterar']/parent::*"))).click() # clica em alterar os dados
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Jornada de Trabalho')]"))).click() # vai para a aba "jornada"
        wait.until(EC.element_to_be_clickable((By.ID, "IdJornadaMensalTrabalho"))).send_keys(Keys.ENTER + jornada + Keys.ENTER)
        wait.until(EC.element_to_be_clickable((By.ID, "HorarioTrabalhoInicio"))).send_keys(ht_inicial + ht_final + hd_inicial + hd_final + Keys.ENTER + labore + Keys.ENTER)
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn"))).click() # salva as informações em "jornada"
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Geral')]"))).click() #vai para a aba "geral"
        wait.until(EC.element_to_be_clickable((By.ID, "CodigoColigada"))).send_keys(Keys.ENTER + "3 - AEC CENTRO DE CONTATOS S/A" + Keys.ENTER) # define a coligada
        
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
            driver.find_element(By.ID, "DataAdmissao").send_keys(dt_modified + Keys.ENTER)
        except InvalidElementStateException:
            print(f":: Virada do agente na linha {index_viradas} já efetuada")
            BASE[f'N{index_viradas}'] = 'Virada já estava feita.'
            index_viradas += 1
            continue
    
        wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='botaosalvar']"))).click() # salva as modificações na aba "geral"

        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Identificação')]"))).click() # volta para a aba de "identificacao"

        wait.until(EC.element_to_be_clickable((By.ID, "SituacaoCandidato"))).send_keys(Keys.ENTER + "Em Admissão" + Keys.ENTER) # muda o status para "em admissao"

        wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[2]/div[2]/form/table/tbody/tr[11]/td/input"))).click() # salva as modifiações na aba "identificacao"
        
        mensagem = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/ul/li/div/div/span"))) # captura o log

        BASE[f'N{index_viradas}'] = mensagem.text
        print(mensagem)
        print(BASE[f'N{index_viradas}'].value)
        wb.save(path)

        index_viradas += 1
        print(index_viradas)

        time.sleep(2)

def main(login, pw, line, pathr):
    config_data = {
        "login": login_et.get(),
        "path": pathr_et.get(),
        "line": str(2)
    }
    if checkbox_lembrar.get():
        with open(ARQUIVO_CONFIG, "w") as f:
            json.dump(config_data, f)
    driver = start_driver()
    wait = WebDriverWait(driver, 90)
    result = viradas(driver, wait, login, pw, line, pathr)
    print(result)

def search_archive():
    pathr_et.delete(0, ctk.END)
    caminho_arquivo = filedialog.askopenfilename(
            title="Selecione um arquivo",
            filetypes=(
                ("Todos os arquivos", "*.*"),
                ("Arquivos de texto", "*.txt")
            )
        )
    pathr_et.insert(0, caminho_arquivo)

def background_task(login, senha, line, path):
    thread_tarefa = threading.Thread(target=main, args=(login, senha, line, path), daemon=True)
    thread_tarefa.start()

ARQUIVO_CONFIG = "config_login.json"

ctk.set_appearance_mode('dark')
app = ctk.CTk()
app.title("Download and sent hominum")
app.geometry("400x500")

login_lb = ctk.CTkLabel(app, text="Login:")
login_lb.pack(pady=3)
login_et = ctk.CTkEntry(app, placeholder_text="Digite seu login hominum", justify="center", width=300)
login_et.pack(pady=3)

pw_lb = ctk.CTkLabel(app, text="Password:")
pw_lb.pack(pady=3)
pw_et = ctk.CTkEntry(app, placeholder_text="Digite sua senha hominum", show="*", justify="center", width=300)
pw_et.pack(pady=3)

checkbox_lembrar = ctk.CTkCheckBox(master=app, text="Lembrar login", command=None, onvalue=True, offvalue=False)
checkbox_lembrar.pack(pady=10)

line_lb = ctk.CTkLabel(app, text="Linha de execução:")
line_lb.pack(pady=3)
line_et = ctk.CTkEntry(app, placeholder_text="Qual linha o arquivo deve iniciar", justify="center", width=300)
line_et.pack(pady=3)

pathr_lb = ctk.CTkLabel(app, text="Arquivo excel de viradas:")
pathr_lb.pack(pady=3)
pathr_et = ctk.CTkEntry(app, placeholder_text="Clique nos tres pontos para selecionar", justify="center", width=300)
pathr_et.pack(pady=3)

if os.path.exists(ARQUIVO_CONFIG):
    with open(ARQUIVO_CONFIG, "r") as f:
            dados = json.load(f)
            login_et.insert(0, dados.get("login", ""))
            pathr_et.delete(0, ctk.END)
            pathr_et.insert(0, dados.get("path", ""))
            line_et.insert(0, dados.get("line", ""))

button_path = ctk.CTkButton(app, text="...", width=40, command=lambda: search_archive())
button_path.pack(pady=10)

button_init = ctk.CTkButton(app, text="init", command=lambda: background_task(login_et.get(), pw_et.get(), line_et.get(), pathr_et.get()))
button_init.pack(pady=10)

kill_process_button = ctk.CTkButton(app, text="kill process", command=app.destroy)
kill_process_button.pack(pady=10)

app.mainloop()