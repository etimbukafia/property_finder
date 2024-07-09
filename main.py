from db_connect import Database
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import ValidationError
from models import SearchRequest, Data
from ai import search_house
from typing import List
import logging
import logging.config
import yaml

from dotenv import load_dotenv
load_dotenv()

# Load logging configuration
with open('logging_config.yaml', 'r') as file:
    config = yaml.safe_load(file.read())
    logging.config.dictConfig(config)

logger = logging.getLogger('myapp')

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    await Database.connect()


@app.on_event("shutdown")
async def shutdown_db_client():
    await Database.close()


@app.get('/listings', response_model=List[Data])
async def read_listings() -> List[Data]:
    collection = Database._collection
    result = collection.find({})
    result_list = await result.to_list(length=20)

    try:
        datum = [Data(**data) for data in result_list]
        return datum
    except ValidationError as e:
        logging.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail="Invalid data format")
    

@app.post('/search')
async def search(request: SearchRequest): 
    try:
        result = await search_house(request.description)
        return result
    except Exception as e:
        logging.error(f"Validation error: {e}")
        raise HTTPException(status_code=500, detail= "An error occured, try again later")

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info")