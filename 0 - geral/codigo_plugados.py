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
import sys

sys.stdout.reconfigure(encoding='utf-8')

def iniciar_driver():
    options = Options()
    options.add_argument("--start-maximized")
    prefs = {"download.prompt_for_download": False}
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=options)

def login(driver, wait):
    driver.get("https://plugadosead.fiqueligadonews.com.br/login?returnTo=%2Fplugados%2Flogin")
    wait.until(EC.presence_of_element_located((By.ID, "branch"))).click()
    webdriver.ActionChains(driver).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()

    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("login" + Keys.ENTER)
    wait.until(EC.presence_of_element_located((By.ID, "password")))

    driver.find_element(By.ID, "username").clear()
    driver.find_element(By.ID, "username").send_keys("login")
    driver.find_element(By.ID, "password").send_keys("senha" + Keys.ENTER)

    wait.until(EC.url_to_be("https://plugadosead.fiqueligadonews.com.br/dashboard"))
    print("✅ Login realizado com sucesso.")

def preparar_pagina(driver, wait):
    driver.get("https://plugadosead.fiqueligadonews.com.br/admin/relatorios/aderencia/novo")
    time.sleep(60)
    input_element = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/app-report-adherence-new/div/div[2]/div[2]/div[2]/ng-select/div/div/div[3]/input")))
    input_element.click()
    webdriver.ActionChains(driver).send_keys(Keys.ARROW_UP).send_keys(Keys.ENTER).perform()
    print("✅ Página preparada para geração de relatório.")

def gerar_e_baixar(driver, wait):
    generate_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/div/app-report-adherence-new/div/div[1]/div/div[2]/app-report-create/button")))
    generate_button.click()
    print("⏳ Gerando relatório... Aguardando 5 minutos.")
    time.sleep(300)

    view_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/div/app-report-adherence-new/div/div[1]/div/div[2]/button")))
    view_button.click()
    time.sleep(10)

    download_link = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/ngb-modal-window/div/div/div[2]/div/div/ngx-datatable/div/datatable-body/datatable-selection/datatable-scroller/datatable-row-wrapper[1]/datatable-body-row/div[2]/datatable-body-cell[5]/div/a")))
    download_link.click()
    time.sleep(10)
    print("✅ Download iniciado...")

    time.sleep(15)
    close_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/ngb-modal-window/div/div/div[1]/button/span")))
    close_button.click()
    print("❎ Modal de resultados fechado.")

    # Diretórios
    download_folder = os.path.expanduser("~/Downloads")
    destino_folder = os.path.expanduser("~/Documents/PLUGADOS/BASE")

    print("🕵️ Aguardando finalização do download...")
    downloaded_file = None

    while not downloaded_file:
        files = [f for f in os.listdir(download_folder) if f.endswith(".xlsx") and not f.endswith(".crdownload")]
        if files:
            files.sort(key=lambda f: os.path.getmtime(os.path.join(download_folder, f)), reverse=True)
            downloaded_file = files[0]
        else:
            time.sleep(2)

    full_download_path = os.path.join(download_folder, downloaded_file)

    # Limpa destino
    if os.path.exists(destino_folder):
        for f in os.listdir(destino_folder):
            file_path = os.path.join(destino_folder, f)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Erro ao deletar {file_path}: {e}")
    else:
        os.makedirs(destino_folder)

    # Move para BASE
    destino_arquivo = os.path.join(destino_folder, downloaded_file)
    try:
        shutil.copy(full_download_path, destino_arquivo)
        print(f"📁 Arquivo movido para {destino_folder}")
    except Exception as e:
        print(f"❌ Erro ao mover o arquivo: {e}")

    # Atualiza QUERY
    query_path = r"C:\Users\lucas.dsnobrega\Documents\PLUGADOS\QUERY\QUERY.xlsx"
    print("🔄 Abrindo e atualizando QUERY.xlsx...")
    time.sleep(10)

    excel = win32com.client.gencache.EnsureDispatch('Excel.Application')
    excel.Visible = False
    wb = excel.Workbooks.Open(query_path)
    wb.RefreshAll()

    print("⏳ Aguardando 3 minutos para atualização da QUERY...")
    time.sleep(180)

    wb.Save()
    wb.Close(False)
    excel.Quit()
    print("✅ QUERY.xlsx atualizada e salva.")

    destino_final = r"C:\Users\lucas.dsnobrega\AeC Centro de Contatos\TREINAMENTO CLARO BRASIL - ORBI CLARO"
    try:
        shutil.copy(query_path, os.path.join(destino_final, "QUERY.xlsx"))
        print("📁 QUERY.xlsx copiada para destino final com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao copiar QUERY.xlsx: {e}")

def main():
    driver = iniciar_driver()
    wait = WebDriverWait(driver, 90)

    try:
        login(driver, wait)
        preparar_pagina(driver, wait)

        while True:
            gerar_e_baixar(driver, wait)
            print("⏳ Aguardando 1 hora até próxima execução...")
            time.sleep(60 * 60)

    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")

    finally:
        print("🔁 Loop encerrado (ou falhou).")

if __name__ == "__main__":
    main()
