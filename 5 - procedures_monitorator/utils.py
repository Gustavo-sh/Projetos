from datetime import datetime
import os

def logging_msg(msg):
    stacktrace = str(datetime.now()) + str(msg) + " - " +  '\n'
    dir = './logs/'
    os.makedirs(dir, exist_ok=True)
    file_path = os.path.join(dir, 'monitoring_msg.txt')
    with open(file_path, 'a') as log_file:
            log_file.write(stacktrace)