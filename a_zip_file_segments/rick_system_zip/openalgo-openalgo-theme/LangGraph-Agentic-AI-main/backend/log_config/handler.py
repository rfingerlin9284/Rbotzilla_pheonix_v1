# logging_handler.py
import logging
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from models import Base, SystemLog
import json
from datetime import datetime

class SQLAlchemyLogHandler(logging.Handler):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
    def emit(self, record):
        try:
            log_entry = SystemLog(
                level=record.levelname,
                component=record.name,
                message=self.format(record),
                details={
                    "pathname": record.pathname,
                    "lineno": record.lineno,
                    "funcName": record.funcName,
                    "stack": record.stack_info
                }
            )
            
            # Add agent context if available
            if hasattr(record, 'agent_id'):
                log_entry.agent_id = record.agent_id
            
            with Session(self.engine) as session:
                session.add(log_entry)
                session.commit()
        except Exception as e:
            print(f"Failed to write log to database: {e}")

def setup_logging(engine):
    """Configure logging for the application"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    
    # Remove default handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add SQLAlchemy handler
    db_handler = SQLAlchemyLogHandler(engine)
    db_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    db_handler.setFormatter(formatter)
    logger.addHandler(db_handler)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
