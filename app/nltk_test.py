from nltk.tokenize import sent_tokenize, word_tokenize
import string
p = '''
hi this is aditya. is everything okay ? you guys seem upset.
let me know if it is anything related to me.
'''
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
        curr += (tkns[start]+' ')
        if(tkns[start] not in res):
            cnt+=1
            curr_wo_pkt.append(tkns[start])
        start+=1
    text.append(curr)
    text_wo_pkt.append(curr_wo_pkt)
    x += slide

print(text)
print(text_wo_pkt)

