from gensim import corpora,models
import gensim
from preprocesamiento import Input_Output
from collections import Counter
from gensim.models import Phrases,Word2Vec,CoherenceModel,ldaseqmodel
import openpyxl,pyLDAvis,pickle


def replaceBigrams(dataset,bigram_model):
	newDataset=[]
	for words_oferta in dataset:
		N_words = len(words_oferta)
		i=0
		while(i < N_words-1):
			possible_bigram = words_oferta[i] + '_' +words_oferta[i+1]
			if (possible_bigram in bigram_model.wv.vocab.keys()):
				words_oferta[i] = possible_bigram # Se reemplaza la palabra del indice i por el bigrama
				words_oferta.pop(i+1)
				N_words-=1
			i+=1
		newDataset.append(words_oferta)
	return newDataset

def DTM():
	inputOutput = Input_Output()
	carrera = 'Informatica'
	k_topic = 11
	thresholds = [15]
	typeProcessing = 'Lemmatizacion'

	datasetLemmatizacion,bigramsLemmatizacion,datasetStemming,bigramsStemming = inputOutput.obtenerDatasetAClasificar_Completo_Bigram('Avisos_'+carrera+'_2011-2016_PrimerPreProcesamiento_Completo.xlsx',thresholds)

	datasetBigram = None

	print('Comenzo bigram_model de '+ typeProcessing)
	if typeProcessing == 'Lemmatizacion':		
		bigramLemmatizacion = bigramsLemmatizacion[0]		
		bigram_model = Word2Vec(bigramLemmatizacion[datasetLemmatizacion],size=100)
		print('Comenzo bigram Lemma Reemplazo')
		datasetBigram = replaceBigrams(datasetLemmatizacion,bigram_model)
	else:
		bigramStemming = bigramsStemming[0]		
		bigram_model = Word2Vec(bigramStemming[datasetStemming],size=100)
		print('Comenzo bigram Steeming Reemplazo')
		datasetBigram = replaceBigrams(datasetStemming,bigram_model)
	
	pickle.dump(datasetBigram,open("datasetBigram_"+ typeProcessing + "_" + str(thresholds[0]) +"_"+ str(k_topic) + ".p","wb"))
	'''
	datasetBigram = pickle.load(open("datasetBigram_"+ typeProcessing + "_" + str(thresholds[0]) +"_"+ str(k_topic) + ".p","rb"))
	'''
	print('Comenzo a obtener diccionarios y corpus para Gensim de '+typeProcessing)
	vocabularyBigram = corpora.Dictionary(datasetBigram)
	corpusBigram = [vocabularyBigram.doc2bow(text) for text in datasetBigram]

	'''
	print('Inicializando LDA')
	
	ldamodel = gensim.models.ldamodel.LdaModel(corpusBigram, num_topics=k_topic,id2word = vocabularyBigram, passes=20,iterations=100)
	pickle.dump(ldamodel,open("ldamodel_"+ typeProcessing + "_" + str(thresholds[0]) +"_"+ str(k_topic)+".p","wb"))
	
	ldamodel = pickle.load(open("ldamodel_"+ typeProcessing + "_" + str(thresholds[0]) +"_"+ str(k_topic)+".p","rb"))
	'''
	'''
	print(ldamodel.print_topics(num_topics=k_topic,num_words=15))
	cm_coherence_Model = CoherenceModel(model=ldamodel,corpus=corpusBigram,texts=datasetBigram,coherence='c_v')
	print('La coherencia c_v del modelo LDA '+ typeProcessing + ' es:' + str(cm_coherence_Model.get_coherence()))
	'''
	time_slice_semester = [619,1424,1636,1653,1369,1397,1552,1513,1282,1295,1101] # num documentos por periodos de tiempo por semestre
	time_slice_trimester = [259,360,498,926,849,787,836,817,717,652,651,746,927,625,765,748,716,566,626,669,622,479] # num documentos por periodos de tiempo por trisemestre
	
	print('Inicializando DTM')
	'''
	dtmModel = ldaseqmodel.LdaSeqModel(lda_model=ldamodel,corpus=corpusBigram,id2word = vocabularyBigram,time_slice=time_slice_semester,num_topics=k_topic)
	print('Inicializo DTM v1')	
	pickle.dump(dtmModel,open("DTM_model_"+ typeProcessing + "_" + str(thresholds[0]) +"_"+ str(k_topic)+".p","wb"))
	'''

	dtmModel = ldaseqmodel.LdaSeqModel(corpus=corpusBigram,id2word = vocabularyBigram,time_slice=time_slice_trimester,num_topics=k_topic)
	print('Inicializo DTM v2')	
	pickle.dump(dtmModel,open("DTM_model_V2_tri_"+ typeProcessing + "_" + str(thresholds[0]) +"_"+ str(k_topic)+".p","wb"))


	#dtmModel = pickle.load(open("DTM_model_"+ typeProcessing + "_" + str(thresholds[0]) +"_"+ str(k_topic)+".p","rb"))

	#dtmModel = pickle.load(open("DTM_model_V2_"+ typeProcessing + "_" + str(thresholds[0]) +"_"+ str(k_topic)+".p","rb"))

	typeTime = 'trimester'

	#cm_DTM = CoherenceModel(model=dtmModel,corpus=corpusBigram,texts=datasetBigram,coherence='c_v')
	#print('La coherencia c_v del modelo LDA '+ typeProcessing + ' es:' + str(cm_DTM.get_coherence()))

	'''
	for iTime in range(len(time_slice_semester)):
		topics_DTM = dtmModel.dtm_coherence(time=iTime)
		cm_DTM = CoherenceModel(topics=topics_DTM,dictionary=vocabularyBigram,texts=datasetBigram,coherence='c_v')
		print('La coherencia c_v del modelo DTM '+ typeProcessing + ' en '+ str(iTime)+ ' es:' + str(cm_DTM.get_coherence()))
	'''

	'''
	for iTopic in range(k_topic):
		F = open(carrera + '_'+ typeProcessing +'_'+str(iTopic)+'_'+typeTime+'.txt','w')
		#print('Topic '+ str(iTopic)+':')
		for iTime in range(len(time_slice_semester)):
			F.write('Time '+ str(iTime)+':\n')
			#print('\tTime '+ str(iTime)+':')
			for tupleWord in dtmModel.print_topic(topic=iTopic,time=iTime):
				F.write('\tWord: '+vocabularyBigram.get(int(tupleWord[0])) + ' - Value: ' + str(tupleWord[1])+'\n')
				#print('\t\tWord: '+vocabularyBigram.get(int(tupleWord[0])) + ' - Value: ' + str(tupleWord[1]))
		F.close()
	'''
	for iTopic in range(k_topic):
		F = open(carrera + '_V2_'+ typeProcessing +'_'+str(iTopic)+'_'+typeTime+'.txt','w')
		#print('Topic '+ str(iTopic)+':')
		for iTime in range(len(time_slice_trimester)):
			F.write('Time '+ str(iTime)+':\n')
			#print('\tTime '+ str(iTime)+':')
			for tupleWord in dtmModel.print_topic(topic=iTopic,time=iTime):
				F.write('\tWord: '+ tupleWord[0] + ' - Value: ' + str(tupleWord[1])+'\n')
				#print('\t\tWord: '+vocabularyBigram.get(int(tupleWord[0])) + ' - Value: ' + str(tupleWord[1]))
		F.close()


	'''
	for iTime in range(len(time_slice_semester)):
		doc_topic, topic_term,doc_lengths, term_frequency,vocab = dtmModel.dtm_vis(time=iTime,corpus=corpusBigram)
		vis_wrapper = pyLDAvis.prepare(topic_term_dists=topic_term,doc_topic_dists=doc_topic,doc_lengths=doc_lengths,vocab=vocab,term_frequency=term_frequency)
		pyLDAvis.display(vis_wrapper)
	'''

