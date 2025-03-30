import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from smartclinic.api.routers import heart, mail, lung

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

app.include_router(mail.router)
app.include_router(heart.router)
app.include_router(lung.router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
