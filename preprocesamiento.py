from nltk.corpus import stopwords
import csv
import operator
import codecs
import string
import math
import unicodedata
import treetaggerwrapper
import openpyxl
import re
import numpy
import warnings
from nltk.stem.snowball import SpanishStemmer
from langdetect import detect
from nltk.tokenize import sent_tokenize
from gensim.models import Phrases,Word2Vec


class TextProcessor:
    lemmatizer=None
    stopEnglish=None
    stopSpanish=None
    spanishStemmer=None

    def __init__(self):
        self.lemmatizer = treetaggerwrapper.TreeTagger(TAGLANG='es')
        self.stopEnglish = stopwords.words('english')
        self.stopSpanish = stopwords.words('spanish')
        self.stopSpanish.append('y/o')
        self.spanishStemmer=SpanishStemmer()
        #string.punctuation+='•'

    def _remove_numbers(self, text):
        "Elimina los números del texto"

        return ''.join([letter for letter in text if not letter.isdigit()])

    def _remove_punctuation(self, text):
        "Elimina los signos de puntuacion del texto"

        regex = re.compile('[%s]' % re.escape(string.punctuation))
        return regex.sub(' ', text)

    def _separateFirstLetterFromPunctuation(self,text):
    	newText=''
    	previousLetter='1'
    	for letter in text:
    		if(previousLetter in string.punctuation and letter.isalpha()):
    			newText+=' '   			
    		newText+=letter
    		previousLetter=letter
    	return newText

    def _retireRareLetters(self,text):
    	return ''.join([letter for letter in text if letter.isalpha() or letter in string.punctuation or letter==' ' or letter=='\n'])

    def _retireUrlsWWW(self,text):
    	return re.sub(r'\s*(?:https?://)?www\.\S*\.[A-Za-z]{2,5}\s*', '', text).strip()

    def _retireUrlsHTTP(self,text):
    	return re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', text).strip()

    def firstpreprocessText(self,text):
    	text=text.lower()
    	text=self._retireRareLetters(text)
    	text=self._retireUrlsWWW(text)
    	text=self._retireUrlsHTTP(text)
    	return text

    def preprocessText(self,text):
    	text=self._remove_punctuation(text)
    	text=self._remove_numbers(text)
    	return text

    def lematizeText(self,text):
    	newText = ""
    	lemmaElement = 2
    	
    	for sentence in sent_tokenize(text,language='spanish'): #Para 
    		textWithSeparatePunctuation=self._separateFirstLetterFromPunctuation(sentence)
    		lemmaResultText = self.lemmatizer.tag_text(textWithSeparatePunctuation)# Return [[word,type of word, lemma]]
    		#print(lemmaResultText)
    		for wordLemmaResult in lemmaResultText:
    			#print(word)
    			word = wordLemmaResult.split('\t')[lemmaElement].lower()
    			if word not in self.stopEnglish and word not in self.stopSpanish:
    				if not(len(word)==1 and not(word in string.punctuation)):
    					newText += ' ' + word
    	
    	return newText.strip()

    def stemText(self,text):
    	text=self._separateFirstLetterFromPunctuation(text)
    	newText = ""
    	for word in text.split():
    		if word not in self.stopEnglish and word not in self.stopSpanish:
    			word = word.replace("\ufeff", "")
    			if not(len(word)==1 and not(word in string.punctuation)):
    				wordStemmed = self.spanishStemmer.stem(word)
    				newText += " " + wordStemmed
    	return newText.strip()

