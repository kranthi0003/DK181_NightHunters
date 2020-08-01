import PyPDF2
from elasticsearch import Elasticsearch, helpers
from timeit import default_timer as timer
#import similarity as sim
#from sih import bertqa
import time
from rake_nltk import Rake
import re
import docx2txt
import nltk.data
import shutil
from pdfminer.high_level import extract_text
from transformers import BertTokenizer, TFBertForQuestionAnswering
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

es = Elasticsearch('http://localhost:9200')
r = Rake()

model_tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
model = TFBertForQuestionAnswering.from_pretrained('data\\models\\bert_large')

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
def allowed_extension(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_text(filename):
    extension = filename.split('.')[1]
    source_file = 'data\\books\\'+filename
    destination_file = 'data\\converted_books\\'+filename.split('.')[0]+'.txt'

	# pdf to txt...
    if(extension == 'pdf'):
        '''
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
        '''
        text = extract_text(source_file)
        time.sleep(5)
        with open(destination_file,'w') as f:
            f.write(text)

	# docx to txt...
    elif(extension == 'docx'):
        text = docx2txt.process(source_file)
        f = open(destination_file,"w+")
        f.write(text)
        f.close()
    else:
        shutil.copy(source_file, 'data\\converted_books')

def get_indices():
    return es.indices.get_alias("*")

def extract_keywords(text):
    r.extract_keywords_from_text(text)
    return ' '.join(r.get_ranked_phrases())


def index_docs(index, filename):
    data = ''
    with open('data\\converted_books\\'+filename+'.txt','r',encoding='utf8') as reader:
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
    print('Indexnig end')
    time.sleep(5)
    es.indices.refresh()
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

def get_answer(question, text):
    input_dict = model_tokenizer(question, text, return_tensors='tf')
    start_scores, end_scores = model(input_dict)
    tokens = model_tokenizer.convert_ids_to_tokens(input_dict["input_ids"].numpy()[0])
    answer_start = tf.math.argmax(start_scores, 1)[0]
    answer_end = tf.math.argmax(end_scores, 1)[0]
    #answer = ' '.join(all_tokens[answer_start : answer_end+1])
    answer = tokens[answer_start]
    for i in range(answer_start+1, answer_end+1):
        if(tokens[i][0:2] == '##'):
            answer += tokens[i][2:]
        else:
            answer += ' ' + tokens[i]
    return answer
'''
if __name__ == "__main__":
    #index = input("Name of the book")
    index = "four_book"
    index_docs(index, "test2")
    es.indices.refresh()
    time.sleep(5)
    qsn = None
    while(qsn != 'exit'):
        qsn = input("Question?\n")
        modified_qsn = extract_keywords(qsn)
        print(modified_qsn)
        l = retrieve_docs(index,modified_qsn)
        time.sleep(5)
        #print(qsn)
        for x in l:
            #print('context:',x,'Score:',sim.similar(x,qsn))
            print('context: ',x, end='\n\n')
        
        print('Choose one.\n1. Short answer\n2. Long answer\n')
        x = int(input())
        if(x==1):
            print('Answer:',bertqa.answer(qsn, l[0]),end='\n\n')
        elif(x==2):
            print('Answer:',l[0],'\n\n')
'''
