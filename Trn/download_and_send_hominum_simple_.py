import threading
import time
import os
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import win32com.client
import selenium
import sys
import customtkinter as ctk
import json
import pythoncom

sys.stdout.reconfigure(encoding='utf-8')

def start_driver():
    options = Options()
    options.add_argument("--start-maximized")
    #options.add_argument("--headless")
    prefs = {"download.prompt_for_download": False}
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=options)

trys = 1

def download_and_send_hominum(driver, wait, login, pw):
    folderCD = os.path.expanduser(r'~\.cache\selenium\chromedriver\win64')
    if os.path.exists(folderCD):
        archivesFolder = os.listdir(folderCD)
        if len(archivesFolder) >= 2:
            return print(fr"Favor remover chromedriver de versao antiga da pasta para que o programa funcione. Pasta: C:\Users\SEU USUARIO\.cache\selenium\chromedriver\win64")
    global trys
    print(f"try number {trys}")
    print("opening the webpage of hominum")
    driver.get(r"https://paladio/PortalRelatorios/Quadro.aspx")
    wait.until(EC.presence_of_element_located((By.ID, "MainContent_txtLogin"))).send_keys(login + Keys.TAB + pw + Keys.TAB + Keys.ENTER)
    time.sleep(3)
    while trys < 6:
        try: 
            driver.get(r"https://paladio/PortalRelatorios/Relatorios.aspx?IDLogo=5&FiltraTudo=0&NomeGrupo=Hominum")
            wait.until(EC.element_to_be_clickable((By.ID, "2414"))).send_keys(Keys.ENTER, Keys.TAB + Keys.ENTER)
            time.sleep(3)

            janelas = driver.window_handles
            driver.switch_to.window(janelas[1])

            print("new page of hominum created")
            wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div[2]/span/div/table/tbody/tr[2]/td/div[1]/div/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/div/select"))).send_keys(Keys.ENTER + Keys.ARROW_DOWN + Keys.ARROW_DOWN + Keys.ENTER)
            wait.until(EC.element_to_be_clickable((By.ID, "ctl00_MainContent_ReportViewer_ctl04_ctl29_ddDropDownButton"))).click()
            wait.until(EC.element_to_be_clickable((By.ID, "ctl00_MainContent_ReportViewer_ctl04_ctl29_divDropDown_ctl00"))).click()
            time.sleep(10)
            wait.until(EC.element_to_be_clickable((By.ID, "ctl00_MainContent_ReportViewer_ctl04_ctl00"))).click()
            print("waiting 180s to load page of hominum")
            time.sleep(120)
            wait.until(EC.element_to_be_clickable((By.ID, "ctl00_MainContent_ReportViewer_ctl05_ctl04_ctl00_ButtonImg"))).click()
            time.sleep(3)
            print("download started")
            wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[3]/div/div/div[2]/span/div/table/tbody/tr[4]/td/div/div/div[4]/table/tbody/tr/td/div[2]/div[5]/a"))).click()
            break
        except selenium.common.exceptions.TimeoutException:
            trys += 1
            if trys == 6: 
                return "Script finished, page of hominum indisponible."
            print("TimeOut received, loop restarted.")
            continue
        
    hominum_downloads = os.path.expanduser("~/Downloads/00821_00.RELATORIO_DE_HIERARQUIAS_COMPLETO.xlsx")
    hominum_pasta = os.path.expanduser("~/Desktop/HOMINUM PALADIO/00821_00.RELATORIO_DE_HIERARQUIAS_COMPLETO.xlsx")
    #hominum_sharepoint = os.path.expanduser(r"~\AeC Centro de Contatos\database - BASES - RELATORIOS\HOMINUM")

    if os.path.exists(hominum_downloads):
        os.remove(hominum_downloads)
        print("old hominum in downloads removed")

    print("waiting until download of hominum finish")
    print("from now on every 'check' corresponding to 25 seconds, it may take a while depending on the hominum page")
    checks = 0
    while True:
        time.sleep(5)
        checks += 1
        if checks % 5 == 0: print(f"checks: {checks}") 
        if os.path.exists(hominum_downloads):
            time.sleep(5)
            os.remove(hominum_pasta)
            time.sleep(5)
            shutil.copy(hominum_downloads, hominum_pasta)
            time.sleep(5)
            # shutil.copy(hominum_downloads, hominum_sharepoint)
            # time.sleep(5)
            os.remove(hominum_downloads)
            print("all done with hominum")
            break
        if checks == 200:
            return "script break - download of hominum has failed"

    try:
        pythoncom.CoInitialize()

        query_path = os.path.expanduser(r"~\Desktop/HOMINUM_TRATADO_v1.0.xlsm")
        excel = win32com.client.DispatchEx('Excel.Application')
        excel.Visible = False
        print("new instance created - opening hominum excel")
        wb = excel.Workbooks.Open(query_path)
        time.sleep(10)
        wb.RefreshAll()
        
        print("refreshing hominum excel and sending him by email")
        time.sleep(120)
        wb.Save()
        excel.Application.Run("EnviarArquivoPorEmail")
        time.sleep(20)
        wb.Close(False)
        excel.Quit()
        print("email sent - script finished")
    except Exception as e:
        print(f"Erro na automação do Excel: {e}")
    finally:
        pythoncom.CoUninitialize()

    driver.quit()

def main(login, pw, lembrar_login):
    chromedriver = os.path.expanduser(r'~\.cache\selenium\chromedriver\win64')
    if os.path.exists(chromedriver):
        if len(os.listdir(chromedriver)) >= 2:
            shutil.rmtree(chromedriver+"\\")
    if lembrar_login:
        with open(ARQUIVO_CONFIG, "w") as f:
            json.dump({"login": login_et.get()}, f)
    driver = start_driver()
    wait = WebDriverWait(driver, 90)
    download_and_send_hominum(driver, wait, login, pw)
    
def background_task(login, senha, lembrar_login):
    thread_tarefa = threading.Thread(target=main, args=(login, senha, lembrar_login), daemon=True)
    thread_tarefa.start()

ARQUIVO_CONFIG = "config_login.json"

ctk.set_appearance_mode('dark')
app = ctk.CTk()
app.title("Download and sent hominum")
app.geometry("400x300")

login_lb = ctk.CTkLabel(app, text="Login:")
login_lb.pack(pady=3)
login_et = ctk.CTkEntry(app, placeholder_text="Digite seu login hominum", justify="center", width=200)
login_et.pack(pady=3)

if os.path.exists(ARQUIVO_CONFIG):
    with open(ARQUIVO_CONFIG, "r") as f:
            dados = json.load(f)
            login_et.insert(0, dados.get("login", ""))

pw_lb = ctk.CTkLabel(app, text="Password:")
pw_lb.pack(pady=3)
pw_et = ctk.CTkEntry(app, placeholder_text="Digite sua senha hominum", show="*", justify="center", width=200)
pw_et.pack(pady=3)

checkbox_lembrar = ctk.CTkCheckBox(master=app, text="Lembrar login", command=None, onvalue=True, offvalue=False)
checkbox_lembrar.pack(pady=5)

button = ctk.CTkButton(app, text="init", command=lambda: background_task(login_et.get(), pw_et.get(), checkbox_lembrar.get()))
button.pack(pady=10)

kill_process_button = ctk.CTkButton(app, text="kill process", command=app.destroy)
kill_process_button.pack(pady=10)

app.mainloop()
