from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 

def similar(X, Y):
	X_list = word_tokenize(X) 
	Y_list = word_tokenize(Y) 

	sw = stopwords.words('english') 
	l1 =[];l2 =[] 

	X_set = {w for w in X_list if w not in sw} 
	Y_set = {w for w in Y_list if w not in sw} 

	rvector = X_set.union(Y_set) 
	for w in rvector: 
		if w in X_set: l1.append(1)
		else: l1.append(0) 
		if w in Y_set: l2.append(1) 
		else: l2.append(0) 
	c = 0

	for i in range(len(rvector)): 
			c+= l1[i]*l2[i] 
	cosine = c / float((sum(l1)*sum(l2))**0.5) 
	return cosine
