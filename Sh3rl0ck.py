# coding: utf-8

import argparse
import os
import re
import Logguer
import Config
import Parsers
from Logguer import DONE_FILE

FILELIST = "list.txt"

def get_done_files():
    list=[]
    try:
        f=open(DONE_FILE,'r')
        for file in f:
            list.append(file.strip())
    except Exception:
        pass
    return list

def resume_scan(previous_list):

    if previous_list == FILELIST:
        print("Error previous file should not be named " + FILELIST)
        exit(1)
    else:
        try:

            file_list=open(previous_list)
            f = open(FILELIST, 'wb')
            done = get_done_files()
            for file in file_list:
                if file.strip() not in done:
                    f.write(file.strip().encode('utf8') + '\n'.encode('utf8'))
            f.close()
            file_list.close()
        except Exception:
            print(str(Exception))
            print("Error when parsing the previous file")
            exit(1)

def searchfiles(path,extensions):
    pattern='\.('
    print('Searching files')
    for ext in extensions:
        pattern+=ext.replace("*","\\w*")  +"|"
    pattern=pattern[:-1]
    pattern+=')$'
    fileliste = [os.path.join(root, name) for root, dirs, files in os.walk(path) for name in files if re.search(pattern,name)]
    f=open(FILELIST,'wb')
    done=get_done_files()
    for file in fileliste:
        if file not in done:
            f.write(file.encode('utf8')+'\n'.encode('utf8'))
        else:
            print("already done")
    f.close()
    print("Search complete")

def analysefile(keywords):
    print('File analysis begin')
    f=open(FILELIST,'r',encoding='utf8')
    for file in f.readlines():
        filename=file.strip()
        file_parser = False
        ext=filename.split('.')[-1]
        parser = Config.PARSER
        for data in parser:
        # look for the appropriated function to launch
            if re.search(data[0].replace("*","\\w*"),ext):
                class_ = getattr(Parsers, data[1])
                finder = class_(filename,keywords)
                if finder.find == True:
                    Logguer.logfound(filename,finder.keyword,finder.data)
                file_parser = True
                break
        if file_parser == False:
            print('Recherche par defaut ')
        #A mettre dans recherche effectuée
        Logguer.logdone(filename)
    f.close()



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-path", help="Share or path to search files", required=False)
    parser.add_argument("-ext", help="Extensions of files to search comma separated", required=False, default="config,xls*,doc*,xml,bat,cmd,pdf,vba,vbe")
    parser.add_argument("-keywords", help="Keyword comma separated", required=False, nargs='+', default=["login","password","pwd"])
    parser.add_argument("-login", help="login to access the share", required=False)
    parser.add_argument("-password", help="password to access the share", required=False)
    parser.add_argument("-resume", help="previously identified files", required=False)
    parser.add_argument("-scanned", help="increase output verbosity", default="./done.txt")
    args = parser.parse_args()

    print (args.ext)
    ''' We list files '''
    if args.resume != None:
        print('Resume scan')
        resume_scan(args.resume)
    else:
        searchfiles(args.path,args.ext.split(','))
    '''We search in file content'''
    analysefile(args.keywords)