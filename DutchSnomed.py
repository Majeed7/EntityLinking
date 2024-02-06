import sqlite3 as sql_module
import sys, os, os.path
from dbCreation.Mapping import *
from nltk.tokenize import word_tokenize
from DutchICD10 import *

from toolz import unique

#path = '%s.sqlite3' % os.path.join(
#    os.getcwd(), "data/DutchSnomedCT")  #getcwd()

path = os.path.abspath('data/DutchSnomedCT.sqlite3')

if not os.path.exists(path):
    raise IOError(
        'Database %s not available.'
        % path)
db = sql_module.connect(path, check_same_thread=False)
db_cursor = db.cursor()
db_cursor.execute("PRAGMA synchronous  = OFF;")
db_cursor.execute("PRAGMA journal_mode = OFF;")

_TERMSEARCHQUERY = "SELECT DISTINCT Description.id FROM Concept, Description, Description_fts WHERE ( Description_fts.term MATCH ? ) AND (Description.id = Description_fts.docid) AND (Description.active=1) AND (Concept.id = Description.conceptId) AND (Concept.active = 1) AND (Description.languageCode = 'nl')"

class DutchSNOMEDCT():

    def __init__(self):
        self.SearchQuery = ""

    def __getitem__(self, dsc_id):
        #db_cursor.execute("SELECT id FROM Description WHERE conceptId=? AND typeId=900000000000003001 AND active=1 AND languageCode = 'nl'", (cnpt_id, ))
        #db_cursor.execute("SELECT id FROM Description WHERE conceptId=? AND typeId=900000000000003001 AND active=1 AND languageCode = 'nl'", (cnpt_id, ))
        #r = db_cursor.fetchone()
        #if not r: raise ValueError()
        #dsc_id = r[0]
        return SNOMEDDescription(dsc_id, self.SearchQuery)

    def first_levels(self):
        return [
            self[code] for code in [
                u"123037004", u"404684003", u"308916002", u"272379006",
                u"106237007", u"363787002", u"410607006", u"373873005",
                u"78621006", u"260787004", u"71388002", u"362981000",
                u"419891008", u"243796009", u"48176007", u"370115009",
                u"123038009", u"254291000", u"105590001"
            ]
        ]

    def search(self, span):
        self.SearchQuery = span

        r=[]
    
        try:
            db_cursor.execute(_TERMSEARCHQUERY, (span.text, ))
            r  += db_cursor.fetchall()
        except:
            pass

        try:
            if span.text != span.lemma_:    
                db_cursor.execute(_TERMSEARCHQUERY, (span.lemma_, ))
                r  += db_cursor.fetchall()
        except:
            pass
                
        #r = set(r) 
        if len(r) > 10000 or len(span.text) < 2:
            r = []

        l = []

        for (code, ) in r:
            try:
                l.append(self[code]) #if self[code] not in l: 
            except ValueError:
                pass
        return l


        #################### A class for each Concept in the Dutch SNOMED

