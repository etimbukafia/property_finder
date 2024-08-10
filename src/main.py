from db_connect import Database
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn
from pydantic import ValidationError
from models import *
#from ai import search_house
from sim_searchAI import similiarity_search, load_model
from typing import List
import logging
import logging.config
import yaml
from io import BytesIO
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
from cProfile import Profile
from pstats import SortKey, Stats


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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await Database.connect()

@app.on_event("startup")
async def startup_load_model():
    await load_model()

@app.on_event("shutdown")
async def shutdown_db_client():
    await Database.close()


@app.get('/listings', response_model=List[House])
async def read_listings() -> List[House]:
    collection = Database._collection
    result = collection.find({})
    result_list = await result.to_list(length=20)

    try:
        # Construct listings with image URLs
        listings_with_images = []
        for data in result_list:
            data['_id'] = str(data['_id'])
            if 'image_id' in data:
                data['image_id'] = str(data['image_id'])
                data['homeImage'] = f"https://hardly-sound-ringtail.ngrok-free.app/images/{data['image_id']}"
            listings_with_images.append(House(**data))
        return listings_with_images
    except ValidationError as e:
        app_logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail="Invalid data format")

# Endpoint to serve images
@app.get("/images/{image_id}")
async def get_image(image_id: str):
    try:
        # Convert string to ObjectId
        file_id = ObjectId(image_id)
        # Retrieve file from GridFS
        file = await Database._fs.get(file_id)
        # Read file content into a BytesIO object
        content = BytesIO(file.read())
        content.seek(0)
        return StreamingResponse(content, media_type="image/jpeg")
    except Exception as e:
        logging.error(f"Error retrieving image: {e}")
        raise HTTPException(status_code=404, detail="Image not found")

# Define the endpoint for searching, which accepts a POST request and returns a SearchResponse
@app.post('/search', response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse: 
    with Profile() as profile:
        try:
            # Extract the query string from the incoming request
            query = request.query
            #debug_logger.debug(f"Query: {query}")

            # Define the fields that will be returned in the search results
            fields_to_return = ["city", "streetAddress", "latestPrice"]

            similar_listings = await similiarity_search(query, fields_to_return)

            # Prepare the response object by populating it with the similar listings
            response = SearchResponse(
                listings=[Listing(
                    id=str(doc['_id']), # Convert the document ID to a string
                    city=doc.get('city', ''), # Get the city from the document, or an empty string if not present
                    streetAddress=doc.get('streetAddress', ''), # Get the street address from the document, or an empty string if not present
                    latestPrice=doc.get('latestPrice', 0.0) # Get the latest price from the document, or 0.0 if not present
                ) for doc in similar_listings] # Iterate over each similar listing to create a Listing object
            )

            # Dump the profile data to a file
            profile.dump_stats('profile_data.prof')

            #Print profiling stats
            with open('profile_stats.txt', 'w') as f:
                stats = Stats('profile_data.prof', stream=f)
                stats.strip_dirs().sort_stats(SortKey.CALLS).print_stats()

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