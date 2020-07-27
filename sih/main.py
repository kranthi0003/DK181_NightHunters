from elasticsearch import Elasticsearch, helpers
from timeit import default_timer as timer
#import similarity as sim
import bertqa
import time
from rake_nltk import Rake
import re

def get_keywords(text):
    r = Rake()
    r.extract_keywords_from_text(text)
    return ' '.join(r.get_ranked_phrases())

def index_docs(es, index):
    with open('data\\test5.txt', 'r', encoding='utf8') as reader:
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
        def gendata():
            for p in subparas:
                yield {
                    "_index": index,
                    "text": p,
                }
        #start = timer()
        helpers.bulk(es, gendata(), request_timeout=60)
        #end = timer()
        #print(end-start)

def retrieve_docs(es, index, qsn):
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


if __name__ == "__main__":
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    #index = input("Name of the book")
    index = "cn"
    index_docs(es,index)
    es.indices.refresh()
    time.sleep(5)
    qsn = None
    while(qsn != 'exit'):
        qsn = input("Question?\n")
        modified_qsn = get_keywords(qsn)
        #print(modified_qsn)
        l = retrieve_docs(es,index,modified_qsn)
        time.sleep(5)
        #print(qsn)
        #for x in l:
            #print('context:',x,'Score:',sim.similar(x,qsn))
            #print('context: ',x,'\n', 'answer:','\n',bertqa.answer(qsn, x), end='\n\n')
        
        print('Choose one.\n1. Short answer\n2. Long answer\n')
        x = int(input())
        if(x==1):
            print('Answer:',bertqa.answer(qsn, l[0]),end='\n\n')
        elif(x==2):
            print('Answer:',l[0],'\n\n')
        
    es.indices.delete(index=index, ignore=[400, 404])
    print("Deleted")


        
