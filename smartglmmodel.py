"""
SmartGlmModel is a class designed to integrate with ZhipuAI's API for text
embedding and answering questions. It uses cloud-based GLM models for
processing and is configured with an API key from the environment. This model
focuses on providing concise answers based on the provided text chunks within
a predefined token budget.
"""


from zhipuai import ZhipuAI
import os # for getting API token from env variable OPENAI_API_KEY

# glmapi_key = '89012926f48183a2d3f9d1e840b7f0ba.e1qEaaov0RHqi0bU'

EMBEDDING_MODEL = "embedding-2"
ANSWER_MODEL = "glm-4"
TOKEN_BUDGET =  4096 - 500

glmapi_key = os.getenv('glmapi_key')

class SmartGlmModel:
    def __init__(self):
        self.name = "云端GLM"
        self.dim = 1024 # Specify the embedding dimension for GptModel
        self.client = ZhipuAI(api_key=glmapi_key)

    def encode(self, text):
        query_embedding_response = self.client.embeddings.create(
            model = EMBEDDING_MODEL,
            input = text
        )
        return query_embedding_response.data[0].embedding


    def answer(self, question, chunks):
        introduction = '利用以下的文本回答问题，如果不能在以下的文本中找到答案，就回答 "我不能找到答案.",如果能找到答案，只返回答案，不要增加其它内容。'
        question = f"\n\n问题: {question}"
        message = introduction
        for string in chunks:
            next_article = f'\n\n文本:\n"""\n{string[0]}\n"""'
            if len(message + next_article + question) > TOKEN_BUDGET:
                break
            else:
                message += next_article
        
        messages = [
            # {"role": "assistant", "content": message},
            # {"role": "user", "content": question},
            {"role": "user", "content": message},
            {"role": "assistant", "content": question},
            {"role": "user", "content": "请回答，只根据我提供的信息回答，不必增加其它内容。"}            
        ]

        response = self.client.chat.completions.create(
            model = ANSWER_MODEL,
            messages = messages
        )
        response_message = response.choices[0].message.content
        return response_message

