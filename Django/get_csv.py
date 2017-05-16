from gensim import corpora,models
from gensim.models import ldaseqmodel
import pickle,csv,json
import numpy as np
from math import *

def get_time_slices(datesLemmatizacion):
	time_slice_semester = [0]
	time_slice_trimester = [0]

	count_sem = 0
	count_trim = 0
	for year in sorted(datesLemmatizacion.keys()):
		for month in sorted(datesLemmatizacion[year].keys()):
			if count_sem==6:
				count_sem = 0
				time_slice_semester.append(0)
			if count_trim==3:
				count_trim = 0
				time_slice_trimester.append(0)
			time_slice_semester[len(time_slice_semester)-1] += datesLemmatizacion[year][month]
			time_slice_trimester[len(time_slice_trimester)-1] += datesLemmatizacion[year][month]

			count_sem += 1
			count_trim += 1

	return time_slice_semester,time_slice_trimester

def getMeanVariationInTimeSlice(variationsInTimeSlice):
	numTopics = len(variationsInTimeSlice[0])
	meanVariation = []
	for numTopic in range(numTopics):
		relevanceInNumTopic = []
		for numDoc in variationsInTimeSlice:
			relevanceInNumTopic.append(numDoc[numTopic])
		mean = np.array(relevanceInNumTopic).mean()
		meanVariation.append(mean)
	return meanVariation


def writeCSVfile(variationPerTimeSlice,career,k_topic,typeTime,dates):
	with open('data_'+career+'_'+str(k_topic)+'_'+typeTime+'.csv', 'w') as csvfile:
		fieldnames = ['key', 'value','date']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

		writer.writeheader()
		for iTopic in range(k_topic-1,-1,-1):
			for iTimeSlice in range(len(dates)):
				if iTimeSlice == len(dates)-1:
					writer.writerow({'key': 'Topic '+str(iTopic+1), 'value': float('%.3f' % (variationPerTimeSlice[iTimeSlice-1][iTopic])),'date':dates[iTimeSlice]})
				else:
					writer.writerow({'key': 'Topic '+str(iTopic+1), 'value': float('%.3f' % (variationPerTimeSlice[iTimeSlice][iTopic])),'date':dates[iTimeSlice]})


def getVariationPerTimeSlice(time_slice,dtmModel):
	variationPerTimeSlice = []
	numDocTS = 0
	for numDocsTSlice in time_slice:
		variationsInTimeSlice = []
		print('NumDoc: '+str(numDocTS))
		for numDoc in range(numDocsTSlice):
			doc_topics = list(dtmModel.doc_topics(numDocTS))
			variationsInTimeSlice.append(doc_topics)
			numDocTS +=1
		print('Obteniendo Mean')
		meanVariation = getMeanVariationInTimeSlice(variationsInTimeSlice)
		variationPerTimeSlice.append(meanVariation)	

	return variationPerTimeSlice

def get_csv():
	career = 'Informatica'
	typeProcessing = 'Lemmatizacion'
	k_topic = 8
	threshold = 15
	porcTFIDF = 3

	typeTime = 'Trim'

	dtmModel = pickle.load(open("DTM_LDA_OWN"+ career + '_' +typeProcessing + "_K_" + str(k_topic) +"_Th_"+ str(threshold) + '_P_'+ str(porcTFIDF) + '_' + typeTime +".p","rb"))
	datesLemmatizacion = pickle.load(open("datesLemmatizacion_" + career + ".p","rb"))
	time_slice_semester, time_slice_trimester = get_time_slices(datesLemmatizacion)
	#print(time_slice_semester)
	print(time_slice_trimester)	
	print('Se obtuvieron los time slices')

	#variationPerTimeSliceSem = getVariationPerTimeSlice(time_slice_semester,dtmModel)
	variationPerTimeSliceTrim = getVariationPerTimeSlice(time_slice_trimester,dtmModel)

	dates_Sem = ['07/11','01/12','07/12','01/13','07/13','01/14','07/14','01/15','07/15','01/16','07/16','01/17']
	dates_Trim = ['07/11','10/11','01/12','04/12','07/12','10/12','01/13','04/13','07/13','10/13','01/14','04/14','07/14','10/14','01/15','04/15','07/15','10/15','01/16','04/16','07/16','10/16','01/17']
	print('Writing CSV')
	#writeCSVfile(variationPerTimeSliceSem,career,k_topic,typeTime,dates_Sem)
	writeCSVfile(variationPerTimeSliceTrim,career,k_topic,typeTime,dates_Trim)

def get_json_labels(filename):

	labels = dict()

	with open(filename+'.txt') as fp:
		numTopicActual = -1
		for line in fp:
			topicTitle = line.strip().split('--')
			if len(topicTitle)>1:
				atributes = topicTitle[0].strip().split(':')
				labels['Topic ' + str(numTopicActual)].append(atributes[2].strip())
			else:
				print(line)
				numTopic = int(line.strip().split(':')[1])+1
				numTopicActual = numTopic
				labels['Topic ' + str(numTopic)] = []

	print(labels)
	with open(filename + '.json', 'w') as outfile:
		json.dump(labels, outfile)
	

def get_json_topic_evolution(typeTime,k_topic):
	filenameFirstPart = 'DTM/Informatica_Lemmatizacion_LDA_OWN_Topic_'
	filenameLastPart = '_Th_15_P_3_'

	topic_evolutions = {}
	for iTopic in range(k_topic):
		wordsPerTime = {}
		with open(filenameFirstPart+str(iTopic)+filenameLastPart+typeTime+'.txt') as fp:
			currentTime = None
			for line in fp:
				word_value = line.strip().split('-')
				if len(word_value)>1:
					word = word_value[0].strip().split(':')[1].strip()
					wordsPerTime[currentTime].append(word)
				else:
					time = int(line.strip().split()[1].split(':')[0].strip())
					currentTime = time
					wordsPerTime[currentTime] = []
		print(wordsPerTime)
		topic_evolutions['Topic ' + str(iTopic+1)] = wordsPerTime

	print(topic_evolutions)

	with open('topic_evolution_'+ typeTime + '.json', 'w') as outfile:
		json.dump(topic_evolutions, outfile)






#get_csv()
#get_json_labels('labels_te_sem')
dates_Sem = ['07/11','01/12','07/12','01/13','07/13','01/14','07/14','01/15','07/15','01/16','07/16','01/17']
dates_Trim = ['07/11','10/11','01/12','04/12','07/12','10/12','01/13','04/13','07/13','10/13','01/14','04/14','07/14','10/14','01/15','04/15','07/15','10/15','01/16','04/16','07/16','10/16','01/17']
get_json_topic_evolution('Sem',8)
