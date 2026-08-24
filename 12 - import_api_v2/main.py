from connect_db import exec_generator, update_importado_sistema_matriz
from file_manager import generate_files
from api import import_api
from utils import notify
from dotenv import load_dotenv
import os

load_dotenv(r"C:\Users\e.gustavo.santos.GRUPO_A&C\Documents\Projetos\12 - import_api_v2\.env")

def main():
    try:
        importacao, alteracao = exec_generator()
        if importacao or alteracao:
            print(f"Gerando {len(importacao)+len(alteracao)} linhas para importações no total.")
            generate_files(importacao, alteracao)
        import_api("e.gustavo.santos@aec.com.br", os.getenv("PASSWORD"))
        update_importado_sistema_matriz()
        notify("\nUpdate do importado efetuado, encerrando a automação...")
    except Exception as e:
        notify(f"Erro geral no orquestrador: {e}")
        raise

if __name__ == "__main__": 
    main()