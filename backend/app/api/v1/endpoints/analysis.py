"""Symptom analysis endpoint"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import time
import pandas as pd
from pathlib import Path

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

# Load medical data
DATA_PATH = Path("data/cleaned_datasets")
try:
    precautions_df = pd.read_csv(DATA_PATH / "precautions_cleaned.csv")
    medications_df = pd.read_csv(DATA_PATH / "medications_cleaned.csv")
    diets_df = pd.read_csv(DATA_PATH / "diets_cleaned.csv")
    workouts_df = pd.read_csv(DATA_PATH / "workouts_cleaned.csv")
    disease_desc_df = pd.read_csv(DATA_PATH / "disease_description_cleaned.csv")
    logger.info("Medical data loaded successfully")
except Exception as e:
    logger.warning(f"Could not load medical data: {e}")
    precautions_df = medications_df = diets_df = workouts_df = disease_desc_df = None


def get_recommendations(disease: str, symptoms: list) -> list:
    """Get health recommendations based on disease"""
    
    recommendations = []
    disease_lower = disease.lower().strip()
    
    # General recommendation
    recommendations.append(
        Recommendation(
            category="general",
            title="Consult a Healthcare Professional",
            description="Please consult with a healthcare provider for proper diagnosis and treatment.",
            priority="high"
        )
    )
    
    # Get medications from CSV
    if medications_df is not None:
        try:
            med_row = medications_df[medications_df['Disease'].str.lower().str.strip() == disease_lower]
            if not med_row.empty:
                medication = med_row.iloc[0]['Medication']
                if pd.notna(medication) and str(medication).strip():
                    recommendations.append(
                        Recommendation(
                            category="medication",
                            title="Recommended Medications",
                            description=str(medication).strip(),
                            priority="high"
                        )
                    )
        except (KeyError, IndexError):
            pass
    
    # Get diet recommendations
    if diets_df is not None:
        try:
            diet_row = diets_df[diets_df['Disease'].str.lower().str.strip() == disease_lower]
            if not diet_row.empty:
                diet = diet_row.iloc[0]['Diet']
                if pd.notna(diet) and str(diet).strip():
                    recommendations.append(
                        Recommendation(
                            category="diet",
                            title="Dietary Recommendations",
                            description=str(diet).strip(),
                            priority="medium"
                        )
                    )
        except (KeyError, IndexError):
            pass
    
    # Get workout recommendations
    if workouts_df is not None:
        try:
            workout_row = workouts_df[workouts_df['Disease'].str.lower().str.strip() == disease_lower]
            if not workout_row.empty:
                workout = workout_row.iloc[0]['Workouts']
                if pd.notna(workout) and str(workout).strip():
                    recommendations.append(
                        Recommendation(
                            category="exercise",
                            title="Exercise Recommendations",
                            description=str(workout).strip(),
                            priority="medium"
                        )
                    )
        except KeyError:
            pass  # Column name might be different
    
    return recommendations


def get_precautions(disease: str, symptoms: list) -> list:
    """Get precautions based on disease"""
    
    precautions = []
    disease_lower = disease.lower().strip()
    
    # Get precautions from CSV
    if precautions_df is not None:
        try:
            prec_row = precautions_df[precautions_df['Disease'].str.lower().str.strip() == disease_lower]
            if not prec_row.empty:
                # Extract all precaution columns
                for col in ['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']:
                    if col in prec_row.columns:
                        prec = prec_row.iloc[0][col]
                        if pd.notna(prec) and str(prec).strip():
                            precautions.append(str(prec).strip())
        except (KeyError, IndexError):
            pass
    
    # Add general precautions if none found
    if not precautions:
        precautions = [
            "Consult a healthcare professional for proper diagnosis",
            "Get adequate rest and sleep",
            "Stay hydrated by drinking plenty of water",
            "Follow prescribed treatment plan"
        ]
    
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
