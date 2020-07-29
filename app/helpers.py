from rake_nltk import Rake
import PyPDF2
import time
import re
import nltk.data
from timeit import default_timer as timer

from elasticsearch import Elasticsearch, helpers

es = Elasticsearch('http://localhost:9200')

ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

FOLDER = 'G:/Projects/SIH/Project_New/'


def allowed_extension(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def convert_to_text(filename):
	extension = filename.split('.')[1]
	source_file = FOLDER+'books/'+filename
	destination_file = FOLDER+'converted_books/'+filename.split('.')[0]+'.txt'

	# pdf to txt...
	if(extension == 'pdf'):
		pdfFileObj = open(source_file, 'rb')
		pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
		num = pdfReader.numPages
		i =0
		file_res = open(destination_file,'w',encoding='UTF-8')
		while(i<num):
			pageObj = pdfReader.getPage(i)
			text=pageObj.extractText()
			file_res.write('\n\nPage: '+str(i+1)+'\n\n'+text)
			i=i+1
		pdfFileObj.close()

	# docx to txt...
	elif(extension == 'docx'):
		text = docx2txt.process(source_file)
		f = open(destination_file,"w+")
		f.write(text)


def extract_keywords(text):
    r.extract_keywords_from_text(text)
    return ' '.join(r.get_ranked_phrases())



def index_docs(index, filename):
    data = ''
    with open('data\\'+filename+'.txt','r',encoding='utf8') as reader:
        for line in reader:
            data += line
    subparas = []
    for p in re.split(r"\n\n|\n\t|\n   *", data):
        lines = tokenizer.tokenize(p)
        if((len(p.splitlines()) == 1) and (len(lines)<=3)):
            continue
        cnt=0
        while(cnt < len(lines)):
            subparas.append(' '.join(lines[cnt:cnt+3]))
            cnt+=3
    def gen_data():
        for p in subparas:
            yield {
                "_index": index,
                "text": p,
            }
    #start = timer()
    print('Indexing started')
    helpers.bulk(es, gen_data(), request_timeout=60)
    time.sleep(5)
    es.indices.refresh()



def search_documents(index, query):
	res = es.search(index=index, body={'query': {'match': {'text': query}}})
	return res