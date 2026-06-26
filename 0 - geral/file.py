from asyncio import wait
from datetime import datetime
import json
import shutil
import sys
import threading
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import customtkinter as ctk

def start_driver():
    options = Options()
    options.add_argument("--start-maximized")
    #prefs = {"download.prompt_for_download": False, "download.default_directory": diretorio_aut}
    #options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=options)

def main_func(driver, wait):
    driver.get("https://pegasus/Orbi/modulo-administrativo/gerenciamento-perfis-concessao") 
    wait.until(EC.presence_of_element_located((By.ID, "Login"))).send_keys("e.gustavo.santos" + Keys.TAB + "GUS*963,*963," + Keys.TAB + Keys.ENTER)
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div[1]/div[2]/div/div/div[2]/div/table/thead/tr[2]/th[4]/input"))).send_keys("BÚSSOLA")
    #elemento = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div[2]/div[2]/div/div/div[3]/div[2]/div/ul/li[9]/a")))
    #driver.execute_script("arguments[0].scrollIntoView();", elemento)
    print("a")
    itens = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "li")))
    print("a")
    for item in itens:
        print(item.text)
    
    print("a")
    time.sleep(10)

driver = start_driver()
wait = WebDriverWait(driver, 90)
main_func(driver, wait)