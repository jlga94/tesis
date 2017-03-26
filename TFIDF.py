from preprocesamiento import Input_Output

import math,numpy, operator, uuid
from textblob import TextBlob as tb
from collections import Counter
from gensim.models import Phrases,Word2Vec
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement
from pymongo import MongoClient
from bson.code import Code

'''
CREATE KEYSPACE tesis
WITH replication = {'class':'SimpleStrategy','replication_factor':3};

USE tesis;

CREATE TABLE career(
career text,
type text,
dictionary list<text>,
PRIMARY KEY (career,type));

CREATE TABLE tf_idf_word(
id uuid,
career text,
type text,
word text,
nDocument int,
tf_idf double,
PRIMARY KEY (id,career,type,word,nDocument));

CREATE TABLE variance_word(
id uuid,
career text,
type text,
word text,
variance double,
PRIMARY KEY (id,career,type,word));


'''


def getDictionaryDistributionInDocuments(dataset):
	dictionaryDistribution = {}
	for document in dataset:
		wordsInDocument=[]
		for word in document:
			if word in dictionaryDistribution.keys() and not (word in wordsInDocument): #Para no contar doble
				dictionaryDistribution[word]+=1
			else:
				dictionaryDistribution[word]=1
				wordsInDocument.append(word)

	return dictionaryDistribution

def insertDictionary(career,typePreprocess,dictionaryDistribution):
	wordsList = sorted(dictionaryDistribution.keys())

	cluster = Cluster()
	session = cluster.connect('tesis')
	query = "INSERT INTO career(career,type,dictionary) VALUES (?,?,?);"
	prepared = session.prepare(query)
	session.execute(prepared,(career,typePreprocess,wordsList))


def get_TFIDF_Cassandra(career,typePreprocess,dataset,dictionaryDistribution): 
	cluster = Cluster()
	session = cluster.connect('tesis')
	query = "INSERT INTO tf_idf_word(id,career,type,word,nDocument,tf_idf) VALUES (?,?,?,?,?,?);"
	prepared = session.prepare(query)

	#TFIDF_dataset=[]
	N_documents = len(dataset)
	wordsList = sorted(dictionaryDistribution.keys())
	print('Cantidad de documentos: '+str(len(dataset)))	
	
	#Se quedo 238
	for iDocument in range(len(dataset)):
		document = dataset[iDocument]
		print('Documento '+ str(iDocument))
		maxCountWord = -1
		tf_words = []

		for word in wordsList: 
			tf = document.count(word)
			if tf > maxCountWord:
				maxCountWord = tf
			tf_words.append(tf)
			if dictionaryDistribution[word]==0:
				print('La palabra '+ word + ' tiene 0 en el IDF')
		
		batch = BatchStatement()
		for itemIndex in range(len(tf_words)): # Se tiene que normalizar el tf y multiplicar por el IDF
			tf_words[itemIndex]/=maxCountWord
			if tf_words[itemIndex]!=0:
				tf_words[itemIndex]*= math.log(N_documents / (1 + dictionaryDistribution[wordsList[itemIndex]])) #Se multiplica por el IDF version smooth

			batch.add(prepared,(uuid.uuid1(),career,typePreprocess,wordsList[itemIndex],iDocument,tf_words[itemIndex]))
		
		session.execute(batch)

		#TFIDF_dataset.append(tf_words)

	#return TFIDF_dataset

def get_TFIDF_MongoDB(career,typePreprocess,dataset,dictionaryDistribution): 
	client = MongoClient('localhost', 27017)
	db = client['tesisdb']
	collection = db[career+'_'+typePreprocess]

	N_documents = len(dataset)
	wordsList = sorted(dictionaryDistribution.keys())
	print('Cantidad de documentos: '+str(len(dataset)))	
	
	for iDocument in range(len(dataset)):
		document = dataset[iDocument]
		print('Documento '+ str(iDocument))
		maxCountWord = -1
		tf_words = []

		for word in wordsList: 
			tf = document.count(word)
			if tf > maxCountWord:
				maxCountWord = tf
			tf_words.append(tf)
			if dictionaryDistribution[word]==0:
				print('La palabra '+ word + ' tiene 0 en el IDF')
		
		insertsDB = {}
		for itemIndex in range(len(tf_words)): # Se tiene que normalizar el tf y multiplicar por el IDF
			tf_words[itemIndex]/=maxCountWord
			if tf_words[itemIndex]!=0:
				tf_words[itemIndex]*= math.log(N_documents / (1 + dictionaryDistribution[wordsList[itemIndex]])) #Se multiplica por el IDF version smooth

			insertsDB[wordsList[itemIndex]] = tf_words[itemIndex]
			
		collection.insert_one(insertsDB)

