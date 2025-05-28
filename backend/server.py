from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class IdeaStatus(str, Enum):
    active = "active"
    archived = "archived"

# Models
class IdeaBase(BaseModel):
    title: str
    content: str
    tags: List[str] = []
    category: str = "General"
    status: IdeaStatus = IdeaStatus.active

class IdeaCreate(IdeaBase):
    pass

class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    status: Optional[IdeaStatus] = None

class Idea(IdeaBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Legacy status check models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# API Routes

# Legacy routes
@api_router.get("/")
async def root():
    return {"message": "Idea Logger API is running!"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Ideas CRUD routes
@api_router.post("/ideas", response_model=Idea)
async def create_idea(idea_data: IdeaCreate):
    idea_dict = idea_data.dict()
    idea_obj = Idea(**idea_dict)
    await db.ideas.insert_one(idea_obj.dict())
    return idea_obj

@api_router.get("/ideas", response_model=List[Idea])
async def get_ideas(
    status: Optional[IdeaStatus] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags")
):
    query = {}
    
    # Filter by status
    if status:
        query["status"] = status
    
    # Filter by category
    if category:
        query["category"] = category
    
    # Filter by tags
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        query["tags"] = {"$in": tag_list}
    
    # Text search
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"content": {"$regex": search, "$options": "i"}}
        ]
    
    ideas = await db.ideas.find(query).sort("updated_at", -1).to_list(1000)
    return [Idea(**idea) for idea in ideas]

@api_router.get("/ideas/{idea_id}", response_model=Idea)
async def get_idea(idea_id: str):
    idea = await db.ideas.find_one({"id": idea_id})
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return Idea(**idea)

@api_router.put("/ideas/{idea_id}", response_model=Idea)
async def update_idea(idea_id: str, idea_data: IdeaUpdate):
    # Find existing idea
    existing_idea = await db.ideas.find_one({"id": idea_id})
    if not existing_idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Update only provided fields
    update_data = {k: v for k, v in idea_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.ideas.update_one({"id": idea_id}, {"$set": update_data})
    
    # Return updated idea
    updated_idea = await db.ideas.find_one({"id": idea_id})
    return Idea(**updated_idea)

@api_router.delete("/ideas/{idea_id}")
async def delete_idea(idea_id: str):
    result = await db.ideas.delete_one({"id": idea_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Idea not found")
    return {"message": "Idea deleted successfully"}

# Archive/Unarchive ideas
@api_router.patch("/ideas/{idea_id}/archive")
async def archive_idea(idea_id: str):
    result = await db.ideas.update_one(
        {"id": idea_id}, 
        {"$set": {"status": IdeaStatus.archived, "updated_at": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Idea not found")
    return {"message": "Idea archived successfully"}

@api_router.patch("/ideas/{idea_id}/unarchive")
async def unarchive_idea(idea_id: str):
    result = await db.ideas.update_one(
        {"id": idea_id}, 
        {"$set": {"status": IdeaStatus.active, "updated_at": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Idea not found")
    return {"message": "Idea unarchived successfully"}

# Get all unique categories
@api_router.get("/categories")
async def get_categories():
    categories = await db.ideas.distinct("category")
    return {"categories": categories}

# Get all unique tags
@api_router.get("/tags")
async def get_tags():
    tags = await db.ideas.distinct("tags")
    return {"tags": tags}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
