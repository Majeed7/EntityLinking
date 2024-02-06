from flask import Flask, render_template, request, url_for, redirect
from flaskext.markdown import Markdown
import html2text
import re

import numpy as np 
import os

from EL import EntityLinking 
from spacy import displacy
from spacy.tokens import Span

template_dir = os.path.abspath('app/templates/')
app = Flask(__name__, template_folder=template_dir)
Markdown(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=["GET", "POST"])
def extract():
    if request.method == "POST":
        rawText = request.form["rawtext"]
        rawText = html2text.html2text(rawText)
        rawText = re.sub('[^A-Za-z0-9]+', '', rawText)

        rawText = "Bij wie wordt het risico op hart en vaatziekten geschat. Voor veel patiënten is een risicocategorie aan te wijzen zonder dat hun risico kwantitatief geschat hoeft te worden met een risicoscore. Denk aan patiënten met bestaande hart en vaatziekten, diabetes mellitus en daarmee gepaard gaande orgaanschade, ernstige chronische nierschade en extreem verhoogde risicofactoren. Deze categorieën staan toegelicht in tabel 1."

        el = EntityLinking(rawText)
        docx = el.doc
        spans=[]
        for candidate in el.AllCandidates:
            spans.append( Span(docx, candidate.variations[0].start, candidate.variations[0].start+len(candidate.variations[0]), "PP") )
        
        #docx.set_ents(spans)
        result = displacy.render(docx, style="ent")

        ents = []
        id = 1
        for candidate in el.AllCandidates:
            if len(candidate.SimilarEntities) > 0:
                ents.append({ "id":id, 
                              "start": candidate.variations[0].start_char, 
                              "end": candidate.variations[0].start_char + len(candidate.variations[0].text), 
                              "label": "S", 
                              "kb_id": "Link", 
                              "kb_url": "#"+str(id),
                              "snomed_concept_id": candidate.SimilarEntities[0].ConceptId,
                              "url": candidate.get_snomed_link(),
                              "snomed_desc": [c.__dict__ for c in candidate.SimilarEntities[0].get_all_descriptions()],
                              "icd10codes": [c.__dict__ for c in candidate.SimilarEntities[0].ToICD10()] if candidate.SimilarEntities[0].ToICD10() != None else None,
                              "guidelines": [c.get_guidelines() for c in candidate.SimilarEntities[0].ToICD10() if c.get_guidelines() is not None] if candidate.SimilarEntities[0].ToICD10() != None else None,
                              })
                id+=1
        for ent in ents:
            if ent["guidelines"] != None and ent["guidelines"] != []:
                ent["guidelines"] = list(np.concatenate(ent["guidelines"]).flat)
                ind = ents.index(ent)
                ents[ind]["guidelines"] = ent["guidelines"][0] #list(np.concatenate(ent["guidelines"]).flat)
                ents[ind]['guidelines']['urls'] = ent['guidelines']['urls'][0]

        ex = [{"text": docx.text,
                "ents": ents,
                "title": None
             }]

        result2 = displacy.render(ex, style="ent", manual=True)

        
        return render_template("result.html", rawtext = rawText, result=result2, ents=ents)
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
