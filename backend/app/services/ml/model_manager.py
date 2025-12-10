"""Model manager for loading and managing ML models"""

import pickle
import json
import os
from typing import Optional, Dict, Any
from pathlib import Path
from app.core.logging import logger
from app.core.config import settings


class ModelManager:
    """Manages ML model loading and versioning"""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or settings.MODEL_PATH
        self.active_model = None
        self.feature_engineer = None
        self.model_metadata = {}
        self.model_version = settings.MODEL_VERSION
    
    def load_model(self, version: str = None) -> bool:
        """Load model and feature engineer"""
        
        version = version or self.model_version
        model_dir = Path(self.model_path) / version
        
        try:
            # Load model
            model_file = model_dir / "model.pkl"
            if not model_file.exists():
                logger.error(f"Model file not found: {model_file}")
                return False
            
            with open(model_file, 'rb') as f:
                self.active_model = pickle.load(f)
            
            logger.info(f"Loaded model from {model_file}")
            
            # Load feature engineer
            feature_file = model_dir / "feature_engineer.pkl"
            if feature_file.exists():
                with open(feature_file, 'rb') as f:
                    self.feature_engineer = pickle.load(f)
                logger.info(f"Loaded feature engineer from {feature_file}")
            else:
                logger.warning("Feature engineer not found, using raw features")
            
            # Load metadata
            metadata_file = model_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    self.model_metadata = json.load(f)
                logger.info(f"Loaded metadata: {self.model_metadata}")
            
            self.model_version = version
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}", exc_info=True)
            return False
    
    def get_model(self):
        """Get active model"""
        return self.active_model
    
    def get_feature_engineer(self):
        """Get feature engineer"""
        return self.feature_engineer
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata"""
        return {
            "version": self.model_version,
            "loaded": self.active_model is not None,
            **self.model_metadata
        }
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.active_model is not None


# Global model manager instance
_model_manager: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    """Get global model manager instance"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager
