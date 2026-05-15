import os
import sys
from datetime import datetime

def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def write_log(message):
    with open(f'log_{datetime.now().strftime("%Y-%m-%d")}.txt', 'a') as log_file:
        log_file.write(message + '\n')

def notify(message):
    print(message)
    write_log(message)