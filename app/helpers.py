from rake_nltk import Rake
import PyPDF2
import docx2txt
import time
import re
import nltk.data
import shutil
from timeit import default_timer as timer

from elasticsearch import Elasticsearch, helpers

#from transformers import BertTokenizer, TFBertForQuestionAnswering
#import tensorflow as tf

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

es = Elasticsearch('http://localhost:9200')
r = Rake()

#model_tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')


''' Uncomment the below two lines if executing for the first time '''
#model = TFBertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
#model.save_pretrained('data\\models')


''' Comment the below line if executing for the first time '''
#model = TFBertForQuestionAnswering.from_pretrained('data\\models')

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')


def allowed_extension(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def convert_to_text(filename):
    extension = filename.split('.')[1]
    source_file = 'data\\books\\'+filename
    destination_file = 'data\\converted_books\\'+filename.split('.')[0]+'.txt'

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
        f.close()


    # txt file
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
    time.sleep(5)
    es.indices.refresh()



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


def multi_retrieve(books, qsn):
    answers = []
    for book in books:
        print(book)
        answers.append(retrieve_docs(book,qsn))
    return answers



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