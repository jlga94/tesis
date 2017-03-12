from gensim import corpora,models
import gensim
from preprocesamiento import Input_Output
from collections import Counter
from gensim.models import Phrases,Word2Vec,CoherenceModel

def writeLDAFile(numArch,tipo,listTopics,dictionary,corpus):
	for i in range(len(listTopics)):
		print('Empezando '+ tipo +' con: '+str(listTopics[i]))
		ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=listTopics[i],id2word = dictionary, passes=20)
		print('Se creo objeto')
		cm = CoherenceModel(model=ldamodel,corpus=corpus,coherence='u_mass')
		print('Coherencia de ' + numArch + '_'+ tipo +'_'+str(listTopics[i]) + ': ' +str(cm.get_coherence()))
		F = open(numArch + '_'+ tipo +'_'+str(listTopics[i])+'.txt','w')
		F.write(str(ldamodel.print_topics(num_topics=listTopics[i],num_words=8)))
		F.close()
		print('Terminando '+ tipo +' con: '+str(listTopics[i]))

def LDA_GENSIM_COMPLETO():
	inputOutput = Input_Output()
	carrera = 'Contabilidad'

	datasetLemmatizacion,datasetSteeming = inputOutput.obtenerDatasetAClasificar_Completo('Avisos_'+carrera+'_2011-2016_PrimerPreProcesamiento_Completo.xlsx')

	dictionaryLemma = corpora.Dictionary(datasetLemmatizacion)
	corpusLemma = [dictionaryLemma.doc2bow(text) for text in datasetLemmatizacion]

	dictionarySteeming = corpora.Dictionary(datasetSteeming)
	corpusSteeming = [dictionarySteeming.doc2bow(text) for text in datasetSteeming]

	listTopics= [10,15,20,25]
	listNumWords = []

	#ldamodelLemma = gensim.models.ldamodel.LdaModel(corpusLemma, num_topics=20,id2word = dictionaryLemma, passes=20)

	writeLDAFile(carrera,'Lemmatizacion',listTopics,dictionaryLemma,corpusLemma)
	writeLDAFile(carrera,'Steeming',listTopics,dictionarySteeming,corpusSteeming)


def LDA_GENSIM_DIVIDIDO():
	inputOutput = Input_Output()
	carrera = 'Industrial'

	datasetLemmatizacion_Title_Descp,datasetLemmatizacion_Qualif,datasetSteeming_Title_Descp,datasetSteeming_Qualif = inputOutput.obtenerDatasetAClasificar_Dividido('Avisos_'+carrera+'_2011-2016_PrimerPreProcesamiento_Dividido.xlsx')

	dictionaryLemma_T_D = corpora.Dictionary(datasetLemmatizacion_Title_Descp)
	corpusLemma_T_D = [dictionaryLemma_T_D.doc2bow(text) for text in datasetLemmatizacion_Title_Descp]

	dictionaryLemma_Q = corpora.Dictionary(datasetLemmatizacion_Qualif)
	corpusLemma_Q = [dictionaryLemma_Q.doc2bow(text) for text in datasetLemmatizacion_Qualif]

	dictionarySteeming_T_D = corpora.Dictionary(datasetSteeming_Title_Descp)
	corpusSteeming_T_D = [dictionarySteeming_T_D.doc2bow(text) for text in datasetSteeming_Title_Descp]

	dictionarySteeming_Q = corpora.Dictionary(datasetSteeming_Qualif)
	corpusSteeming_Q = [dictionarySteeming_Q.doc2bow(text) for text in datasetSteeming_Qualif]

	listTopics= [10,15,20,25]
	
	#ldamodelLemma = gensim.models.ldamodel.LdaModel(corpusLemma, num_topics=20,id2word = dictionaryLemma, passes=20)

	writeLDAFile(carrera,'Lemmatizacion_T_D',listTopics,dictionaryLemma_T_D,corpusLemma_T_D)
	writeLDAFile(carrera,'Lemmatizacion_Q',listTopics,dictionaryLemma_Q,corpusLemma_Q)
	writeLDAFile(carrera,'Steeming_T_D',listTopics,dictionarySteeming_T_D,corpusSteeming_T_D)
	writeLDAFile(carrera,'Steeming_Q',listTopics,dictionarySteeming_Q,corpusSteeming_Q)

