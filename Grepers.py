# coding: utf-8
import re

def grep_string(content,regex):
    data=str(content).strip()
    m=regex.search(data)
    if m is not None: return [True,m.group(0),data]
    return [False]