class Input_Output:
    procesadorTextos=None

    def __init__(self):
        self.procesadorTextos=TextProcessor()
        self.secciones={}
        self.nombColumnas=[]

    def limpiarDataset_Steeming(self, dataset):
    	newDataset = []
    	for ofertaText in dataset:
    		ofertaText = self.procesadorTextos.preprocessText(ofertaText)
    		ofertaText = self.procesadorTextos.stemText(ofertaText)
    		listaPalabras = ofertaText.strip().split()
    		newDataset.append(listaPalabras)
    	print('Se termino de limpiarlo completamente con Steeming.')
    	return newDataset

    def limpiarDataset_Lemmatizacion(self, dataset):
    	newDataset = []
    	for oferta in dataset:
    		cadenaLemmatizada = self.procesadorTextos.lematizeText(oferta.strip())
    		cadenaPreProcesadaLemmatizada = self.procesadorTextos.preprocessText(cadenaLemmatizada)
    		listaPalabras = cadenaPreProcesadaLemmatizada.split()
    		newDataset.append(listaPalabras)
    	print('Se termino de limpiarlo completamente con Lemmatizacion.')
    	return newDataset

    def limpiarDataset_Steeming_Bigram(self, dataset):
    	bigram = Phrases(threshold=20)
    	newDataset = []
    	for ofertaText in dataset:
    		ofertaText = self.procesadorTextos.preprocessText(ofertaText)
    		ofertaText = self.procesadorTextos.stemText(ofertaText)
    		listaPalabras = ofertaText.strip().split()
    		bigram.add_vocab([listaPalabras])
    		newDataset.append(listaPalabras)
    	print('Se termino de limpiarlo completamente con Steeming-Bigram.')
    	return newDataset,bigram

    def limpiarDataset_Lemmatizacion_Bigram(self, dataset):
    	bigram = Phrases(threshold=20)
    	newDataset = []
    	for oferta in dataset:
    		cadenaLemmatizada = self.procesadorTextos.lematizeText(oferta.strip())
    		cadenaPreProcesadaLemmatizada = self.procesadorTextos.preprocessText(cadenaLemmatizada)
    		listaPalabras = cadenaPreProcesadaLemmatizada.split()
    		bigram.add_vocab([listaPalabras])
    		newDataset.append(listaPalabras)
    	print('Se termino de limpiarlo completamente con Lemmatizacion-Bigram.')
    	return newDataset,bigram

    def leerSecciones(self, filename):
    	dataset = []
    	wb = openpyxl.load_workbook(filename)
    	sheets = wb.get_sheet_names()
    	sheetAviso = wb.get_sheet_by_name(sheets[0])
    	maxColumnas = sheetAviso.max_column + 1
    	primeraFila = 1
    	for iColumna in range(1,maxColumnas):
    		seccion = str(sheetAviso.cell(row=primeraFila, column=iColumna).value)
    		self.nombColumnas.append(seccion)
    		self.secciones[seccion]=iColumna
    
    def buscarNombre_Descripcion_Conocimientos_Ofertas():
    	columnasABuscar=[]
    	columnasABuscar.append(self.secciones['Job: Job Title'])
    	columnasABuscar.append(self.secciones['Job: Description'])
    	columnasABuscar.append(self.secciones['Job: Qualifications'])
    	return columnasABuscar

    def obtenerDatasetAClasificar_Completo(self, filename):
        "Se lee un archivo Excel con las ofertas a clasificar"

        dataset = []
        wb = openpyxl.load_workbook(filename)
        sheets = wb.get_sheet_names()
        sheetAviso = wb.get_sheet_by_name(sheets[0])
        maxFilas = sheetAviso.max_row + 1

        for num_oferta in range(1, maxFilas):
            text = str(sheetAviso.cell(row=num_oferta, column=1).value)
            dataset.append(text)
        
        datasetLemmatizacion = self.limpiarDataset_Lemmatizacion(dataset)
        #datasetSteeming = self.limpiarDataset_Steeming(dataset)

        #return datasetSteeming
        return datasetLemmatizacion
        #return datasetLemmatizacion,datasetSteeming

    def obtenerDatasetAClasificar_Completo_Bigram(self, filename):
        "Se lee un archivo Excel con las ofertas a clasificar"

        dataset = []
        wb = openpyxl.load_workbook(filename)
        sheets = wb.get_sheet_names()
        sheetAviso = wb.get_sheet_by_name(sheets[0])
        maxFilas = sheetAviso.max_row + 1
        infoColumn = 1

        for num_oferta in range(1, maxFilas):
            text = str(sheetAviso.cell(row=num_oferta, column=infoColumn).value)
            dataset.append(text)
        
        datasetLemmatizacion,bigramLemmatizacion = self.limpiarDataset_Lemmatizacion_Bigram(dataset)
        #datasetSteeming,bigramSteeming = self.limpiarDataset_Steeming_Bigram(dataset)

        #return datasetSteeming
        return datasetLemmatizacion,bigramLemmatizacion#,datasetSteeming,bigramSteeming
        #return datasetLemmatizacion,datasetSteeming

    def obtenerDatasetAClasificar_Dividido(self, filename):
    	dataset_Title_Descp = []
    	dataset_Qualif = []
    	wb = openpyxl.load_workbook(filename)
    	sheets = wb.get_sheet_names()
    	sheetAviso = wb.get_sheet_by_name(sheets[0])
    	maxFilas = sheetAviso.max_row + 1
    	for num_oferta in range(1, maxFilas):
    		text_Title_Descp = str(sheetAviso.cell(row=num_oferta, column=1).value)
    		dataset_Title_Descp.append(text_Title_Descp)
    		
    		text_Qualif = str(sheetAviso.cell(row=num_oferta, column=2).value)
    		if (text_Qualif!=''):
    			dataset_Qualif.append(text_Qualif)

    	datasetLemmatizacion_Title_Descp = self.limpiarDataset_Lemmatizacion(dataset_Title_Descp)
    	datasetLemmatizacion_Qualif = self.limpiarDataset_Lemmatizacion(dataset_Qualif)

    	datasetSteeming_Title_Descp = self.limpiarDataset_Steeming(dataset_Title_Descp)
    	datasetSteeming_Qualif = self.limpiarDataset_Steeming(dataset_Qualif)

    	return datasetLemmatizacion_Title_Descp,datasetLemmatizacion_Qualif,datasetSteeming_Title_Descp,datasetSteeming_Qualif

    def contarIdiomasEnOfertas(self, filename):
    	dataset = []
    	wb = openpyxl.load_workbook(filename)
    	sheets = wb.get_sheet_names()
    	sheetAviso = wb.get_sheet_by_name(sheets[0])
    	maxFilas = sheetAviso.max_row + 1
    	maxColumnas = sheetAviso.max_column + 1

    	self.leerSecciones(filename)
    	columnasABuscar=[]
    	columnasABuscar.append(self.secciones['Job: Job Title'])
    	columnasABuscar.append(self.secciones['Job: Description'])
    	columnasABuscar.append(self.secciones['Job: Qualifications'])

    	ofertasRaras={}
    	idiomas={}
    	for num_oferta in range(2, maxFilas):
    		completeText = ''
    		for nColumna in columnasABuscar:
    			text = str(sheetAviso.cell(row=num_oferta, column=nColumna).value)
    			#completeText+=self.procesadorTextos.firstpreprocessText(text)
    			completeText+=' '+text.lower()
    		idioma = detect(completeText.strip())
    		if(idioma not in idiomas.keys()):
    			idiomas[idioma]=1
    		else:
    			idiomas[idioma]+=1
    		if(idioma!='es' and idioma!='en'):
    			if(idioma not in ofertasRaras.keys()):
    				ofertasRaras[idioma]=[completeText]
    			else:
    				ofertasRaras[idioma].append(completeText)
    	return idiomas,ofertasRaras
            


    def primeraLimpiezaADatasetAClasificar_Completo(self, filename):
    	wb = openpyxl.load_workbook(filename)
    	sheets = wb.get_sheet_names()
    	sheetAviso = wb.get_sheet_by_name(sheets[0])
    	maxFilas = sheetAviso.max_row + 1
    	maxColumnas = sheetAviso.max_column + 1

    	newExcel = openpyxl.Workbook()
    	newSheet = newExcel.active

    	self.leerSecciones(filename)
    	columnasABuscar=[]
    	columnasABuscar.append(self.secciones['Job: Job Title'])
    	columnasABuscar.append(self.secciones['Job: Description'])
    	columnasABuscar.append(self.secciones['Job: Qualifications'])

    	numColNewExcel_Text = 1
    	numColNewExcel_Year = 2
    	numColNewExcel_Month = 3

    	numRowNewExcel=1
    	for num_oferta in range(2, maxFilas):
    		completeText = ''
    		for nColumna in columnasABuscar:
    			text = str(sheetAviso.cell(row=num_oferta, column=nColumna).value)
    			completeText+=' ' + text.lower()
    		idioma = detect(completeText.strip())
    		if(idioma=='es'):
    			text = self.procesadorTextos.firstpreprocessText(completeText)
    			newSheet.cell(row=numRowNewExcel, column=numColNewExcel_Text).value = text

    			date = str(sheetAviso.cell(row=num_oferta, column=self.secciones['Job: Posting Date']).value)
    			print(date)
    			ddmmyyyy = date.split('/')

    			newSheet.cell(row=numRowNewExcel, column=numColNewExcel_Year).value = int(ddmmyyyy[2])
    			newSheet.cell(row=numRowNewExcel, column=numColNewExcel_Month).value = int(ddmmyyyy[1])

    			numRowNewExcel+=1

    	filenameWithoutExtension = filename.split('.')[0]
    	newExcel.save(filenameWithoutExtension + '_PrimerPreProcesamiento_Completo.xlsx')

    def primeraLimpiezaADatasetAClasificar_Dividido(self, filename):
    	wb = openpyxl.load_workbook(filename)
    	sheets = wb.get_sheet_names()
    	sheetAviso = wb.get_sheet_by_name(sheets[0])
    	maxFilas = sheetAviso.max_row + 1
    	maxColumnas = sheetAviso.max_column + 1

    	newExcel = openpyxl.Workbook()
    	newSheet = newExcel.active

    	self.leerSecciones(filename)
    	columnasABuscar=[]
    	columnasABuscar.append(self.secciones['Job: Job Title'])
    	columnasABuscar.append(self.secciones['Job: Description'])
    	#columnasABuscar.append(self.secciones['Job: Qualifications'])

    	nColQualifications = self.secciones['Job: Qualifications']

    	numColNewExcel_Title_Descp=1
    	numColNewExcel_Qualifications=2
    	numColNewExcel_Year=3
    	numColNewExcel_Month = 4

    	numRowNewExcel=1
    	for num_oferta in range(2, maxFilas):
    		title_descp_Text = ''
    		qualif_Text = str(sheetAviso.cell(row=num_oferta, column=nColQualifications).value).lower().strip()

    		for nColumna in columnasABuscar:
    			text = str(sheetAviso.cell(row=num_oferta, column=nColumna).value)
    			title_descp_Text+=' ' + text.lower()
    		title_descp_Text.strip()

    		idioma = detect(title_descp_Text+' '+qualif_Text) # Debe hacerse al texto completo
    		if(idioma=='es'):
    			title_descp_Text = self.procesadorTextos.firstpreprocessText(title_descp_Text)
    			qualif_Text = self.procesadorTextos.firstpreprocessText(qualif_Text)
    			
    			newSheet.cell(row=numRowNewExcel, column=numColNewExcel_Title_Descp).value = title_descp_Text
    			newSheet.cell(row=numRowNewExcel, column=numColNewExcel_Qualifications).value = qualif_Text
    			
    			date = str(sheetAviso.cell(row=num_oferta, column=self.secciones['Job: Posting Date']).value)
    			print(date)
    			ddmmyyyy = date.split('/')

    			newSheet.cell(row=numRowNewExcel, column=numColNewExcel_Year).value = int(ddmmyyyy[2])
    			newSheet.cell(row=numRowNewExcel, column=numColNewExcel_Month).value = int(ddmmyyyy[1])
    			
    			numRowNewExcel+=1

    	filenameWithoutExtension = filename.split('.')[0]
    	newExcel.save(filenameWithoutExtension + '_PrimerPreProcesamiento_Dividido.xlsx')

