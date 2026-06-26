from datetime import datetime
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pyautogui

diretorio_aut = os.path.dirname(os.path.abspath(__file__))

def main_func(driver, wait): 
    driver.get('https://1drv.ms/x/c/caf487f0f18e4ff2/EfJPjvHwh_QggMoD5AEAAAABMH99yb9zq0yk0UtQdVHSyQ?e=aPc07h')
    time.sleep(10) 
    x, y = 43, 207
    pyautogui.click(x=x, y=y)
    print(x, y)
    time.sleep(5) 
    x, y = 102, 300
    pyautogui.click(x=x, y=y)
    print(x, y)
    time.sleep(5) 
    x, y = 339, 357
    pyautogui.click(x=x, y=y)
    print(x, y)
    time.sleep(10) 

def start_driver():
    options = Options()
    options.add_argument("--start-maximized")
    prefs = {"download.prompt_for_download": False, "download.default_directory": diretorio_aut}
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=options)

def main():
    if os.path.exists(os.path.join(diretorio_aut, "Paleta de Cores.xlsx")):
        os.remove(os.path.join(diretorio_aut, "Paleta de Cores.xlsx"))
    folderCD = os.path.expanduser(r'~\.cache\selenium\chromedriver\win64')
    if os.path.exists(folderCD):
        archivesFolder = os.listdir(folderCD)
        if len(archivesFolder) >= 2:
            return print(fr"Favor remover chromedriver de versao antiga da pasta para que o programa funcione. Pasta: C:\Users\SEU USUARIO\.cache\selenium\chromedriver\win64")
    driver = start_driver()
    wait = WebDriverWait(driver, 90)
    main_func(driver, wait)

if __name__ == "__main__":
    main()


# def background_task(login, senha, lembrar, CT):
#     if lembrar:
#         with open("config_login.json", "w") as f:
#             json.dump({"login": login}, f)
#     thread_task = threading.Thread(target=main, args=(login, senha, CT), daemon=True)
#     thread_task.start()

# ctk.set_appearance_mode("dark")  # "light", "dark", "system"
# ctk.set_default_color_theme("blue")  # cores: "blue", "green", "dark-blue"

# class App(ctk.CTk):
#     def __init__(self):
#         super().__init__()

#         folderCD = os.path.expanduser(r'~\.cache\selenium\chromedriver\win64')
#         if os.path.exists(folderCD):
#             archivesFolder = os.listdir(folderCD)
#             if len(archivesFolder) >= 2:
#                 print(fr"Favor remover chromedriver de versao antiga da pasta para que o programa funcione. Pasta: C:\Users\SEU USUARIO\.cache\selenium\chromedriver\win64")
#                 time.sleep(20)
#                 sys.exit()
        
#         self.title("Tittle")
#         self.geometry("500x400")

#         # Criar um notebook (abas)
#         self.tabview = ctk.CTkTabview(self, width=480, height=350)
#         self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

#         # Adicionar duas abas
#         self.tabview.add("INICIO")
#         self.tabview.add("LOG")

#         # Chamar métodos para montar cada aba
#         self.aba_inicio()
#         self.aba_log()

#     def aba_inicio(self):
#         ARQUIVO_CONFIG = "config_login.json"
#         tab1 = self.tabview.tab("INICIO")

#         label1 = ctk.CTkLabel(tab1, text="Digite seu LOGIN:")
#         label1.pack(pady=10)

#         self.entry_nome = ctk.CTkEntry(tab1, justify="center", placeholder_text="LOGIN")
#         self.entry_nome.pack(pady=5)

#         if os.path.exists(ARQUIVO_CONFIG):
#             with open(ARQUIVO_CONFIG, "r") as f:
#                 dados = json.load(f)
#                 self.entry_nome.insert(0, dados.get("login", ""))

#         label2 = ctk.CTkLabel(tab1, text="Digite sua SENHA:")
#         label2.pack(pady=10)

#         self.entry_senha = ctk.CTkEntry(tab1, justify="center", show="*", placeholder_text="SENHA")
#         self.entry_senha.pack(pady=5)

#         checkbox_lembrar = ctk.CTkCheckBox(master=tab1, text="Lembrar login", command=None, onvalue=True, offvalue=False)
#         checkbox_lembrar.pack(pady=5) 

#         botao1 = ctk.CTkButton(tab1, text="Iniciar a automação", command=lambda: background_task(self.entry_nome.get(), self.entry_senha.get(), checkbox_lembrar.get(), self))
#         botao1.pack(pady=10)

#     def aba_log(self):
#         LOG_PERSISTENTE = 'log.txt'
#         tab2 = self.tabview.tab("LOG")

#         label2 = ctk.CTkLabel(tab2, text="Log de Execução:")
#         label2.pack(pady=10)

#         # Caixa de texto para exibir o log
#         self.log_box = ctk.CTkTextbox(tab2, width=450, height=200)
#         self.log_box.pack(pady=5)

#         if os.path.exists(LOG_PERSISTENTE):
#             with open(LOG_PERSISTENTE, "r") as l:
#                 dados = l.read()
#                 self.log_box.insert("1.0", dados)

#         # Redirecionar o stdout para o textbox
#         class StdoutRedirector:
#             def __init__(self, textbox):
#                 self.textbox = textbox

#             def write(self, message):
#                 if message.strip() != "":
#                     self.textbox.insert("end", message + "\n")
#                     self.textbox.see("end")  # rolar até o final

#             def flush(self):  # necessário para compatibilidade
#                 pass

#         sys.stdout = StdoutRedirector(self.log_box)
  
# if __name__ == "__main__":
#     app = App()
#     app.mainloop()