def printTopicsDTM(career,typeProcessing,k_topic,threshold,porcTFIDF,typeTime,time_slice,dtmModel):
	for iTopic in range(k_topic):
		F = open(career + '_'+ typeProcessing +'_Topic_'+str(iTopic)+'_Th_'+ str(threshold) + '_P_'+ str(porcTFIDF) + '_'+typeTime+'.txt','w')
		#print('Topic '+ str(iTopic)+':')
		for iTime in range(len(time_slice)):
			F.write('Time '+ str(iTime)+':\n')
			#print('\tTime '+ str(iTime)+':')
			for tupleWord in dtmModel.print_topic(topic=iTopic,time=iTime):
				F.write('\tWord: '+ tupleWord[0] + ' - Value: ' + str(tupleWord[1])+'\n')
				#print('\t\tWord: '+vocabularyBigram.get(int(tupleWord[0])) + ' - Value: ' + str(tupleWord[1]))
		F.close()

def process_DTM_TimeSlice(career,typeProcessing,k_topic,threshold,porcTFIDF,typeTime,corpus,vocabulary,time_slice):
	print('Inicializando DTM ' + typeProcessing + '_'+ typeTime)
	dtmModel = ldaseqmodel.LdaSeqModel(corpus=corpus,id2word = vocabulary,time_slice=time_slice,num_topics=k_topic)
	print('Inicializo DTM ' + typeProcessing + '_'+ typeTime)
	pickle.dump(dtmModel,open("DTM_"+ career + '_' +typeProcessing + "_K_" + str(k_topic) +"_Th_"+ str(threshold) + '_P_'+ str(porcTFIDF) + '_' + typeTime +".p","wb"))
	print('Imprimiendo topicos de DTM ' + typeProcessing + '_'+ typeTime)
	printTopicsDTM(career,typeProcessing,k_topic,threshold,porcTFIDF,typeTime,time_slice,dtmModel)

def process_DTM_TimeSlice_LDA(career,typeProcessing,k_topic,threshold,porcTFIDF,typeTime,corpus,vocabulary,time_slice):
	print('Inicializando LDA '+ typeProcessing)
	ldamodel = gensim.models.ldamodel.LdaModel(corpus=corpus, num_topics=k_topic,id2word = vocabulary, passes=20,iterations=100)
	pickle.dump(ldamodel,open("LDA_model_"+ typeProcessing + "_K_" + str(k_topic) +"_Th_"+ str(threshold) + '_P_'+ str(porcTFIDF)+".p","wb"))

	print('Inicializando DTM_LDA ' + typeProcessing + '_'+ typeTime)
	dtmModel = ldaseqmodel.LdaSeqModel(lda_model=ldamodel,sstats=(len(vocabulary.items()),k_topic),corpus=corpus,id2word = vocabulary,time_slice=time_slice,num_topics=k_topic)
	print('Inicializo DTM ' + typeProcessing + '_'+ typeTime)
	pickle.dump(dtmModel,open("DTM_LDA_"+ career + '_' +typeProcessing + "_K_" + str(k_topic) +"_Th_"+ str(threshold) + '_P_'+ str(porcTFIDF) + '_' + typeTime +".p","wb"))
	print('Imprimiendo topicos de DTM_LDA ' + typeProcessing + '_'+ typeTime)
	printTopicsDTM(career,typeProcessing+'_LDA',k_topic,threshold,porcTFIDF,typeTime,time_slice,dtmModel)

def process_DTM_by_Typeprocessing(career,typeProcessing,k_topic,threshold,porcTFIDF,dataset_TFIDF,time_slice_semester,time_slice_trimester):
	print('Comenzo a obtener diccionarios y corpus para Gensim de '+typeProcessing)
	vocabulary = corpora.Dictionary(dataset_TFIDF)
	corpus = [vocabulary.doc2bow(text) for text in dataset_TFIDF]

	typeTime = 'Sem'
	#process_DTM_TimeSlice(career,typeProcessing,k_topic,threshold,porcTFIDF,typeTime,corpus,vocabulary,time_slice_semester)
	process_DTM_TimeSlice_LDA(career,typeProcessing,k_topic,threshold,porcTFIDF,typeTime,corpus,vocabulary,time_slice_semester)

	typeTime = 'Trim'
	process_DTM_TimeSlice(career,typeProcessing,k_topic,threshold,porcTFIDF,typeTime,corpus,vocabulary,time_slice_trimester)
	process_DTM_TimeSlice_LDA(career,typeProcessing,k_topic,threshold,porcTFIDF,typeTime,corpus,vocabulary,time_slice_trimester)


def DTM_BIGRAM_TFIDF():
	career = 'Informatica'
	
	k_topic_Lemma = 7
	threshold_Lemma = 24
	porcTFIDF_Lemma = 3

	k_topic_Stem = 12
	threshold_Stem = 24
	porcTFIDF_Stem = 1

	#dataset_TFIDF_Lemma = pickle.load(open("DatasetTFIDF_" + career + '_'+ 'Lemmatizacion' + "_Th_" + str(threshold_Lemma) + '_Porc_' + str(porcTFIDF_Lemma)+".p","rb"))
	#dataset_TFIDF_Stem = pickle.load(open("DatasetTFIDF_" + career + '_'+ 'Stemming' + "_Th_" + str(threshold_Stem) + '_Porc_' + str(porcTFIDF_Stem)+".p","rb"))

	dataset_TFIDF_Lemma = pickle.load(open("DatasetTFIDF_Filter_DQ_" + career + '_'+ 'Lemmatizacion_Filter_DQ_' + "_Th_" + str(threshold_Lemma) + '_Porc_' + str(porcTFIDF_Lemma)+".p","rb"))
	#dataset_TFIDF_Stem = pickle.load(open("DatasetTFIDF_Filter_DQ_" + career + '_'+ 'Stemming_Filter_DQ_' + "_Th_" + str(threshold_Stem) + '_Porc_' + str(porcTFIDF_Stem)+".p","rb"))
	print(len(dataset_TFIDF_Lemma))


	time_slice_semester = [619,1419,1636,1653,1368,1397,1552,1513,1285,1294,1102] # num documentos por periodos de tiempo por semestre
	time_slice_trimester = [259,360,495,924,849,787,837,816,716,652,651,746,927,625,765,748,719,566,626,668,623,479] # num documentos por periodos de tiempo por trisemestre

	typeProcessing = 'Lemmatizacion'
	process_DTM_by_Typeprocessing(career,typeProcessing,k_topic_Lemma,threshold_Lemma,porcTFIDF_Lemma,dataset_TFIDF_Lemma,time_slice_semester,time_slice_trimester)

	#typeProcessing = 'Stemming'
	#process_DTM_by_Typeprocessing(career,typeProcessing,k_topic_Stem,threshold_Stem,porcTFIDF_Stem,dataset_TFIDF_Stem,time_slice_semester,time_slice_trimester)


#DTM()
DTM_BIGRAM_TFIDF()