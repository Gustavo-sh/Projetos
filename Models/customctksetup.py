import json
import os
import sys
import time
import customtkinter as ctk

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
        
        self.title("Titulo")
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

        botao1 = ctk.CTkButton(tab1, text="Iniciar a automação", command=lambda: self.iniciar())
        botao1.pack(pady=10)

    def aba_log(self):
        tab2 = self.tabview.tab("LOG")

        label2 = ctk.CTkLabel(tab2, text="Log de Execução:")
        label2.pack(pady=10)

        # Caixa de texto para exibir o log
        self.log_box = ctk.CTkTextbox(tab2, width=400, height=200)
        self.log_box.pack(pady=5)

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

    def iniciar(self):
        tab1 = self.tabview.tab("INICIO")
        botao1 = ctk.CTkButton(tab1, text="Printar 1+1", command=lambda: print(1+1))
        botao1.pack(pady=10)
    
if __name__ == "__main__":
    app = App()
    app.mainloop()

# folderCD = os.path.expanduser(r'~\.cache\selenium\chromedriver\win64')
# if os.path.exists(folderCD):
#     archivesFolder = os.listdir(folderCD)
#     if len(archivesFolder) >= 2:
#         print(fr"Favor remover chromedriver de versao antiga da pasta para que o programa funcione. Pasta: C:\Users\SEU USUARIO\.cache\selenium\chromedriver\win64")
#         time.sleep(15)
#         sys.exit()

# ARQUIVO_CONFIG = "config_login.json"

# ctk.set_appearance_mode('dark')
# app = ctk.CTk()
# app.title("Chamados de Acesso")
# app.geometry("400x300")

# login_lb = ctk.CTkLabel(app, text="Login:")
# login_lb.pack(pady=3)
# login_et = ctk.CTkEntry(app, placeholder_text="Digite seu login GX", justify="center", width=200)
# login_et.pack(pady=3)

# if os.path.exists(ARQUIVO_CONFIG):
#     with open(ARQUIVO_CONFIG, "r") as f:
#             dados = json.load(f)
#             login_et.insert(0, dados.get("login", ""))

# pw_lb = ctk.CTkLabel(app, text="Password:")
# pw_lb.pack(pady=3)
# pw_et = ctk.CTkEntry(app, placeholder_text="Digite sua senha GX", show="*", justify="center", width=200)
# pw_et.pack(pady=3)

# checkbox_lembrar = ctk.CTkCheckBox(master=app, text="Lembrar login", command=None, onvalue=True, offvalue=False)
# checkbox_lembrar.pack(pady=5)

# button = ctk.CTkButton(app, text="Iniciar a automação", command=lambda: background_task(login_et.get(), pw_et.get(), checkbox_lembrar.get()))
# button.pack(pady=10)

# app.mainloop()