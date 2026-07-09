import subprocess
import time
import socket
import os


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
            print("Túnel já estava aberto...")
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
            ],
            env=env,
        )

        while not self.tunnel_aberto():
            time.sleep(2)

    def stop(self):

        if self.process:

            self.process.kill()