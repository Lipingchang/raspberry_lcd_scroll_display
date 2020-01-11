# -*- coding:utf8 -*-

from multiprocessing import Process, current_process
from time import sleep
import os
import sys
import psutil
import fcntl
from LCD import LCD

PROCESS_NAME = 'keepRunning'
LOG_FILE_PATH = '/var/log/lcd.log'
PID_FILE_PATH = '/var/log/lcd.pid'

l2c_addr = 0x27
max_len = 16 # lcd 的字符串宽度


def pid_file_is_locked():
    with open(PID_FILE_PATH, 'a') as pid_file:
        pid_fileno = pid_file.fileno()
        try:
            fcntl.flock(pid_fileno, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except:
            return True
        return False

def kill_pid_file():
    with open(PID_FILE_PATH, 'r') as pid_file:
        pid = pid_file.read()
        p = psutil.Process(int(pid))
        p.terminate()

def keep_running(msg):
    if pid_file_is_locked():
        kill_pid_file()
    
    pid_file = open(PID_FILE_PATH, 'w+')
    fcntl.flock(pid_file.fileno(), fcntl.LOCK_EX)
    pid_file.write('%d' % os.getpid())
    print('%d' % os.getpid())
    pid_file.flush()

    lcd = LCD(2, l2c_addr, True)
    lcd.clear()
    if len(msg) <= max_len:
        while True:
            lcd.message(msg, 1) 
            sleep(5)
    else:
        msg = msg + '   ' # 滚动的字符串之间的间隔
        start = 0
        while(True):
            display_msg = msg[start:start+max_len]
            if start + max_len > len(msg):
                display_msg = display_msg + msg[0: start+max_len-len(msg)]
            lcd.message(display_msg, 1);
            # print '>', display_msg, '<'
            start = start + 1
            if start == len(msg):
                start = 0
            sleep(1)
            
 
def main():
    # p = Process(name=PROCESS_NAME, target=keep_running, args=['123456789abcdefghijklmn'])
    msg = 'hello dick world' if len(sys.argv)<2 else sys.argv[1]  
    p = Process(name=PROCESS_NAME, target=keep_running, args=[msg])
    p.start();
    os._exit(0)

if __name__ == '__main__':
    main()

