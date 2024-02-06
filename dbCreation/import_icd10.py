
import sys, os, os.path
import spacy
nlp = spacy.load("nl_core_news_md")

full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)
ICD10_DIR = os.path.join(path,"ICD10")#"/home/jiba/telechargements/base_med/icd10"

# (optional) Get CIM10 French translation and extension from ATIH (NB choose "XML" format) :
# http://www.atih.sante.fr/plateformes-de-transmission-et-logiciels/logiciels-espace-de-telechargement/id_lot/456

CIM10_DIR = False #"/home/jiba/telechargements/base_med/cim10"


CODE_2_CHAPTER = {
  "A00-B99" : "I",
  "C00-D48" : "II",
  "D50-D89" : "III",
  "E00-E90" : "IV",
  "F00-F99" : "V",
  "G00-G99" : "VI",
  "H00-H59" : "VII",
  "H60-H95" : "VIII",
  "I00-I99" : "IX",
  "J00-J99" : "X",
  "K00-K93" : "XI",
  "L00-L99" : "XII",
  "M00-M99" : "XIII",
  "N00-N99" : "XIV",
  "O00-O99" : "XV",
  "P00-P96" : "XVI",
  "Q00-Q99" : "XVII",
  "R00-R99" : "XVIII",
  "S00-T98" : "XIX",
  "V01-Y98" : "XX",
  "Z00-Z99" : "XXI",
  "U00-U99" : "XXII",
  }

import sys, os, os.path, stat, sqlite3

if len(sys.argv) >= 3:
  ICD10_DIR = sys.argv[1]
  CIM10_DIR = sys.argv[2]


import xml.sax as sax, xml.sax.handler as handler

if sys.version[0] == "2":
  from StringIO import StringIO
else:
  from io import StringIO

HERE = "." #os.path.dirname(sys.argv[0]) or "."
#sys.path.append(os.path.join(HERE, ".."))

from db import *

SQLITE_FILE = os.path.join(HERE, "ICD10DUT.sqlite3")

db = create_db(SQLITE_FILE)
db_cursor = db.cursor()

#r = open("/tmp/log.sql", "w")
def do_sql(sql, *args):
  #r.write(sql)
  #r.write(";\n")
  db_cursor.execute(sql, *args)
  
def sql_escape(s): return s.replace(u'"', u'""').replace(u'\r', u'').replace(u'\x92', u"'")


do_sql(u"PRAGMA synchronous  = OFF")
do_sql(u"PRAGMA journal_mode = OFF")

do_sql(u"""
CREATE TABLE Concept (
  id INTEGER PRIMARY KEY,
  parent_code VARCHAR(7),
  code VARCHAR(7),
  term TEXT,
  dagger INTEGER,
  star INTEGER,
  mortality1 TEXT,
  mortality2 TEXT,
  mortality3 TEXT,
  mortality4 TEXT,
  morbidity TEXT,
  atih_extension INTEGER,
  pmsi_restriction INTEGER
)
""")

do_sql(u"""
CREATE TABLE Concept_lemmatized (
  id INTEGER,
  term TEXT
  )
""")

do_sql(u"""
CREATE TABLE Text (
  id INTEGER PRIMARY KEY,
  code VARCHAR(7),
  relation VARCHAR(13),
  text TEXT,
  dagger INTEGER,
  reference TEXT
)
""")

CONCEPTS = {}
class Concept(object):
  def __init__(self, code):
    self.parent_code      = ""
    self.code             = code
    self.term          = ""
    self.dagger           = 0
    self.star             = 0
    self.mortality1       = ""
    self.mortality2       = ""
    self.mortality3       = ""
    self.mortality4       = ""
    self.morbidity        = ""
    self.atih_extension   = 0
    self.pmsi_restriction = 0
    self.texts            = []
    CONCEPTS[code] = self

  def add_text(self, relation, text_en, dagger, reference):
    self.texts.append((relation, text_en, dagger, reference))
    
  def sql(self):
    if self.mortality1 == u"UNDEF": self.mortality1 = u""
    if self.mortality2 == u"UNDEF": self.mortality2 = u""
    if self.mortality3 == u"UNDEF": self.mortality3 = u""
    if self.mortality4 == u"UNDEF": self.mortality4 = u""
    if self.morbidity  == u"UNDEF": self.morbidity  = u""
    return u"""(NULL, "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")""" % (self.parent_code, self.code, sql_escape(self.term), self.dagger, self.star, self.mortality1, self.mortality2, self.mortality3, self.mortality4, self.morbidity, self.atih_extension, self.pmsi_restriction)

  def sql_text(self):
    return [
      u"""(NULL, "%s", "%s", "%s", "%s", "%s")""" % (self.code, relation, sql_escape(text), dagger, reference)
      for (relation, text, dagger, reference) in self.texts
      ]