def replaceBigrams(dataset,bigram_model):
	newDataset=[]
	for words_oferta in dataset:
		N_words = len(words_oferta)
		i=0
		while(i < N_words-1):
			possible_bigram = words_oferta[i] + '_' +words_oferta[i+1]
			if (possible_bigram in bigram_model.vocab.keys()):
				words_oferta[i] = possible_bigram # Se reemplaza la palabra del indice i por el bigrama
				words_oferta.pop(i+1)
				N_words-=1
			i+=1
		newDataset.append(words_oferta)
	return newDataset

def replaceBigrams_v2(dataset,bigram_model):
	newDataset=[]
	for words_oferta in dataset:
		N_words = len(words_oferta)
		i=0
		while(i < N_words-1):
			possible_bigram = words_oferta[i] + '_' +words_oferta[i+1]
			if (possible_bigram in bigram_model.vocab.keys()):
				words_oferta.insert(i,possible_bigram) #se agrega el bigrama como indice sin borrar los unigramas
				i+=1
				N_words+=1
			i+=1
		newDataset.append(words_oferta)
	return newDataset


def LDA_GENSIM_COMPLETO_BIGRAM():
	inputOutput = Input_Output()
	carrera = 'Informatica'

	datasetLemmatizacion,bigramLemmatizacion,datasetSteeming,bigramSteeming = inputOutput.obtenerDatasetAClasificar_Completo_Bigram('Avisos_'+carrera+'_2011-2016_PrimerPreProcesamiento_Completo.xlsx')

	print('Comenzo bigram Lemma')
	bigram_model_Lemmatizacion = Word2Vec(bigramLemmatizacion[datasetLemmatizacion],size=100)
	print('Comenzo bigram Steeming')
	bigram_model_Steeming = Word2Vec(bigramSteeming[datasetSteeming],size=100)

	print('Comenzo bigram Lemma Reemplazo')
	datasetLemmatizacionBigram = replaceBigrams(datasetLemmatizacion,bigram_model_Lemmatizacion)
	print('Comenzo bigram Steeming Reemplazo')
	datasetSteemingBigram = replaceBigrams(datasetSteeming,bigram_model_Steeming)

	dictionaryLemma = corpora.Dictionary(datasetLemmatizacionBigram)
	corpusLemma = [dictionaryLemma.doc2bow(text) for text in datasetLemmatizacionBigram]

	dictionarySteeming = corpora.Dictionary(datasetSteemingBigram)
	corpusSteeming = [dictionarySteeming.doc2bow(text) for text in datasetSteemingBigram]

	listTopics= [18,19,21,22]
	listNumWords = []

	writeLDAFile(carrera,'Lemmatizacion_Bigram',listTopics,dictionaryLemma,corpusLemma)
	writeLDAFile(carrera,'Steeming_Bigram',listTopics,dictionarySteeming,corpusSteeming)


	'''
	#print(str(bigram_model.vocab))
	#print(str(bigram_model.vocab.keys()))
	nBigramas=0
	bigram_model_counter = Counter()
	for key in bigram_model.vocab.keys():
		if len(key.split("_"))>1 :
			bigram_model_counter[key] += bigram_model.vocab[key].count
			nBigramas+=1

	print('Cantidad de Keys: ' + str(len(bigram_model.vocab.keys())))
	print('Cantidad de Bigramas: '+ str(nBigramas))
	for key, counts in bigram_model_counter.most_common(50):
		print (key + ' - '+str(counts))'''



LDA_GENSIM_COMPLETO_BIGRAM()
#LDA_GENSIM_COMPLETO()
#LDA_GENSIM_DIVIDIDO()