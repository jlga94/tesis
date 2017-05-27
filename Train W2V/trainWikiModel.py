from gensim.models import Word2Vec
from preprocesamiento import TextProcessor
import wikipedia,pickle
from nltk.tokenize import sent_tokenize
from pymongo import MongoClient
import _thread
from mw.xml_dump import Iterator
import re,itertools
from bson.code import Code

def readFile(filename):
	topics = []
	with open(filename+'.txt') as fp:
	    for line in fp:
	        #print(line)
	        topicsFrec = line.strip().split('+')
	        topicWords = []
	        for topicFrec in topicsFrec:
		        topicName = topicFrec.split('*')[1].strip()
		        topicName = topicName.split('"')[1]
		        topicWords.append(topicName)
	        topics.append(topicWords)
			
	return topics

def readFile_v2(filename):
	topics = []
	with open(filename+'.txt') as fp:
		for line in fp:
			topicWords = line.strip().split('-')
			topics.append(topicWords)
			
	return topics

def titleArticles(topics):
	wikipedia.set_lang('es')
	wikiArticles = set()
	numTopic = 0
	for topicWords in topics:
		print("NunTopic: "+ str(numTopic))

		for word in topicWords:
			terms = word.split('_')
			query = '"' + terms[0] + '"'
			if(len(terms)>1):
				query += ' AND "' + terms[1] + '"'
			titles = wikipedia.search(query,results=500)
			titles = set(titles)
			wikiArticles = wikiArticles.union(titles)

		for indFirstWord in range(len(topicWords)-1):

			for indSecondWord in range(indFirstWord+1,len(topicWords)):
				print('First: '+ topicWords[indFirstWord] + ' - Second: '+ topicWords[indSecondWord])
				terms = topicWords[indFirstWord].split('_')
				query = '"' + terms[0] + '"'
				if(len(terms)>1):
					query += ' AND "' + terms[1] + '"'
				terms = topicWords[indSecondWord].split('_')
				query += ' AND "' + terms[0] + '"'
				if(len(terms)>1):
					query += ' AND "' + terms[1] + '"'
				#print(query)
				titles = wikipedia.search(query,results=500)
				titles = set(titles)
				wikiArticles = wikiArticles.union(titles)
		numTopic += 1
	return wikiArticles

def retireParenthesis_Brackets(test_str):
	ret = ''
	skip1c = 0
	skip2c = 0
	for i in test_str:
		if i == '[':
			skip1c += 1
		elif i == '(':
			skip2c += 1
		elif i == ']' and skip1c > 0:
			skip1c -= 1
		elif i == ')'and skip2c > 0:
			skip2c -= 1
		elif skip1c == 0 and skip2c == 0:
			ret += i
	return ret

def cleanhtml(raw_html):
	cleanr = re.compile('<.*?>')
	cleantext = re.sub(cleanr, '', raw_html)
	return cleantext

def retire_HTMLParts(test_str):
	ret = ''
	skip1c = 0
	skip2c = 0
	for i in test_str:
		if i == '<':
			skip1c += 1
		elif i == '{':
			skip2c += 1
		elif i == '>' and skip1c > 0:
			skip1c -= 1
		elif i == '}'and skip2c > 0:
			skip2c -= 1
		elif skip1c == 0 and skip2c == 0:
			ret += i
	return ret

def importantText(text):
	text = text.split('== Enlaces externos ==')[0]
	text = text.split('== Referencias y notas ==')[0]
	text = text.split('== Enlaces relacionados ==')[0]
	text = text.split('== Bibliografía ==')[0]
	text = text.split('== Notas y referencias ==')[0]
	text = text.split('== Véase también ==')[0]
	text = text.split('== Referencias ==')[0]
	text = text.split('== Notas ==')[0]
	text = text.split('== Enlaces externosEditar ==')[0]
	text = text.split('== Véase tambiénEditar ==')[0]
	text = text.split('== ReferenciasEditar ==')[0]
	text = text.split('=== Referencias generales ===')[0]
	#text = retireParenthesis_Brackets(text)
	return text.strip()


#client = MongoClient('localhost', 27017,maxPoolSize=200)
def scrappingWikiArticles(numThread,wikiArticles,start,counter):
	#client = MongoClient('localhost', 27017+numThread)
	#print('creo cliente')
	wikipedia.set_lang('es')
	db = client['tesisdb']
	career = 'Informatica'
	collection = db[career+'_wiki_phrases']
	print('Creo collection')
	print(str(numThread) + ' ' + str(start))
	for numArticle in range(start,counter):
		titleArticle = wikiArticles[numArticle]
		print(titleArticle)
		try:
			pageArticle = wikipedia.page(titleArticle)
			print('Se obtuvo pageArticle')
			text = importantText(pageArticle.content)
			text = tp.firstpreprocessText(text)
			sentencesPerArticle = []
			for sentence in sent_tokenize(text,language='spanish'):
				cadenaLemmatizada = tp.lematizeText(sentence)
				cadenaPreProcesadaLemmatizada = tp.preprocessText(cadenaLemmatizada)
				sentenceTokens = tp.removeStopwordsInList(cadenaPreProcesadaLemmatizada)
				sentencesPerArticle.append(sentenceTokens)
			insertsDB = {}
			insertsDB['nameArticle'] = titleArticle
			insertsDB['numArticle'] = numArticle
			insertsDB['sentences'] = sentencesPerArticle
			print('Antes de Insert')
			collection.insert_one(insertsDB)
			print('Despues de Insert')
		except:
			pass


 
def getValue(mongoCursorItem):
	#print(mongoCursorItem)
	sentences = mongoCursorItem['Sentences']
	return [x for x in sentences if len(x)>0]



def trainWord2Vec_Final():
	client = MongoClient('localhost', 27017,maxPoolSize=200)
	db = client['tesisdb']
	career = 'Informatica'
	collection = db[career+'_wiki_phrases_te_sem']

	
	#map = Code(open('map.js','r').read())
	#reduce = Code(open('reduce.js','r').read())
	#finalize = Code(open('finalize.js','r').read())

	#dataset_Result = collection.map_reduce(map,reduce,out={'inline':1})#['results'][0]['Sentences']

	'''rangeLimitInferior = 0
	rangeLimitSuperior = 20000
	query = {'NumArticleFound': {"$gt":rangeLimitInferior,"$lt":rangeLimitSuperior}}
	print('Empezo consulta 1')
	globalSentences = collection.map_reduce(map,reduce,query=query,out={'inline':1},finalize=finalize)['results'][0]['Sentences']
	#print(dataset_Result)
	print('Instanciando Word2Vec')
	modelw2c = Word2Vec(globalSentences, size=100, window=5, min_count=25, workers=4)


	rangeLimitInferior = 19999
	rangeLimitSuperior = 40000
	query = {'NumArticleFound': {"$gt":rangeLimitInferior,"$lt":rangeLimitSuperior}}
	print('Empezo consulta 2')
	globalSentences = collection.map_reduce(map,reduce,query=query,out={'inline':1},finalize=finalize)['results'][0]['Sentences']
	print('Entrenando Word2Vec')
	modelw2c.train(globalSentences)


	rangeLimitInferior = 39999
	rangeLimitSuperior = 60000
	query = {'NumArticleFound': {"$gt":rangeLimitInferior,"$lt":rangeLimitSuperior}}
	print('Empezo consulta 3')
	globalSentences = collection.map_reduce(map,reduce,query=query,out={'inline':1},finalize=finalize)['results'][0]['Sentences']
	print('Entrenando Word2Vec')
	modelw2c.train(globalSentences)

	rangeLimitInferior = 59999
	rangeLimitSuperior = 70000
	query = {'NumArticleFound': {"$gt":rangeLimitInferior,"$lt":rangeLimitSuperior}}
	print('Empezo consulta 3')
	globalSentences = collection.map_reduce(map,reduce,query=query,out={'inline':1},finalize=finalize)['results'][0]['Sentences']
	print('Entrenando Word2Vec')
	modelw2c.train(globalSentences)'''

	'''rangeLimitInferior = 0
	rangeLimitSuperior = 25000
	#print('Empezo consulta 1')
	globalSentencesPerDocument = list(map(getValue,collection.find({'NumArticleFound': {"$gt":rangeLimitInferior,"$lt":rangeLimitSuperior}},{'Sentences':1,'_id':0})))
	#globalSentencesPerDocument = list(filter(lambda x: len(x)>0,collection.find({'NumArticleFound': {"$gt":rangeLimitInferior,"$lt":rangeLimitSuperior}},{'Sentences':1,'_id':0})))
	#print(globalSentencesPerDocument[0:3])
	print('Empezo a concatenar')

	globalSentences = [item for sublist in globalSentencesPerDocument for item in sublist]
	print(globalSentences[0:3])
	print('Instanciando Word2Vec')
	modelw2c = Word2Vec(globalSentences, size=100, window=5, min_count=25, workers=4)

	rangeLimitInferior = 24999
	rangeLimitSuperior = 50000
	print('Empezo consulta 2')
	globalSentencesPerDocument = list(map(getValue,collection.find({'NumArticleFound': {"$gt":rangeLimitInferior,"$lt":rangeLimitSuperior}},{'Sentences':1,'_id':0})))
	globalSentences = [item for sublist in globalSentencesPerDocument for item in sublist]
	print('Entrenando Word2Vec')
	modelw2c.train(globalSentences)

	rangeLimitInferior = 49999
	rangeLimitSuperior = 70000
	print('Empezo consulta 3')
	globalSentencesPerDocument = list(map(getValue,collection.find({'NumArticleFound': {"$gt":rangeLimitInferior,"$lt":rangeLimitSuperior}},{'Sentences':1,'_id':0})))
	globalSentences = [item for sublist in globalSentencesPerDocument for item in sublist]
	print('Entrenando Word2Vec')
	modelw2c.train(globalSentences)'''

	#rangeLimitInferior = 59999
	#rangeLimitSuperior = 70000
	#print('Empezo consulta 4')
	#globalSentences = list(map(getValue,collection.find({'NumArticleFound': {"$gt":rangeLimitInferior,"$lt":rangeLimitSuperior}},{'Sentences':1,'_id':0})))
	#print('Entrenando Word2Vec')
	#modelw2c.train(globalSentences)

	#print('Se obtuvo la lista despues del map')

	#print('Empezo a concatenar')
	#globalSentences = [item for sublist in globalSentencesPerDocument for item in sublist]
	#print('Finalizo de concatenar')
	#print('Cantidad de Sentences: ' + str(len(globalSentences)))


	#modelw2v = Word2Vec(iter=5, size=400, window=5, min_count=15, workers=4)
	globalSentences = []
	numDoc = 0
	numGlobal = 0
	trainBefore = False
	print('Entrenando word2vec')
	for doc in collection.find({},{'Sentences':1,'_id':0}):
		print('NumDoc: '+str(numDoc))
		sentences = doc['Sentences']
		cleanSentences = [x for x in sentences if len(x)>0]
		'''if numGlobal== 18000:
			numGlobal = 0
			if trainBefore:
				modelw2c.build_vocab(globalSentences,update=True)
				modelw2c.train(sentences)
			else:
				modelw2c.build_vocab(globalSentences,update=False)
				modelw2c.train(sentences)
				trainBefore = True
			globalSentences = []
		else:'''
		
		globalSentences.extend(cleanSentences)
		
		#globalSentences.extend(doc['Sentences'])
		numDoc+=1
		#numGlobal+=1
	print('Build_vocab')
	#modelw2v.build_vocab(globalSentences)
	print('Train')
	#modelw2v.train(globalSentences)

	modelw2v = Word2Vec(sentences=globalSentences,iter=5, size=400, window=5, min_count=15, workers=4)
	'''numDoc = 0
	for doc in collection.find({},{'Sentences':1,'_id':0}):
		print('NumDoc: '+str(numDoc))
		sentences = doc['Sentences']
		cleanSentences = [x for x in sentences if len(x)>0]
		
		modelw2c.train(sentences)

		#globalSentences.extend(doc['Sentences'])
		numDoc+=1'''
	
	#modelw2c = Word2Vec(globalSentences, size=100, window=5, min_count=25, workers=4)
	

	#print('Guardando wikisentences')
	#pickle.dump(globalSentences,open("wikiSentences" +  ".p","wb"))
	#print('Entrenando word2vec')
	#modelw2c = Word2Vec(globalSentences, size=100, window=5, min_count=25, workers=4)
	print('Guardando word2vec')
	pickle.dump(modelw2v,open("modelw2v_wiki_te_sem" +  ".p","wb"))
	#modelw2v.save('/word2vec')


def unionAllArticles(filename):
	wikiTopicArticles = pickle.load(open(filename +  ".p","rb"))
	wikiAllArticles = set()
	for articlesPerTopic in wikiTopicArticles:
		wikiAllArticles = wikiAllArticles.union(articlesPerTopic)
	return wikiAllArticles


