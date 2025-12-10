"""Structured logging configuration"""

import logging
import sys
from typing import Any
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON log formatter"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


def setup_logging(log_level: str = "INFO", log_format: str = "json"):
    """Setup application logging"""
    
    # Create logger
    logger = logging.getLogger("symptoguide")
    logger.setLevel(log_level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Set formatter
    if log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


# Create default logger
logger = setup_logging()


def log_prediction(symptoms: list, prediction: str, confidence: float, duration_ms: float):
    """Log prediction with structured data"""
    logger.info(
        "Prediction made",
        extra={
            "extra_data": {
                "symptoms_count": len(symptoms),
                "prediction": prediction,
                "confidence": confidence,
                "duration_ms": duration_ms,
            }
        }
    )
