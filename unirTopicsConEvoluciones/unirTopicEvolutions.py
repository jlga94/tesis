import openpyxl,pyLDAvis,pickle
from gensim.models import Phrases,Word2Vec,CoherenceModel,ldaseqmodel
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

def countWordsPerEvolutions():
	topics = readFile('topics')
	filenameFirst = 'Informatica_Lemmatizacion_LDA_OWN_Topic_'
	filenameSemLast = '_Th_15_P_3_Sem.txt'
	filenameTrimLast = '_Th_15_P_3_Trim.txt'

	numTopicGeneral = 0
	for topicWords in topics:
		wordsSem=dict()
		wordsTrim=dict()
		for topicWord in topicWords:
			wordsSem[topicWord]=0
			wordsTrim[topicWord]=0

		countTotalSem = {}
		countTotalTrim = {}
		for numTopic in range(len(topics)):
			countWordSem = dict(wordsSem)
			with open(filenameFirst+str(numTopic)+filenameSemLast) as fp:
				for line in fp:
					word_value = line.strip().split('-')
					if len(word_value)==2:
						word = word_value[0].split(':')[1].strip()
						if word in countWordSem.keys():
							countWordSem[word] += 1

			countWordTrim = dict(wordsTrim)
			with open(filenameFirst+str(numTopic)+filenameTrimLast) as fp:
				for line in fp:
					word_value = line.strip().split('-')
					if len(word_value)==2:
						word = word_value[0].split(':')[1].strip()
						if word in countWordTrim.keys():
							countWordTrim[word] += 1

			countTotalSem[numTopic] = sum(countWordSem.values())
			countTotalTrim[numTopic] = sum(countWordTrim.values())

		counterSem = Counter(countTotalSem)
		counterTrim = Counter(countTotalTrim)

		'''print('NumTopicGeneral: ' + str(numTopicGeneral) + ' - Sem')
		i=1
		for tup in counterSem.most_common(5):
			print(str(i)+': Topic: '+ str(tup[0]) + ' - Number of words: '+ str(tup[1]))
			i+=1'''

		print('NumTopicGeneral: ' + str(numTopicGeneral) + ' - Trim')
		i=1
		for tup in counterTrim.most_common(5):
			print(str(i)+': Topic: '+ str(tup[0]) + ' - Number of words: '+ str(tup[1]))
			i+=1

		numTopicGeneral += 1

def writeFile(topics,typeTime):
	F = open('topics_v2_'+typeTime+'.txt','w')
	for topicWords in topics:
		F.write(topicWords[0])
		for iTopicWord in range(1,len(topicWords)):
			F.write('-'+topicWords[iTopicWord])
		F.write('\n')
	F.close()

def relevantWordsPerTopicEvolution():
	filenameFirst = 'Informatica_Lemmatizacion_LDA_OWN_Topic_'
	filenameSemLast = '_Th_15_P_3_Sem.txt'
	filenameTrimLast = '_Th_15_P_3_Trim.txt'

	topicsSem = []
	topicsTrim = []

	for numTopic in range(8):
		countWordSem = dict()
		with open(filenameFirst+str(numTopic)+filenameSemLast) as fp:
			for line in fp:
				word_value = line.strip().split('-')
				if len(word_value)==2:
					word = word_value[0].split(':')[1].strip()
					if word in countWordSem.keys():
						countWordSem[word] += 1
					else:
						countWordSem[word] = 1

		countWordTrim = dict()
		with open(filenameFirst+str(numTopic)+filenameTrimLast) as fp:
			for line in fp:
				word_value = line.strip().split('-')
				if len(word_value)==2:
					word = word_value[0].split(':')[1].strip()
					if word in countWordTrim.keys():
						countWordTrim[word] += 1
					else:
						countWordTrim[word] = 1

		counterTopicSem = Counter(countWordSem)
		counterTopicTrim = Counter(countWordTrim)

		wordsTopTopicSem = []
		for tup in counterTopicSem.most_common(10):
			wordsTopTopicSem.append(tup[0])
		topicsSem.append(wordsTopTopicSem)

		wordsTopTopicTrim = []
		for tup in counterTopicTrim.most_common(10):
			wordsTopTopicTrim.append(tup[0])
		topicsTrim.append(wordsTopTopicTrim)

	writeFile(topicsSem,'Sem')
	writeFile(topicsTrim,'Trim')


#countWordsPerEvolutions()
relevantWordsPerTopicEvolution()
