"""Pydantic schemas for request/response validation"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from enum import Enum


class GenderEnum(str, Enum):
    """Gender enumeration"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class SeverityEnum(str, Enum):
    """Severity level enumeration"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class SymptomAnalysisRequest(BaseModel):
    """Request model for symptom analysis"""
    
    symptoms: List[str] = Field(..., min_length=1, max_length=20, description="List of symptoms")
    severity: Dict[str, int] = Field(default_factory=dict, description="Symptom severity (1-10)")
    duration: Optional[Dict[str, str]] = Field(default=None, description="Symptom duration")
    
    # Patient context
    age: Optional[int] = Field(None, ge=0, le=120, description="Patient age")
    gender: Optional[GenderEnum] = Field(None, description="Patient gender")
    
    # Medical history
    medical_history: Optional[str] = Field(None, max_length=1000, description="Medical history")
    current_medications: Optional[str] = Field(None, max_length=500, description="Current medications")
    allergies: Optional[str] = Field(None, max_length=500, description="Known allergies")
    
    # Follow-up questions
    follow_up_answers: Optional[Dict[str, Any]] = Field(default=None, description="Follow-up question answers")
    
    @field_validator("symptoms")
    @classmethod
    def validate_symptoms(cls, v: List[str]) -> List[str]:
        """Validate and clean symptoms"""
        # Remove empty strings and duplicates
        cleaned = list(set([s.strip().lower() for s in v if s.strip()]))
        if not cleaned:
            raise ValueError("At least one valid symptom is required")
        return cleaned
    
    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: Dict[str, int]) -> Dict[str, int]:
        """Validate severity values"""
        for symptom, level in v.items():
            if not 1 <= level <= 10:
                raise ValueError(f"Severity for '{symptom}' must be between 1 and 10")
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "symptoms": ["headache", "fever", "fatigue"],
                "severity": {"headache": 7, "fever": 8, "fatigue": 6},
                "age": 35,
                "gender": "male",
                "medical_history": "No significant history",
                "current_medications": "None",
                "allergies": "None"
            }
        }
    }


class PredictionResult(BaseModel):
    """Single prediction result"""
    
    disease: str = Field(..., description="Predicted disease name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability score")
    severity_level: Optional[SeverityEnum] = Field(None, description="Estimated severity")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "disease": "Common Cold",
                "confidence": 0.85,
                "probability": 0.82,
                "severity_level": "mild"
            }
        }
    }


class Recommendation(BaseModel):
    """Health recommendation"""
    
    category: str = Field(..., description="Recommendation category")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed description")
    priority: str = Field(..., description="Priority level: high, medium, low")


class ModelMetadata(BaseModel):
    """Model metadata"""
    
    model_version: str = Field(..., description="Model version")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    features_used: int = Field(..., description="Number of features used")


class AnalysisResponse(BaseModel):
    """Response model for symptom analysis"""
    
    success: bool = Field(default=True, description="Whether analysis was successful")
    predictions: List[PredictionResult] = Field(..., description="List of predictions")
    primary_prediction: PredictionResult = Field(..., description="Most likely prediction")
    
    # Recommendations
    recommendations: List[Recommendation] = Field(default_factory=list, description="Health recommendations")
    precautions: List[str] = Field(default_factory=list, description="Precautions to take")
    
    # Explanations
    explanation: Optional[Dict[str, Any]] = Field(None, description="Model explanation (SHAP values)")
    key_symptoms: List[str] = Field(default_factory=list, description="Most influential symptoms")
    
    # Metadata
    metadata: ModelMetadata = Field(..., description="Analysis metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "predictions": [
                    {
                        "disease": "Common Cold",
                        "confidence": 0.85,
                        "probability": 0.82,
                        "severity_level": "mild"
                    }
                ],
                "primary_prediction": {
                    "disease": "Common Cold",
                    "confidence": 0.85,
                    "probability": 0.82,
                    "severity_level": "mild"
                },
                "recommendations": [],
                "precautions": ["Rest well", "Stay hydrated"],
                "key_symptoms": ["fever", "cough"],
                "metadata": {
                    "model_version": "v1",
                    "processing_time_ms": 150.5,
                    "features_used": 230
                }
            }
        }
    }


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    model_loaded: bool = Field(..., description="Whether ML model is loaded")
    model_version: Optional[str] = Field(None, description="Loaded model version")
