import sqlite3 as sql_module
import sys, os, os.path
#import spacy
#from zmq import PROTOCOL_ERROR_ZMTP_MALFORMED_COMMAND_MESSAGE
from DutchSnomed import *
from DutchICD10 import *

#path = '%s.sqlite3' % os.path.join(
#    os.getcwd(), "data/SNOMED2ICD10")  #getcwd()

path = os.path.abspath('data/SNOMED2ICD10.sqlite3')

if not os.path.exists(path):
    raise IOError(
        'Database %s not available.'
        % path)
db = sql_module.connect(path, check_same_thread=False)
db_cursor = db.cursor()
db_cursor.execute("PRAGMA synchronous  = OFF;")
db_cursor.execute("PRAGMA journal_mode = OFF;")


class Mapping:
    
    def __init__(self):
        pass

    def SNOMED2ICD(self, snomed_id):
        query = u"SELECT match_type, code2 FROM Mapping WHERE code1=?"
        db_cursor.execute(query, (snomed_id,))
        r = db_cursor.fetchall()
        
        if not r: return []
        r = set(r)
        icd10_codes = []
        for t in r: 
            if ICD10Concept(t[1]) not in icd10_codes:
                icd10_codes.append(ICD10Concept(t[1]))
        return icd10_codes

    def ICD2SNOMED(self, icd_id):
        query = u"SELECT match_type, code1 FROM Mapping WHERE code2=?"
        db_cursor.execute(query, (icd_id,))
        r = db_cursor.fetchall()
        
        if not r: return None
        
        snomed_codes = []
        for t in r: 
            snomed_codes.append(ICD10Concept(t[1]))
        return snomed_codes

################## Main 
if __name__ == "__main__":
    map = Mapping()
    ls =  map.SNOMED2ICD(snomed_id="16623961000119100")
    print(ls)