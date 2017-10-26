# coding: utf-8
import re

def grep_string(content,keywords):
    data=str(content).strip()
    for keyword in keywords:
        m=re.search(keyword,data,re.MULTILINE|re.IGNORECASE)
        if m is not None: return [True,keyword,data]
    return [False]

