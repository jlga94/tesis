from preprocesamiento import Input_Output
from gensim.models import Phrases,Word2Vec

def getVocabularyDistributionInDocuments(dataset):
	vocabularyDistribution = {}
	for document in dataset:
		for word in document:
			if word in vocabularyDistribution.keys():
				vocabularyDistribution[word]+=1
			else:
				vocabularyDistribution[word]=1
	return vocabularyDistribution

def collocationsTesting():
	inputOutput = Input_Output()
	carrera = 'Informatica'

	datasetLemmatizacion,bigramLemmatizacion,datasetSteeming,bigramSteeming = inputOutput.obtenerDatasetAClasificar_Completo_Bigram('Avisos_'+carrera+'_2011-2016_PrimerPreProcesamiento_Completo.xlsx')

	print('Obteniendo Vocabulario de Lemmatizacion')
	vocabularyLemmatizeDistribution = getVocabularyDistributionInDocuments(datasetLemmatizacion)
	#print('Obteniendo Vocabulario de Steeming')
	#vocabularySteemingDistribution = getVocabularyDistributionInDocuments(datasetSteeming)

	wordsTest = ['él','el','le','año','ser','hacer','tener','experiencia','bueno','afín','afine']

	print('Buscando palabras en Vocabulario Normal')
	for word in wordsTest:
		if word in vocabularyLemmatizeDistribution.keys():
			print(word + ': Se encuentra en vocabulario de Lemmatizacion')

	
	print('Comenzo bigram Lemma')
	bigram_model_Lemmatizacion = Word2Vec(bigramLemmatizacion[datasetLemmatizacion],size=100)
	#print('Comenzo bigram Steeming')
	#bigram_model_Steeming = Word2Vec(bigramSteeming[datasetSteeming],size=100)

	vocabularyLemmatizeBigram = bigram_model_Lemmatizacion.vocab.keys()

	print('Buscando palabras en Vocabulario Bigram')
	for word in wordsTest:
		if word in vocabularyLemmatizeBigram:
			print(word + ': Se encuentra en vocabulario de Lemmatizacion Bigram')
	
	'''
	nBigramas=0
	bigram_model_counter = Counter()
	for key in bigram_model.vocab.keys():
		if len(key.split("_"))>1 :
			bigram_model_counter[key] += bigram_model.vocab[key].count
			nBigramas+=1

	print('Cantidad de Keys: ' + str(len(bigram_model.vocab.keys())))
	print('Cantidad de Bigramas: '+ str(nBigramas))
	for key, counts in bigram_model_counter.most_common(50):
		print (key + ' - '+str(counts))
	'''

collocationsTesting()