def preProcessWikiArticles(filename):
	wikiArticles = pickle.load(open(filename +  ".p","rb"))
	#wikiArticles = unionAllArticles(filename)
	print('Cantidad de articulos: '+ str(len(wikiArticles)))
	fileNameDump = 'eswiki/eswiki-20170420-pages-articles-multistream.xml'
	dump = Iterator.from_file(open(fileNameDump))
	tp = TextProcessor()
	client = MongoClient('localhost', 27017,maxPoolSize=200)
	db = client['tesisdb']
	career = 'Informatica'
	collection = db[career+'_wiki_phrases_te_sem']

	#globalSentences = []
	numArticlesFounds = 0
	# Iterate through pages
	numpage=0
	for page in dump:
		if page.title in wikiArticles:
			numArticlesFounds+=1
			print('NumArticleFound: ' + str(numArticlesFounds) + ' - Numpage: ' + str(numpage) + ' - Title: ' + page.title)
			# Iterate through a page's revisions
			revisionText = ''
			for revision in page:
				revisionText += revision.text + '\n'
			text = cleanhtml(revisionText.strip()).strip()
			text = retire_HTMLParts(text).strip()
			text = retireParenthesis_Brackets(text).strip()
			text = importantText(text)
			text = tp.firstpreprocessText(text)
			sentencesPerArticle = []
			for sentence in sent_tokenize(text,language='spanish'):
				sentence = cleanhtml(sentence).strip()
				cadenaLemmatizada = tp.lematizeText(sentence)
				cadenaPreProcesadaLemmatizada = tp.preprocessText(cadenaLemmatizada)
				sentenceTokens = tp.removeStopwordsInList(cadenaPreProcesadaLemmatizada)
				if len(sentenceTokens) > 0:
					sentencesPerArticle.append(sentenceTokens)
				#globalSentences.append(sentenceTokens)

			insertsDB = {}
			insertsDB['NameArticle'] = page.title
			insertsDB['NumArticleFound'] = numArticlesFounds
			insertsDB['NumPageArticle'] = numpage
			insertsDB['Sentences'] = sentencesPerArticle
			collection.insert_one(insertsDB)

		numpage+=1

	#pickle.dump(globalSentences,open("wikiSentences" +  ".p","wb"))
	#modelw2c = Word2Vec(globalSentences, size=100, window=5, min_count=25, workers=4)
	#pickle.dump(modelw2c,open("modelw2c_wiki" +  ".p","wb"))
	#modelw2c.save('/word2vec')


def trainWord2Vec(filename):
	tp = TextProcessor()
	wikiArticles = pickle.load(open(filename +  ".p","rb"))
	wikipedia.set_lang('es')

	#client = MongoClient('localhost', 27017)
	db = client['tesisdb']
	career = 'Informatica'
	collection = db[career+'_wiki_phrases']

	wikiArticles = list(wikiArticles)
	wikiArticles.sort()
	print(len(wikiArticles))
	numThreads = 4
	numArticles = int(len(wikiArticles)/numThreads)
	numExtraArticles = int(len(wikiArticles)%numThreads)

	'''try:
		for numThread in range(numThreads):
			if numThread<numThreads-1:
				_thread.start_new_thread( scrappingWikiArticles, (numThread,wikiArticles, numThread*numArticles, numArticles, ) )
			else:
				_thread.start_new_thread( scrappingWikiArticles, (numThread,wikiArticles, numThread*numArticles, numArticles+numExtraArticles, ) )
	except:
		print ("Error: unable to start thread")	'''
	globalSentences = []
	numArticle = 1
	for titleArticle in wikiArticles:
		print('NumArticle: '+ str(numArticle)+ ' - ' +titleArticle)
		numArticle+=1
		try:
			pageArticle = wikipedia.page(titleArticle)
			text = importantText(pageArticle.content)
			text = tp.firstpreprocessText(text)
			sentencesPerArticle = []
			for sentence in sent_tokenize(text,language='spanish'):
				cadenaLemmatizada = tp.lematizeText(sentence)
				cadenaPreProcesadaLemmatizada = tp.preprocessText(cadenaLemmatizada)
				sentenceTokens = tp.removeStopwordsInList(cadenaPreProcesadaLemmatizada)
				sentencesPerArticle.append(sentenceTokens)
				globalSentences.append(sentenceTokens)

			insertsDB = {}
			insertsDB['nameArticle'] = titleArticle
			insertsDB['numArticle'] = numArticle
			insertsDB['sentences'] = sentencesPerArticle
			collection.insert_one(insertsDB)
		except:
			pass

	pickle.dump(globalSentences,open("wikiSentences" +  ".p","wb"))
	modelw2c = Word2Vec(sentences, size=100, window=5, min_count=25, workers=4)
	modelw2c.save('/word2vec')


#topics = readFile_v2('topics_v2_Sem')
#wikiArticles = titleArticles(topics)
#pickle.dump(wikiArticles,open("wikiArticles_v2_te_sem" +  ".p","wb"))

#trainWord2Vec("wikiArticles_v2") ya no sirve
#preProcessWikiArticles("wikiArticles_v2_te_sem")
#preProcessWikiArticles("wikiTopicArticles")
trainWord2Vec_Final()