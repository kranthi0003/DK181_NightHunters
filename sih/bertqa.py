from transformers import BertTokenizer, TFBertForQuestionAnswering
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf

tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
model = TFBertForQuestionAnswering.from_pretrained('data\\models\\bert_large')

def answer(question, text):
    input_dict = tokenizer(question, text, return_tensors='tf')
    start_scores, end_scores = model(input_dict)
    tokens = tokenizer.convert_ids_to_tokens(input_dict["input_ids"].numpy()[0])
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