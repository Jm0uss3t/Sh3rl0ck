# coding: utf-8


SEPARATOR=","
SUCCESS_FILE="success.csv"
DONE_FILE="done.txt"

def logfound(file,keyword,line):
    f=open(SUCCESS_FILE,'a')
    f.write(file+SEPARATOR+keyword+SEPARATOR+line+"\n")
    f.close()
    print(file+SEPARATOR+keyword+SEPARATOR+line)


def logdone(file):
    f=open(DONE_FILE,'a')
    f.write(file+"\n")
    f.close()

