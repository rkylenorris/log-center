from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import LogEntry, LogLevel
from typing import List

class LogQuery:
    def __init__(self, database_url: str = "sqlite:///./logs.db"):
        self.engine = create_engine(database_url, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_logs_by_level(self, level: LogLevel) -> List[LogEntry]:
        with self.SessionLocal() as session:
            return session.query(LogEntry).filter(LogEntry.level == level.value).all()
    
    def get_logs_by_process(self, process_name: str) -> List[LogEntry]:
        with self.SessionLocal() as session:
            return session.query(LogEntry).filter(LogEntry.process_name == process_name).all()
    
    def get_logs_by_message_keyword(self, keyword: str) -> List[LogEntry]:
        with self.SessionLocal() as session:
            return session.query(LogEntry).filter(LogEntry.message.contains(keyword)).all()
    
    def get_recent_logs(self, limit: int = 10) -> List[LogEntry]:
        with self.SessionLocal() as session:
            return session.query(LogEntry).order_by(LogEntry.timestamp.desc()).limit(limit).all()
    
# Example usage
if __name__ == "__main__":
    log_query = LogQuery()
    errors = log_query.get_logs_by_level(LogLevel.ERROR)
    print(f"Found {len(errors)} error logs")
    
    process_logs = log_query.get_logs_by_process("MyProcess")
    print(f"Found {len(process_logs)} logs for MyProcess")
    
    keyword_logs = log_query.get_logs_by_message_keyword("failure")
    print(f"Found {len(keyword_logs)} logs containing 'failure'")
    
    recent_logs = log_query.get_recent_logs()
    print(f"Most recent logs: {recent_logs}")
