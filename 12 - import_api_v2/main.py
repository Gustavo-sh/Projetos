from connect_db import exec_generator, update_sistema_matriz
from file_manager import generate_files
from api import import_api
from utils import notify
from dotenv import load_dotenv
import os

load_dotenv(r"C:\Users\e.gustavo.santos\Documents\Github\Projetos\12 - import_api_v2\.env")

def main():
    try:
        importacao, alteracao = exec_generator()
        generate_files(importacao, alteracao)
        import_api(os.getenv("USERNAME"), os.getenv("PASSWORD"))
        update_sistema_matriz()
    except Exception as e:
        notify(f"Erro geral no orquestrador: {e}")
        raise

if __name__ == "__main__": 
    main()