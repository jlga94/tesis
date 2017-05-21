import re
from bs4 import BeautifulSoup
import urllib.request as urllib2
import pickle
from nltk.tokenize import sent_tokenize


def getHTML_carreras():

	webpage='https://www.miproximopaso.org/find/browse?c=0'
	hdr = {'User-Agent': 'Mozilla/5.0'}
	req = urllib2.Request(webpage,headers=hdr)
	page = urllib2.urlopen(req)
	html = page.read()
	BsObj = BeautifulSoup(html,'lxml');
	htmltext = html.decode('utf-8')
	#print(htmltext)

	#<td class="title odd"><a href="/profile/summary/23-1011.00">Abogados</a></td>
	#<td class="title even"><a href="/profile/summary/39-3031.00">Acomodadores y Controladores de Boletos de Admisión</a></td>

	oddUrls = re.findall('<td class="title odd"><a href="(.*?)</a></td>', htmltext,flags=re.S)
	evenUrls = re.findall('<td class="title even"><a href="(.*?)</a></td>', htmltext,flags=re.S)

	carreras = {}

	for url in oddUrls:
		url_carrera = url.split('">')
		carreras[url_carrera[1]] = 'https://www.miproximopaso.org' + url_carrera[0]

	for url in evenUrls:
		url_carrera = url.split('">')
		carreras[url_carrera[1]] = 'https://www.miproximopaso.org' + url_carrera[0]

	print(len(carreras.keys()))

	pickle.dump(carreras,open("carreras_onet_"+ ".p","wb"))

def cleanhtml(raw_html):
	cleanr = re.compile('<.*?>')
	cleantext = re.sub(cleanr, '', raw_html)
	return cleantext


def get_content(htmltext):
	otros_nombres = re.findall('<b>También llamado:</b>(.*?)</p>', htmltext,flags=re.S)
	if (len(otros_nombres)>0):
		otros_nombres = otros_nombres[0].replace('\n','').strip().lower()
	else:
		otros_nombres = ''

	descripcion = re.findall('>Lo que hacen:</div>(.*?)</div>', htmltext,flags=re.S)[0]
	descripcion = descripcion.replace('\n','').strip().lower()
	funciones = re.findall('>En el trabajo, usted:</div>(.*?)</ul>', htmltext,flags=re.S)[0]
	funciones = re.findall('<li>(.*?)</li>', funciones,flags=re.S)
	for i in range(len(funciones)):
		funciones[i] = funciones[i].strip().lower()

	atributos = re.findall('<div class="wrapper">(.*?)</td>', htmltext,flags=re.S)
	atributosCleanText = []
	for i in range(5):
		cleanText = cleanhtml(atributos[i])
		cleanText = cleanText.strip().lower()
		#cleanText = cleanText.replace('\n',' ').strip().lower()
		atributosCleanText.append(cleanText)

	conocimiento = sent_tokenize(atributosCleanText[0],language='spanish')
	aptitudes = sent_tokenize(atributosCleanText[1],language='spanish')
	habilidades = sent_tokenize(atributosCleanText[2],language='spanish')
	personalidad = sent_tokenize(atributosCleanText[3],language='spanish')
	tecnologia = sent_tokenize(atributosCleanText[4],language='spanish')

	#print(atributosCleanText)

	atributos = dict()
	atributos['otros_nombres'] = otros_nombres
	atributos['descripcion'] = descripcion
	atributos['funciones'] = funciones
	atributos['conocimiento'] = conocimiento
	atributos['aptitudes'] = aptitudes
	atributos['habilidades'] = habilidades
	atributos['personalidad'] = personalidad
	atributos['tecnologia'] = tecnologia

	return atributos



def get_content_per_career(filename):
	carreras = pickle.load(open(filename+ ".p","rb"))
	carrerasXatributos = {}
	hdr = {'User-Agent': 'Mozilla/5.0'}

	i = 0
	for carrera,url in carreras.items():
		print(str(i)+': ' + carrera)
		req = urllib2.Request(url,headers=hdr)
		page = urllib2.urlopen(req)
		html = page.read()
		BsObj = BeautifulSoup(html,'lxml');
		htmltext = html.decode('utf-8')
		result = get_content(htmltext)
		result['url'] = url
		carrerasXatributos[carrera] = result
		
		i += 1
		
	print(carrerasXatributos)
	pickle.dump(carrerasXatributos,open("carrerasXatributos"+ ".p","wb"))








#getHTML_carreras()
get_content_per_career("carreras_onet_")



