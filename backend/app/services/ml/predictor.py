"""Prediction service with async support"""

import time
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from app.services.ml.model_manager import get_model_manager
from app.core.logging import logger, log_prediction
from app.core.cache import get_cache_manager
from app.models.schemas import PredictionResult, SeverityEnum


class PredictionService:
    """Service for making predictions"""
    
    def __init__(self):
        self.model_manager = get_model_manager()
        self.cache_manager = get_cache_manager()
        self.all_symptoms = self._load_all_symptoms()
    
    def _load_all_symptoms(self) -> List[str]:
        """Load all possible symptoms from feature engineer or model metadata"""
        # Try feature engineer first
        feature_engineer = self.model_manager.get_feature_engineer()
        if feature_engineer and hasattr(feature_engineer, 'symptom_columns'):
            return feature_engineer.symptom_columns
        
        # Fall back to model metadata
        metadata = self.model_manager.get_metadata()
        if metadata and 'feature_names' in metadata:
            logger.info(f"Loaded {len(metadata['feature_names'])} symptoms from model metadata")
            return metadata['feature_names']
        
        logger.warning("No symptom list found - predictions may fail")
        return []
    
    async def predict(
        self,
        symptoms: List[str],
        severity: Optional[Dict[str, int]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[PredictionResult], Dict[str, Any]]:
        """
        Make prediction with caching and feature engineering
        
        Args:
            symptoms: List of symptom names
            severity: Optional severity scores (1-10)
            context: Optional patient context (age, gender, history)
        
        Returns:
            Tuple of (predictions, explanation)
        """
        
        start_time = time.time()
        
        # Check cache
        cache_key = self.cache_manager.generate_cache_key(
            prefix="prediction",
            symptoms=sorted(symptoms),
            severity=severity,
            context=context
        )
        
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            logger.info("Returning cached prediction")
            return cached_result
        
        # Get model and feature engineer
        model = self.model_manager.get_model()
        feature_engineer = self.model_manager.get_feature_engineer()
        
        if model is None:
            raise ValueError("Model not loaded")
        
        # Prepare features
        X = self._prepare_features(symptoms, severity)
        
        # Apply feature engineering
        if feature_engineer:
            X_transformed = feature_engineer.transform(X)
        else:
            X_transformed = X
        
        # Make prediction
        try:
            # Get probabilities
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(X_transformed)[0]
                predictions = model.predict(X_transformed)[0]
            else:
                predictions = model.predict(X_transformed)[0]
                probabilities = np.array([1.0])
            
            # Get class names
            if hasattr(model, 'classes_'):
                classes = model.classes_
            else:
                classes = [predictions]
            
            # Create prediction results
            results = self._format_predictions(
                classes,
                probabilities,
                top_k=5
            )
            
            # Create explanation
            explanation = self._create_explanation(
                X_transformed,
                symptoms,
                feature_engineer
            )
            
            # Calculate processing time
            duration_ms = (time.time() - start_time) * 1000
            
            # Log prediction
            if results:
                log_prediction(
                    symptoms=symptoms,
                    prediction=results[0].disease,
                    confidence=results[0].confidence,
                    duration_ms=duration_ms
                )
            
            # Cache result
            result = (results, explanation)
            await self.cache_manager.set(cache_key, result, ttl=3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {e}", exc_info=True)
            raise
    
    def _prepare_features(
        self,
        symptoms: List[str],
        severity: Optional[Dict[str, int]] = None
    ) -> pd.DataFrame:
        """Prepare feature vector from symptoms"""
        
        # Normalize input symptoms (lowercase, strip)
        normalized_symptoms = [s.strip().lower() for s in symptoms]
        
        # Create feature vector with all symptoms
        features = {}
        
        if self.all_symptoms:
            # Use known symptoms from training
            for symptom in self.all_symptoms:
                symptom_normalized = symptom.lower()
                
                # Check if this symptom is present
                if symptom_normalized in normalized_symptoms:
                    # Use severity if provided, otherwise 1
                    if severity and symptom in severity:
                        features[symptom] = severity[symptom] / 10.0  # Normalize to 0-1
                    else:
                        features[symptom] = 1
                else:
                    features[symptom] = 0
            
            logger.info(f"Prepared features for {len(normalized_symptoms)} symptoms out of {len(self.all_symptoms)} total")
        else:
            # Fallback: just use provided symptoms
            logger.warning("No symptom list available, using provided symptoms only")
            for symptom in symptoms:
                if severity and symptom in severity:
                    features[symptom] = severity[symptom] / 10.0
                else:
                    features[symptom] = 1
        
        return pd.DataFrame([features])
    
    def _format_predictions(
        self,
        classes: np.ndarray,
        probabilities: np.ndarray,
        top_k: int = 5
    ) -> List[PredictionResult]:
        """Format predictions into response format"""
        
        # Get top k predictions
        top_indices = np.argsort(probabilities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            prob = float(probabilities[idx])
            
            # Skip very low probability predictions
            if prob < 0.01:
                continue
            
            # Estimate severity based on probability and disease name
            severity_level = self._estimate_severity(
                str(classes[idx]),
                prob
            )
            
            result = PredictionResult(
                disease=str(classes[idx]).replace('_', ' ').title(),
                confidence=prob,
                probability=prob,
                severity_level=severity_level
            )
            results.append(result)
        
        return results
    
    def _estimate_severity(self, disease: str, confidence: float) -> SeverityEnum:
        """Estimate severity level"""
        
        # Keywords for severity estimation
        severe_keywords = ['cancer', 'heart attack', 'stroke', 'failure', 'sepsis']
        moderate_keywords = ['infection', 'pneumonia', 'bronchitis', 'diabetes']
        
        disease_lower = disease.lower()
        
        if any(keyword in disease_lower for keyword in severe_keywords):
            return SeverityEnum.SEVERE
        elif any(keyword in disease_lower for keyword in moderate_keywords):
            return SeverityEnum.MODERATE
        else:
            return SeverityEnum.MILD
    
    def _create_explanation(
        self,
        X: pd.DataFrame,
        original_symptoms: List[str],
        feature_engineer: Optional[Any]
    ) -> Dict[str, Any]:
        """Create simple explanation of prediction"""
        
        # Get feature importances if available
        model = self.model_manager.get_model()
        
        feature_importance = {}
        
        if hasattr(model, 'feature_importances_'):
            # For tree-based models
            importances = model.feature_importances_
            feature_names = X.columns.tolist()
            
            # Get top features
            top_indices = np.argsort(importances)[::-1][:10]
            for idx in top_indices:
                if idx < len(feature_names):
                    feature_importance[feature_names[idx]] = float(importances[idx])
        
        return {
            "key_symptoms": original_symptoms[:5],  # Top symptoms
            "feature_importance": feature_importance,
            "total_features": len(X.columns),
            "active_symptoms": len([s for s in original_symptoms if s])
        }


def get_prediction_service() -> PredictionService:
    """Get prediction service instance"""
    return PredictionService()
