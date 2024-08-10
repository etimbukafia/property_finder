from dotenv import load_dotenv
from db_connect import Database
import logging
load_dotenv()
from typing import List
#from mistralai.client import MistralClient
from sentence_transformers import SentenceTransformer, util

# Define the loggers
app_logger = logging.getLogger('app_logger')
debug_logger = logging.getLogger('debug_logger')

model = None

async def load_model():
    global model # ensures that the global model variable is updated with the loaded SentenceTransformer instance, and this instance is accessible throughout the program.
    model = SentenceTransformer('all-MiniLM-L6-v2')
    logging.info("Model loaded successfully")


async def similiarity_search(query: str, fields: List[str] = ["city", "streetAddress", "latestPrice"]) -> List[dict]:
    """
    Perform a similarity search on the real estate listings based on the provided query.
    
    Args:
        query (str): The search query describing desired property features.
        fields (List[str], optional): List of fields to be included in the result. Defaults to ["city", "streetAddress", "latestPrice"].
    
    Returns:
        List[dict]: A list of dictionaries representing the top similar documents."""
    
    global model
    if model is None:
        await load_model()

    #client = MistralClient(api_key="zxEthFKy97XUYXSHj4oMJGOjNBqIaklj")

    #embedding_response = client.embeddings(
    #model="mistral-embed",
    #input=[query])

    #embedding_object = embedding_response.data[0]

    #query_embedding = embedding_object.embedding

    #Encode the query into an embedding vector
    app_logger.info("embedding query")
    query_embedding = model.encode(query).tolist()
    app_logger.info("query embedded")
    #debug_logger.debug(f"Query embedding for '{query}': {query_embedding}")

     # Connect to the database
    collection = await Database.connect()

    # Check if the database connection was successful
    if collection is None:
        logging.error("Can't connect to database")
        return []

        # Retrieve all documents and their embeddings
    try:
        """ docs_with_embeddings = [] Initialize a list to hold documents with their embeddings. 
        As the code iterates over documents retrieved from the database, it appends each document that contains an embedding to this list."""
        docs_with_embeddings = []

        # Create a projection dictionary to specify which fields to retrieve
        # Ensure that the 'embedding' field is included for similarity comparison
        projection = {field: 1 for field in fields} #for field in fields iterates over each item in the fields list. {field: 1} creates a key-value pair where the key is the current item from fields, and the value is 1
        projection['embedding'] = 1  # Ensure embedding field is included for similarity comparison

        # Retrieve all documents that have an 'embedding' field
        async for doc in collection.find({"embedding": {"$exists": True}}, projection):
            docs_with_embeddings.append(doc)
        
        # Check if any documents with embeddings were found
        if not docs_with_embeddings:
            app_logger.warning("No documents with embeddings found")
            return []
        
        # Debug statement to check retrieved documents
        #debug_logger.debug(f"Documents with embeddings: {docs_with_embeddings}")

        # Extract the embeddings from the retrieved documents
        doc_embeddings = [doc['embedding'] for doc in docs_with_embeddings]
        #debug_logger.debug(f"Document embeddings: {doc_embeddings}")

        # Compute the similarity scores between the query embedding and document embeddings
        similarities = util.cos_sim(query_embedding, doc_embeddings).tolist()[0]
        #debug_logger.debug(f"Similarities: {similarities}")

        # Sort the documents by their similarity scores in descending order
        """The key argument specifies a function to be called on each item in the iterable for sorting. 
        In this case, key=lambda x: x[1] means that the sorting should be based on the second item in each tuple (i.e., the similarity score).

        reverse=True specifies that the sorting should be in descending order, so higher similarity scores come first."""
        sorted_docs = sorted(zip(docs_with_embeddings, similarities), key=lambda x: x[1], reverse=True)
        #debug_logger.debug(f"Sorted documents: {sorted_docs}")

        # Define the number of top similar documents to return
        top_n = 5
        #iterates over each of these top top_n tuples and extracts only the doc (document) part from each tuple.
        similar_docs = [doc for doc, sim in sorted_docs[:top_n]] 
        #debug_logger.debug(f"Top {top_n} similar documents: {similar_docs}")

        return similar_docs
    
    except Exception as e:
        app_logger.error(f"Error while finding similar listings: {e}")
        return []