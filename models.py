from pydantic import BaseModel, Field 
"""#The Field method in Pydantic is used to provide additional metadata and validation to the fields of a Pydantic model. 
It allows you to specify things like default values, aliases, constraints (e.g., min/max length, regex patterns), descriptions, and examples, among other options."""
from typing import List, Any, Optional

class SearchRequest(BaseModel):
    description: str

class House(BaseModel):
    _id: str = Field(..., alias="_id") 
    """The alias parameter in Pydantic's Field method allows you to specify an alternative name for a field when serializing and deserializing data. 
    This can be particularly useful when the field names in your Pydantic models do not match the field names in the input or output data you are working with. """
    city: str
    streetAddress: str
    livingAreaSqFt: float
    numOfBedrooms: int
    numOfBathrooms: float
    image_id: Optional[str]
    homeImage: Optional[Any]
    homeType: str
    latestPrice: int
    description: str

