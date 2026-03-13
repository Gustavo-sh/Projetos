import customtkinter as ctk

# Configurações iniciais
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da janela
        self.title("Ícones Lado a Lado")
        self.geometry("400x150")

        # Cria um frame que será o nosso contêiner para os ícones
        # Usar um frame é a melhor prática para organizar grupos de widgets
        self.icon_frame = ctk.CTkFrame(self)
        self.icon_frame.pack(pady=20, padx=20, fill="x")

        # Cria os botões que atuarão como ícones e os empacota com side='left'
        # O pack() vai colocando um widget ao lado do outro, da esquerda para a direita
        self.icon_1 = ctk.CTkButton(self.icon_frame, text="Icone 1")
        self.icon_1.pack(side="left", padx=5)

        self.icon_2 = ctk.CTkButton(self.icon_frame, text="Icone 2")
        self.icon_2.pack(side="left", padx=5)

        self.icon_3 = ctk.CTkButton(self.icon_frame, text="Icone 3")
        self.icon_3.pack(side="left", padx=5)

        self.icon_4 = ctk.CTkButton(self.icon_frame, text="Icone 4")
        self.icon_4.pack(side="left", padx=5)

if __name__ == "__main__":
    app = App()
    app.mainloop()