from gensim import corpora,models
import gensim
from preprocesamiento import Input_Output

inputOutput = Input_Output()

idiomas,ofertasRaras = inputOutput.contarIdiomasEnOfertas('Avisos_Informatica_2011-2016.xlsx')

print(idiomas)
print(ofertasRaras)