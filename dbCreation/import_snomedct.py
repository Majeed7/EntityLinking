

SNOMEDCT_DIR       = "/Users/majidmohammadi/surfdrive/Research/VU/Richtlijn/Code/SNOMED/SnomedCT_Netherlands_20210930" #/home/jiba/telechargements/base_med/SnomedCT_InternationalRF2_PRODUCTION_20170731T150000Z"
SNOMEDCT_CORE_FILE = ""#"/home/jiba/telechargements/base_med/SNOMEDCT_CORE_SUBSET_201708.txt"
#SNOMEDCT_DIR       = "/home/jiba/telechargements/base_med/SnomedCT_RF2Release_INT_20150131"
#SNOMEDCT_CORE_FILE = "/home/jiba/telechargements/base_med/SNOMEDCT_CORE_SUBSET_201502.txt"
#SNOMEDCT_DIR       = "/home/jiba/telechargements/base_med/SnomedCT_Release_INT_20140131/RF2Release"
#SNOMEDCT_CORE_FILE = "/home/jiba/telechargements/base_med/SNOMEDCT_CORE_SUBSET_201408.txt"

#ONLY_ACTIVE_CONCEPT = 1
ONLY_ACTIVE_CONCEPT = 0

import sys, os, os.path, stat, sqlite3
import spacy
nlp = spacy.load("nl_core_news_md")

HERE = os.path.dirname(sys.argv[0])
sys.path.append(os.path.join(HERE, ".."))


from db import *

if len(sys.argv) >= 3:
  SNOMEDCT_DIR       = sys.argv[1]
  SNOMEDCT_CORE_FILE = sys.argv[2]

LANGUAGE    = "nl"
NB          = SNOMEDCT_DIR.split("_")[-1]
if NB.endswith("/RF2Release"): NB = NB.replace("/RF2Release", "")
NB = NB[:8]

SQLITE_FILE = os.path.join(HERE, "..", "snomedct.sqlite3")

db = create_db(SQLITE_FILE)
db_cursor = db.cursor()

#r = open("/tmp/log.sql", "w")
def do_sql(sql, *args):
  #r.write(sql.encode("utf8"))
  #r.write(";\n")
  db_cursor.execute(sql, *args)
  
def sql_escape(s):
  return s.replace(u'"', u'""').replace(u'\r', u'').replace(u'\x92', u"'")


do_sql(u"PRAGMA synchronous  = OFF")
do_sql(u"PRAGMA journal_mode = OFF")
do_sql(u"PRAGMA locking_mode = EXCLUSIVE")

do_sql(u"""
CREATE TABLE Concept (
  id BIGINT PRIMARY KEY,
  effectiveTime DATE,
  active INTEGER,
  moduleId BIGINT,
  definitionStatusId BIGINT,
  is_in_core INTEGER
)""")

do_sql(u"""
CREATE TABLE Description (
  id BIGINT PRIMARY KEY,
  effectiveTime DATE,
  active INTEGER,
  moduleId BIGINT,
  conceptId BIGINT,
  languageCode CHAR(2),
  typeId BIGINT,
  term TEXT,
  caseSignificanceId BIGINT
)""")

do_sql(u"""
CREATE TABLE TextDefinition (
  id BIGINT PRIMARY KEY,
  effectiveTime DATE,
  active INTEGER,
  moduleId BIGINT,
  conceptId BIGINT,
  languageCode CHAR(2),
  typeId BIGINT,
  term TEXT,
  caseSignificanceId BIGINT
)""")

do_sql(u"""
CREATE TABLE Relationship (
  id BIGINT PRIMARY KEY,
  effectiveTime DATE,
  active INTEGER,
  moduleId BIGINT,
  sourceId BIGINT,
  destinationId BIGINT,
  relationshipGroup INTEGER,
  typeId BIGINT,
  characteristicTypeId BIGINT
)""")


CORE_IDS = set()
if SNOMEDCT_CORE_FILE:
  for line in open(SNOMEDCT_CORE_FILE).read().split("\n")[1:]:
    if line:
      words = line.split("|")
      if words[7] == "False": CORE_IDS.add(words[0])

sys.stderr.write("%s SNOMED CT terms in CORE Problem list.\n" %  len(CORE_IDS))

ACTIVE_CONCEPTS = set()

