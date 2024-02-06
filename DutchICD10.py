import os, os.path
import sqlite3 as sql_module
import pandas as pd

#from guidelines.models import *


_TERMSEARCHQUERY  = "SELECT Concept.code FROM Concept, Concept_fts WHERE Concept_fts.term MATCH ? AND Concept.id = Concept_fts.docid"

#_TERMSEARCHQUERY  = "SELECT Concept.code FROM Concept, Concept_fts WHERE Concept_fts.term MATCH ? AND Concept.id = Concept_fts.docid AND Concept_fts.isMain == 1"
_TEXTSEARCHQUERY  = "SELECT Concept.code FROM Concept, Concept_fts WHERE Concept_fts.term MATCH ? AND Concept.id = Concept_fts.docid AND Concept_fts.isMain == 0"
_CONCEPTQUERY = "SELECT Concept.parent_code, Concept.term, Concept_fts.term FROM Concept, Concept_fts WHERE Concept.code=?"

#path = '%s.sqlite3' % os.path.join(
#    os.getcwd(), "data/ICD10DUT")  #getcwd()

path = os.path.abspath('data/ICD10DUT.sqlite3')
if not os.path.exists(path):
    raise IOError(
        'Database %s not available'
        % path)
db = sql_module.connect(path, check_same_thread=False)
db_cursor = db.cursor()
#db_cursor.execute("PRAGMA synchronous  = OFF;")
#db_cursor.execute("PRAGMA journal_mode = OFF;")

## Get the excel file of the guidlines
# guidelines = pd.read_excel("data/Richtlijnen_separated.xlsx", index_col=False)
# guide_navs = pd.read_csv("data/guide_navs.csv")

class ICD10Dutch():

    def __init__(self):
        pass
        
    def first_levels(self):
        return [self[code] for code in ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII"]]

    def __getitem__(self, code):
        return ICD10Concept(code)

    def connectToSql(self, dbName):
        path = '%s.sqlite3' % os.path.join(os.getcwd(), dbName)
        if not os.path.exists(path):
            raise IOError(
                'Database %s not available.'
                % path)
        db = sql_module.connect(path)
        return db

    def search(self, span):
        self.SearchQuery = span
    
        # if span.text == span.lemma_ or span.text in span.lemma_:
        #     db_cursor.execute(_TERMSEARCHQUERY, (span.text, ))
        #     r = db_cursor.fetchall()

        # elif span.lemma_ in span.text:
        #     db_cursor.execute(_TERMSEARCHQUERY, (span.lemma_, ))

        #     r = db_cursor.fetchall()
        # else:
        #     db_cursor.execute(_TERMSEARCHQUERY, (span.text, ))
        #     r = db_cursor.fetchall()

        #     db_cursor.execute(_TERMSEARCHQUERY, (span.lemma_, ))
        #     r += db_cursor.fetchall() 
        
        search_text = span.text + " OR " + span.lemma_
        try:
            db_cursor.execute(_TERMSEARCHQUERY, (search_text, ))
            r  = db_cursor.fetchall()
        except:
            r = []
        
        l = []
        for (code, ) in r:
            try:
                l.append(self[code])
            except ValueError:
                pass
        return l


        #################### A class for each Concept in the Dutch ICD10
class ICD10Concept():

    def __init__(self, code):
        if code.startswith(u"("): code = code[1:-1]
        self.Code  = code
        #self.SearchQuery = searchQuery
        db_cursor.execute(_CONCEPTQUERY, (code,))
        r = db_cursor.fetchone()
        if not r:
            raise ValueError(code)
        self.ParentCode = r[0]
        self.Term             = r[1]
        self._set_lemmatized(r[2])
        if not self.Term:
            db_cursor.execute("SELECT Concept.term, Concept_fts.term FROM Concept, Concept_fts WHERE concept.code=?", (code,))
            self.Term = db_cursor.fetchone()[0]
            self._set_lemmatized(r[1])

    def __str__(self):
        return "ICD10[{}]    # {} \n".format(self.Code, self.Term)

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.Term) #len(self.ConceptSpacy)
    
    def _set_lemmatized(self, extended_term):
        if '||' in extended_term:
            self.Lemmatized = extended_term.split('||')[1]
        else:
            self.Lemmatized = extended_term

    def get_guidelines(self):
        guidelineTag = apps.get_model('guidelines','GuidelineTags')
        all_tagged = guidelineTag.objects.filter(code = self.Code)
        
        # if len(all_tagged) == 0 and self.Code.find('.') != -1:
        #     code = self.Code[:self.Code.index('.')]
        #     all_tagged = guidelineTag.objects.filter(code = code)

        return [t.guideline for t in all_tagged]
    
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
        
        #GuidelineTags.objects.filter(code == self.Code)
        # res = guidelines.loc[guidelines['ICD10Codes'].str.contains(r"[ ;]"+ self.Code + "[; ]|^"+ self.Code + "[; ]", case=False)]
        # if res.empty and self.Code.find('.') != -1:
        #     code = self.Code[:self.Code.index('.')]
        #     res = guidelines.loc[guidelines['ICD10Codes'].str.contains(r"[ ;]"+ code + "[; ]|^"+ code + "[; ]", case=False)]

        # if res.empty:
        #     return None
        # else:
        #     res_dict = res.to_dict('records')
        #     for item in res_dict:
        #         guideline_id = item['ID']
        #         items = guide_navs.loc[guide_navs['guideline_id'] == guideline_id]
        #         item['urls'] = items.to_dict('records')
        #     return res_dict

##############
if __name__ == "__main__":
    import spacy

    x = ICD10Dutch()
    nlp = spacy.load("nl_core_news_md")
    search_span = nlp("Diabetes mellitus")[0:]
    (l) = x.search(search_span)
    print(l)
