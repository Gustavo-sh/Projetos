import customtkinter as ctk
import os
import sys
import json
import time
from api import main
import threading
from utils import resource_path, notify

ctk.set_appearance_mode("dark")  # "light", "dark", "system"
ctk.set_default_color_theme("blue")  # cores: "blue", "green", "dark-blue"

def background_task(login, senha, lembrar_login, is_alteration, CT):
    if lembrar_login:
        with open(resource_path("config_login.json"), "w") as f:
            json.dump({"login": login}, f)
    thread_tarefa = threading.Thread(target=main, args=(login, senha, is_alteration, CT), daemon=True)
    thread_tarefa.start()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        folderCD = os.path.expanduser(r'~\.cache\selenium\chromedriver\win64')
        if os.path.exists(folderCD):
            archivesFolder = os.listdir(folderCD)
            if len(archivesFolder) >= 2:
                notify(fr"Favor remover chromedriver de versao antiga da pasta para que o programa funcione. Pasta: C:\Users\SEU USUARIO\.cache\selenium\chromedriver\win64")
                time.sleep(20)
                sys.exit()
        
        self.title("Importação de Metas - Robbyson")
        self.geometry("1100x600")

        # Criar um notebook (abas)
        self.tabview = ctk.CTkTabview(self, width=800, height=350)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        # Adicionar duas abas
        self.tabview.add("INICIO")
        self.tabview.add("LOG")

        # Chamar métodos para montar cada aba
        self.aba_inicio()
        self.aba_log()

    def aba_inicio(self):
        ARQUIVO_CONFIG = resource_path("config_login.json")
        tab1 = self.tabview.tab("INICIO")

        label1 = ctk.CTkLabel(tab1, text="Digite seu LOGIN:")
        label1.pack(pady=10)

        self.entry_nome = ctk.CTkEntry(tab1, justify="center", placeholder_text="LOGIN", width=250)
        self.entry_nome.pack(pady=5)

        if os.path.exists(ARQUIVO_CONFIG):
            with open(ARQUIVO_CONFIG, "r") as f:
                try:
                    dados = json.load(f)
                except:
                    dados = {}
                self.entry_nome.insert(0, dados.get("login", ""))

        label2 = ctk.CTkLabel(tab1, text="Digite sua SENHA:")
        label2.pack(pady=10)

        self.entry_senha = ctk.CTkEntry(tab1, justify="center", show="*", placeholder_text="SENHA", width=250)
        self.entry_senha.pack(pady=5)

        checkbox_lembrar = ctk.CTkCheckBox(master=tab1, text="Lembrar login", command=None, onvalue=True, offvalue=False)
        checkbox_lembrar.pack(pady=5)

        checkbox_alterations = ctk.CTkCheckBox(master=tab1, text="Alterar Matriz", command=None, onvalue=True, offvalue=False)
        checkbox_alterations.pack(pady=5)

        botao1 = ctk.CTkButton(tab1, text="Iniciar a automação", command=lambda: background_task(self.entry_nome.get(), self.entry_senha.get(), checkbox_lembrar.get(), checkbox_alterations.get(), self))
        botao1.pack(pady=10)

    def aba_log(self):
        LOG_PERSISTENTE = 'log.txt'
        tab2 = self.tabview.tab("LOG")

        label2 = ctk.CTkLabel(tab2, text="Log de Execução:")
        label2.pack(pady=10)

        # Caixa de texto para exibir o log
        self.log_box = ctk.CTkTextbox(tab2, width=1050, height=500)
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
                if message and message.strip():
                    self.textbox.insert("end", message + "\n")
                    self.textbox.see("end")  # rolar até o final

            def flush(self):  # necessário para compatibilidade
                pass

        sys.stdout = StdoutRedirector(self.log_box)
  
if __name__ == "__main__":
    app = App()
    app.mainloop()