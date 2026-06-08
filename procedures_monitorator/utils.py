from datetime import datetime

def logging_msg(msg):
    stacktrace = str(msg) + " - " + str(datetime.now()) + '\n'
    with open('monitoring_msg.txt', 'a') as log_file:
            log_file.write(stacktrace)