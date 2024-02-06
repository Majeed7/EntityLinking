# EntityLinking
Unsupervised Entity Linking for (Dutch) Biomedical text

## Introduction
This package inlcudes an entity-linking method parituclalry tested on Dutch biomedical text. The method is unsupervised and identifies the similar entities to a part of text based on its similarity to the SNOMED concepts.


## Features
- It is unsupervised;
- It is tested for entity linking to SNOMED and ICD-10, both terminologies are stored in relational databases for fast search;
- The entity linking is based on a context-aware similarity metric that accounts for the context where the term in the text appears;
- It has a customized tokenization that can be applied dirctly to HTML-formatted texts;

## Installation
The SNOMED and ICD-10 databases could be constructed from their files by running the scripts in folder dbCreation.
Two databases based on the recent version of SNOMED and ICD-10 are created available at  https://surfdrive.surf.nl/files/index.php/s/jtF1auvFjVIqbT7 

For running a sample entity linking, download the databases and place them in the folder data, then execute run_me.py

## Credits
This package is inspired and uses some scripts from PymedTermino (https://github.com/MedevaKnowledgeSystems/pymedtermino) for using SQLite text search capability. 

## Visualization 
There is a small FLask app wrttien to visualize the results of entity linking. Check flask_app.py for further information.


## Usage
In the following, we show how one can use the entity-linking method for a piece of Dutch biomedical text:
```python
from EL import EntityLinking

doc = "Bij wie wordt het risico op hart en vaatziekten geschat. Voor veel patiënten is een risicocategorie aan te wijzen zonder dat hun risico kwantitatief geschat hoeft te worden met een risicoscore. Denk aan patiënten met bestaande hart en vaatziekten, diabetes mellitus en daarmee gepaard gaande orgaanschade, ernstige chronische nierschade en extreem verhoogde risicofactoren. Deze categorieën staan toegelicht in tabel 1."


el = EntityLinking(doc)
print("Finished!")
```

## Citing This Package

If you use our package in your research or wish to refer to it in your academic papers, please cite the following paper:

```bibtex
@article{crosslinking_clinicalguideline,
  title={Cross-linking clinical practice guideline for multimorbidity},
  author={Majid Mohammadi, Annette ten Teije, Tim Christen, Janke de Groot, Marlies Verheoff},
  journal={Submitted},
  volume={2},
  number={21},
  pages={10-20},
  year={2024},
  publisher={Elsevier},
  doi={10.xxxx/xxxxxx}
}

