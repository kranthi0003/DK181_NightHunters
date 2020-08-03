import re
from nltk.tokenize import word_tokenize
from elasticsearch import Elasticsearch, helpers
from timeit import default_timer as timer
import time
import logging
logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.INFO)
import gensim.downloader as api
from fse import IndexedList
from fse.models import uSIF
import string

es = Elasticsearch('http://localhost:9200')
glove = api.load("glove-wiki-gigaword-100")
model = uSIF(glove, workers=2, lang_freq="en")

mapping = '''{
"mappings":{  
      "properties":{  
        "context":{  
          "type": "text"
        },
        "context_vector":{
            "type": "dense_vector",
            "dims": 100
        }
      }
    }
  }
'''

def vectorize(contexts):
    start = timer()
    end= timer()
    print('Model load time:', end-start)
    s = IndexedList(contexts)
    model.train(s)
    return model.sv


def index_docs(index, filename, b):
    
    data = ''
    with open('data\\converted_books\\'+filename+'.txt','r',encoding='utf-8') as reader:
        for line in reader:
            if(len(word_tokenize(line)) > 7):
                data += line
    window = 10
    slide = 5

    res = string.punctuation
    tkns = word_tokenize(data)
    x = 0
    text = []
    text_wo_pkt = []
    while((x+window)<len(tkns)):
        curr = ""
        curr_wo_pkt = []
        cnt = 0
        start = x
        while(cnt<window):
            if(start >= len(tkns)):
                break
            curr += (tkns[start]+' ')
            if(tkns[start] not in res):
                cnt+=1
                curr_wo_pkt.append(tkns[start])
            start+=1
        text.append(curr)
        text_wo_pkt.append(curr_wo_pkt)
        x += slide
    context_vectors = vectorize(text_wo_pkt)
    n = len(text)
    print(context_vectors[5], text[5])
    def gen_data():
        for i in range(n):
            yield{
                "_index": index,
                "context": text[i],
                "context_vector": context_vectors[i].tolist()
            }
    es.indices.create(index, body=mapping)
    start = timer()
    
    for ok, status in helpers.streaming_bulk(es, gen_data(), chunk_size = b):
        if(not ok):
            print(status)

    es.indices.refresh()
    end = timer()
    print('batch_size',b,'index time',end-start)

def search(index, query):
    q = (query.split(),0)
    query_vector = model.infer([q]).tolist()
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, doc['context_vector']) + 1.0",
                "params": {"query_vector": query_vector}
            }
        }
    }
    
    result = es.search(index=index, body={"query":script_query}) 
    print(result)

if __name__ == "__main__":
    filename = 'CN_Text_Book'
    index = 'test_9'
    #index_docs(index, filename, 3000)
    
    qsn = None
    while(qsn != "exit"):
        qsn = input()
        search(index, qsn)
    
    #es.indices.delete(index)