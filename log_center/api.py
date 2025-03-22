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


@router.post("/keys/deactivate/{key}", response_model=APIKeyResponse)
def deactivate_api_key(
    key: str,
    request: Request,
    x_admin_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if x_admin_api_key != request.app.state.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid admin key")

    api_key = db.query(APIKey).filter(APIKey.key == key).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    api_key.deactivated_at = datetime.now()
    db.commit()
    db.refresh(api_key)
    return api_key


@router.post("/keys/deactivate/{owner_email}", response_model=APIKeyResponse)
def deactivate_api_key_by_owner(
    owner_email: EmailStr,
    request: Request,
    x_admin_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if x_admin_api_key != request.app.state.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid admin key")

    api_keys = db.query(APIKey).filter(APIKey.owner_email == owner_email, APIKey.deactivated_at == None).all()
    if not api_keys:
        raise HTTPException(status_code=404, detail="No active API keys found for this owner")

    for api_key in api_keys:
        api_key.deactivated_at = datetime.now()
        
    db.commit()

    return api_keys

@router.get("/keys/active/{owner_email}", response_model=List[APIKeyResponse])
def get_active_api_keys_by_owner(
    owner_email: EmailStr,
    request: Request,
    db: Session = Depends(get_db),
    x_admin_api_key: Optional[str] = Header(None)
):
    if x_admin_api_key != request.app.state.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid admin key")
    
    api_keys = db.query(APIKey).filter(APIKey.owner_email == owner_email, APIKey.deactivated_at == None).all()
    if not api_keys:
        raise HTTPException(status_code=404, detail="No active API keys found for this owner")
    return api_keys


@router.get("/keys/active/", response_model=List[APIKeyResponse])
def get_active_api_keys(
    request: Request,
    db: Session = Depends(get_db),
    x_admin_api_key: Optional[str] = Header(None)
):
    if x_admin_api_key != request.app.state.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid admin key")
    
    api_keys = db.query(APIKey).filter(APIKey.deactivated_at == None).all()
    if not api_keys:
        raise HTTPException(status_code=404, detail="No active API keys found")
    return api_keys

@router.get("/keys/deactivated/", response_model=List[APIKeyResponse])
def get_deactivated_api_keys(
    request: Request,
    db: Session = Depends(get_db),
    x_admin_api_key: Optional[str] = Header(None)
):
    if x_admin_api_key != request.app.state.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid admin key")
    
    api_keys = db.query(APIKey).filter(APIKey.deactivated_at != None).all()
    if not api_keys:
        raise HTTPException(status_code=404, detail="No deactivated API keys found")
    return api_keys


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


@router.get("/logs/filter/{process_name}/messages/{keyword}", response_model=List[LogEntryCreate])
def get_logs_by_process_and_msg_keyword(process_name: str, keyword: str, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    filtered_logs = db.query(LogEntry).filter(LogEntry.process_name == process_name, LogEntry.message.contains(keyword)).all()
    if not filtered_logs:
        raise HTTPException(status_code=404, detail="No logs found for this process name and keyword")
    return filtered_logs
