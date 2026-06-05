import requests
from auth import get_session_key
from datetime import datetime
from utils import notify, resource_path, write_log
import time
import subprocess
import pandas as pd
import pytz
import json

def search_attribute(session, token, id_indicador, data_inicio, atributo):
    tz = pytz.timezone("America/Sao_Paulo")
    data = tz.localize(
        datetime.strptime(data_inicio, "%d/%m/%Y")
    )
    timestamp = int(data.timestamp() * 1000)

    headers_get = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://app.robbyson.com',
        'priority': 'u=1, i',
        'referer': 'https://app.robbyson.com/',
        'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sessionkey': token,
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36',
        'x-system-id': '2',
    }

    params = {
        'active': 'true',
        'indicatorId': id_indicador,
        'keyWord': '',
        'page': '1',
        'per': '42',
        'searchAttributesValueDescription': atributo,
        'startDateEquals': timestamp,
    }

    response_get = session.get('https://api.robbyson.com/goal/adminList', params=params, headers=headers_get, timeout=60)

    notify("\n" + str(response_get.status_code) + " - Get do disable\n")
    write_log(response_get.text)
    notify(f":: Data inicio enviada neste get do disable: {data_inicio}, timestamp: {timestamp}, atributo: {atributo} ::")

    if response_get.status_code != 200:
        raise Exception(response_get.text)

    data = response_get.json()

    return data

