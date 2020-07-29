import re
import nltk.data

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

with open('data\\test7.txt','r',encoding='utf8') as reader:
    data = ''
    for line in reader:
        data += line
    subparas = []
    for p in re.split(r"\n\n|\n\t|\n   *", data):
        liness = tokenizer.tokenize(p)
        if((len(p.splitlines()) == 1) and (len(liness)<=3)):
            continue
        cnt=0
        while(cnt < len(liness)):
            subparas.append(' '.join(liness[cnt:cnt+3]))
            cnt+=3