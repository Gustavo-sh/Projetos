import requests

TOKEN = "8427382302:AAGLT0_8PrmhelsWPpbX1Te2rCQ0ZOBETog"

resp = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": -5275539166, "text": "Teste novo bot"},
            timeout=15,
        )