def _update_Mean_Variance(n,x,mean,M2):
	n+=1
	delta = float(x - mean)
	mean += float(delta/n)
	delta2 = float(x - mean)
	M2 += float(delta*delta2)
	return mean,M2


def get_TFIDF_Mean_Variance(dataset,dictionaryDistribution): 

	N_documents = len(dataset)
	wordsList = sorted(dictionaryDistribution.keys())
	wordsMean = [0.0]*len(wordsList)
	wordsM2 = [0.0]*len(wordsList)
	print('Cantidad de documentos: '+str(len(dataset)))	
	
	for iDocument in range(len(dataset)):
		document = dataset[iDocument]
		print('Documento '+ str(iDocument))
		maxCountWord = -1
		tf_words = []

		for word in wordsList: 
			tf = document.count(word)
			if tf > maxCountWord:
				maxCountWord = tf
			tf_words.append(tf)
			if dictionaryDistribution[word]==0:
				print('La palabra '+ word + ' tiene 0 en el IDF')
		
		for itemIndex in range(len(tf_words)): # Se tiene que normalizar el tf y multiplicar por el IDF
			tf_words[itemIndex]/=maxCountWord
			if tf_words[itemIndex]!=0:
				tf_words[itemIndex]*= math.log(N_documents / (1 + dictionaryDistribution[wordsList[itemIndex]])) #Se multiplica por el IDF version smooth

			mean,M2 = _update_Mean_Variance(iDocument,tf_words[itemIndex],wordsMean[itemIndex],wordsM2[itemIndex])
			wordsMean[itemIndex] = mean
			wordsM2[itemIndex] = M2

	dictionaryMean = {}
	dictionaryVariance = {}
	for wordIndex in range(len(wordsList)):
		dictionaryMean[wordsList[wordIndex]] = wordsMean[wordIndex]
		dictionaryVariance[wordsList[wordIndex]] = wordsM2[wordIndex]/(len(wordsList)-1) #El numero de documentos debe ser mayor a 1
		print(wordsList[wordIndex]+': Mean = ' + str(wordsMean[wordIndex]) + ' - Varianza: '+ str(wordsM2[wordIndex]/(len(wordsList)-1)))

	return dictionaryMean,dictionaryVariance



def getVariance(dictionaryDistribution,TFIDF_dataset):
	wordsList = sorted(dictionaryDistribution.keys())
	wordsVarianceDictionary = {}
	cantidadPalabras = len(wordsList)
	print('Cantidad de palabras: '+str(cantidadPalabras))
	for wordIndex in range(cantidadPalabras):
		print('Palabra '+str(wordIndex)+': '+wordsList[wordIndex])
		tfidf_Word = []
		for documentIndex in range(len(TFIDF_dataset)):
			tfidf_Word.append(TFIDF_dataset[documentIndex][wordIndex])
		wordsVarianceDictionary[wordsList[wordIndex]] = numpy.array(tfidf_Word).var()
	return wordsVarianceDictionary

def getVariance_Cassandra(career,typePreprocess):
	cluster = Cluster()
	session = cluster.connect('tesis')
	query_tfidf_per_word = "SELECT tf_idf from tf_idf_word where career=? AND type=? AND word=?;"
	query_variance = "INSERT INTO variance_word(career,type,word,variance) VALUES (?,?,?,?);"


	wordsList = session.execute('SELECT dictionary from career where career='+career+' AND type=' + typePreprocess+';')
	
	print('Cantidad de palabras: '+str(len(wordsList)))
	for wordIndex in range(len(wordsList)):
		print('Palabra '+str(wordIndex)+': '+wordsList[wordIndex])
		prepared = session.prepare(query_tfidf_per_word)
		tfidf_Word = session.execute(prepared,(career,typePreprocess,wordsList[wordIndex]))
		variance_word = numpy.array(tfidf_Word).var()

		prepared = session.prepare(query_variance)
		session.execute(prepared,(career,typePreprocess,wordsList[wordIndex],variance_word))

