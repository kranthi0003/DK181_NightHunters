from rake_nltk import Rake
import PyPDF2

from elasticsearch import Elasticsearch
from elasticsearch import helpers

es = Elasticsearch('http://localhost:9200')

ALLOWED_EXTENSIONS = set(['txt', 'pdf'])


def allowed_extension(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def convert_to_text(filename):
	pdfFileObj = open('G:/Projects/SIH/Project/SIH/uploads/'+filename, 'rb')
	pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	#print("Number of pages:-"+str(pdfReader.numPages))
	num = pdfReader.numPages
	i =0
	file_res = open('G:/Projects/SIH/Project/SIH/converts/'+filename.split('.')[0]+'.txt','w',encoding='UTF-8')
	while(i<num):
		pageObj = pdfReader.getPage(i)
		text=pageObj.extractText()
		file_res.write('\n\nPage: '+str(i+1)+'\n\n'+text)
		i=i+1



def extract_keywords(text):
	r = Rake()
	r.extract_keywords_from_text(text)
	a = r.get_ranked_phrases()
	b = r.get_ranked_phrases_with_scores()
	return a



def indexing(index, filename):
	with open('G:/Projects/SIH/Project/SIH/converts/'+filename+'.txt') as input:
		input_ = input.read().split("\n\n")

	jsons = []
	for para in input_:
		jsons.append({
			"_index": index,
			"text": para
		})
		if(len(jsons) == 200):
			res = helpers.bulk(es, jsons, index=index)
			jsons = []
	res = helpers.bulk(es, jsons, index=index)



def search_documents(index, query):
	res = es.search(index=index, body={'query': {'match': {'text': query}}})
	return res