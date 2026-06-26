from datetime import datetime
import json
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
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import customtkinter as ctk

enc = False
diretorio_aut = os.path.dirname(os.path.abspath(__file__))

def start_driver():
    options = Options()
    options.add_argument("--start-maximized")
    prefs = {"download.prompt_for_download": False, "download.default_directory": diretorio_aut}
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=options)

def encerrar(driver, CT):
    print(":: Automação encerrada em tempo de execução de forma segura")
    print(":: O log ficara disponivel para verificação por 30 segundos")
    print(datetime.now())
    driver.quit()
    with open("log.txt", "a") as l:
        l.write(CT.log_box.get("1.0", "end"))
    time.sleep(30)
    CT.destroy()

def set_event():
    global enc
    print(":: Solicitação de encerramento recebida")
    print(":: A automação irá encerrar no proximo checkpoint seguro")
    enc = True

def gx(login, pw, driver, wait, CT):
    tab1 = CT.tabview.tab("INICIO")
    button = ctk.CTkButton(tab1, text="Encerrar a automação", command=lambda: set_event())
    button.pack(pady=10)
    print(":: Automação rodando")
    try:
        actions = ActionChains(driver)
        archive = os.path.expanduser(os.path.join(diretorio_aut, "Todos Chamados.xlsx"))
        print(":: Acessando a pagina do GX azul com link v2")
        driver.get("https://srv_gx_ti.grupoaec.com.br/Paginas/Portal")
        wait.until(EC.element_to_be_clickable((By.ID, "edtLogin"))).send_keys(login + Keys.TAB + pw + Keys.ENTER) # login e senha
        time.sleep(2)
        driver.get("https://srv_gx_ti.grupoaec.com.br/Chamados/TodosV2")
        print(":: Acessando aba todos os chamados")
        if enc: encerrar(driver, CT) ##checkpoint##
        wait.until(EC.element_to_be_clickable((By.ID, "ctl00_MainContent_rdStatus_Input"))).click() # filtro
        actions.double_click(wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[1]/div/div/div/label/input")))).perform() # todos
        wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[1]/div/div/ul/li[1]/label/input"))).click() # abertos
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@id='ctl00_MainContent_btnTodos']/span[2]"))).click() # buscar
        print(":: Buscando todos os chamados de liberação de acesso abertos")
        time.sleep(5)
    except Exception as e:
         print(f":: Erro: {e}")

    if os.path.exists(archive):
         os.remove(archive)
         print(":: Arquivo antigo de todos os chamados em excel removido")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@id='ctl00_MainContent_btnExportar']/span[2]"))).click() #exportar
    print(":: Baixando arquivo de todos os chamados abertos")
    if enc: encerrar(driver, CT) ##checkpoint##
    while not os.path.exists(archive):
         time.sleep(5)

    df = pd.read_excel(archive, sheet_name="Todos Chamados")
    df_filtrado = df[df["Serviço"].str.contains("Liberação de Acesso", case=False, na=False)]
    df_filtrado = df_filtrado.reset_index(drop=True)
    chamados = []
    print(":: Arquivo baixado")

    for i in range(len(df_filtrado)):
         chamados.append(df_filtrado.loc[i, "Código"])

    if len(chamados) == 0:
         print(":: Nenhum chamado de acesso a ser respondido.")
         print(datetime.now())
         with open("log.txt", "a") as l:
            l.write(CT.self.log_box.get())
         return
    if enc: encerrar(driver, CT) ##checkpoint##
    print(":: Filtrando todos os chamados")
    wait.until(EC.element_to_be_clickable((By.ID, "ctl00_MainContent_rdStatus_Input"))).click() # filtro
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[1]/div/div/div/label/input"))).click() # todos
    wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@id='ctl00_MainContent_btnTodos']/span[2]"))).click() # buscar
    time.sleep(10)

    for i in chamados:
        if enc: encerrar(driver, CT) ##checkpoint##
        try:
            print(f":: Pesquisando o chamado {i} para assumir e fechar com texto padrão")
            driver.find_element(By.ID, "ctl00_MainContent_gridchamados_ctl00_ctl02_ctl02_FilterTextBox_CODIGO").clear() # limpa o texto de pesquisa do chamado
            wait.until(EC.element_to_be_clickable((By.ID, "ctl00_MainContent_gridchamados_ctl00_ctl02_ctl02_FilterTextBox_CODIGO"))).send_keys(i + Keys.ENTER) # pesquisa o chamado
            time.sleep(10)
            wait.until(EC.element_to_be_clickable((By.ID, "ctl00_MainContent_gridchamados_ctl00_ctl04_imgIncidente"))).click() # assumir
            iframe_confirmar = wait.until(EC.presence_of_element_located((By.XPATH, "//iframe[@name='Assumir']"))) # iframe confirmar
            driver.switch_to.frame(iframe_confirmar)
            wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[5]/div[1]/table/tbody/tr[2]/td/span[2]"))).click() # confirmar
            driver.switch_to.default_content()
            wait.until(EC.element_to_be_clickable((By.ID, "ctl00_MainContent_gridchamados_ctl00_ctl04_imgEditInc"))).click() # editar
            iframe_corpo = wait.until(EC.presence_of_element_located((By.XPATH, "//iframe[@name='radChamado']"))) # iframe corpo do chamado
            driver.switch_to.frame(iframe_corpo)
            driver.find_element(By.ID, "rdStatus_Input").clear()
            time.sleep(1)
            driver.find_element(By.ID, "rdStatus_Input").send_keys("RESOLVIDO") # status
            time.sleep(1)
            driver.find_element(By.ID, "rdStatus_Input").send_keys(Keys.DOWN)
            time.sleep(1)
            driver.find_element(By.ID, "rdStatus_Input").send_keys(Keys.ENTER)
            time.sleep(1)
            driver.find_element(By.ID, "cbbCategoria_Input").send_keys("Criação") # tipo de resolução
            time.sleep(1)
            driver.find_element(By.ID, "cbbCategoria_Input").send_keys(Keys.DOWN)
            time.sleep(1)
            driver.find_element(By.ID, "cbbCategoria_Input").send_keys(Keys.ENTER)

            wait.until(EC.element_to_be_clickable((By.ID, "edtDescPublica"))).send_keys("Bom dia/tarde/noite. Acessos liberados para os relatórios que pertencem a nossa área (Excelência Operacional). Para outros relatórios, acionar as áreas responsáveis por cada.") # preenche o texto
            if enc: encerrar(driver, CT) ##checkpoint##
            driver.execute_script("arguments[0].scrollIntoView();", driver.find_element(By.ID, "btnSalvar_input")) # schrola para baixo
            driver.find_element(By.ID, "btnSalvar_input").click() # salva
            print(f":: Chamado {i} fechado, indo para o proximo")
            time.sleep(2)

            driver.switch_to.default_content()

        except Exception as e:
             print(f":: Erro: {e}")
        finally:
             print(":: Chamados fechados.")
             print(datetime.now())
             with open("log.txt", "a") as l:
                l.write(CT.self.log_box.get())

