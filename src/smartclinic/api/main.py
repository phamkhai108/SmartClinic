import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from smartclinic.api.dependencies import get_elasticsearch_client
from smartclinic.api.routers import (
    brain,
    chat,
    chat_history,
    files,
    heart,
    lung,
    mail,
    search,
)
from smartclinic.vectordb.elasticsearch.es_setup import create_chunk_index

app = FastAPI(
    title="AISP API",
    description="Handle searching, chat interactions, providing responses.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brain.router)
app.include_router(heart.router)
app.include_router(lung.router)
app.include_router(chat.router)
app.include_router(chat_history.router)
app.include_router(mail.router)
app.include_router(files.router)
app.include_router(search.router)
create_chunk_index(client=get_elasticsearch_client())
if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
