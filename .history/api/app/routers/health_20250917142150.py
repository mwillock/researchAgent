from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from ..db.session import get_db

router = APIRouter(tags=["health"])

@router.get("/health") #?? Learn more about
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "up"}
    