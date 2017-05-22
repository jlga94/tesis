from gensim.models import Word2Vec
from preprocesamiento import TextProcessor
import wikipedia,pickle
from nltk.tokenize import sent_tokenize
from pymongo import MongoClient
import _thread
from mw.xml_dump import Iterator
import re,itertools
from bson.code import Code

def cleanSentenceÌnTokens(textprocessor,sentence):
	cadenaLemmatizada = textprocessor.lematizeText(sentence)
	cadenaPreProcesadaLemmatizada = textprocessor.preprocessText(cadenaLemmatizada)
	return textprocessor.removeStopwordsInList(cadenaPreProcesadaLemmatizada)

def trainWord2Vec(filename):
	carrerasXatributos = pickle.load(open(filename+ ".p","rb"))

	globalSentences = []
	numDoc = 0
	numGlobal = 0
	textprocessor = TextProcessor()
	for nameCareer,atributes in carrerasXatributos.items():
		print('NumDoc: '+str(numDoc))
		sentence = cleanSentenceÌnTokens(textprocessor,nameCareer)
		globalSentences.append(sentence)
		if atributes['otros_nombres'] != '':
			sentence = cleanSentenceÌnTokens(textprocessor,atributes['otros_nombres'])
			globalSentences.append(sentence)

		for sentence in sent_tokenize(atributes['descripcion'],language='spanish'):
			sentence = cleanSentenceÌnTokens(textprocessor,sentence)
			globalSentences.append(sentence)

		for sentence in atributes['funciones']:
			sentence = sentence.replace('\n','')
			sentence = cleanSentenceÌnTokens(textprocessor,sentence)
			globalSentences.append(sentence)

		for sentence in atributes['conocimiento']:
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n',' ')
			sentence = cleanSentenceÌnTokens(textprocessor,sentence)
			globalSentences.append(sentence)

		for sentence in atributes['aptitudes']:
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n',' ')
			sentence = cleanSentenceÌnTokens(textprocessor,sentence)
			globalSentences.append(sentence)

		for sentence in atributes['habilidades']:
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n',' ')
			sentence = cleanSentenceÌnTokens(textprocessor,sentence)
			globalSentences.append(sentence)

		for sentence in atributes['personalidad']:
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n',' ')
			sentence = cleanSentenceÌnTokens(textprocessor,sentence)
			globalSentences.append(sentence)

		for sentence in atributes['tecnologia']:
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n\n','\n')
			sentence = sentence.replace('\n',' ')
			sentence = cleanSentenceÌnTokens(textprocessor,sentence)
			globalSentences.append(sentence)

		numDoc+=1
	print('Build_vocab')
	print('Train')
	
	
	modelw2v = Word2Vec(sentences=globalSentences,iter=5, size=400, window=5, min_count=3, workers=4)
	print('Guardando word2vec')
	pickle.dump(modelw2v,open("modelw2v_onet" +  ".p","wb"))
	#modelw2v.save('/word2vec')

trainWord2Vec('carrerasXatributos')