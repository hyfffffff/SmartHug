"""
SmartGptModel integrates with the OpenAI API to perform text embedding and 
generate answers using GPT 3.5 Turbo. It leverages an API key for 
authentication, embedding dimensions for text processing, and manages 
responses within a specified token budget.
"""

from openai import OpenAI # for calling the OpenAI API
import os # for getting API token from env variable OPENAI_API_KEY

EMBEDDING_MODEL = "text-embedding-ada-002"
ANSWER_MODEL = "gpt-3.5-turbo"
TOKEN_BUDGET =  4096 - 500

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class SmartGptModel:
    def __init__(self):
        self.name = "GPT 3.5 Turbo"
        self.dim = 1536 # Specify the embedding dimension for GptModel
        self.client = OpenAI()

    def encode(self, text):
        query_embedding_response = self.client.embeddings.create(
            model = EMBEDDING_MODEL,
            input = text
        )
        return query_embedding_response.data[0].embedding


    def answer(self, question, chunks):
        introduction = '利用以下的文本回答问题，如果不能在以下的文本中找到答案，就回答 "我不能找到答案."'
        question = f"\n\n问题: {question}"
        message = introduction
        for string in chunks:
            next_article = f'\n\n文本:\n"""\n{string[0]}\n"""'
            if len(message + next_article + question) > TOKEN_BUDGET:
                break
            else:
                message += next_article
        
        messages = [
            {"role": "system", "content": message},
            {"role": "user", "content": question},
            
        ]

        response = self.client.chat.completions.create(
            model = ANSWER_MODEL,
            messages = messages,
            temperature = 0
        )
        response_message = response.choices[0].message.content
        return response_message

