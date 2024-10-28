from pydantic import BaseModel, Field 
"""#The Field method in Pydantic is used to provide additional metadata and validation to the fields of a Pydantic model. 
It allows you to specify things like default values, aliases, constraints (e.g., min/max length, regex patterns), descriptions, and examples, among other options."""
from typing import List, Any, Optional
from bson import ObjectId

#class SearchRequest(BaseModel):
    #description: str

class House(BaseModel):
    city: str
    streetAddress: str
    livingAreaSqFt: float
    numOfBedrooms: int
    numOfBathrooms: float
    homeType: str
    latestPrice: int
    description: str
    cloudinaryUrl: Optional[str] = Field(..., alias="image_link")

class Listing(BaseModel):
    """Represents a single listing with fields for ID, city, street address, and latest price."""
    id: str
    city: str
    streetAddress: str
    latestPrice: float

    class Config:
        """allows Pydantic to handle MongoDB's ObjectId correctly by converting it to a string, which is useful for serializing responses."""
        json_encoders = {
            ObjectId: str
        }

class SearchRequest(BaseModel):
    query: str

class SearchResponse(BaseModel):
    listings: List[Listing]

class Result(BaseModel):
    expanded_queries: list[str] 