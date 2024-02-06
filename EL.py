from DutchSnomed import DutchSNOMEDCT
from DutchICD10 import ICD10Dutch
from TermCandidate import TermCandidate

import re
import spacy
from spacy.tokens import Doc, Span, Token
from spacy.symbols import ORTH 
from spacy import util
from spacy.tokenizer import Tokenizer
from gensim.utils import tokenize

fulltag_pattern = r'<[\w\d/\'\"\.=\:]+[ ][\w\s\d/ _\'\"\.=\:\-?\&\#\;\<%]+>'
opentag_pattern = r'<[\w\s\d/ \"\.=]*>'
closetag_pattern = r'</[\w\d\s ]+>'
special_pattern = r'&[\w\s\d/ \":\\\.=]*;'

html_tokenization = True

class EntityLinking():

    def __init__(self, docString, nlp=None):
        docString  = docString.replace(">", "> ").replace("<", " <") 
        self.nlp = spacy.load("nl_core_news_md") if nlp is None else spacy.load(nlp)
        stopwords = set(self.nlp.Defaults.stop_words)
        Span.set_extension('stopwords', default=stopwords, force=True)

        #if html_tokenization:
        #    self.nlp.tokenizer = create_html_tokenizer()(self.nlp)

        regeces = re.findall( fulltag_pattern , docString)
        
        for regex in regeces:
            self.nlp.Defaults.tokenizer_exceptions[regex] = [{ ORTH: regex }]
        
        # self.nlp.Defaults.tokenizer_exceptions['Type 1'] = [{ ORTH: 'Type 1' }]
        # self.nlp.Defaults.tokenizer_exceptions['type 1'] = [{ ORTH: 'type 1' }]
        # self.nlp.Defaults.tokenizer_exceptions['Type 2'] = [{ ORTH: 'Type 2' }]
        # self.nlp.Defaults.tokenizer_exceptions['type 2'] = [{ ORTH: 'type 2' }]
        
        self.excluded_candidates = regeces 
        self.excluded_candidates += re.findall(closetag_pattern, docString)
        self.excluded_candidates += re.findall(opentag_pattern, docString)

        self.nlp.tokenizer = self.custom_tokenizer()
        self.doc = self.nlp(docString)
        
        allCandidates = self.getAllCandidates() # Getting term candidates
        for cand in allCandidates: cand.variations = sorted(cand.variations, key=len, reverse=True)
        allCandidates = sorted(allCandidates, key= lambda x: x.variations[0].start_char)
        self.AllCandidates = allCandidates
        db = DutchSNOMEDCT() # ICD10Dutch() # 
        self.AllCandidates = self.__reduceCandidates(allCandidates, db)
        
        #self.doc.ents = self.AllCandidates
        # Get the entity candidates from SNOMED for each of the term candidate
        for term_candidate in self.AllCandidates:
            term_candidate.getEntityCandidates() # Getting the Entity Candidates 
            term_candidate.getEntitySelection()
            print(term_candidate.SimilarEntities[0].get_span(), "==>", term_candidate.SimilarEntities[0], term_candidate.similarities[0]) if len(term_candidate.SimilarEntities) > 0 else None

        self.AllCandidates = [item for item in self.AllCandidates if len(item.SimilarEntities) > 0]
        
        
    def getAllCandidates(self):
        allCandidates=[]
        Doc.set_extension('cands', default=[], force=True)
        Span.set_extension('cands', default=[], force=True)
        #sent_list = list(self.doc.sents)
        for sent in self.doc.sents:
            sent_candids = self.__getCandidatesInSentences(sent)
            
            sent_tokens = []
            [sent_tokens.append(list(tokenize(z.lemma_))[0]) if len(list(tokenize(z.lemma_))) > 0 else sent_tokens.append(z.lemma_)
                            for x in sent_candids for y in x.variations for z in y if z.lemma_ not in sent_tokens]
            #[sent_tokens.append(z.lemma_) for x in sent_candids for y in x.variations for z in y if z.lemma_ not in sent_tokens]
            sent._.cands = set(sent_tokens)

            for candidate in sent_candids:
                allCandidates.append(candidate) 
        # spans=[]
        # [spans.append(z) for x in allCandidates for y in x.variations for z in y if z not in spans]
        # Doc._.cands = spans

        return allCandidates

    def __getCandidatesInSentences(self, sent):
        if sent.text == ' ' or list(filter(lambda token: token.dep_ == "ROOT", sent)) == []:
            return []
            
        root = list(filter(lambda token: token.dep_ == "ROOT", sent))[0]

        excluded_children = []
        candidates = []

        def get_candidates(node, doc):

            if (node.pos_ in ["PROPN", "NOUN", "SYM"]) and node.pos_ not in ["PRON"] and not node._.is_tag and node.text not in self.excluded_candidates:
                term_candidates = TermCandidate(doc[node.i:node.i + 1]) #doc[node.i:node.i + 1] #

                for child in node.children:

                    start_index = min(node.i, child.i)
                    end_index = max(node.i, child.i)

                    if child.dep_ == "compound" or child.dep_ == "amod":
                        subtree_tokens = list(child.subtree)
                        if all([c.dep_ == "compound" for c in subtree_tokens]):
                            start_index = min([c.i for c in subtree_tokens])
                        term_candidates.append(doc[start_index:end_index + 1])

                        if not child.dep_ == "amod":
                            term_candidates.append(doc[start_index:start_index + 1])
                        excluded_children.append(child)

                    if child.dep_ == "prep" and child.text == "van":
                        end_index = max([c.i for c in child.subtree])
                        term_candidates.append(doc[start_index:end_index + 1])

                candidates.append(term_candidates)

            for child in node.children:
                if child.text in self.excluded_candidates:
                    continue
                get_candidates(child, doc)

        get_candidates(root, self.doc)

        return candidates

    def __reduceCandidates(self, allCandidates, db):
        def combine_candidates(candidate1, candidate2, db):
            #candidate1.variations = sorted(candidate1.variations, key=len, reverse=True)
            #candidate2.variations = sorted(candidate2.variations, key=len, reverse=True)
            new_terms = []
            for term1 in candidate1.variations:
                for term2 in candidate2.variations:
                    temp = term1.doc[term1.start:term2.end]
                    res = db.search(temp)
                    if len(res) > 0:# and temp.__len__() > max_length:
                        # candidate1.variations.insert(0, temp)
                        # index = candidate2.variations.index(term2)
                        # candidate2.variations[index:] = []
                        new_terms.append(temp) if temp not in new_terms else None 
                        # candidate2.variations.insert(0, temp)
                        # index = candidate1.variations.index(term1)
                        # candidate2.variations += candidate1.variations[:index] #if candidate1.variations[:index] != [] else []
                        # candidate1.variations = [] #candidate1.variations[index:] = []
                        # candidate2.variations = sorted(candidate2.variations, key=len, reverse=True)
                        
                        
            if new_terms != []:
                candidate2.variations.extend(new_terms)
                candidate1.variations = []
                candidate2.variations = sorted(candidate2.variations, key=len, reverse=True)

        for i in range(len(allCandidates)-1):
            combine_candidates(allCandidates[i], allCandidates[i+1], db)

        allCandidates = [item for item in allCandidates if len(item.variations) > 0]

        return allCandidates

    def custom_tokenizer(self):
        nlp = self.nlp
        prefixes = [r'<[\w\s\d \"\.=]*>',] + nlp.Defaults.prefixes #['^<i>',]
        suffixes = [r'</[\w\d\s ]+>', ] + nlp.Defaults.suffixes #+ ['</i>$',]
        # remove the tag symbols from prefixes and suffixes
        prefixes = list(prefixes)
        prefixes.remove('<')
        prefixes = tuple(prefixes)
        suffixes = list(suffixes)
        suffixes.remove('>')
        suffixes = tuple(suffixes) 
        infixes = nlp.Defaults.infixes
        rules = nlp.Defaults.tokenizer_exceptions
        #token_match = re.compile(r'<[\w\s\d/ \":\\\.=]*>').match #TOKEN_MATCH
        token_match = re.compile(special_pattern).match #TOKEN_MATCH
        prefix_search = (util.compile_prefix_regex(prefixes).search)
        suffix_search = (util.compile_suffix_regex(suffixes).search)
        infix_finditer = (util.compile_infix_regex(infixes).finditer)

        tag_getter = lambda token: bool(re.match(special_pattern, token.text) ) or bool(re.match(opentag_pattern, token.text) ) or bool(re.match(closetag_pattern, token.text) ) or bool(re.match(fulltag_pattern, token.text) ) 
        Token.set_extension('is_tag', getter=tag_getter, force=True)

        return Tokenizer(nlp.vocab, rules=rules,
                        prefix_search=prefix_search,
                        suffix_search=suffix_search,
                        infix_finditer=infix_finditer,
                        token_match=token_match
                        )

if __name__ == "__main__":
    doc = "Bij wie wordt het risico op hart en vaatziekten geschat. Voor veel patiënten is een risicocategorie aan te wijzen zonder dat hun risico kwantitatief geschat hoeft te worden met een risicoscore. Denk aan patiënten met bestaande hart en vaatziekten, diabetes mellitus en daarmee gepaard gaande orgaanschade, ernstige chronische nierschade en extreem verhoogde risicofactoren. Deze categorieën staan toegelicht in tabel 1."
    
    f = open('testfile.txt','r')
    doc = f.read()
    f.close()

    el = EntityLinking(doc)
    print("Finished!")
