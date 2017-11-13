# coding: utf-8

from Grepers import *
from Logguer import *
import chardet


class Search():
    def __init__(self):
        self.find= False
        self.keyword=None
        self.data=None

class DefaultParser(Search):
    def __init__(self,file,keywords):
        super().__init__()
        try:
            '''
            with open(file) as f:
                for line in f.readlines():
                    if self.find == False:
                        is_found = grep_string(line, keywords)
                        if is_found[0] == True:
                            self.find = True
                            self.keyword = is_found[1]
                            self.data = is_found[2]
                            return
            '''
            with open(file, 'rb') as f:
                encodage = chardet.detect(f.read())

                f.seek(0)
                if encodage['encoding'] is not None:
                    for line in f.read().decode(encoding=encodage['encoding']).splitlines():
                        if self.find == False:
                            is_found = grep_string(line, keywords)
                            if is_found[0] == True:
                                self.find = True
                                self.keyword = is_found[1]
                                self.data = is_found[2]
                                return
        except Exception as e:
            logerror(file, e)


class Excel(Search):

    def __init__(self,file,keywords):
        super().__init__()
        ext = re.split("\.", file)[-1]
        if re.search("xl.$", ext):
            self.search_excel2003(file,keywords)
        else:
            self.search_excel2010(file,keywords)

    def search_excel2010(self,file,keywords):
            from openpyxl import load_workbook
            try:
                wb = load_workbook(filename=file, read_only=True)
                for ws in wb.worksheets:
                    if self.find == False:
                        for row in ws.rows:
                            for cell in row:
                                is_in_cell = grep_string(cell.value, keywords)
                                if is_in_cell[0] == True:
                                    self.find = True
                                    self.keyword= is_in_cell[1]
                                    self.data = is_in_cell[2]
                                    return
            except Exception as e:
                logerror(file, e)


    def search_excel2003(self,file,keywords):
        import xlrd
        try:
            wb = xlrd.open_workbook(file)
            for ws in wb.sheet_names():
                if self.find == False:
                    for row in range(wb.sheet_by_name(ws).nrows):
                        for cell in wb.sheet_by_name(ws).row_values(row):
                            is_in_cell = grep_string(cell, keywords)
                            if is_in_cell[0] == True:
                                self.find = True
                                self.keyword = is_in_cell[1]
                                self.data = is_in_cell[2]
                                return
        except Exception as e:
            logerror(file,e)


class Word(Search):
    def __init__(self, file, keywords):
        super().__init__()
        ext = re.split("\.", file)[-1]
        if re.search("do.$", ext):
            self.search_word2003(file, keywords)
        else:
            self.search_word2010(file, keywords)
    def search_word2010(self, file, keywords):
        import docx2txt
        try:
            text = docx2txt.process(file)
            for i in text.split('\n'):
                is_in_data = grep_string(i.strip(), keywords)
                if is_in_data[0] == True:
                    self.find = True
                    self.keyword = is_in_data[1]
                    self.data = is_in_data[2]
                    return
        except Exception as e:
            logerror(file,e)

    def search_word2003(self, file, keywords):
        import olefile

        ole = olefile.OleFileIO(file)
        #print(ole.listdir())
        pics = ole.openstream('WordDocument')
        data = pics.read()
        content=data.decode('iso8859').rstrip('\x00')
        for data in content.split('\n'):
            is_in_data=grep_string(data,keywords)
            if is_in_data[0] == True:
                self.find=True
                self.keyword=is_in_data[1]
                ### NEED TO EXTRACT THE DATA ###
                self.data = 'Please open the doc'
