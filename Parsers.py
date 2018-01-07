# coding: utf-8

from Grepers import *
from Logguer import *
import chardet
import olefile


class Search():
    def __init__(self):
        self.find= False
        self.keyword=None
        self.data=None

class DefaultParser(Search):
    def __init__(self,file,keywords):
        super().__init__()
        try:
            f=open(file, 'rb')
            for line in f:
                encodage = chardet.detect(line)
                print(encodage['encoding'])
                print(line.decode(encodage['encoding']))
                if self.find == False:
                    is_found = grep_string(line.decode(encodage['encoding']), keywords)
                    if is_found[0] == True:
                        self.find = True
                        self.keyword = is_found[1]
                        self.data = is_found[2]
                        f.close()
                        return
            f.close()
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
                                    wb._archive.close()
                                    del wb
                                    return
                wb._archive.close()
                del wb
            except Exception as e:
                logerror(file, e)


    def search_excel2003(self,file,keywords):
        import xlrd
        try:
            wb = xlrd.open_workbook(file, on_demand = True)
            for ws in wb.sheet_names():
                if self.find == False:
                    for row in range(wb.sheet_by_name(ws).nrows):
                        for cell in wb.sheet_by_name(ws).row_values(row):
                            is_in_cell = grep_string(cell, keywords)
                            if is_in_cell[0] == True:
                                self.find = True
                                self.keyword = is_in_cell[1]
                                self.data = is_in_cell[2]
                                wb.release_resources()
                                del wb
                                return
            wb.release_resources()
            del wb
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
                    del text
                    return
            del text
        except Exception as e:
            logerror(file,e)

    def search_word2003(self, file, keywords):
        import olefile
        try:
            ole = olefile.OleFileIO(file)
            #print(ole.listdir())
            pics = ole.openstream('WordDocument')
            data = pics.read()
            content=data.decode('iso8859').rstrip('\x00')
            for data in content.split('\n'):
                is_in_data=grep_string(data,keywords)
                print (data)
                if is_in_data[0] == True:
                    self.find=True
                    self.keyword=is_in_data[1]
                    ### NEED TO EXTRACT THE DATA ###
                    self.data = is_in_data[2]
                    ole.close()
                    del ole
                    return
            ole.close()
            del ole
        except Exception as e:
            logerror(file, e)

class Outlook(Search):
    def __init__(self, file, keywords):
        super().__init__()
        try:
            file = olefile.OleFileIO(file)
            if file.exists('__substg1.0_1000001E'):
                stream_dir = '__substg1.0_1000001E'
            elif file.exists('__substg1.0_1000001F'):
                stream_dir = '__substg1.0_1000001F'
            stream = file.openstream(stream_dir)
            data = stream.read()
            encoding = chardet.detect(data)
            content = data.decode(encoding['encoding'])
            for line in content.splitlines():
                is_in_data = grep_string(line.strip(), keywords)
                if is_in_data[0] == True:
                    self.find = True
                    self.keyword = is_in_data[1]
                    self.data = is_in_data[2]
                    file.close()
                    del file
                    return
            file.close()
            del file
            return
        except Exception as e:
          logerror(file, e)
