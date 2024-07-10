from pydantic import BaseModel
from typing import List, Any, Optional

class SearchRequest(BaseModel):
    description: str

class House(BaseModel):
    city: str
    streetAddress: str
    livingAreaSqFt: float
    numOfBedrooms: int
    numOfBathrooms: float
    homeImage: Optional[Any]
    homeType: str
    latestPrice: int
    description: str

