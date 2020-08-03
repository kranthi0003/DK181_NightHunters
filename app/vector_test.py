
from timeit import default_timer as timer
import logging
logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.INFO)

import gensim.downloader as api
from fse import IndexedList
start = timer()
glove = api.load("glove-wiki-gigaword-100")
end= timer()
print('Model load time:', end-start)
query  = "What is a data link layer ?"

s = IndexedList([query.split()])

from fse.models import uSIF
model = uSIF(glove, workers=2, lang_freq="en")

model.train(s)
print(model)

print(model.sv[0])
print(type(model.sv[0]))
mq1 = "Data link layer"
mq2 = "Data link layer is the protocol in which various combine"