def getValue(mongoCursorItem):
	#print(mongoCursorItem)
	return list(mongoCursorItem.values())[0]

def getVariance_MongoDB(career,typePreprocess):
	client = MongoClient('localhost', 27017)
	db = client['tesisdb']
	collectionVariance = db[career+'_'+typePreprocess+'_Estadistics']
	collectionTFIDF = db[career+'_'+typePreprocess]

	cluster = Cluster()
	session = cluster.connect('tesis')
	wordsList = session.execute('SELECT dictionary from career ;')[0].dictionary
	
	#print(wordsList)

	wordsVarianceDictionary = {}
	numWords = len(wordsList)
	print('Cantidad de palabras: '+str(numWords))
	for wordIndex in range(numWords):
		print('Palabra '+str(wordIndex)+': '+wordsList[wordIndex])
		tfidf_Word_Result = list(map(getValue,collectionTFIDF.find({},{wordsList[wordIndex]:1,'_id':0})))	
		print(len(tfidf_Word_Result))
		'''tfidf_Word = []
		for document in tfidf_Word_Result:
			#print(document)
			#print(document[wordsList[wordIndex]])
			tfidf_Word.append(document[wordsList[wordIndex]])'''
		print('Ya se tiene tfidf de: '+ wordsList[wordIndex])
		wordsVarianceDictionary[wordsList[wordIndex]] = numpy.array(tfidf_Word_Result).var()
		print('Ya se tiene varianza de: '+ wordsList[wordIndex])
	return wordsVarianceDictionary

def getVariance_MongoDB_MapReduce(career,typePreprocess):
	client = MongoClient('localhost', 27017)
	db = client['tesisdb']
	collectionEstadistics = db[career+'_'+typePreprocess+'__Estadistics']
	collectionTFIDF = db[career+'_'+typePreprocess]

	cluster = Cluster()
	session = cluster.connect('tesis')
	wordsList = session.execute('SELECT dictionary from career ;')[0].dictionary
	
	map = Code(open('map.js','r').read())
	reduce = Code(open('reduce.js','r').read())
	finalize = Code(open('finalize.js','r').read())


	wordsVarianceDictionary = {}
	numWords = len(wordsList)
	print('Cantidad de palabras: '+str(numWords))
	for wordIndex in range(numWords):
		print('Palabra '+str(wordIndex)+': '+wordsList[wordIndex])
		
		#query = {{},{wordsList[wordIndex]:1,'_id':0}}
		tfidf_Word_Result = collectionTFIDF.map_reduce(map,reduce,out={'inline':1},finalize=finalize,scope={'word':wordsList[wordIndex]})['results'][0]['value']

		print(tfidf_Word_Result)
		
		insertDocument = {'word':wordsList[wordIndex],'variance':tfidf_Word_Result['variance'],'average':tfidf_Word_Result['avg'],'stddev':tfidf_Word_Result['stddev'],
		'min':tfidf_Word_Result['min'],'max':tfidf_Word_Result['max'],
		'sum':tfidf_Word_Result['sum']}
		
		collectionEstadistics.insert_one(insertDocument)
		wordsVarianceDictionary[wordsList[wordIndex]] = tfidf_Word_Result['variance'] #lo bota como una lista por lo que hay ingresar como primer elemento
		print('Ya se tiene varianza de: '+ wordsList[wordIndex])


	return wordsVarianceDictionary


def mostrarMasRelevantes(diccionario,TFIDF_dataset,numArch,tipo):
	F = open(numArch + '_'+ tipo +'_TF_IDF.txt','w')
	diccionarioPalabras = sorted(diccionario.keys())
	nOferta=0
	for TFIDF_oferta in TFIDF_dataset:
		sorted_words = sorted(range(len(TFIDF_oferta)), key=lambda k:TFIDF_oferta[k], reverse=True)
		for i in range(5):
			F.write("Oferta: {}\tWord: {}, TF-IDF: {}\n".format(nOferta,diccionarioPalabras[sorted_words[i]], round(TFIDF_oferta[sorted_words[i]], 5)))
		nOferta+=1

	F.close()

def insertEstadistics_MongoDB(career,typePreprocess,dictionaryMean,dictionaryVariance):
	client = MongoClient('localhost', 27017)
	db = client['tesisdb']
	collectionEstadistics = db['Estadistics']

	wordsList = sorted(dictionaryVariance.keys())
	for word in wordsList:
		newDocument = {'career':career,'typePreprocess':typePreprocess,'word':word,'mean':float(dictionaryMean[word]),'variance':float(dictionaryVariance[word])}
		collectionEstadistics.insert_one(newDocument)


