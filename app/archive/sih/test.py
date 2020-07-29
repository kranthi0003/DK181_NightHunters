'''import re
with open('data\\test6.txt', 'r', encoding='utf8') as reader:
        data = ''
        for line in reader:
            data += line
        #paras = data.split('\n\n')
        subparas = []
        for p in re.split(r"\n\n|\n\t|\n   *", data):
            lines = re.findall(r".*?[.!?]", p)
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
print(subparas)'''