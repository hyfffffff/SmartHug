"""
SmartGlmLocalModel utilizes SentenceTransformer for embedding and a local 
GLM model for answering queries. It incorporates a multilingual embedding 
model and the ChatGLM3-6B model for generating responses based on text 
chunks within a token budget.
"""

from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel

EMBEDDING_MODEL = 'distiluse-base-multilingual-cased-v2'
ANSWER_MODEL = "THUDM/chatglm3-6b"


TOKEN_BUDGET = 4096 - 500


class SmartGlmLocalModel:
    def __init__(self):
        self.name = "ChatGLM3-6B"
        self.dim = 512
        self.encoder = SentenceTransformer(EMBEDDING_MODEL)

        # model_path = "xverse/XVERSE-13B-Chat"

        self.tokenizer = AutoTokenizer.from_pretrained(ANSWER_MODEL, trust_remote_code=True)
        self.glmmodel = AutoModel.from_pretrained(ANSWER_MODEL, trust_remote_code=True).half().cuda()


    def encode(self, text):
    
        embeddings = self.encoder.encode([text])
        return embeddings[0]

    def answer(self, query, chunks):
        introduction =  '利用以下的文本回答问题，如果不能在以下的文本中找到答案，就回答 "我不能找到答案."'
        question = f"\n\n问题: {query}"
        message = introduction + question
        for string in chunks:
            next_article = f'\n\n文本:\n"""\n{string[0]}\n"""'
            if len(message + next_article + question) > TOKEN_BUDGET:
                break
            else:
                message += next_article

        response, history = self.glmmodel.chat(self.tokenizer, message, history=None)

        return response
        
