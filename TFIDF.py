from preprocesamiento import Input_Output

import math,numpy, operator, pickle
from textblob import TextBlob as tb
from collections import Counter
from gensim.models import Phrases,Word2Vec,CoherenceModel

'''def tf(word, blob):
	return blob.words.count(word) / len(blob.words)

def n_containing(word, bloblist):
	return sum(1 for blob in bloblist if word in blob.words)

def idf(word, bloblist):
	return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))

def tfidf(word, blob, bloblist):
	return tf(word, blob) * idf(word, bloblist)

def example():
	document1 = tb(str("""Python is a 2000 made-for-TV horror movie directed by Richard
	Clabaugh. The film features several cult favorite actors, including William
	Zabka of The Karate Kid fame, Wil Wheaton, Casper Van Dien, Jenny McCarthy,
	Keith Coogan, Robert Englund (best known for his role as Freddy Krueger in the
	A Nightmare on Elm Street series of films), Dana Barron, David Bowe, and Sean
	Whalen. The film concerns a genetically engineered snake, a python, that
	escapes and unleashes itself on a small town. It includes the classic final
	girl scenario evident in films like Friday the 13th. It was filmed in Los Angeles,
	 California and Malibu, California. Python was followed by two sequels: Python
	 II (2002) and Boa vs. Python (2004), both also made-for-TV films.""").lower())

	document2 = tb(str("""Python, from the Greek word (πύθων/πύθωνας), is a genus of
	nonvenomous pythons[2] found in Africa and Asia. Currently, 7 species are
	recognised.[2] A member of this genus, P. reticulatus, is among the longest
	snakes known.""").lower())

	document3 = tb(str("""The Colt Python is a .357 Magnum caliber revolver formerly
	manufactured by Colt's Manufacturing Company of Hartford, Connecticut.
	It is sometimes referred to as a "Combat Magnum".[1] It was first introduced
	in 1955, the same year as Smith &amp; Wesson's M29 .44 Magnum. The now discontinued
	Colt Python targeted the premium revolver market segment. Some firearm
	collectors and writers such as Jeff Cooper, Ian V. Hogg, Chuck Hawks, Leroy
	Thompson, Renee Smeets and Martin Dougherty have described the Python as the
	finest production revolver ever made.""").lower())

	bloblist = [document1, document2, document3]
	for i, blob in enumerate(bloblist):
		print("Top words in document {}".format(i + 1))
		scores = {word: tfidf(word, blob, bloblist) for word in blob.words}
		
		sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
		print(sorted_words)
		for word, score in sorted_words[:3]:
			print("\tWord: {}, TF-IDF: {}".format(word, round(score, 5)))'''

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

def get_TFIDF(dataset,dictionaryDistribution): 
	TFIDF_dataset=[]
	N_documents = len(dataset)
	wordsList = sorted(dictionaryDistribution.keys())
	print('Cantidad de documentos: '+str(len(dataset)))	
	#i = 0

	for i in range(len(dataset)):
		document = dataset[i]
		print('Documento '+ str(i))
		maxCountWord = -1
		tf_words = []
		#print('Contando frecuencias')
		for word in wordsList: 
			tf = document.count(word)
			if tf > maxCountWord:
				maxCountWord = tf
			tf_words.append(tf)
			if dictionaryDistribution[word]==0:
				print('La palabra '+ word + ' tiene 0 en el IDF')
		#print('Normalizando y Multiplicando por IDF')
		for itemIndex in range(len(tf_words)): # Se tiene que normalizar el tf y multiplicar por el IDF
			tf_words[itemIndex]/=maxCountWord
			if tf_words[itemIndex]!=0:
				tf_words[itemIndex]*= math.log(N_documents / (1 + dictionaryDistribution[wordsList[itemIndex]])) #Se multiplica por el IDF version smooth

		TFIDF_dataset.append(tf_words)

	return TFIDF_dataset

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

def showImportantVariance(wordsVarianceDictionary,numArch,tipo):
	sortedByValue = sorted(wordsVarianceDictionary.items(),key=operator.itemgetter(1))
	quince_porciento = int(len(sortedByValue)*0.15)
	F = open(numArch + '_'+ tipo +'_Variance.txt','w')
	F.write('Los '+str(quince_porciento)+' primeros\n')
	for i in range(quince_porciento):
		F.write(str(i)+': '+sortedByValue[i][0]+' - '+ str(sortedByValue[i][1])+'\n')

	F.write('\nLos '+str(quince_porciento)+' ultimos\n')
	for i in range(len(sortedByValue)-1,len(sortedByValue)-quince_porciento-1,-1):
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
		diccionario = getDictionaryDistributionInDocuments(datasets[i])
		print('Procesando TF-IDF de ' + tipos[i])
		TFIDF_dataset = get_TFIDF(datasets[i],diccionario)
		pickle.dump(TFIDF_dataset,open("tfidf.p","wb"))

		print('Obteniendo varianza de '+ tipos[i])
		#wordsVarianceDictionary = getVariance(diccionario,TFIDF_dataset)
		print('Imprimiendo varianza de '+ tipos[i])
		#showImportantVariance(wordsVarianceDictionary,carrera,tipos[i])


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


TF_IDF_COMPLETO_BIGRAM('Informatica')