def showImportantVariance(wordsVarianceDictionary,numArch,tipo):
	sortedByValue = sorted(wordsVarianceDictionary.items(),key=operator.itemgetter(1))
	venticinco_porciento = int(len(sortedByValue)*0.25)
	F = open(numArch + '_'+ tipo +'_Variance.txt','w')
	F.write('Los '+str(venticinco_porciento)+' primeros\n')
	for i in range(venticinco_porciento):
		F.write(str(i)+': '+sortedByValue[i][0]+' - '+ str(sortedByValue[i][1])+'\n')

	F.write('\nLos '+str(venticinco_porciento)+' ultimos\n')
	for i in range(len(sortedByValue)-1,len(sortedByValue)-venticinco_porciento-1,-1):
		F.write(str(i)+': '+sortedByValue[i][0]+' - '+ str(sortedByValue[i][1])+'\n')

	F.close()

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


def TF_IDF_COMPLETO(carrera):
	inputOutput = Input_Output()
	datasetSteeming = inputOutput.obtenerDatasetAClasificar_Completo('Avisos_'+carrera+'_2011-2016_PrimerPreProcesamiento_Completo.xlsx')
	datasets = [datasetSteeming]
	tipos = ['Lemmatizacion']

	for i in range(len(tipos)):
		print('Procesando diccionario de '+ tipos[i])
		diccionario = getDictionaryDistributionInDocuments(datasets[i])
		print('Procesando TF-IDF de ' + tipos[i])
		TFIDF_dataset = get_TFIDF(datasets[i],diccionario)
		print(tipos[i] + ' Completo')
		mostrarMasRelevantes(diccionario,TFIDF_dataset,carrera,tipos[i])

	'''print('Procesando diccionario de Steeming')
	diccionarioSteeming = getDictionaryDistributionInDocuments(datasetSteeming)
	print('Procesando TF-IDF de Steeming')
	TFIDF_dataset_Steeming = get_TFIDF(datasetSteeming,diccionarioSteeming)
	print('Steeming Completo')
	mostrarMasRelevantes(diccionarioSteeming,TFIDF_dataset_Steeming)'''

def TF_IDF_COMPLETO_BIGRAM(carrera):
	inputOutput = Input_Output()
	#datasetLemmatizacion,bigramLemmatizacion,datasetSteeming,bigramSteeming = inputOutput.obtenerDatasetAClasificar_Completo_Bigram('Avisos_'+carrera+'_2011-2016_PrimerPreProcesamiento_Completo.xlsx')
	#datasetLemmatizacion,bigramLemmatizacion = inputOutput.obtenerDatasetAClasificar_Completo_Bigram('Avisos_'+carrera+'_2011-2016_PrimerPreProcesamiento_Completo.xlsx')

	print('Comenzo bigram Lemma')
	#bigram_model_Lemmatizacion = Word2Vec(bigramLemmatizacion[datasetLemmatizacion],size=100)
	#print('Comenzo bigram Steeming')
	#bigram_model_Steeming = Word2Vec(bigramSteeming[datasetSteeming],size=100)

	print('Comenzo bigram Lemma Reemplazo')
	#datasetLemmatizacionBigram = replaceBigrams(datasetLemmatizacion,bigram_model_Lemmatizacion)
	#print('Comenzo bigram Steeming Reemplazo')
	#datasetSteemingBigram = replaceBigrams(datasetSteeming,bigram_model_Steeming)

	#datasets = [datasetLemmatizacionBigram]
	tipos = ['Lemmatizacion']

	for i in range(len(tipos)):
		print('Procesando diccionario de '+ tipos[i])
		#diccionario = getDictionaryDistributionInDocuments(datasets[i])
		print('Insertando diccionario a BD de '+ tipos[i])
		#insertDictionary(carrera,tipos[i],diccionario)
		print('Procesando TF-IDF de ' + tipos[i])
		#TFIDF_dataset = get_TFIDF(carrera,tipos[i],datasets[i],diccionario)
		#get_TFIDF_MongoDB(carrera,tipos[i],datasets[i],diccionario)
		print('Obteniendo varianza de '+ tipos[i])
		#wordsVarianceDictionary = getVariance(diccionario,TFIDF_dataset)
		wordsVarianceDictionary = getVariance_MongoDB_MapReduce(carrera,tipos[i])
		print('Imprimiendo varianza de '+ tipos[i])
		showImportantVariance(wordsVarianceDictionary,carrera,tipos[i])

