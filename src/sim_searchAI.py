from dotenv import load_dotenv
from utils import llm
import io,json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from db_connect import Database
from sentence_transformers import SentenceTransformer, util
import logging
import asyncio
load_dotenv()
from typing import List

async def similiarity_search(query: str, fields: List[str] = ["city", "streetAddress", "latestPrice"]) -> List[dict]:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode(query).tolist()
    collection = await Database.connect()

    if collection is None:
        logging.error("Can't connect to database")
        return []

        # Retrieve all documents and their embeddings
    try:
        docs_with_embeddings = []
        projection = {field: 1 for field in fields}
        projection['embedding'] = 1  # Ensure embedding field is included for similarity comparison

        async for doc in collection.find({"embedding": {"$exists": True}}, projection):
            docs_with_embeddings.append(doc)
        
        if not docs_with_embeddings:
            logging.warning("No documents with embeddings found")
            return []

        # Compute similarity scores
        doc_embeddings = [doc['embedding'] for doc in docs_with_embeddings]
        similarities = util.dot_score(query_embedding, doc_embeddings)

        # Sort documents by similarity
        sorted_docs = sorted(zip(docs_with_embeddings, similarities), key=lambda x: x[1], reverse=True)

        top_n = 5
        similar_docs = [doc for doc, sim in sorted_docs[:top_n]]
        return similar_docs
    
    except Exception as e:
        logging.error(f"Error while finding similar listings: {e}")
        return []