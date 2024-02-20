"""
SmartBaiduModel is a class that integrates with Baidu's Erniebot for text 
embedding and answering queries. It utilizes specified API tokens for 
authentication and is designed to answer questions based on given text 
chunks, with a token budget to manage response length.
"""


import erniebot
import tiktoken  # for counting tokens
import os


EMBEDDING_MODEL = 'ernie-text-embedding'
ANSWER_MODEL = "ernie-3.5"
TOKEN_BUDGET = 4096 - 500

# Set authentication params
erniebot.api_type = os.getenv("erniebot.api_type")
erniebot.access_token = os.getenv('erniebot.access_token')

class SmartBaiduModel:
    def __init__(self):
        self.name = "文心一言 3.5"
        self.dim = 384 # Specify the embedding dimension for GptModel

    def encode(self, text):
    
        response = erniebot.Embedding.create(
        model="ernie-text-embedding",
        input=[text] 
        )
        return response.get_result()[0]



    def answer(self, query, chunks):
        introduction =  '我是assistant, 利用以下的文本回答问题，如果不能在以下的文本中找到答案，就回答 "我不能找到答案."'
        question = f"\n\n问题: {query}"
        message = introduction
        for string in chunks:
            next_article = f'\n\n文本:\n"""\n{string[0]}\n"""'
            if len(message + next_article + question) > TOKEN_BUDGET:
                break
            else:
                message += next_article

        messages = [
            {"role": "user", "content": message},
            {"role": "assistant", "content": question},
            {"role": "user", "content": "请回答，只根据我提供的信息回答，不必增加其它内容。"}
        ]

        response = erniebot.ChatCompletion.create(
            model=ANSWER_MODEL,
            messages = messages,
            temperature = 0.1
        )
        response_message = response.get_result()
        return response_message
        
