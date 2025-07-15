from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.routes import admin
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS si tu accèdes à l'API depuis un frontend (React, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tu peux restreindre à ["https://tonsite.com"] en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(admin.router, prefix="/admin", tags=["Admin"])

@app.get("/")
async def root():
    return {"message": "Admin service is running!"}
