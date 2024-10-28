import faiss
from typing import List
import numpy as np
import os
import logging
import diskcache as dc

# Define the loggers
app_logger = logging.getLogger('app_logger')
debug_logger = logging.getLogger('debug_logger')

# File path to store the FAISS index
FAISS_INDEX_PATH = os.path.join('..', 'utility', 'data_files', 'faiss-index')
cache_path = os.path.join('..', 'utility', 'data_files', 'embeddings_cache')
cache = dc.Cache(cache_path)

async def build_and_store_index(doc_embeddings):
    """ Build and store FAISS index on disk. """
    dimension = doc_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)  # Create FAISS index
    index.add(doc_embeddings)  # Add document embeddings to index
    
    # Save FAISS index to disk
    faiss.write_index(index, FAISS_INDEX_PATH)
    app_logger.info(f"FAISS index stored at: {FAISS_INDEX_PATH}")

def load_faiss_index():
    """ Load FAISS index from disk if available, otherwise return None. """
    if os.path.exists(FAISS_INDEX_PATH):
        index = faiss.read_index(FAISS_INDEX_PATH)
        app_logger.info("FAISS index loaded from disk.")
        return index
    else:
        app_logger.info("No prebuilt FAISS index found.")
        return None
    

async def get_doc_embeddings(collection, fields: List[str] = ["city", "streetAddress", "latestPrice"]):
    #List to hold documents with embeddings
    docs_with_embeddings = []
    # Create a projection dictionary to specify which fields to retrieve
    projection = {field: 1 for field in fields} #for field in fields iterates over each item in the fields list. {field: 1} creates a key-value pair where the key is the current item from fields, and the value is 1
    projection['embedding'] = 1  # Ensure embedding field is included for similarity comparison

    # Retrieve all documents that have an 'embedding' field
    async for doc in collection.find({"embedding": {"$exists": True}}, projection):
        docs_with_embeddings.append(doc)
        
    # Check if any documents with embeddings were found
    if not docs_with_embeddings:
        debug_logger.debug("No documents with embeddings found")
        return []

    # Extract the embeddings from the retrieved documents
    doc_embeddings = np.array([doc['embedding'] for doc in docs_with_embeddings]).astype('float32')
    return doc_embeddings, docs_with_embeddings


async def initialize_cache(collection):
    try:
        if 'doc_embeddings' not in cache:
            doc_embeddings, docs_with_embeddings = await get_doc_embeddings(collection)
            cache.set('doc_embeddings', doc_embeddings)
            cache.set('docs_with_embeddings', docs_with_embeddings)
            logging.info("Cache initialized")
    except Exception as e:
        debug_logger.error(f"Error initializing cache: {e}")

def get_cached_embeddings():
    try:
        doc_embeddings = cache.get('doc_embeddings')
        docs_with_embeddings = cache.get('docs_with_embeddings')
        return doc_embeddings, docs_with_embeddings
    except Exception as e:
        debug_logger.error(f"Error retrieving from cache: {e}")
        return None, None