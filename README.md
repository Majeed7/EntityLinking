# EntityLinking
## A Framework for Unsupervised Entity Linking in Dutch Biomedical Texts

### Introduction
This package inlcudes an entity-linking method parituclalry tested on Dutch biomedical text. The method is unsupervised and identifies the similar entities to a part of text based on its similarity to the SNOMED concepts.

### Features
- **Unsupervised Approach:** Operates without the need for manually labeled training data.
- **Compatibility with SNOMED and ICD-10:** Incorporates both terminologies, stored in optimized relational databases, ensuring swift lookup and retrieval.
- **Context-Aware Similarity:** Employs a sophisticated metric that evaluates term similarity within the textual context, enhancing accuracy in entity identification.
- **Customized Tokenization:** Features a specialized tokenizer designed to process HTML-formatted texts effectively, facilitating broader application.

### Installation
To utilize the package, begin by constructing the necessary SNOMED and ICD-10 databases using scripts found in the `dbCreation` directory. Pre-built databases, reflecting the latest versions of SNOMED and ICD-10, are available for download at [here](https://surfdrive.surf.nl/files/index.php/s/jtF1auvFjVIqbT7). After downloading, place these databases in the `data` folder and initiate a sample entity linking process by running `run_me.py`.

### Credits
EntityLinking draws inspiration and leverages certain functionalities from PymedTermino, specifically its SQLite text search capabilities. This integration allows for enhanced performance and flexibility in handling biomedical terminologies. (See [PymedTermino](https://github.com/MedevaKnowledgeSystems/pymedtermino))

### Visualization
Included in the package is a lightweight Flask application designed to visually represent the results of the entity linking process. For details on deploying and using this visualization tool, consult `flask_app.py`.

### Requirements
The core functionalities of EntityLinking depend on several third-party Python libraries listed below. These must be installed to ensure the package operates as intended:
```
gensim==4.2.0
nltk==3.6.5
numpy==1.22.4
spacy==3.2.4
toolz==0.11.1
```

Additional requirements for the Flask visualization app include:
```
Flask==2.0.2
Flask_Bcrypt==1.0.1
html2text==2020.1.16
```

### Entity Linking for Other Languages
To extend the EntityLinking package for use with languages other than Dutch, the key step involves incorporating the appropriate SNOMED CT and ICD-10 terminologies for the target language. This process begins by obtaining the SNOMED and ICD-10 terminology files, which are essential for the entity-linking process. Once these terminology files are acquired, users can utilize the provided scripts in the `dbCreation` directory to construct searchable databases from these terminologies. These databases should then be placed in the `data` folder of this package. This adaptation allows the package to be applied to biomedical text analysis across different linguistic contexts.

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
```
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
```

### Contact
For any questions or inquiries regarding the EntityLinking package, please feel free to reach out to Majid Mohammadi (majid.mohammadi690@gmail.com). We welcome your feedback and are here to assist with any issues or clarifications you may need.
