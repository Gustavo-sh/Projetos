import customtkinter as ctk

# Configurações iniciais
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da janela
        self.title("Ícones Lado a Lado (Grid)")
        self.geometry("600x150")

        # Cria um frame para os ícones
        self.icon_frame = ctk.CTkFrame(self)
        self.icon_frame.pack(pady=20, padx=20, fill="x")

        # Cria os botões e os posiciona usando grid()
        # Todos ficam na linha 0, mas em colunas diferentes (0, 1, 2, 3)
        self.icon_1 = ctk.CTkButton(self.icon_frame, text="Icone 1")
        self.icon_1.grid(row=0, column=0, padx=5, pady=5)

        self.icon_2 = ctk.CTkButton(self.icon_frame, text="Icone 2")
        self.icon_2.grid(row=0, column=1, padx=5, pady=5)

        self.icon_3 = ctk.CTkButton(self.icon_frame, text="Icone 3")
        self.icon_3.grid(row=2, column=2, padx=5, pady=5)

        self.icon_4 = ctk.CTkButton(self.icon_frame, text="Icone 4")
        self.icon_4.grid(row=2, column=3, padx=5, pady=5)

        # Adiciona um rótulo para demonstrar que o grid é flexível
        self.label = ctk.CTkLabel(self, text="Outros elementos podem ser colocados aqui.")
        self.label.pack(pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()