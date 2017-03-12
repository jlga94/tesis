from gensim import corpora,models
import gensim
from preprocesamiento import Input_Output

def LDA_GENSIM():
	inputOutput = Input_Output()
	carrera = 'Industrial'

	datasetLemmatizacion,datasetSteeming = inputOutput.obtenerDatasetAClasificar('Avisos_'+carrera+'_2011-2016_PrimerPreProcesamiento_Completo.xlsx')

	dictionaryLemma = corpora.Dictionary(datasetLemmatizacion)
	corpusLemma = [dictionaryLemma.doc2bow(text) for text in datasetLemmatizacion]

	dictionarySteeming = corpora.Dictionary(datasetSteeming)
	corpusSteeming = [dictionarySteeming.doc2bow(text) for text in datasetSteeming]

	listTopics= [10,15,20,25]
	listNumWords = []

	#ldamodelLemma = gensim.models.ldamodel.LdaModel(corpusLemma, num_topics=20,id2word = dictionaryLemma, passes=20)

	numArch = carrera
	for i in range(4):
		print('Empezando Lemma con: '+str(listTopics[i]))
		ldamodelLemma = gensim.models.ldamodel.LdaModel(corpusLemma, num_topics=listTopics[i],id2word = dictionaryLemma, passes=20)
		print('Se creo objeto')
		F = open(numArch + '_Lemmatizacion_'+str(listTopics[i])+'.txt','w')
		F.write(str(ldamodelLemma.print_topics(num_topics=listTopics[i],num_words=8)))
		F.close()
		print('Terminando Lemma con: '+str(listTopics[i]))

	for i in range(4):
		print('Empezando Steeming con: '+str(listTopics[i]))
		ldamodelSteeming = gensim.models.ldamodel.LdaModel(corpusSteeming, num_topics=listTopics[i],id2word = dictionarySteeming, passes=20)
		print('Se creo objeto')
		F = open(numArch + '_Steeming_'+str(listTopics[i])+'.txt','w')
		F.write(str(ldamodelSteeming.print_topics(num_topics=listTopics[i],num_words=8)))
		F.close()
		print('Terminando Steeming con: '+str(listTopics[i]))

LDA_GENSIM()