def disable_attribute(session, token, indicator_id, mes_ano, atributo):

    data = search_attribute(session, token, indicator_id, mes_ano, atributo)
    
    items = data["data"]["items"]

    if not items:
        notify(f":: Pulando indicador {indicator_id} na data inicio {mes_ano}, pois não encontrou nenhum item :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return None

    ids = [item["_id"] for item in items]

    notify(":: IDs encontrados: " + ", ".join(ids) + " :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    headers_post = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://app.robbyson.com',
        'priority': 'u=1, i',
        'referer': 'https://app.robbyson.com/',
        'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sessionkey': token,
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36',
        'x-system-id': '2',
    }

    response_disable = session.post('https://api.robbyson.com/goal/disableMany', headers=headers_post, json={
            "_ids": ids
        }, timeout=60
    )

    notify("\n" + str(response_disable.status_code) + " - Post do disable")
    write_log(response_disable.text)

    if response_disable.status_code != 200:
        raise Exception(response_disable.text)

    time.sleep(1)

    return response_disable.json()

def main(username, password, is_alteration, CT):
    try:
        proxy_active = subprocess.run(resource_path("ligar_proxy.bat"), shell=True)
        if proxy_active.returncode != 0:
            notify(":: Falha ao ligar proxy, verifique o arquivo ligar_proxy.bat :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            exit()
        time.sleep(1)
        CT.tabview.set("LOG")
        notify("\n:: Automacao rodando, aguarde... :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        BASE_URL = "https://api.robbyson.com"
        TOKEN = None

        session = requests.Session()

        with open("config_session.json", "a+") as f:
            f.seek(0)
            try:
                dados = json.load(f)
            except:
                dados = {}
            TOKEN = dados.get("sessionKey", "")

        if not TOKEN:
            TOKEN = get_session_key(username, password)

        try:
            search_attribute(session, TOKEN, '901', '01/06/2026', 'TEST ATTRIBUTE') # to validate the session token
            notify(":: Token obtido do json validado com sucesso ::")
            deslig_proxy = resource_path("desligar_proxy.bat")
            proxy_inactive = subprocess.run(deslig_proxy, shell=True)
            if proxy_inactive.returncode != 0:
                notify(":: Falha ao desligar proxy, verifique o arquivo ligar_proxy.bat :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                exit()
        except Exception as e:
            if 'token' in str(e) or 'session' in str(e):
                notify(":: Token do json expirado, obtendo um novo token :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                write_log("\n:: erro_token ::\n" + str(e))
                TOKEN = get_session_key(username, password)

        headers = {
            'accept': 'application/json, text/plain, */*',
            'origin': 'https://app.robbyson.com',
            'referer': 'https://app.robbyson.com/',
            'sessionkey': TOKEN,
            'timezoneoffset': '180',
            'user-agent': 'Mozilla/5.0',
            'x-system-id': '2'
        }

        session.headers.update(headers)

        if is_alteration:
            notify("\n:: Iniciando desabilitação de atributos :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            df = pd.read_excel("ImportacaoMatriz.xls", sheet_name="Plan1")
            notify(f"Iniciando desativação para {len(df.index)} linhas em 5 segundos.\nPrimeiro atributo do arquivo: {df.iloc[0]['ATRIBUTOS']} :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            time.sleep(5)
            for indice, row in df.iterrows():
                if pd.isna(row["INDICADOR"]) or pd.isna(row["ATRIBUTOS"]) or pd.isna(row["DATA_INICIO"]) or pd.isna(row["DATA_FIM"]) or pd.isna(row["VALOR_META"]) or pd.isna(row["ATIVO"]):
                    notify(f":: Problema encontrado na linha {indice}, valide o arquivo e execute novamente :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    return
                disable_attribute(session, TOKEN, row["INDICADOR"], row['DATA_INICIO'], row["ATRIBUTOS"])
        
        ### PASSO 1

        with open("ImportacaoMatriz.xls", "rb") as f:

            files = {
                "file": f
            }

            response = session.post(
                f"{BASE_URL}/goal/import",
                files=files,
                timeout=60
            )

        if response.status_code != 200:
            notify("\n" + str(response.status_code) + " - " + response.text)
            raise Exception("Erro no import")

        notify("\n" + str(response.status_code) + " - Import")
        write_log("\n:: response_import ::\n" + response.text)

        data = response.json()

        cache_id = data["data"]["_id"]

        ### PASSO 2

        payload = {
            "goalImportingCache_id": cache_id,
            "timezone": 180
        }

        time.sleep(2)

        response_save = session.put(
            f"{BASE_URL}/goal/save-importing-cache",
            json=payload,
            timeout=60
        )

        if response_save.status_code != 200:
            notify("\n" + str(response_save.status_code) + " - " + response_save.text)
            raise Exception("Erro ao salvar")

        notify("\n" + str(response_save.status_code) + " - Save Importing Cache")
        write_log("\n:: response_save ::\n" + response_save.text)

        ### PASSO 3

        trys = 0

        while True:

            response_get = session.get(
                f"{BASE_URL}/goal/importingCache",
                params={
                    "goalImportingCache_id": cache_id
                },
                timeout=60
            )

            if response_get.status_code != 200:
                raise Exception(
                    f"Erro ao consultar cache: {response_get.status_code}"
                )

            data = response_get.json()

            status = data["data"]["status"]

            notify(
                f"Tentativa {trys + 1} - status: {status}"
            )

            if status.lower() == "done":
                notify(":: Processamento concluído ::")
                break
            elif status.lower() == "error":
                
                notify(data["data"]["processingErrors"])
                
                raise Exception(
                    "Erro no processamento \n"
                )

            trys += 1
            time.sleep(2)
            

        ### PASSO 4

        time.sleep(2)

        response_delete = session.delete(
            f"{BASE_URL}/goal/importingCache",
            params={
                "goalImportingCache_id": cache_id
            },
            timeout=60
        )

        if response_delete.status_code != 200:
            notify("\n" + str(response_delete.status_code) + " - " + response_delete.text)
            raise Exception("Erro ao deletar cache")

        notify("\n" + str(response_delete.status_code) + " - Delete Importing Cache")
        write_log("\n:: response_delete ::\n" + response_delete.text)

        notify("\n:: Automacao encerrada :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    except Exception as e:
        notify("\n:: Erro na automação :: " + str(e) + " :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))