from fastapi import APIRouter, Depends, HTTPException, Header, Request
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
import secrets

from .models import LogEntry, APIKey, get_db, LogLevel

router = APIRouter()

class LogEntryCreate(BaseModel):
    level: LogLevel
    message: str
    process_name: str
    timestamp: datetime = datetime.now()

class APIKeyCreate(BaseModel):
    owner_email: EmailStr

class APIKeyResponse(BaseModel):
    key: str
    owner_email: EmailStr
    created_at: datetime
    deactivated_at: Optional[datetime] = None


def verify_api_key(x_api_key: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not x_api_key or not db.query(APIKey).filter(APIKey.key == x_api_key).first():
        raise HTTPException(status_code=401, detail="Invalid API key")


@router.post("/keys/", response_model=APIKeyResponse)
def create_api_key(
    request: Request,
    api_key_data: APIKeyCreate,
    x_admin_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if x_admin_api_key != request.app.state.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid admin key")

    new_key = secrets.token_hex(32)
    api_key = APIKey(
        key=new_key,
        created_at=datetime.utcnow(),
        owner_email=api_key_data.owner_email,
        deactivated_at=None
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key

@router.post("/logs/")
def post_log(entry: LogEntryCreate, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    log = LogEntry(level=entry.level, message=entry.message, process_name=entry.process_name, timestamp=entry.timestamp)
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"message": "Log saved", "log": log}

@router.get("/logs/", response_model=List[LogEntryCreate])
def get_logs(db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    return db.query(LogEntry).all()

@router.get("/logs/{level}", response_model=List[LogEntryCreate])
def get_logs_by_level(level: str, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    filtered_logs = db.query(LogEntry).filter(LogEntry.level == level).all()
    if not filtered_logs:
        raise HTTPException(status_code=404, detail="No logs found for this level")
    return filtered_logs

@router.get("/logs/process/{process_name}", response_model=List[LogEntryCreate])
def get_logs_by_process_name(process_name: str, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    filtered_logs = db.query(LogEntry).filter(LogEntry.process_name == process_name).all()
    if not filtered_logs:
        raise HTTPException(status_code=404, detail="No logs found for this process name")
    return filtered_logs

@router.get("/logs/filter/{process_name}/{level}", response_model=List[LogEntryCreate])
def get_logs_by_process_and_level(process_name: str, level: str, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    filtered_logs = db.query(LogEntry).filter(LogEntry.process_name == process_name, LogEntry.level == level).all()
    if not filtered_logs:
        raise HTTPException(status_code=404, detail="No logs found for this process name and level")
    return filtered_logs
