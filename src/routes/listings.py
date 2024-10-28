from fastapi import APIRouter, Request, Query, HTTPException
from models import House
from typing import List, Optional
import logging

app_logger = logging.getLogger('app_logger')
debug_logger = logging.getLogger('debug_logger')

router = APIRouter()

@router.get('/listings', response_model=List[House])
async def display(request: Request, limit: int = Query(20, ge=1, le=100), skip: Optional[int] = None) -> List[House]:
    # If 'skip' is not provided, set is as 1 x limit
    if skip is None:
        skip = limit

    collection = request.app.state.config["collection"]  
    
    try:
        # MongoDB query to get the product data with limit and skip
        result = collection.find({}).skip(skip).limit(limit)
        result_list = await result.to_list(length=limit)

        houses = []

        for data in result_list:
            data["cloudinaryUrl"] = data.get("image_link", None)
        
            try:
                # Create a Products instance and append it to the products list
                houses.append(House(**data))
            except Exception as e:
                debug_logger.error(f"Error parsing product: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error parsing product: {str(e)}")
                
            
        if not houses:
            debug_logger.error("No products found")
            raise HTTPException(status_code=404, detail="No products found")
        
        return houses
    
    except Exception as e:
        debug_logger.error(f"Error retrieving products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving products: {str(e)}")