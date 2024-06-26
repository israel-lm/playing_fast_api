import contextlib
import motor.motor_asyncio as motor

from fastapi import FastAPI, HTTPException, Query
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId
from fastapi.encoders import jsonable_encoder

from playing_fast_api.defs import DB_URL, DB_NAME

app = FastAPI()
mongo_client = motor.AsyncIOMotorClient(DB_URL)
db = mongo_client[DB_NAME]


@app.get("/courses")
async def get_courses(sort_by: str = "date", domain: str = None) -> list:
    """
    Retrieves all courses in the database.

    Args:
        sort_by: The field to sort by.
        domain: Course domain, if any.

    Returns:
        List of courses.
    """
    
    cursor = db.courses.find()
    async for course in cursor:
        total = 0
        count = 0
        
        for chapter in course["chapters"]:
            total += chapter["rating"]["total"]
            count += chapter["rating"]["count"]
        
        await db.courses.update_one(
            {"_id": course["_id"]},
            {"$set": {"rating": {"total": total, "count": count}}}
        )
    
    if sort_by == "date":
        sort_field = "date"
        sort_order = DESCENDING
    elif sort_by == "rating":
        sort_field = "rating.total"
        sort_order = DESCENDING
    else:
        sort_field = "name"
        sort_order = ASCENDING
    
    query = {}
    if domain:
        query["domain"] = domain
        
    cursor = db.courses.find(
        query,
        {"name": True, "date": True, "description": True, "domain": True, "_id": False}
    ).sort(sort_field, sort_order)
    
    return await cursor.to_list(None)


@app.get("/courses/{course_name}")
async def get_course(course_name: str) -> dict:
    """
    Get details about a specific course.

    Args:
        course_name: Name of the course to get details about.

    Returns:
        Dictionary containing course information.
    """
    
    course = await find_course(course_name)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    
    try:
        course["rating"] = course["rating"]["total"]
    except KeyError:
        course["rating"] = "Not rated yet."
    return course

@app.get("/courses/{course_name}/{chapter_id}")
async def get_chapter(course_name: str, chapter_id: str) -> dict:
    """
    Get information about a chapter of a course.

    Args:
        course_name: Name of the course.
        chapter_id: Index identifying the chapter.

    Returns:
        Dictionary with chapter information.
    """
    
    chapter = await find_chapter(course_name, chapter_id)
    if chapter:
        return chapter
    else:
        raise HTTPException(status_code=404, detail="Chapter not found.")

@app.post("/courses/{course_name}/{chapter_id}")
async def rate_chapter(course_name: str, chapter_id: str, rating: int = Query(..., gt=-2, lt=2)) -> list:
    """
    Update the rating of a chapter.

    Args:
        course_name: Name of the course.
        chapter_id: Index identifying the chapter.
        rating: 1 for a good rating, -1 for a bad rating.

    Raises:
        HTTPException: _description_

    Returns:
        Update list of chapters.
    """
    
    chapters = await find_chapters(course_name)
    
    try:
        chapter = chapters[int(chapter_id)]
    except (ValueError, IndexError):
        raise HTTPException(status_code=404, detail='Chapter not found')
    
    try:
        chapter["rating"]["total"] += rating
        chapter["rating"]["count"] += 1
    except KeyError:
        chapter["rating"] = {"total": rating, "count": 1}
    
    await db.courses.update_one({"name": course_name}, {"$set": {"chapters": chapters}})
    return chapters


#### Helper functions below ####

async def find_course(course_name: str, include_chapter: bool = False):
    return await db.courses.find_one({"name": course_name}, {"_id": False, "chapters": include_chapter})

async def find_chapters(course_name: str):
    course = await find_course(course_name, True)
    if course:
        chapters = course.get('chapters')
    else:
        chapters = None
    return chapters

async def find_chapter(course_name: str, chapter_id: str):
    chapters = await find_chapters(course_name)
    if chapters:
        try:
            chapter = chapters[int(chapter_id)]
        except Exception:
            chapter = None
    else:
        chapter = None
    return chapter