from fastapi import APIRouter, Depends, HTTPException
from app.db import db
from app.models.quiz import ThemeCreate, QuestionCreate, QuestionUpdate
from app.auth import admin_required
from bson import ObjectId
from typing import List

router = APIRouter()

# Theme CRUD Operations

@router.post("/add-theme")
async def add_theme(theme: ThemeCreate, user=Depends(admin_required)):
    """
    Add a new theme
    """
    existing = await db.themes.find_one({"name": theme.name})
    if existing:
        raise HTTPException(status_code=400, detail="Theme already exists.")
    
    await db.themes.insert_one(theme.dict())
    return {"message": f"Theme '{theme.name}' added successfully."}

@router.get("/themes", response_model=List[str])
async def get_themes(user=Depends(admin_required)):
    """
    Get all themes
    """
    themes = await db.themes.find().to_list(length=None)
    return [theme["name"] for theme in themes]

@router.put("/themes/{theme_name}")
async def update_theme(
    theme_name: str, 
    updated_theme: ThemeCreate, 
    user=Depends(admin_required)
):
    """
    Update a theme name
    """
    # Check if theme exists
    existing = await db.themes.find_one({"name": theme_name})
    if not existing:
        raise HTTPException(status_code=404, detail="Theme not found.")
    
    # Check if new name already exists
    if theme_name != updated_theme.name:
        name_exists = await db.themes.find_one({"name": updated_theme.name})
        if name_exists:
            raise HTTPException(status_code=400, detail="New theme name already exists.")
    
    # Update theme and all related questions
    await db.themes.update_one(
        {"name": theme_name},
        {"$set": {"name": updated_theme.name}}
    )
    
    await db.questions.update_many(
        {"theme": theme_name},
        {"$set": {"theme": updated_theme.name}}
    )
    
    return {"message": f"Theme updated to '{updated_theme.name}' successfully."}

@router.delete("/themes/{theme_name}")
async def delete_theme(theme_name: str, user=Depends(admin_required)):
    """
    Delete a theme and all its questions
    """
    # Check if theme exists
    existing = await db.themes.find_one({"name": theme_name})
    if not existing:
        raise HTTPException(status_code=404, detail="Theme not found.")
    
    # Delete theme and its questions in a transaction
    async with await db.client.start_session() as session:
        async with session.start_transaction():
            await db.themes.delete_one({"name": theme_name}, session=session)
            await db.questions.delete_many({"theme": theme_name}, session=session)
    
    return {"message": f"Theme '{theme_name}' and all its questions deleted successfully."}

# Question CRUD Operations

@router.post("/add-question")
async def add_question(question: QuestionCreate, user=Depends(admin_required)):
    """
    Add a new question
    """
    # Verify theme exists
    theme = await db.themes.find_one({"name": question.theme})
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found.")
    
    # Validate correct answer is in options
    if question.correct_answer not in question.options:
        raise HTTPException(
            status_code=400, 
            detail="Correct answer must be one of the options."
        )
    
    await db.questions.insert_one(question.dict())
    return {"message": "Question added successfully."}

@router.get("/questions", response_model=List[QuestionCreate])
async def get_questions(
    theme: str = None, 
    user=Depends(admin_required)
):
    """
    Get all questions, optionally filtered by theme
    """
    query = {}
    if theme:
        # Verify theme exists
        theme_exists = await db.themes.find_one({"name": theme})
        if not theme_exists:
            raise HTTPException(status_code=404, detail="Theme not found.")
        query["theme"] = theme
    
    questions = await db.questions.find(query).to_list(length=None)
    return questions

@router.put("/questions/{question_id}")
async def update_question(
    question_id: str, 
    updated_question: QuestionUpdate, 
    user=Depends(admin_required)
):
    """
    Update a question
    """
    # Validate ObjectId
    if not ObjectId.is_valid(question_id):
        raise HTTPException(status_code=400, detail="Invalid question ID format.")
    
    # Check if question exists
    existing = await db.questions.find_one({"_id": ObjectId(question_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Question not found.")
    
    # If theme is being changed, verify new theme exists
    if updated_question.theme and updated_question.theme != existing["theme"]:
        theme_exists = await db.themes.find_one({"name": updated_question.theme})
        if not theme_exists:
            raise HTTPException(status_code=404, detail="New theme not found.")
    
    # Prepare update data
    update_data = updated_question.dict(exclude_unset=True)
    
    # Validate correct answer is in options if options are being updated
    if "options" in update_data and "correct_answer" in update_data:
        if update_data["correct_answer"] not in update_data["options"]:
            raise HTTPException(
                status_code=400, 
                detail="Correct answer must be one of the options."
            )
    elif "options" in update_data:
        if existing["correct_answer"] not in update_data["options"]:
            raise HTTPException(
                status_code=400, 
                detail="Existing correct answer must be in new options."
            )
    elif "correct_answer" in update_data:
        if update_data["correct_answer"] not in existing["options"]:
            raise HTTPException(
                status_code=400, 
                detail="New correct answer must be in existing options."
            )
    
    # Perform the update
    await db.questions.update_one(
        {"_id": ObjectId(question_id)},
        {"$set": update_data}
    )
    
    return {"message": "Question updated successfully."}

@router.delete("/questions/{question_id}")
async def delete_question(question_id: str, user=Depends(admin_required)):
    """
    Delete a question
    """
    # Validate ObjectId
    if not ObjectId.is_valid(question_id):
        raise HTTPException(status_code=400, detail="Invalid question ID format.")
    
    # Check if question exists
    result = await db.questions.delete_one({"_id": ObjectId(question_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Question not found.")
    
    return {"message": "Question deleted successfully."}
