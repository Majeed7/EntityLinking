from DutchSnomed import DutchSNOMEDCT, SNOMEDDescription
from DutchICD10 import ICD10Dutch, ICD10Concept
from itertools import groupby
import numpy as np
from toolz import unique

class TermCandidate:
    def __init__(self, span):
        self.variations = [span]
        #self.getEntityCandidates()
        self.SimilarEntities = []
        self.ExactMatches = []
        self.similarities = []

    def __repr__(self):
        return self.__str__()

    def pretty_print(self):
        print("Term Candidates are [{}]".format(self))

    def append(self, span):
        self.variations.append(span)

    def has_plural(self, variation):
        return any([t.tag_ == "NNS" for t in variation])

    def get_singular(self, variation):
        return ' '.join([t.text if t.tag_ != "NNS" else t.lemma_ for t in variation])

    def get_snomed_link(self):
        return "https://browser.ihtsdotools.org/?perspective=full&conceptId1={}&edition=MAIN/SNOMEDCT-NL/2022-03-31&release=&languages=nl,en".format(self.SimilarEntities[0].ConceptId)

    def __str__(self):
        return ', '.join([variation.text for variation in self.variations])

    def __set_sents_tokens(self):
        sents = []
        tokens = []
        for variation in self.variations:
            ## Set the sentence of the variation
            sent=''
            sent = ' '.join([''.join(x.text.lower()) for x in variation.sents]) + '. '
            sent += ' '.join([''.join(x.lemma_) for x in variation.sents])
            sents.append(sent)

            ## Set the tokens for the variations
            termTokens = set()
            for sent in variation.sents:
                termTokens = termTokens.union(sent._.cands)
            tokens.append(termTokens)

        self.sents = sents
        self.variation_tokens = tokens

    @property
    def sent(self):
        return self.variations[0].sent

    def getEntityCandidates(self):
        db = DutchSNOMEDCT()
        #db = ICD10Dutch()
        
        entityElements = [] 
        # for variation in self.variations:
        #     entityElements += db.search(variation)

        [entityElements.append(t) for variation in self.variations for t in db.search(variation) if t not in entityElements]
            
        self.EntityCandidates = entityElements

    ## Entity Matcher functions
    def getEntitySelection(self):
        if len(self.EntityCandidates) < 1:
            return 

        self.__set_sents_tokens()

        entities_group_length = self._get_grouped_by_length(self.EntityCandidates)
        entities_lengths = sorted(list(entities_group_length.keys()), reverse=True)

        for lngth in entities_lengths:
            filtered_by_length = entities_group_length[lngth]
            self.match_variation = self.variations.index(filtered_by_length[0].get_span())
            sent_of_tokens = self.sents[self.match_variation]
            self.ExactMatches = list(filter(lambda cand: cand.Term.lower() in sent_of_tokens or cand.Lemmatized.lower() in sent_of_tokens, filtered_by_length))
            self.compute_similarities(filtered_by_length)
            if self.similarities.max() > 0.5:
                # Filter the similar entities with a value of more than 0.5
                inds = np.argwhere(self.similarities > 0.5).ravel()
                self.similarities = self.similarities[inds]
                filtered_by_length = [filtered_by_length[i] for i in inds]

                # Sort the entities
                sort_double = sorted(zip(self.similarities, filtered_by_length), key= lambda ent: (-ent[0], -len(ent[1]),  ent[1] not in self.ExactMatches))
                unique_entities = list(unique(sort_double, key=lambda ent:ent[1].DescriptionID))
                self.similarities = np.array(list(zip(*unique_entities))[0])
                self.SimilarEntities = list(list(zip(*unique_entities))[1])

                #inds = np.argsort(-self.similarities)
                #self.similarities = self.similarities[inds]
                #self.SimilarEntities = [filtered_by_length[i] for i in inds]

                # if len(self.SimilarEntities[0].tokens) > 2 and len(self.variations[self.match_variation]) == 1:
                #     self.SimilarEntities = []
                #     continue
                
                # Filter based on the most similar entity
                filtered_most_similar = self._filter_most_similar(self.SimilarEntities)
                sorted_by_length = sorted(filtered_most_similar, key=lambda ent: (-len(ent.Term), ent not in self.ExactMatches))
                self.FilteredSimilarEntities = sorted_by_length

                break
                
    def _get_grouped_by_length(self, entities):
        sorted_by_len = sorted(entities, key=lambda entity: len(entity.get_span()), reverse=True)

        entities_by_length = {}
        for length, group in groupby(sorted_by_len, lambda entity: len(entity.get_span())):
            entities_len = list(group)
            entities_by_length[length] = entities_len

        return entities_by_length

    def _filter_max_length(self, entities):
        entities_by_length = self._get_grouped_by_length(entities)
        max_length = max(list(entities_by_length.keys()))
        entities_lengthwise = entities_by_length[max_length]
        return entities_lengthwise

    def _get_similariy(self, term, entity):

        # Exact match == similarity of 1
        #if entity.Lemmatized in term.sent.lemma_:
        #    return 1

        #termTokens = set()
        #for sent in term.sents:
        #    termTokens = termTokens.union(sent._.cands)
        stopword_no = len(entity.tokens.intersection(term.sent._.stopwords))
        entity_tokenNo = len(entity.tokens) - stopword_no 
        denominator = entity_tokenNo
        
        if denominator == 0: return 0

        termTokens = self.variation_tokens[self.match_variation]
        
        entityTokens = entity.all_tokens.difference(term.sent._.stopwords)
        nominator = len(termTokens.intersection(entityTokens))

        # if the number of stopwords is more than equal to the number of tokens
        # all the stopwords count for computing similarities
        if stopword_no >= entity_tokenNo:
            denominator = len(entity.tokens)
            nominator = len(termTokens.intersection(entity.all_tokens))

        
        return (nominator) / denominator

    def _filter_most_similar(self, entities):
        max_indices = np.where(self.similarities == self.similarities.max())[0].tolist()

        return [entities[i] for i in max_indices]

    def compute_similarities(self, entities):
        self.similarities = np.array(
            [self._get_similariy(self.variations[self.match_variation], entity) for entity in entities])