class SNOMEDDescription():

    def __init__(self, des_id, search_query=None):
        self.DescriptionID = des_id
        #self.SearchQuery = searchQuery
        db_cursor.execute(
            "SELECT Description.conceptId, Description.term, Description.typeId, Description_fts.term FROM Description, Description_fts WHERE Description.id=? AND Description.active=1 AND Description.id = Description_fts.docid",
            (des_id, ))  #typeId=900000000000003001
        r = db_cursor.fetchone()
        if not r: 
            raise ValueError()
        self.ConceptId = r[0]
        self.Term = r[1].strip() 
          
        self.TypeCode = r[2]
        self._set_lemmatized(r[3])
        self._set_tokenized()
        self.span = search_query
        self.icd10 = None
        self.guidelines = None
        #self.ConceptSpacy = nlp(self.Term)

        if self.TypeCode != 900000000000003001:
            db_cursor.execute(
                "SELECT id FROM Description WHERE conceptId=? AND typeId=900000000000003001 AND active=1 AND languageCode = 'nl'",
                (self.ConceptId, ))
            r = db_cursor.fetchone()
            self.IsMainTerm = False
            #self.MainTerm = SNOMEDDescription(r[0])
        else:
            self.IsMainTerm = True

    def __str__(self):
        return " SNOMEDCT[{}]    # {} \n".format(self.DescriptionID, self.Term)

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.Term) #len(self.ConceptSpacy)

    def __getitem__(self, dsc_id):
        return SNOMEDDescription(dsc_id)

    def get_span(self):
        return self.span

    def __getattr__(self, attr):
        if attr == "parents":
            db_cursor.execute(
                "SELECT DISTINCT destinationId FROM Relationship WHERE sourceId=? AND typeId=116680003 AND active=1",
                (self.code, ))  # 116680003 = is_a
            self.parents = [
                self.terminology[code] for (code, ) in db_cursor.fetchall()
            ]
            return self.parents

        elif attr == "children":
            db_cursor.execute(
                "SELECT DISTINCT sourceId FROM Relationship WHERE destinationId=? AND typeId=116680003 AND active=1",
                (self.code, ))  # 116680003 = is_a
            self.children = [
                self.terminology[code] for (code, ) in db_cursor.fetchall()
            ]
            return self.children

        elif attr == "relations":
            pass
            # if pymedtermino.REMOVE_SUPPRESSED_RELATIONS and self.active:
            #   db_cursor.execute("SELECT DISTINCT typeId FROM Relationship WHERE sourceId=? AND active=1", (self.code,))
            # else:
            #   db_cursor.execute("SELECT DISTINCT typeId FROM Relationship WHERE sourceId=?", (self.code,))

            # self.relations = set(code_2_relation[rel] for (rel,) in db_cursor.fetchall() if rel != 116680003) # 116680003 = is_a

            # if pymedtermino.REMOVE_SUPPRESSED_RELATIONS and self.active:
            #   db_cursor.execute("SELECT DISTINCT typeId FROM Relationship WHERE destinationId=? AND active=1", (self.code,))
            # else:
            #   db_cursor.execute("SELECT DISTINCT typeId FROM Relationship WHERE destinationId=?", (self.code,))

            # for (rel,) in db_cursor.fetchall():
            #   if rel != 116680003:
            #     self.relations.add("INVERSE_%s" % code_2_relation[rel])
            # return self.relations

        elif (attr == "groups") or (attr == "out_of_group"):
            pass
            # db_cursor.execute("SELECT DISTINCT relationshipGroup, typeId, destinationId FROM Relationship WHERE sourceId=? AND active=1", (self.code,))
            # data = db_cursor.fetchall()
            # groups = [Group() for i in range(1 + max([0] + [group_id for (group_id, rel, code) in data]))]
            # for (group_id, rel, code) in data:
            #   if rel == 116680003: continue # 116680003 = is_a
            #   group = groups[group_id]
            #   group.add_relation(code_2_relation[rel], self.terminology[code])
            # self.groups       = [group for group in groups[1:] if group.relations] # Pourquoi y a-t-il des groupes vides dans la SNOMED CT ???
            # self.out_of_group = groups[0]
            # if attr == "groups": return self.groups
            # else:                return self.out_of_group

        # elif attr in relation_2_code:
        #   relation_code = relation_2_code[attr]
        #   if pymedtermino.REMOVE_SUPPRESSED_RELATIONS and self.active:
        #     db_cursor.execute("SELECT DISTINCT destinationId FROM Relationship WHERE sourceId=? AND typeId=? AND active=1", (self.code, relation_code))
        #   else:
        #     db_cursor.execute("SELECT DISTINCT destinationId FROM Relationship WHERE sourceId=? AND typeId=?", (self.code, relation_code))

        #   l = [self.terminology[code] for (code,) in db_cursor.fetchall()]
        #   setattr(self, attr, l)
        #   return l

        # elif attr.startswith(u"INVERSE_"):
        #   relation_code = relation_2_code[attr[8:]]
        #   if pymedtermino.REMOVE_SUPPRESSED_RELATIONS and self.active:
        #     db_cursor.execute("SELECT DISTINCT sourceId FROM Relationship WHERE destinationId=? AND typeId=? AND active=1", (self.code, relation_code))
        #   else:
        #     db_cursor.execute("SELECT DISTINCT sourceId FROM Relationship WHERE destinationId=? AND typeId=?", (self.code, relation_code))

        #   l = [self.terminology[code] for (code,) in db_cursor.fetchall()]
        #   setattr(self, attr, l)
        #   return l

        elif attr == "active":
            db_cursor.execute("SELECT active FROM Concept WHERE id=?",
                              (self.code, ))
            self.active = db_cursor.fetchone()[0]
            return self.active

        elif attr == "terms":
            db_cursor.execute(
                "SELECT term FROM Description WHERE conceptId=? AND active=1 AND (Description.languageCode = 'nl')",
                (self.code, ))
            self.terms = [l[0] for l in db_cursor.fetchall()]
            return self.terms

        # elif attr == "definition_status":
        #   db_cursor.execute("SELECT definitionStatusId FROM Concept WHERE id=?", (self.code,))
        #   self.definition_status = SNOMEDCT[db_cursor.fetchone()[0]]
        #   return self.definition_status

        elif attr == "module":
            pass
            # db_cursor.execute("SELECT moduleId FROM Concept WHERE id=?", (self.code,))
            # self.module = SNOMEDCT[db_cursor.fetchone()[0]]
            # return self.module

        elif attr == "is_in_core":
            db_cursor.execute("SELECT is_in_core FROM Concept WHERE id=?",
                              (self.code, ))
            self.is_in_core = int(db_cursor.fetchone()[0])
            return self.is_in_core

        raise AttributeError(attr)

    def _set_lemmatized(self, extended_term):
        if '||' in extended_term:
            self.Lemmatized = extended_term.split('||')[1].strip()
        else:
            self.Lemmatized = extended_term.strip()

    def _set_tokenized(self):
        tokens = set(word_tokenize(self.Lemmatized, language='dutch'))
        self.tokens = set([t.replace('-','') for t in tokens])
        tokens_lemma = set(word_tokenize(self.Term, language='dutch'))
        self.tokens_lemma = set([t.lower().replace('-','') for t in tokens_lemma])

        self.all_tokens = self.tokens.union(self.tokens_lemma)

    def get_icd10(self):
        if self.icd10 == None:
            self.icd10 = Mapping().SNOMED2ICD(self.ConceptId)

        return self.icd10
    
    def get_guidelines(self):
        if self.icd10 == None:
            self.get_icd10()
        if self.guidelines == None:
            all_guidelines = []
            for code in self.icd10:
                level = 0
                all_guidelines.extend(self.guidelinesByLevel(code, level))
                
                # getting the guidelines for the codes positioned higher in the ICD-10 hierarchy
                cur_code = code
                while cur_code.ParentCode != '':
                    level -= 1
                    cur_code = ICD10Concept(cur_code.ParentCode)
                    
                    all_guidelines.extend(self.guidelinesByLevel(cur_code, level))

            self.guidelines = list(unique(all_guidelines, key=lambda ent:ent['guidelineId'])) #all_guidelines

        return self.guidelines

    def guidelinesByLevel(self, code, level):
        all_gd = []
        for gd in code.get_guidelines():
            all_gd.append({'guidelineId':gd.guidelineId, 'id':gd.id, 'title':gd.title, 'icd': code, 'icd_term' : code.Term, 'level': level})

        return all_gd

    def ToICD10(self):
        return self.icd10
    
    def get_snomed_link(self):
        return "https://browser.ihtsdotools.org/?perspective=full&conceptId1={}&edition=MAIN/SNOMEDCT-NL/2022-09-30&release=&languages=nl,en".format(self.ConceptId)

    def get_all_descriptions(self):
        db_cursor.execute(
                "SELECT id FROM Description WHERE conceptId=? AND active=1 AND languageCode = 'nl'",
                (self.ConceptId, ))
        r = db_cursor.fetchall()

        desc = []
        for (code, ) in r:
            try:
                desc.append(self[code])
            except ValueError:
                pass

        return desc


##############
if __name__ == "__main__":
    import spacy
    nlp = spacy.load("nl_core_news_lg")
    
    x = DutchSNOMEDCT()
    search_span = nlp("hart- en vaatziekte")[0:]

    l = x.search(search_span)
    print(l)
