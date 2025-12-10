"""Advanced feature engineering with symptom interactions and weighting"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from sklearn.preprocessing import StandardScaler
import pickle
import os


class AdvancedFeatureEngineer:
    """Advanced feature engineering for symptom data"""
    
    def __init__(self):
        self.symptom_weights = {}
        self.symptom_cooccurrence = defaultdict(lambda: defaultdict(float))
        self.symptom_idf = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        self.symptom_columns = []
        
    def fit(self, X: pd.DataFrame, y: pd.Series) -> 'AdvancedFeatureEngineer':
        """Fit feature engineer on training data"""
        
        # Store symptom columns
        self.symptom_columns = X.columns.tolist()
        
        # Calculate symptom weights
        self._calculate_symptom_weights(X, y)
        
        # Calculate symptom co-occurrence
        self._calculate_cooccurrence(X)
        
        # Calculate IDF scores
        self._calculate_idf(X)
        
        # Transform data to get feature names
        X_transformed = self.transform(X, y)
        self.feature_names = X_transformed.columns.tolist()
        
        # Fit scaler
        self.scaler.fit(X_transformed)
        
        return self
    
    def transform(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> pd.DataFrame:
        """Transform features with advanced engineering"""
        
        X_new = X.copy()
        
        # 1. Weighted symptoms
        X_weighted = self._apply_symptom_weights(X_new)
        
        # 2. Symptom count features
        X_new['total_symptoms'] = X_new.sum(axis=1)
        X_new['symptom_diversity'] = (X_new > 0).sum(axis=1)
        
        # 3. Co-occurrence features
        X_cooccur = self._create_cooccurrence_features(X_new)
        
        # 4. IDF-weighted features
        X_idf = self._apply_idf_weights(X_new)
        
        # 5. Interaction features (top symptoms only to avoid explosion)
        X_interact = self._create_interaction_features(X_new)
        
        # Combine all features
        result = pd.concat([
            X_new,
            X_weighted,
            X_cooccur,
            X_idf,
            X_interact
        ], axis=1)
        
        return result
    
    def fit_transform(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """Fit and transform in one step"""
        self.fit(X, y)
        return self.transform(X, y)
    
    def _calculate_symptom_weights(self, X: pd.DataFrame, y: pd.Series):
        """Calculate symptom importance weights"""
        
        for symptom in X.columns:
            if X[symptom].sum() == 0:
                self.symptom_weights[symptom] = 0.0
                continue
            
            # Calculate discriminative power
            diseases_with_symptom = y[X[symptom] > 0].unique()
            total_diseases = y.nunique()
            
            # Specificity score: fewer diseases = more specific
            specificity = 1.0 - (len(diseases_with_symptom) / total_diseases)
            
            # Frequency score: moderate frequency is best
            frequency = X[symptom].sum() / len(X)
            frequency_score = 1.0 - abs(frequency - 0.3)  # Prefer ~30% frequency
            
            # Combined weight
            self.symptom_weights[symptom] = (specificity * 0.6 + frequency_score * 0.4)
    
    def _calculate_cooccurrence(self, X: pd.DataFrame):
        """Calculate symptom co-occurrence patterns"""
        
        for idx, row in X.iterrows():
            active_symptoms = [col for col in X.columns if row[col] > 0]
            
            # Count co-occurrences
            for i, sym1 in enumerate(active_symptoms):
                for sym2 in active_symptoms[i+1:]:
                    self.symptom_cooccurrence[sym1][sym2] += 1
                    self.symptom_cooccurrence[sym2][sym1] += 1
    
    def _calculate_idf(self, X: pd.DataFrame):
        """Calculate Inverse Document Frequency for symptoms"""
        
        total_samples = len(X)
        
        for symptom in X.columns:
            doc_freq = (X[symptom] > 0).sum()
            if doc_freq > 0:
                self.symptom_idf[symptom] = np.log((total_samples + 1) / (doc_freq + 1)) + 1
            else:
                self.symptom_idf[symptom] = 1.0
    
    def _apply_symptom_weights(self, X: pd.DataFrame) -> pd.DataFrame:
        """Apply learned symptom weights"""
        
        X_weighted = pd.DataFrame()
        
        for symptom in X.columns:
            weight = self.symptom_weights.get(symptom, 1.0)
            X_weighted[f'{symptom}_weighted'] = X[symptom] * weight
        
        return X_weighted
    
    def _apply_idf_weights(self, X: pd.DataFrame) -> pd.DataFrame:
        """Apply IDF weights to symptoms"""
        
        X_idf = pd.DataFrame()
        
        for symptom in X.columns:
            idf = self.symptom_idf.get(symptom, 1.0)
            X_idf[f'{symptom}_idf'] = X[symptom] * idf
        
        return X_idf
    
    def _create_cooccurrence_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Create co-occurrence strength features"""
        
        cooccur_strength = []
        
        for idx, row in X.iterrows():
            active_symptoms = [col for col in X.columns if row[col] > 0]
            
            # Calculate total co-occurrence strength
            strength = 0.0
            count = 0
            
            for i, sym1 in enumerate(active_symptoms):
                for sym2 in active_symptoms[i+1:]:
                    strength += self.symptom_cooccurrence[sym1].get(sym2, 0)
                    count += 1
            
            avg_strength = strength / count if count > 0 else 0.0
            cooccur_strength.append(avg_strength)
        
        return pd.DataFrame({
            'cooccurrence_strength': cooccur_strength
        })
    
    def _create_interaction_features(self, X: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """Create interaction features for top symptoms"""
        
        # Get top symptoms by weight
        top_symptoms = sorted(
            self.symptom_weights.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        top_symptom_names = [s[0] for s in top_symptoms if s[0] in X.columns]
        
        X_interact = pd.DataFrame()
        
        # Create pairwise interactions
        for i, sym1 in enumerate(top_symptom_names):
            for sym2 in top_symptom_names[i+1:]:
                X_interact[f'{sym1}_x_{sym2}'] = X[sym1] * X[sym2]
        
        return X_interact
    
    def save(self, filepath: str):
        """Save feature engineer"""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(filepath: str) -> 'AdvancedFeatureEngineer':
        """Load feature engineer"""
        with open(filepath, 'rb') as f:
            return pickle.load(f)
