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

def start_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    prefs = {"download.prompt_for_download": False}
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=options)

def download_and_send_hominum(driver, wait):
    trys = 1
    try:
        print("TimeOut received, loop restarted.")
        print("opening the webpage of hominum")
        driver.get(r"https://paladio/PortalRelatorios/Quadro.aspx")
        wait.until(EC.presence_of_element_located((By.ID, "MainContent_txtLogin"))).send_keys("e.gustavo.santos" + Keys.TAB + "GUS*963,*963," + Keys.TAB + Keys.ENTER)
        driver.get(r"https://paladio/PortalRelatorios/Relatorios.aspx?IDLogo=5&FiltraTudo=0&NomeGrupo=Hominum")
        wait.until(EC.presence_of_element_located((By.ID, "2414"))).send_keys(Keys.ENTER, Keys.TAB + Keys.ENTER)
        time.sleep(3)

        janelas = driver.window_handles
        driver.switch_to.window(janelas[1])

        print("new page of hominum created")
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/form/div[3]/div/div/div[2]/span/div/table/tbody/tr[2]/td/div[1]/div/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/div/select"))).send_keys(Keys.ENTER + Keys.ARROW_DOWN + Keys.ARROW_DOWN + Keys.ENTER)
        time.sleep(20)
        wait.until(EC.presence_of_element_located((By.ID, "ctl00_MainContent_ReportViewer_ctl04_ctl00"))).click()
        print("waiting 180s to load page of hominum")
        time.sleep(180)
        wait.until(EC.presence_of_element_located((By.ID, "ctl00_MainContent_ReportViewer_ctl05_ctl04_ctl00_ButtonImg"))).click()
        time.sleep(3)
        print("download started")
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/form/div[3]/div/div/div[2]/span/div/table/tbody/tr[4]/td/div/div/div[4]/table/tbody/tr/td/div[2]/div[5]/a"))).click()
    except selenium.common.exceptions.TimeoutException:
        trys += 1
        print(f"try number {trys}")
        if trys == 6: 
            return "Script finished, page of hominum indisponible."
        
    hominum_downloads = os.path.expanduser("~/Downloads/00821_00.RELATORIO_DE_HIERARQUIAS_COMPLETO.xlsx")
    pasta_hominum = os.path.expanduser("~/Desktop/HOMINUM PALADIO/")
    hominum_pasta = os.path.expanduser("~/Desktop/HOMINUM PALADIO/00821_00.RELATORIO_DE_HIERARQUIAS_COMPLETO.xlsx")
    hominum_sharepoint = os.path.expanduser(r"C:\Users\e.gustavo.santos\AeC Centro de Contatos\database - RELATORIOS\BASES - RELATORIOS\HOMINUM")

    print("waiting until download of hominum finish")
    checks = 0
    while True:
        time.sleep(5)
        checks += 1
        if checks % 5 == 0: print(f"checks: {checks}") 
        if os.path.exists(hominum_downloads):
            time.sleep(10)
            os.remove(hominum_pasta)
            print("hominum_pasta removed")
            shutil.copy(hominum_downloads, hominum_pasta)
            print("hominum_downloads copied to hominum_pasta")
            time.sleep(10)
            shutil.copy(hominum_downloads, hominum_sharepoint)
            print("hominum_downloads copied to hominum_sharepoint")
            time.sleep(10)
            os.remove(hominum_downloads)
            print("hominum_downloads removed")
            break
        if trys == 200:
            return "script break - download of hominum has failed"

    query_path = r"c:\Users\e.gustavo.santos\Desktop\HOMINUM_TRATADO_v1.0.xlsm"
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

    driver.quit()

driver = start_driver()
wait = WebDriverWait(driver, 90)
download_and_send_hominum(driver, wait)