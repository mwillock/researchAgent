from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from app.db.session import get_db
from dotenv import load_dotenv
import httpx, os

#Defining Global Var
load_dotenv(dotenv_path=".env")
url = os.getenv("OLLAMA_URL")
print("OLLAMA_URL =", os.getenv("OLLAMA_URL"))

router = APIRouter(tags=["health"])

@router.get("/health") #?? Learn more about
def health(db: Session = Depends(get_db)):
    #DB Check 
    db.execute(text("SELECT 1"))
    
    #Ollama Check
    ollama_url = os.getenv("OLLAMA_URL", url)
    r = httpx.get(f"{ollama_url}/api/tags", timeout=2.0)
    r.raise_for_status()
    
    return {
            "status": "ok",
            "db": "up",
            "ollama":"running",
            "models":r.json().get("models", [])
        }
    