def TF_IDF_COMPLETO_BIGRAM_V2(carrera):
	inputOutput = Input_Output()
	#datasetLemmatizacion,bigramLemmatizacion,datasetSteeming,bigramSteeming = inputOutput.obtenerDatasetAClasificar_Completo_Bigram('Avisos_'+carrera+'_2011-2016_PrimerPreProcesamiento_Completo.xlsx')
	datasetLemmatizacion,bigramLemmatizacion = inputOutput.obtenerDatasetAClasificar_Completo_Bigram('Avisos_'+carrera+'_2011-2016_PrimerPreProcesamiento_Completo.xlsx')

	print('Comenzo bigram Lemma')
	bigram_model_Lemmatizacion = Word2Vec(bigramLemmatizacion[datasetLemmatizacion],size=100)
	#print('Comenzo bigram Steeming')
	#bigram_model_Steeming = Word2Vec(bigramSteeming[datasetSteeming],size=100)

	print('Comenzo bigram Lemma Reemplazo')
	datasetLemmatizacionBigram = replaceBigrams(datasetLemmatizacion,bigram_model_Lemmatizacion)
	#print('Comenzo bigram Steeming Reemplazo')
	#datasetSteemingBigram = replaceBigrams(datasetSteeming,bigram_model_Steeming)

	datasets = [datasetLemmatizacionBigram]
	tipos = ['Lemmatizacion']

	for i in range(len(tipos)):
		print('Procesando diccionario de '+ tipos[i])
		dictionaryDistribution = getDictionaryDistributionInDocuments(datasets[i])
		print('Insertando diccionario a BD de '+ tipos[i])
		insertDictionary(carrera,tipos[i],dictionaryDistribution)
		print('Procesando TF-IDF/Media/Varianza de ' + tipos[i])
		dictionaryMean,dictionaryVariance = get_TFIDF_Mean_Variance(datasets[i],dictionaryDistribution)
		print('Imprimiendo varianza de '+ tipos[i])
		showImportantVariance(dictionaryVariance,carrera,tipos[i])
		print('Insertando estadisticas de ' + tipos[i])
		insertEstadistics_MongoDB(carrera,tipos[i],dictionaryMean,dictionaryVariance)

def TF_IDF_DIVIDIDO(carrera):
	inputOutput = Input_Output()
	datasetLemmatizacion_Title_Descp,datasetLemmatizacion_Qualif,datasetSteeming_Title_Descp,datasetSteeming_Qualif = inputOutput.obtenerDatasetAClasificar_Dividido('Avisos_'+carrera+'_2011-2016_PrimerPreProcesamiento_Dividido.xlsx')
	datasets=[datasetLemmatizacion_Title_Descp,datasetLemmatizacion_Qualif,datasetSteeming_Title_Descp,datasetSteeming_Qualif]
	tipos = ['Lemmatizacion_Titulo_Descripcion','Lemmatizacion_Qualifications','Steeming_Titulo_Descripcion','Steeming_Qualifications']

	for i in range(len(tipos)):
		print('Procesando diccionario de '+ tipos[i])
		diccionario = getDictionaryDistributionInDocuments(datasets[i])
		print('Procesando TF-IDF de ' + tipos[i])
		TFIDF_dataset = get_TFIDF(datasets[i],diccionario)
		print(tipos[i] + ' Completo')
		mostrarMasRelevantes(diccionario,TFIDF_dataset,carrera,tipos[i])

	'''print('Procesando diccionario de Lemmatizacion Titulo-Descripcion')
	diccionarioLemmatizacion = getDictionaryDistributionInDocuments(datasetLemmatizacion)
	print('Procesando TF-IDF de Lemmatizacion Titulo-Descripcion')
	TFIDF_dataset_Lemmatizacion = get_TFIDF(datasetLemmatizacion,diccionarioLemmatizacion)
	print('Lemmatizacion Titulo-Descripcion')
	mostrarMasRelevantes(diccionarioLemmatizacion,TFIDF_dataset_Lemmatizacion)'''


TF_IDF_COMPLETO_BIGRAM_V2('Informatica')
