from langchain_fireworks import ChatFireworks
from sentence_transformers import SentenceTransformer
import logging
from pymilvus import MilvusClient

class Configs:
    def __init__(self):
        self.llm = None
        self.embeddings = None

        
    async def initialize(self):
        try:
            self.embeddings_model = SentenceTransformer("jinaai/jina-embeddings-v2-small-en", trust_remote_code=True)
            self.llm = ChatFireworks(
                model="accounts/fireworks/models/llama-v3p1-8b-instruct",
                temperature=0.5,
                max_tokens=1024,
                model_kwargs={"top_p": 1},
                cache=None,
            )
        except Exception as e:
            print(f"Error during model initialization: {e}")
            raise

    def get_llm(self):
        if self.llm is None:
            raise ValueError("LLM has not been initialized")
        logging.info("LLM loaded successfully")
        return self.llm

    def get_embeddings_model(self):
        if self.embeddings_model is None:
            raise ValueError("Embeddings model has not been initialized")
        logging.info("Embedding model loaded successfully")
        return self.embeddings_model