from db_connect import Database
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
import uvicorn
from pydantic import ValidationError
from models import *
#from ai import search_house
from sim_searchAI import similiarity_search
from typing import List
import logging
import logging.config
import yaml
from io import BytesIO
from bson import ObjectId
from gridfs.errors import NoFile
from fastapi.middleware.cors import CORSMiddleware
from query_processor import *
from config import Configs
from dotenv import load_dotenv
load_dotenv()

# Load logging configuration
with open('logging_config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    logging.config.dictConfig(config)

# Define the loggers
app_logger = logging.getLogger('app_logger')
debug_logger = logging.getLogger('debug_logger')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

configs = Configs()

vector_store = None
llm = None


@app.on_event("startup")
async def startup_db_client():
    global vector_store, llm
    try:
        await Database.connect()
        await configs.initialize()
        llm = configs.get_llm()
    except Exception as e:
        app_logger.error(f"Startup failed: {e}")
        raise RuntimeError("Failed to start application")

@app.on_event("shutdown")
async def shutdown_db_client():
    try:
        await Database.close()
    except Exception as e:
        app_logger.error(f"Shutdown failed: {e}")


@app.get('/listings', response_model=List[House])
async def read_listings(limit: int = Query(20, ge=1, le=100), skip: int=0) -> List[House]:
    """
    Fetches house listings from the MongoDB collection, enriches them with image URLs,
    and returns the listings in a structured format as a list of `House` objects.

    Returns:
        List[House]: A list of house listings, each containing relevant details
        and an image URL if available.

        The read_listings() function returns a list of house listings, 
        including image URLs like https://hardly-sound-ringtail.ngrok-free.app/images/abc123.

    Raises:
        HTTPException: If there is a validation error with the data format.
    """

    collection = Database._collection
    result = collection.find({}).skip(skip).limit(limit)
    result_list = await result.to_list(length=limit)

    try:
        # Construct listings with image URLs
        listings_with_images = []
        for data in result_list:
            # Convert ObjectId fields to strings for compatibility
            data['_id'] = str(data['_id'])
            if 'image_id' in data:
                data['image_id'] = str(data['image_id'])
                # Construct the image URL using the image_id and add it to the data
                data['homeImage'] = f"https://hardly-sound-ringtail.ngrok-free.app/images/{data['image_id']}"

            # Create a House object from the data and add it to the list
            listings_with_images.append(House(**data))

        # Return the list of enriched house listings
        return listings_with_images
    except ValidationError as e:
        # Log the validation error and raise an HTTP 400 exception with a relevant message
        app_logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail="Invalid data format")

# Endpoint to serve images
@app.get("/images/{image_id}")
async def get_image(image_id: str):
    """Serves individual images when requested. 
    This endpoint provides the actual image files in response to requests for specific images."""
    try:
        # Convert string to ObjectId
        file_id = ObjectId(image_id)
        # Retrieve file from GridFS
        file = await Database._fs.get(file_id)
        # Read file content into a BytesIO object
        content = BytesIO(file.read())
        content.seek(0)
        return StreamingResponse(content, media_type="image/jpeg")
    except NoFile as e:
        logging.error(f"No file found: {e}")
        raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        logging.error(f"Error retrieving image: {e}")
        raise HTTPException(status_code=404, detail="Image not found")

# Define the endpoint for searching, which accepts a POST request and returns a SearchResponse
@app.post('/search', response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse: 
    try:
        # Extracts the query and filter from the incoming request
        query = request.query

        # Defines the fields that will be returned in the search results
        fields_to_return = ["city", "streetAddress", "latestPrice"]

        # Performs search with filters
        similar_listings = await similiarity_search(query, fields_to_return)

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
        
    except Exception as e:
        app_logger.error(f"Error in search endpoint: {e}")
        return SearchResponse(listings=[])
        
    #try:
        #result = await search_house(request.description)
        #return result
    #except Exception as e:
        #logging.error(f"Validation error: {e}")
        #raise HTTPException(status_code=500, detail= "An error occured, try again later")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, log_level="info")