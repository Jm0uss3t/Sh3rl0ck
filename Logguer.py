# coding: utf-8


SEPARATOR=","
SUCCESS_FILE="success.csv"
DONE_FILE="done.txt"
ERROR_FILE="error.txt"
import threading

def logfound(file,keyword,line):
    f=open(SUCCESS_FILE,'a')
    f.write(file+SEPARATOR+keyword+SEPARATOR+line+"\n")
    f.close()
    #print(file+SEPARATOR+keyword+SEPARATOR+line)


def logdone(file):
    f=open(DONE_FILE,'a')
    f.write(file+"\n")
    f.close()

def logerror(file,error):
    with threading.RLock():
        f = open(ERROR_FILE, 'a')
        f.write(file + ' :' + str(error) + "\n")
        f.close()