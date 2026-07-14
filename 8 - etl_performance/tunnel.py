import subprocess
import time
import socket
import os
from utils import write_log
import re

def tunnel_aberto():
    try:
        with socket.create_connection(("127.0.0.1", 26017), timeout=1):
            return True
    except OSError:
        return False

def start_tunnel():

    if tunnel_aberto():
        write_log("Encontrado túnel aberto.")

        kill_existing_tunnel()

    #GCLOUD = "C:\\Program Files (x86)\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\gcloud.cmd"
    GCLOUD = r"C:\GoogleCloudSDK\google-cloud-sdk\bin\gcloud.cmd"

    env = os.environ.copy()
    env["CLOUDSDK_CONFIG"] = r"C:\gcloud"

    process = subprocess.Popen(
        [
            GCLOUD,
            "compute",
            "start-iap-tunnel",
            "vm-postgresql-reports-2",
            "27017",
            "--local-host-port=127.0.0.1:26017",
            "--project",
            "robbyson-production",
            "--zone=us-east4-c"
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    inicio = time.time()
    while not tunnel_aberto():
        if process.poll() is not None:
            out, err = process.communicate()

            write_log(out)
            write_log(err)

            raise Exception("gcloud encerrou")
        
        if time.time() - inicio > 300:
            raise TimeoutError("Tunnel não abriu em 300 segundos.")
        
        write_log("Tunnel ainda não foi aberto, aguarando 5 segundos para tentar novamente...")
        time.sleep(5)

    write_log("Tunnel aberto, prosseguindo...")

def kill_existing_tunnel():

    saida = subprocess.check_output(
        ["netstat", "-ano"],
        text=True
    )

    for linha in saida.splitlines():

        if ":26017" in linha and "LISTENING" in linha:

            pid = re.split(r"\s+", linha.strip())[-1]

            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", pid],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            write_log(f"Tunnel existente (PID {pid}) finalizado.")
            return