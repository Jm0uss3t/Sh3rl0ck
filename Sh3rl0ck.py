# coding: utf-8
import time
import argparse
import os
import re
import Logguer
import Config
import Parsers
import threading
from Logguer import DONE_FILE
import json
import timeit
import queue
from pathlib import Path


FILELIST = "list.txt"
FILES={}
SEARCHEND=False
FILEQUEUE=queue.Queue(maxsize=0)
COUNTER = 0
ITERATION = 0
SEARCH_SEMAPHORE=None

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

def searchfiles(path,pattern):
    global FILES
    global FILEQUEUE
    global FILELIST
    for file in [os.path.join(root, name) for root, dirs, files in os.walk(path) for name in files if re.search(pattern,name)]:
        if file not in FILES:
            FILES[file] = 'todo'
            FILEQUEUE.put(file)
    print("Search complete " +path)

def analyzefile(keywords):
    global FILES
    global FILEQUEUE
    global COUNTER
    global ITERATION
    print('analyse')
    while (True):
        if ITERATION > 30:
            with threading.RLock():
                f=open(FILELIST,'w')
                f.write(json.dumps(FILES))
                f.close()
                ITERATION=0
        with threading.RLock():
            counter = len([t for t in threading.enumerate() if t.name == 'searcher'])
        if ((counter > 0) or (not FILEQUEUE.empty())):
            if (not FILEQUEUE.empty()):
                file=FILEQUEUE.get()
                filename = file.strip()
                file_parser = False
                ext = filename.split('.')[-1]
                parser = Config.PARSER
                for data in parser:
                    # look for the appropriated function to launch
                    if re.search(data[0].replace("*", "\\w*"), ext):
                        class_ = getattr(Parsers, data[1])
                        finder = class_(filename, keywords)
                        if finder.find == True:
                            Logguer.logfound(filename, finder.keyword, finder.data)
                        file_parser = True
                        break
                if file_parser == False:
                    finder = Parsers.DefaultParser(filename, keywords)
                    if finder.find == True:
                        Logguer.logfound(filename, finder.keyword, finder.data)
                FILES[file] = 'done'
                FILEQUEUE.task_done()
        else:
            break
        with threading.RLock():
            ITERATION+=1

    print('ANALYSE DONE')
    with threading.RLock():
        f = open(FILELIST, 'w')
        f.write(json.dumps(FILES))
        f.close()

def get_top_directory(path,pattern):
    global  FILES
    global FILEQUEUE
    root_dir =[]
    it = os.scandir(path)
    for entry in it:
        if entry.is_dir():
            root_dir.append(entry.path)
        elif re.search(pattern,entry.path):
            if entry.path not in FILES:
                FILES[entry.path] = 'todo'
                FILEQUEUE.put(entry.path)
    return  root_dir

def searcher(path,extensions):
    global COUNTER
    global SEARCH_SEMAPHORE
    with SEARCH_SEMAPHORE:
        with threading.Lock():
            COUNTER +=1
        searchfiles(path, extensions)
        with threading.Lock():
            COUNTER+=-1

def analyser(keywords):
    with threading.Semaphore(2):
        analyzefile(keywords)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-path", help="Share or path to search files", required=True)
    parser.add_argument("-ext", help="Extensions of files to search comma separated", required=False, default="config,xls*,doc*,xml,bat,cmd,pdf,vba,vbe")
    parser.add_argument("-keywords", help="Keyword comma separated", required=False, default='login,password,pwd')
    parser.add_argument("-resume", help="previously identified files", required=False)
    parser.add_argument("-scanned", help="increase output verbosity", default="./done.txt")
    args = parser.parse_args()

    if Path(FILELIST).is_file():
        Join = input('A previous session file has been found.\nDo you want load analyse status from it [Y/N]?')
        if Join.lower() == 'yes' or Join.lower() == 'y':
            print("load")
            FILE= json.loads(open(FILELIST).read())
            toanalyse = [key for key,value in FILE.items() if value == 'todo' ]
            for file in toanalyse:
                FILEQUEUE.put(file)

    # Generate regex with files extensions for research
    extensions = args.ext.split(',')
    pattern_extensions = '\.('
    for ext in extensions:
        pattern_extensions += ext.replace("*", "\\w*") + "|"
    pattern_extensions = pattern_extensions[:-1]
    pattern_extensions += ')$'

    # Launch one thread by directory found in the root directory
    # 4 thread will run simultanously
    SEARCH_SEMAPHORE = threading.Semaphore(4)
    for dir in get_top_directory(args.path,pattern_extensions):
        t = threading.Thread(target=searcher, name='searcher', args=(dir,pattern_extensions))
        t.start()

    # Generate and compile regex with keywords to search in files
    pattern_keywords = '('
    for keyword in args.keywords.split(','):
        if keyword not in [' ']:
            pattern_keywords+=keyword+'|'
    pattern_keywords=pattern_keywords[:-1]
    pattern_keywords+=')'
    regex_keyword=re.compile(pattern_keywords,re.MULTILINE|re.IGNORECASE)

    analyzer1 = threading.Thread(target=analyzefile, name='analyser',args=((regex_keyword,)))
    analyzer1.start()
    analyzer2 = threading.Thread(target=analyzefile, name='analyser',args=((regex_keyword,)))
    analyzer2.start()
