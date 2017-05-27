from gensim.models import Word2Vec
from preprocesamiento import TextProcessor
import wikipedia,pickle
from nltk.tokenize import sent_tokenize
from pymongo import MongoClient
import _thread
from mw.xml_dump import Iterator
import re,operator
from gensim import corpora,models
from bson.code import Code
from collections import Counter


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
	wikiTopicArticles = []
	numTopic = 0
	for topicWords in topics:
		print("NunTopic: "+ str(numTopic))
		wikiArticlesPerTopic = set()

		for word in topicWords:
			terms = word.split('_')
			query = '"' + terms[0] + '"'
			if(len(terms)>1):
				query += ' AND "' + terms[1] + '"'
			titles = wikipedia.search(query,results=20)
			titles = set(titles)
			wikiArticlesPerTopic = wikiArticlesPerTopic.union(titles)

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
				titles = wikipedia.search(query,results=20)
				titles = set(titles)
				wikiArticlesPerTopic = wikiArticlesPerTopic.union(titles)
		wikiTopicArticles.append(wikiArticlesPerTopic)
		numTopic += 1
	return wikiTopicArticles

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


def getWikiTitleArticlesPerTopic():
	#topics = readFile('topics')
	topics = readFile_v2('topics_v2_Sem')
	wikiTopicArticles = titleArticles(topics)
	pickle.dump(wikiTopicArticles,open("wikiTopicArticles_te_sem" +  ".p","wb"))

def getWikiArticlePerTopic(filename):
	wikiTopicArticles = pickle.load(open(filename +  ".p","rb"))
	fileNameDump = 'eswiki/eswiki-20170420-pages-articles-multistream.xml'
	dump = Iterator.from_file(open(fileNameDump))

	client = MongoClient('localhost', 27017,maxPoolSize=200)
	db = client['tesisdb']
	career = 'Informatica'
	collection = db[career+'_wikiArticles_per_topic_te_sem']

	tp = TextProcessor()

	numTopics = len(wikiTopicArticles)

	numpage=0
	numArticlesFounds = 0
	for page in dump:
		articlesInTopic = []
		for articlesPerTopic in wikiTopicArticles:
			articlesInTopic.append(page.title in articlesPerTopic)

		if articlesInTopic.count(True)>0:
			numArticlesFounds+=1
			print('In topics: '+str(articlesInTopic) + ' - NumArticleFound: ' + str(numArticlesFounds) + ' - Numpage: ' + str(numpage) + ' - Title: ' + page.title)
			# Iterate through a page's revisions
			revisionText = ''
			for revision in page:
				revisionText += revision.text + '\n'
			text = cleanhtml(revisionText.strip()).strip()
			text = retire_HTMLParts(text).strip()
			text = retireParenthesis_Brackets(text).strip()
			text = importantText(text)
			text = tp.firstpreprocessText(text)
			WordsPerArticle = []
			for sentence in sent_tokenize(text,language='spanish'):
				sentence = cleanhtml(sentence).strip()
				cadenaLemmatizada = tp.lematizeText(sentence)
				cadenaPreProcesadaLemmatizada = tp.preprocessText(cadenaLemmatizada)
				sentenceTokens = tp.removeStopwordsInList(cadenaPreProcesadaLemmatizada)
				if len(sentenceTokens) > 0:
					WordsPerArticle.extend(sentenceTokens)

			insertsDB = {}
			for numTopic in range(numTopics):
				insertsDB['NumTopic '+str(numTopic)] = articlesInTopic[numTopic]

			insertsDB['NameArticle'] = page.title
			insertsDB['NumArticleFound'] = numArticlesFounds
			insertsDB['NumPageArticle'] = numpage
			insertsDB['Words'] = WordsPerArticle
			collection.insert_one(insertsDB)
		numpage+=1


