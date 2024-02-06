
from EL import EntityLinking

doc = "Bij wie wordt het risico op hart en vaatziekten geschat. Voor veel patiënten is een risicocategorie aan te wijzen zonder dat hun risico kwantitatief geschat hoeft te worden met een risicoscore. Denk aan patiënten met bestaande hart en vaatziekten, diabetes mellitus en daarmee gepaard gaande orgaanschade, ernstige chronische nierschade en extreem verhoogde risicofactoren. Deze categorieën staan toegelicht in tabel 1."

# HTML file test
#f = open('html_test.txt','r')
#doc = f.read()
#f.close()

el = EntityLinking(doc)
print("Finished!")

