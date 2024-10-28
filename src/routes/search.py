from fastapi import APIRouter, Request, HTTPException
from models import Listing, SearchResponse, SearchRequest
import logging
from aiHelpers.query_expander import query_expansion
from aiHelpers.multiQueryRetriever import multi_query_search
import httpx

app_logger = logging.getLogger('app_logger')
debug_logger = logging.getLogger('debug_logger')

router = APIRouter()

# Define the endpoint for searching, which accepts a POST request and returns a SearchResponse
@router.post('/search', response_model=SearchResponse)
async def search(request:Request, query: SearchRequest) -> SearchResponse: 
    try:
        client = request.app.state.config["client"]
        model = request.app.state.config["model"]

        # Extracts the query and filter from the incoming request
        query_text = query.query
        expanded_query = query_expansion(client, query_text)
        queries = expanded_query['expanded_queries'] 

        # Performs search with filters
        similar_listings = await multi_query_search(model, queries)

        # Prepares the response object by populating it with the similar listings
        response = SearchResponse(
            listings=[Listing(
                id=str(doc['_id']), # Convert the document ID to a string
                city=doc.get('city', ''), # Get the city from the document, or an empty string if not present
                streetAddress=doc.get('streetAddress', ''), # Get the street address from the document, or an empty string if not present
                latestPrice=doc.get('latestPrice', 0.0) # Get the latest price from the document, or 0.0 if not present
            ) for doc in similar_listings] # Iterate over each similar listing to create a Listing object
        )
        return response
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 412:
            debug_logger.error(f"Precondition Failed: {e.response.json()}")
            raise HTTPException(status_code=412, detail="Precondition Failed. Please verify request conditions.")
        else:
            debug_logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
    except HTTPException as e:
        debug_logger.error(f"HTTP error in search endpoint: {e.detail}")
        raise e  # Reraise the HTTPException to send it as a response
    
    except Exception as e:
        debug_logger.error(f"Unexpected error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")