def labelTopicByWordsInDocs(topicWordsWithPhrases,top_ten_words_per_doc,modelw2c):
	trained_model = modelw2c.wv

	topicWords = []
	for wordPosiblePhrase in topicWordsWithPhrases:
		for term in wordPosiblePhrase.split('_'):
			if term in trained_model.vocab.keys():
				topicWords.append(term)

	indMax = -1
	maxSimilarity = -100
	numDoc = 0
	contador = {}
	for top_ten_words in top_ten_words_per_doc:
		if len(top_ten_words)>0:
			AllInVocabTop = True
			for word in top_ten_words:
				if word not in trained_model.vocab.keys():
					AllInVocabTop = False
					break

			if AllInVocabTop:
				similarity = trained_model.n_similarity(topicWords, top_ten_words)
				#print(similarity)
				#if similarity > maxSimilarity:
				#	indMax = numDoc
				#	maxSimilarity = similarity
				contador[numDoc]=similarity
		numDoc+=1

	return Counter(contador)

def getValueTitle(mongoCursorItem):
	#print(mongoCursorItem)
	#title = mongoCursorItem['NameArticle']
	#words = mongoCursorItem['Words']
	#return (title,words)
	title = mongoCursorItem['NameArticle']
	return title

def getValueWords(mongoCursorItem):
	#print(mongoCursorItem)
	words = mongoCursorItem['Words']
	return [x for x in words if x!='']

def labelTopics():
	topics = readFile('topics')
	modelw2c = pickle.load(open("modelw2v_wiki_te_sem" +  ".p","rb"))

	client = MongoClient('localhost', 27017,maxPoolSize=200)
	db = client['tesisdb']
	career = 'Informatica'
	collection = db[career+'_wikiArticles_per_topic_te_sem']
	#list(map(getValue,collectionTFIDF.find({},{wordsList[wordIndex]:1,'_id':0})))

	for numTopic in range(len(topics)):
		#print('Find de Numtopic: ' + str(numTopic))
		titleArticles = list(map(getValueTitle,collection.find({'NumTopic '+str(numTopic):True},{'NameArticle':1,'_id':0})))
		dataset = list(map(getValueWords,collection.find({'NumTopic '+str(numTopic):True},{'Words':1,'_id':0})))
		#dataset = list(map(getValue,collection.find({'NumTopic '+str(numTopic):True},{'Words':1,'_id':0})))

		#print(articles_titles_words[0])
		#print(dataset)
		#dataset = []
		#titleArticles = []
		#print('Pasando a docs de Numtopic: ' + str(numTopic))
		#for doc in docs:
		#	dataset.append(doc['Words'])
		#	titleArticles.append(doc['NameArticle'])
		#'data mart' in modelw2c.wv.vocab.keys()

		dictionary = corpora.Dictionary(dataset)
		corpus = [dictionary.doc2bow(text) for text in dataset]

		#print('Instanciando TFIDF de Numtopic: ' + str(numTopic))
		tfidf = models.TfidfModel(corpus)
		corpus_tfidf = tfidf[corpus]

		#print('Obteniendo 10 mayores TFIDF de Numtopic: ' + str(numTopic))
		top_ten_words_per_doc=[]
		for doc in corpus_tfidf:
			d_valuePerDoc = {}
			for id, value in doc:
				word = dictionary.get(id)
				d_valuePerDoc[word] = value
			sortedByValue = sorted(d_valuePerDoc.items(),key=operator.itemgetter(1))
			top_ten_words= []
			maxWords = 10
			i = 0
			for tupleWord in sortedByValue:
				top_ten_words.append(sortedByValue[i][0])
				if i >= maxWords:
					break
				i+=1

			#for i in range(10):
			#	top_ten_words.append(sortedByValue[i][0])
			top_ten_words_per_doc.append(top_ten_words)
		#print('Cantidad de posibilidades: '+ str(len(top_ten_words_per_doc)))
		#print('Similitud de Numtopic: ' + str(numTopic))
		counter = labelTopicByWordsInDocs(topics[numTopic],top_ten_words_per_doc,modelw2c)
		print('NumTopic: '+ str(numTopic))
		i=1
		for tup in counter.most_common(10):
			print(str(i)+': Title: '+ titleArticles[tup[0]] + ' - Similarity: '+ str(tup[1]))
			i+=1
		 

getWikiTitleArticlesPerTopic()
getWikiArticlePerTopic("wikiTopicArticles_te_sem")
labelTopics()