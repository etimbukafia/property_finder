from db_connect import Database
from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
#from ai import search_house
import logging
from fastapi.middleware.cors import CORSMiddleware
from config import Configs
from helpers.util import initialize_cache
from routes.listings import router as listings_router
from routes.search import router as search_router
from dotenv import load_dotenv

# LOGGING
app_logger = logging.getLogger('app_logger')
debug_logger = logging.getLogger('debug_logger')

configs = Configs()
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await configs.initialize()
        collection = await Database.connect()
        await initialize_cache(collection)
        llm = configs.get_llm()
        model = configs.get_embeddings_model()
        client = configs.get_client()
    
        app.state.config = {
            "collection": collection,
            "llm": llm,
            "model": model,
            "client": client
        }
        yield

    except Exception as e:
        debug_logger.error(f"Startup failed: {e}")
        raise RuntimeError("Failed to start application")
    
    finally:
        app.state.config.clear()
        app_logger.info("Application shutdown complete")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(listings_router)
app.include_router(search_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3001, log_level="info")