class Handler(handler.ContentHandler):
  def __init__(self):
    self.concept   = None
    self.inhibited = 0
    self.content   = u""
    self.reference = u""
    
  def startElement(self, name, attrs):
    if self.inhibited: return
    
    if   name == "Fragment":
      self.content = u"%s " % self.content.strip()
      if attrs.get("usage") == "dagger":
        self.dagger = 1
        
    elif name == "Reference":
      self.content = u"%s " % self.content.strip()
      
    elif name == "Label":
      self.content   = u""
      self.reference = u""
      self.dagger    = 0
      
    if   (name == "Modifier") or (name == "ModifierClass"):
      self.inhibited += 1
      
    elif name == "Class":
      self.concept = Concept(attrs["code"])
      if attrs.get("usage") == "dagger": self.concept.dagger = 1
      if attrs.get("usage") == "aster":  self.concept.star   = 1
      
    elif name == "SuperClass":
      self.concept.parent_code = attrs["code"]
      
    elif name == "Meta":
      if   attrs["name"] == "MortL1Code": self.concept.mortality1 = attrs["value"]
      elif attrs["name"] == "MortL2Code": self.concept.mortality2 = attrs["value"]
      elif attrs["name"] == "MortL3Code": self.concept.mortality3 = attrs["value"]
      elif attrs["name"] == "MortL4Code": self.concept.mortality4 = attrs["value"]
      elif attrs["name"] == "MortBCode" : self.concept.morbidity  = attrs["value"]
      
    elif name == "Rubric":
      self.kind = attrs["kind"]
      
    elif name == "Reference":
      self.reference = attrs.get("code", u"")
      
  def endElement(self, name):
    if (name == "Modifier") or (name == "ModifierClass"): self.inhibited -= 1
    if self.inhibited: return

    self.content = self.content.strip()
    if self.content:
      if   name == "Label":
        if   self.kind == "preferred": self.concept.term = self.content
        else:
          self.concept.add_text(self.kind, self.content, self.dagger, self.reference)
          
      elif name == "Reference":
        if not self.reference: self.reference = self.content.strip().split()[-1]
        
      elif name == "Fragment":
        if self.content.endswith(":"): self.content = self.content[:-1]
        
  def characters(self, content):
    if self.inhibited: return
    self.content += content
  

xml = open(os.path.join(ICD10_DIR, "20211214_ICD-10-2021v2-C.xml")).read()
xml = xml.replace("""<!DOCTYPE ClaML SYSTEM "ClaML.dtd">""", "")
xml = StringIO(xml)
parser = sax.make_parser()
parser.setContentHandler(Handler())
parser.parse(xml)



      
for concept in CONCEPTS.values():
  do_sql(u"INSERT INTO Concept VALUES %s" % concept.sql())
  
for concept in CONCEPTS.values():
  for sql in concept.sql_text():
    do_sql(u"INSERT INTO Text VALUES %s" % sql)

do_sql(u"""CREATE UNIQUE INDEX Concept_code_index ON Concept(code)""")
do_sql(u"""CREATE INDEX Concept_parent_code_index ON Concept(parent_code)""")

do_sql(u"""CREATE INDEX Text_code_index          ON Text(code)""")
do_sql(u"""CREATE INDEX Text_code_relation_index ON Text(code, relation)""")


select_query = "SELECT id, term FROM Concept;"
db_cursor.execute(select_query)
r = db_cursor.fetchall()
for concept in r:
  id = concept[0]
  cpt = concept[1]
  cpt_lemma =  nlp(concept[1])[0:].lemma_
  cpt += ' || ' + cpt_lemma if cpt.lower() != cpt_lemma else '' 

  do_sql(u"""INSERT INTO Concept_lemmatized(id, term) VALUES(?, ?);""", (id, cpt))

do_sql(u"""CREATE VIRTUAL TABLE Concept_fts USING fts4(term);""")
do_sql(u"""INSERT INTO Concept_fts(docid, term) SELECT id, term FROM Concept_lemmatized;""")
do_sql(u"""INSERT INTO Concept_fts(Concept_fts) VALUES('optimize');""")
do_sql(u"""drop TABLE Concept_lemmatized""")

#do_sql(u"""INSERT INTO Concept_fts(docid, term) SELECT Concept.id, Text.text FROM Text, Concept WHERE Concept.code = Text.code;""")

# do_sql(u"""CREATE VIRTUAL TABLE Concept_fts USING fts3(content="Concept", term, isMain);""")
# do_sql(u"""CREATE VIRTUAL TABLE Concept_fts USING fts3(content="Concept", term, isMain);""")
# do_sql(u"""INSERT INTO Concept_fts(docid, term, isMain) SELECT id, term, 1 FROM Concept;""")
# do_sql(u"""INSERT INTO Concept_fts(docid, term, isMain) SELECT Concept.id, Text.text, 0 FROM Text, Concept WHERE Concept.code = Text.code;""")
# do_sql(u"""INSERT INTO Concept_fts(Concept_fts) VALUES('optimize');""")

#do_sql(u"""VACUUM;""")

close_db(db, SQLITE_FILE)

print("ICD10 Database creation completed!")