import PyPDF2
from elasticsearch import Elasticsearch, helpers
from timeit import default_timer as timer
#import similarity as sim
from sih import bertqa
import time
from rake_nltk import Rake
import re


ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

es = Elasticsearch('http://localhost:9200')
r = Rake()

def allowed_extension(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_text(filename):
	pdfFileObj = open('data\\'+filename, 'rb')
	pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	#print("Number of pages:-"+str(pdfReader.numPages))
	num = pdfReader.numPages
	i =0
	#file_res = open('G:/Projects/SIH/Project/SIH/converts/'+filename.split('.')[0]+'.txt','w',encoding='UTF-8')
	file_res = open('data\\'+filename.split('.')[0]+'.txt','w',encoding='UTF-8')
	while(i<num):
		pageObj = pdfReader.getPage(i)
		text=pageObj.extractText()
		file_res.write("\n\nPage: "+str(i+1)+"\n\n"+text)
		i+=1


def extract_keywords(text):
    r.extract_keywords_from_text(text)
    return ' '.join(r.get_ranked_phrases())


def index_docs(index, filename):
	with open('data\\'+filename+'.txt') as reader:
		data = ''
		for line in reader:
			data += line
        #paras = data.split('\n\n')
	subparas = []
	for p in re.split(r"\n\n|\n\t|\n   *", data):
		lines = re.findall(r".*?[.!\?]", p)
		if((len(p.splitlines()) == 1) and (len(lines)<=3)):
			continue
		cnt = 0
		subpara = ''
		for line in lines:        
			if(cnt<3):
				subpara += (line+'.')
				cnt+=1
			else:
				subparas.append(subpara)
				subpara = ''
				cnt = 0
		if(cnt<3):
			subparas.append(subpara)
		def gen_data():
			for p in subparas:
				yield {
					"_index": index,
					"text": p,
				}
        #start = timer()
		helpers.bulk(es, gen_data(), request_timeout=60)
        #end = timer()
        #print(end-start)

def retrieve_docs(index, qsn):
    result = es.search(index=index, body={
        "query": {
            "match": {
                "text": qsn
            }
        }
    })
    l = []
    for x in result['hits']['hits']:
        l.append(x['_source']['text'])
    return l