from langchain_fireworks import ChatFireworks
from sentence_transformers import SentenceTransformer
import logging
import os
from dotenv import load_dotenv
from fireworks.client import Fireworks
import openai
load_dotenv()

app_logger = logging.getLogger('app_logger')
debug_logger = logging.getLogger('debug_logger')

class Configs:
    def __init__(self):
        self.llm = None
        self.embeddings = None
        self.client = None

        
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
            self.client = openai.OpenAI(
                base_url="https://api.fireworks.ai/inference/v1",
                api_key=os.environ.get("FIREWORKS_API_KEY")
            )
            
        except Exception as e:
            debug_logger.error(f"Error during model initialization: {e}")
            raise

    def get_llm(self):
        if self.llm is None:
            debug_logger.debug("LLM has not been initialized")
            raise ValueError
        app_logger.info("LLM loaded successfully")
        return self.llm

    def get_embeddings_model(self):
        if self.embeddings_model is None:
            debug_logger.debug("Embeddings model has not been initialized")
            raise ValueError
        app_logger.info("Embedding model loaded successfully")
        return self.embeddings_model
    
    def get_client(self):
        if self.client is None:
            debug_logger.debug("Client has not been initialized")
            raise ValueError
        app_logger.info("Client loaded successfully")
        return self.client