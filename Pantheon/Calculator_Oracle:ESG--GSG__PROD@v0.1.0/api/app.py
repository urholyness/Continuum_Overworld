from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from dotenv import load_dotenv

from models import get_db, init_db
from routes import batches, legs, hubs, calculate

load_dotenv()

app = FastAPI(
    title="ESG Calculator Oracle",
    description="ISO 14083 compliant emissions calculator for GreenStemGlobal",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Include routers
app.include_router(batches.router, prefix="/batches", tags=["batches"])
app.include_router(legs.router, prefix="/batches", tags=["legs"])
app.include_router(hubs.router, prefix="/batches", tags=["hubs"])
app.include_router(calculate.router, prefix="/batches", tags=["calculate"])

@app.get("/")
async def root():
    return {
        "name": "Calculator_Oracle:ESG--GSG__PROD",
        "version": "0.1.0",
        "status": "operational",
        "methodology": "ISO 14083 + GLEC Framework v3",
        "factors": os.getenv("FACTOR_PACK", "DEFRA-2024")
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}