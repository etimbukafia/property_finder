from dotenv import load_dotenv
import logging
load_dotenv()
from typing import List
import numpy as np
from helpers.util import load_faiss_index, build_and_store_index, get_cached_embeddings

# Define the loggers
app_logger = logging.getLogger('app_logger')
debug_logger = logging.getLogger('debug_logger')

async def multi_query_search(model, queries: List[str]) -> List[dict]:
    """
    Perform a similarity search on the real estate listings based on the provided query.
    
    Args:
        query (str): The search query describing desired property features.
        fields (List[str], optional): List of fields to be included in the result. Defaults to ["city", "streetAddress", "latestPrice"].
    
    Returns:
        List[dict]: A list of dictionaries representing the top similar documents.
    """

    app_logger.info("Getting document embeddings from db")
    doc_embeddings, docs_with_embeddings = get_cached_embeddings()

    query_embedding_list = []
    for num_query, query in enumerate(queries, start=1):
        query_embedding = model.encode(query, normalize_embeddings=True) #Encode the query into an embedding vector
        query_embedding = np.array(query_embedding).astype('float32')
        app_logger.info(f"query embedded {num_query}")
        query_embedding_list.append(query_embedding)

    try:
        index = load_faiss_index()

        if index is None:
            app_logger.info("Building Faiss index from scratch")
            await build_and_store_index(doc_embeddings)
            index = load_faiss_index()
        
        # Retrieve the top k similar documents
        top_k_docs = await find_matching_listings(index, query_embedding_list, docs_with_embeddings)
        return top_k_docs

    except Exception as e:
        app_logger.error(f"Error while finding similar listings: {e}")
        return []


async def find_matching_listings(index, query_embedding_list, docs_with_embeddings, k=3):
    """
    Perform the FAISS index search for each query embedding asynchronously and gather top documents.
    
    Args:
        index: The FAISS index used for searching.
        query_embedding_list (List[np.array]): List of query embeddings.
        docs_with_embeddings (List[dict]): Documents that correspond to the embeddings.
        k (int): Number of top documents to retrieve per query.
    
    Returns:
        List[dict]: List of top documents, re-ranked by similarity scores.
    """

    top_k_docs = []

    for query_embedding in query_embedding_list:
        distances, indices = index.search(query_embedding.reshape(1,-1),k)  #FAISS expects a 2D array

        #Collect top-k documents and their similarity scores
        for i, dist in zip(indices[0], distances[0]):
            doc = docs_with_embeddings[i]
            doc["similarity_score"] = dist
            top_k_docs.append(doc)
            
    # Re-rank the documents by similarity score
    top_k_docs = sorted(top_k_docs, key=lambda x: x['similarity_score'])
    return top_k_docs
