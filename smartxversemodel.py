from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.generation.utils import GenerationConfig
import torch

TOKEN_BUDGET = 4096 - 500


class SmartXVerseModel:
    def __init__(self):
        self.name = "XVERSE-13B-Chat"
        self.dim = 512
        self.encoder = SentenceTransformer('distiluse-base-multilingual-cased-v2')

        model_path = "xverse/XVERSE-13B-Chat"
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.xversemodel = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True, torch_dtype=torch.bfloat16, device_map='auto')
        self.xversemodel.generation_config = GenerationConfig.from_pretrained(model_path)

        # self.answerer = pipeline("question-answering", "timpal0l/mdeberta-v3-base-squad2")

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


        history = [{"role": "user", "content": message}]
        response = self.xversemodel.chat(self.tokenizer, history)

        return response
        
