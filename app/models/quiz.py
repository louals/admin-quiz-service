from pydantic import BaseModel, Field
from typing import List, Optional

# Used by admins to create themes (optional category for scalability)
class ThemeCreate(BaseModel):
    name: str
    category: Optional[str] = None

# Used by admins to add questions to the DB
class QuestionCreate(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    theme: str  # Must match a theme name already in DB

# Used to return questions to the player (no correct_answer!)
class QuestionOut(BaseModel):
    id: str
    question: str
    options: List[str]

class QuestionOutAdmin(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_answer: str


class AnswerItem(BaseModel):
    question_id: str
    answer: str

class AnswerSubmission(BaseModel):
    theme: str   
    answers: List[AnswerItem]