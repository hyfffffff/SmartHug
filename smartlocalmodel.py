"""
SmartLocalModel is a streamlined local model for text processing, combining 
multilingual embeddings and question answering capabilities. It uses 
SentenceTransformer for embeddings and a Deberta model for answering, 
optimized for concise and contextually relevant responses within a token budget.
"""

from sentence_transformers import SentenceTransformer, util
from transformers import pipeline


TOKEN_BUDGET = 4096 - 500


class SmartLocalModel:
    def __init__(self):
        self.name = "简单本地"
        self.dim = 512
        self.encoder = SentenceTransformer('distiluse-base-multilingual-cased-v2')
        self.answerer = pipeline("question-answering", "timpal0l/mdeberta-v3-base-squad2")

    def encode(self, text):
    
        embeddings = self.encoder.encode([text])
        return embeddings[0]

    def answer(self, query, chunks):
        introduction =  '利用以下的文本回答问题，如果不能在以下的文本中找到答案，就回答 "我不能找到答案."'
        question = f"\n\n问题: {query}"
        message = introduction
        for string in chunks:
            next_article = f'\n\n文本:\n"""\n{string[0]}\n"""'
            if len(message + next_article + question) > TOKEN_BUDGET:
                break
            else:
                message += next_article


        answer = self.answerer(question = question, context = message)

        return answer['answer']
        
