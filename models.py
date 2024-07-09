from pydantic import BaseModel
from typing import Optional, List, Any

class SearchRequest(BaseModel):
    description: str

class Data(BaseModel):
    city: str
    streetAddress: str
    livingAreaAqFt: float
    numOfBedrooms: int
    numOfBathrooms: float
    homeImage: Any
    homeType: str
    latestPrice: int
    description: str