for table, language_dependent in [
    ("Concept"       , False),
    ("TextDefinition", False),
    ("Description"   , False),
    ("Relationship"  , False),
  ]:
  if language_dependent:
    filename = os.path.join(SNOMEDCT_DIR, "Snapshot", "Terminology", "sct2_%s_Snapshot-%s_NL_%s.txt" % (table, LANGUAGE, NB))
  else:
    filename = os.path.join(SNOMEDCT_DIR, "Snapshot", "Terminology", "sct2_%s_Snapshot_NL_%s.txt" % (table, NB))
    
  sys.stderr.write("Importing %s ...\n" % filename)
  
  for line in read_file(filename).split(u"\n")[1:]:
    if line:
      words = line.replace(u"\r", u"").split(u"\t")
      
      if   table == "Concept":
        if words[2] == u"1": ACTIVE_CONCEPTS.add(words[0])
        if words[0]in CORE_IDS: words.append("1")
        else:                   words.append("0")
        
      #elif table == "Description":
        #if not words[4] in ACTIVE_CONCEPTS:
          #continue # Active description of an inactive concept...!
          #words[2] = u"0"
          
      #elif table == "TextDefinition":
        #if not words[4] in ACTIVE_CONCEPTS:
          #continue # Active def of an inactive concept...!
          #words[2] = u"0"
        
      #elif table == "Relationship":
        #if (not words[4] in ACTIVE_CONCEPTS) or (not words[5] in ACTIVE_CONCEPTS):
          #continue # Active relation with an inactive concept...!
          #words[2] = u"0"
          
      #del words[1:3]
      
      if table == "Relationship": del words[-1] # modifierId is unused yet
      
      data = u"""("%s")""" % '", "'.join(map(sql_escape, words))
      sql  = u"""INSERT INTO %s VALUES %s""" % (table, data)
      do_sql(sql)
    
  if ONLY_ACTIVE_CONCEPT and (table == "Concept"): sys.stderr.write("%s active concepts\n" % len(ACTIVE_CONCEPTS))

  db.commit()
  
sys.stderr.write("Indexing ...\n")

do_sql(u"""CREATE INDEX Description_conceptId_index             ON Description(conceptId)""")

do_sql(u"""CREATE INDEX TextDefinition_conceptId_index          ON TextDefinition(conceptId)""")

do_sql(u"""CREATE INDEX Relationship_sourceId_typeId_index      ON Relationship(sourceId, typeId)""")
do_sql(u"""CREATE INDEX Relationship_destinationId_typeId_index ON Relationship(destinationId, typeId)""")


################## Create lemmatized version of the text and insert into virtual tables
do_sql(u"""
CREATE TABLE Description_lemmatized (
  id INTEGER,
  term TEXT
  )
""")

do_sql(u"""
CREATE TABLE TextDefinition_lemmatized (
  id INTEGER,
  term TEXT
  )
""")

select_query = "SELECT id, term FROM Description;"
db_cursor.execute(select_query)
r = db_cursor.fetchall()
for concept in r:
  id = concept[0]
  cpt = concept[1]
  cpt_lemma =  nlp(concept[1])[0:].lemma_
  cpt += ' || ' + cpt_lemma if cpt.lower() != cpt_lemma else '' 

  do_sql(u"""INSERT INTO Description_lemmatized(id, term) VALUES(?, ?);""", (id, cpt))

do_sql(u"""CREATE VIRTUAL TABLE Description_fts USING fts4(term);""")
do_sql(u"""INSERT INTO Description_fts(docid, term) SELECT id, term FROM Description_lemmatized;""")
do_sql(u"""INSERT INTO Description_fts(Description_fts) VALUES('optimize');""")
do_sql(u"""drop TABLE Description_lemmatized""")


select_query = "SELECT id, term FROM TextDefinition;"
db_cursor.execute(select_query)
r = db_cursor.fetchall()
for concept in r:
  id = concept[0]
  cpt = concept[1]
  cpt_lemma =  nlp(concept[1])[0:].lemma_
  cpt += ' || ' + cpt_lemma if cpt.lower() != cpt_lemma else '' 

  do_sql(u"""INSERT INTO TextDefinition_lemmatized(id, term) VALUES(?, ?);""", (id, cpt))

do_sql(u"""CREATE VIRTUAL TABLE TextDefinition_fts USING fts4(term);""")
do_sql(u"""INSERT INTO TextDefinition_fts(docid, term) SELECT id, term FROM TextDefinition_lemmatized;""")
do_sql(u"""INSERT INTO TextDefinition_fts(TextDefinition_fts) VALUES('optimize');""")
do_sql(u"""drop TABLE TextDefinition_lemmatized""")

#do_sql(u"""VACUUM;""")

db.commit()

do_sql(u"""PRAGMA integrity_check;""")
for l in db_cursor.fetchall():
  print(" ".join(l))

close_db(db, SQLITE_FILE)


# do_sql(u"""CREATE VIRTUAL TABLE Description_fts USING fts4(content="Description", term);""")
# do_sql(u"""INSERT INTO Description_fts(docid, term) SELECT id, term FROM Description;""")
# do_sql(u"""INSERT INTO Description_fts(Description_fts) VALUES('optimize');""")

# do_sql(u"""CREATE VIRTUAL TABLE TextDefinition_fts USING fts4(content="TextDefinition", term);""")
# do_sql(u"""INSERT INTO TextDefinition_fts(docid, term) SELECT id, term FROM TextDefinition;""")
# do_sql(u"""INSERT INTO TextDefinition_fts(TextDefinition_fts) VALUES('optimize');""")