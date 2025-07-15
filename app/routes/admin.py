from fastapi import APIRouter, Depends, HTTPException
from app.db import db
from app.models.quiz import ThemeCreate, QuestionCreate
from app.auth import admin_required  # 👈 vérifie bien ce chemin

router = APIRouter()

@router.post("/add-theme")
async def add_theme(theme: ThemeCreate, user=Depends(admin_required)):
    existing = await db.themes.find_one({"name": theme.name})
    if existing:
        raise HTTPException(status_code=400, detail="Ce thème existe déjà.")
    
    await db.themes.insert_one(theme.dict())
    return {"message": f"Thème '{theme.name}' ajouté avec succès."}

@router.post("/add-question")
async def add_question(question: QuestionCreate, user=Depends(admin_required)):
    theme = await db.themes.find_one({"name": question.theme})
    if not theme:
        raise HTTPException(status_code=404, detail="Thème non trouvé.")
    
    if question.correct_answer not in question.options:
        raise HTTPException(status_code=400, detail="La réponse correcte doit être dans les options.")
    
    await db.questions.insert_one(question.dict())
    return {"message": "Question ajoutée avec succès."}
