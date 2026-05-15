import requests
from auth import get_session_key
from datetime import datetime
from utils import notify
import time

def main(username, password, CT):
    CT.tabview.set("LOG")
    notify("\n:: Automacao rodando, aguarde... :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    BASE_URL = "https://api.robbyson.com"
    TOKEN = get_session_key(username, password)

    session = requests.Session()

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

    notify("\n" + str(response.status_code) + " - " + response.text)

    data = response.json()

    cache_id = data["data"]["_id"]

    ### PASSO 2

    payload = {
        "goalImportingCache_id": cache_id,
        "timezone": 180
    }

    time.sleep(1)

    response_save = session.put(
        f"{BASE_URL}/goal/save-importing-cache",
        json=payload,
        timeout=60
    )

    if response_save.status_code != 200:
        notify("\n" + str(response_save.status_code) + " - " + response_save.text)
        raise Exception("Erro ao salvar")

    notify("\n" + str(response_save.status_code) + " - " + response_save.text)

    ### PASSO 3

    time.sleep(1)

    response_get = session.get(
        f"{BASE_URL}/goal/importingCache",
        params={
            "goalImportingCache_id": cache_id
        },
        timeout=60
    )

    if response_get.status_code != 200:
        notify("\n" + str(response_get.status_code) + " - " + response_get.text)
        raise Exception("Erro ao deletar cache")

    notify("\n" + str(response_get.status_code) + " - " + response_get.text)

    ### PASSO 4

    time.sleep(1)

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

    notify("\n" + str(response_delete.status_code) + " - " + response_delete.text)

    notify("\n:: Automacao encerrada :: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))