def main(login, pw, lembrar, CT):
    if lembrar:
        with open("config_login.json", "w") as f:
            json.dump({"login": login}, f)
    driver = start_driver()
    wait = WebDriverWait(driver, 90)
    gx(login, pw, driver, wait, CT)

def background_task(login, senha, lembrar_login, CT):
    thread_tarefa = threading.Thread(target=main, args=(login, senha, lembrar_login, CT), daemon=True)
    thread_tarefa.start()

ctk.set_appearance_mode("dark")  # "light", "dark", "system"
ctk.set_default_color_theme("blue")  # cores: "blue", "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        folderCD = os.path.expanduser(r'~\.cache\selenium\chromedriver\win64')
        if os.path.exists(folderCD):
            archivesFolder = os.listdir(folderCD)
            if len(archivesFolder) >= 2:
                print(fr"Favor remover chromedriver de versao antiga da pasta para que o programa funcione. Pasta: C:\Users\SEU USUARIO\.cache\selenium\chromedriver\win64")
                time.sleep(20)
                sys.exit()
        
        self.title("Chamados de Liberação de acesso GX")
        self.geometry("500x400")

        # Criar um notebook (abas)
        self.tabview = ctk.CTkTabview(self, width=480, height=350)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        # Adicionar duas abas
        self.tabview.add("INICIO")
        self.tabview.add("LOG")

        # Chamar métodos para montar cada aba
        self.aba_inicio()
        self.aba_log()

    def aba_inicio(self):
        ARQUIVO_CONFIG = "config_login.json"
        tab1 = self.tabview.tab("INICIO")

        label1 = ctk.CTkLabel(tab1, text="Digite seu LOGIN:")
        label1.pack(pady=10)

        self.entry_nome = ctk.CTkEntry(tab1, justify="center", placeholder_text="LOGIN")
        self.entry_nome.pack(pady=5)

        if os.path.exists(ARQUIVO_CONFIG):
            with open(ARQUIVO_CONFIG, "r") as f:
                dados = json.load(f)
                self.entry_nome.insert(0, dados.get("login", ""))

        label2 = ctk.CTkLabel(tab1, text="Digite sua SENHA:")
        label2.pack(pady=10)

        self.entry_senha = ctk.CTkEntry(tab1, justify="center", show="*", placeholder_text="SENHA")
        self.entry_senha.pack(pady=5)

        checkbox_lembrar = ctk.CTkCheckBox(master=tab1, text="Lembrar login", command=None, onvalue=True, offvalue=False)
        checkbox_lembrar.pack(pady=5) 

        botao1 = ctk.CTkButton(tab1, text="Iniciar a automação", command=lambda: background_task(self.entry_nome.get(), self.entry_senha.get(), checkbox_lembrar.get(), self))
        botao1.pack(pady=10)

    def aba_log(self):
        LOG_PERSISTENTE = 'log.txt'
        tab2 = self.tabview.tab("LOG")

        label2 = ctk.CTkLabel(tab2, text="Log de Execução:")
        label2.pack(pady=10)

        # Caixa de texto para exibir o log
        self.log_box = ctk.CTkTextbox(tab2, width=450, height=200)
        self.log_box.pack(pady=5)

        if os.path.exists(LOG_PERSISTENTE):
            with open(LOG_PERSISTENTE, "r") as l:
                dados = l.read()
                self.log_box.insert("1.0", dados)

        # Redirecionar o stdout para o textbox
        class StdoutRedirector:
            def __init__(self, textbox):
                self.textbox = textbox

            def write(self, message):
                if message.strip() != "":
                    self.textbox.insert("end", message + "\n")
                    self.textbox.see("end")  # rolar até o final

            def flush(self):  # necessário para compatibilidade
                pass

        sys.stdout = StdoutRedirector(self.log_box)
  
if __name__ == "__main__":
    app = App()
    app.mainloop()
