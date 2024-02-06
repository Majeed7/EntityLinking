# EntityLinking
## A Framework for Unsupervised Entity Linking in Dutch Biomedical Texts

### Introduction
EntityLinking is a sophisticated package designed specifically for unsupervised entity linking within Dutch biomedical texts. Utilizing an innovative unsupervised approach, this tool excels at identifying entities that closely resemble terms within a given text segment, correlating them with concepts from SNOMED. The methodology underpinning EntityLinking is particularly adept at navigating the complex landscape of biomedical terminology, providing valuable insights and connections to the SNOMED database without the need for supervised training.

### Features
- **Unsupervised Approach:** Operates without the need for manually labeled training data.
- **Compatibility with SNOMED and ICD-10:** Incorporates both terminologies, stored in optimized relational databases, ensuring swift lookup and retrieval.
- **Context-Aware Similarity:** Employs a sophisticated metric that evaluates term similarity within the textual context, enhancing accuracy in entity identification.
- **Customized Tokenization:** Features a specialized tokenizer designed to process HTML-formatted texts effectively, facilitating broader application.

### Installation
To utilize EntityLinking, begin by constructing the necessary SNOMED and ICD-10 databases using scripts found in the `dbCreation` directory. Pre-built databases, reflecting the latest versions of SNOMED and ICD-10, are available for download at [SURFdrive](https://surfdrive.surf.nl/files/index.php/s/jtF1auvFjVIqbT7). After downloading, place these databases in the `data` folder and initiate a sample entity linking process by running `run_me.py`.

### Credits
EntityLinking draws inspiration and leverages certain functionalities from PymedTermino, specifically its SQLite text search capabilities. This integration allows for enhanced performance and flexibility in handling biomedical terminologies. (See [PymedTermino](https://github.com/MedevaKnowledgeSystems/pymedtermino))

### Visualization
Included in the package is a lightweight Flask application designed to visually represent the results of the entity linking process. For details on deploying and using this visualization tool, consult `flask_app.py`.

### Requirements
The core functionalities of EntityLinking depend on several third-party Python libraries listed below. These must be installed to ensure the package operates as intended:

gensim==4.2.0
nltk==3.6.5
numpy==1.22.4
spacy==3.2.4
toolz==0.11.1


Additional requirements for the Flask visualization app include:

Flask==2.0.2
Flask_Bcrypt==1.0.1
html2text==2020.1.16


### Usage
Below is an example illustrating how to apply the EntityLinking method to analyze a snippet of Dutch biomedical text:

```python
from EL import EntityLinking

doc = "Bij wie wordt het risico op hart en vaatziekten geschat. Voor veel patiënten is een risicocategorie aan te wijzen zonder dat hun risico kwantitatief geschat hoeft te worden met een risicoscore. Denk aan patiënten met bestaande hart en vaatziekten, diabetes mellitus en daarmee gepaard gaande orgaanschade, ernstige chronische nierschade en extreem verhoogde risicofactoren. Deze categorieën staan toegelicht in tabel 1."

el = EntityLinking(doc)
print("Finished!")
```

### Citing This Package
For academic use of EntityLinking or references within research, please cite the following publication:
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

## Requirements
The following packages are the prerequisite for this package:

gensim==4.2.0
nltk==3.6.5
numpy==1.22.4
spacy==3.2.4
toolz==0.11.1

Also, for running the Flask app, the following packages are needed:

Flask==2.0.2
Flask_Bcrypt==1.0.1
html2text==2020.1.16

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

