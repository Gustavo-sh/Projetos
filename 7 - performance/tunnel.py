import subprocess
import time
import socket
import os
from utils import write_log


class Tunnel:

    def __init__(self):

        self.process = None

    def tunnel_aberto(self):
        try:
            with socket.create_connection(("127.0.0.1", 26017), timeout=1):
                return True
        except OSError:
            return False

    def start(self):

        if self.tunnel_aberto():
            write_log("Túnel já estava aberto...")
            return

        #GCLOUD = "C:\\Program Files (x86)\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\gcloud.cmd"
        GCLOUD = r"C:\GoogleCloudSDK\google-cloud-sdk\bin\gcloud.cmd"

        env = os.environ.copy()
        env["CLOUDSDK_CONFIG"] = r"C:\gcloud"

        self.process = subprocess.Popen(
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

        while not self.tunnel_aberto():
            if self.process.poll() is not None:
                out, err = self.process.communicate()

                write_log(out)
                write_log(err)

                raise Exception("gcloud encerrou")
            
            time.sleep(5)
            write_log("Tunnel ainda não foi aberto, aguarando 5 segundos para tentar novamente...")

    def stop(self):

        if self.process:

            self.process.kill()