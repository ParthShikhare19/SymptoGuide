"""Symptom analysis endpoint"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import time

from app.models.schemas import (
    SymptomAnalysisRequest,
    AnalysisResponse,
    ModelMetadata,
    Recommendation
)
from app.services.ml.predictor import get_prediction_service, PredictionService
from app.services.ml.model_manager import get_model_manager
from app.core.logging import logger

router = APIRouter()


def get_recommendations(disease: str, symptoms: list) -> list:
    """Get health recommendations based on disease"""
    
    recommendations = []
    
    # General recommendations
    recommendations.append(
        Recommendation(
            category="general",
            title="Consult a Healthcare Professional",
            description="Please consult with a healthcare provider for proper diagnosis and treatment.",
            priority="high"
        )
    )
    
    # Symptom-specific recommendations
    if any(s in symptoms for s in ['fever', 'high fever']):
        recommendations.append(
            Recommendation(
                category="symptom_management",
                title="Monitor Temperature",
                description="Keep track of your temperature and stay hydrated. Rest is important.",
                priority="medium"
            )
        )
    
    if any(s in symptoms for s in ['cough', 'persistent cough']):
        recommendations.append(
            Recommendation(
                category="symptom_management",
                title="Manage Cough",
                description="Stay hydrated, use humidifier, and avoid irritants. Seek medical advice if persistent.",
                priority="medium"
            )
        )
    
    return recommendations


def get_precautions(disease: str, symptoms: list) -> list:
    """Get precautions based on disease"""
    
    precautions = [
        "Wash hands frequently with soap and water",
        "Get adequate rest and sleep",
        "Stay hydrated by drinking plenty of water",
        "Avoid self-medication without consulting a doctor"
    ]
    
    # Add specific precautions based on symptoms
    if any(s in symptoms for s in ['fever', 'cough', 'cold']):
        precautions.extend([
            "Avoid close contact with others to prevent spread",
            "Cover your mouth when coughing or sneezing",
            "Monitor your symptoms and seek medical help if they worsen"
        ])
    
    return precautions


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_symptoms(
    request: SymptomAnalysisRequest,
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """
    Analyze symptoms and provide disease predictions
    
    - **symptoms**: List of symptom names (required)
    - **severity**: Symptom severity scores 1-10 (optional)
    - **age**: Patient age (optional)
    - **gender**: Patient gender (optional)
    - **medical_history**: Medical history (optional)
    """
    
    start_time = time.time()
    
    try:
        # Check if model is loaded
        model_manager = get_model_manager()
        if not model_manager.is_loaded():
            raise HTTPException(
                status_code=503,
                detail="ML model not loaded. Please try again later."
            )
        
        # Prepare context
        context = {}
        if request.age:
            context['age'] = request.age
        if request.gender:
            context['gender'] = request.gender
        if request.medical_history:
            context['medical_history'] = request.medical_history
        
        # Make prediction
        predictions, explanation = await prediction_service.predict(
            symptoms=request.symptoms,
            severity=request.severity,
            context=context if context else None
        )
        
        if not predictions:
            raise HTTPException(
                status_code=400,
                detail="Unable to make prediction. Please check your symptoms."
            )
        
        # Get primary prediction
        primary = predictions[0]
        
        # Get recommendations and precautions
        recommendations = get_recommendations(primary.disease, request.symptoms)
        precautions = get_precautions(primary.disease, request.symptoms)
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Get model metadata
        metadata = model_manager.get_metadata()
        
        response = AnalysisResponse(
            predictions=predictions,
            primary_prediction=primary,
            recommendations=recommendations,
            precautions=precautions,
            explanation=explanation,
            key_symptoms=explanation.get('key_symptoms', request.symptoms[:5]),
            metadata=ModelMetadata(
                model_version=metadata.get('version', 'unknown'),
                processing_time_ms=processing_time_ms,
                features_used=explanation.get('total_features', 0)
            )
        )
        
        logger.info(
            f"Analysis completed for {len(request.symptoms)} symptoms in {processing_time_ms:.2f}ms"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in symptom analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during analysis: {str(e)}"
        )
