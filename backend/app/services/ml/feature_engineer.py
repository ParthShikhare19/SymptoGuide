"""Advanced Feature Engineering for symptom analysis"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from collections import defaultdict, Counter
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class AdvancedFeatureEngineer:
    """Advanced feature engineering for improved accuracy"""
    
    def __init__(self):
        self.symptom_columns = []
        self.symptom_severity_weights = {}
        self.symptom_idf = {}
        self.symptom_cooccurrence = defaultdict(lambda: defaultdict(int))
        self.interaction_pairs = []
        self.scaler = StandardScaler()
        self.disease_symptom_freq = defaultdict(lambda: defaultdict(int))
        
    def fit(self, df: pd.DataFrame, target_col: str = 'Disease'):
        """
        Fit the feature engineer on training data
        
        Args:
            df: Training dataframe with symptoms and diseases
            target_col: Name of the target column
        """
        logger.info("Fitting feature engineer...")
        
        # Get symptom columns (all columns except Disease)
        self.symptom_columns = [col for col in df.columns if col != target_col]
        logger.info(f"Found {len(self.symptom_columns)} symptom features")
        
        # Calculate IDF for symptoms (how discriminative each symptom is)
        self._calculate_symptom_idf(df, target_col)
        
        # Calculate severity weights based on frequency and discriminative power
        self._calculate_severity_weights(df, target_col)
        
        # Build co-occurrence matrix
        self._build_cooccurrence_matrix(df)
        
        # Calculate disease-symptom frequencies
        self._calculate_disease_frequencies(df, target_col)
        
        # Identify important symptom pairs for interactions
        self._identify_interaction_pairs(df, target_col, top_k=50)
        
        logger.info("Feature engineer fitted successfully")
        
        return self
    
    def _calculate_symptom_idf(self, df: pd.DataFrame, target_col: str):
        """Calculate IDF (Inverse Document Frequency) for each symptom"""
        n_diseases = df[target_col].nunique()
        
        for symptom in self.symptom_columns:
            # Count how many diseases have this symptom
            n_diseases_with_symptom = (df.groupby(target_col)[symptom].sum() > 0).sum()
            
            # IDF formula: log((total_diseases + 1) / (diseases_with_symptom + 1)) + 1
            idf = np.log((n_diseases + 1) / (n_diseases_with_symptom + 1)) + 1
            self.symptom_idf[symptom] = idf
    
    def _calculate_severity_weights(self, df: pd.DataFrame, target_col: str):
        """Calculate weights for symptoms based on multiple factors"""
        for symptom in self.symptom_columns:
            # Factor 1: Overall frequency (rarity bonus)
            freq = df[symptom].sum() / len(df)
            rarity_score = 1 / (freq + 0.01)  # Rare symptoms get higher weight
            
            # Factor 2: IDF score (discriminative power)
            idf_score = self.symptom_idf.get(symptom, 1.0)
            
            # Factor 3: Conditional probability variance across diseases
            disease_probs = df.groupby(target_col)[symptom].mean()
            variance_score = disease_probs.var() if len(disease_probs) > 1 else 0.5
            
            # Combined weight
            weight = (0.3 * rarity_score + 0.4 * idf_score + 0.3 * variance_score)
            self.symptom_severity_weights[symptom] = weight
    
    def _build_cooccurrence_matrix(self, df: pd.DataFrame):
        """Build symptom co-occurrence matrix"""
        for idx, row in df.iterrows():
            active_symptoms = [col for col in self.symptom_columns if row[col] == 1]
            
            # Count co-occurrences
            for i, sym1 in enumerate(active_symptoms):
                for sym2 in active_symptoms[i+1:]:
                    self.symptom_cooccurrence[sym1][sym2] += 1
                    self.symptom_cooccurrence[sym2][sym1] += 1
    
    def _calculate_disease_frequencies(self, df: pd.DataFrame, target_col: str):
        """Calculate symptom frequencies for each disease"""
        for disease in df[target_col].unique():
            disease_df = df[df[target_col] == disease]
            for symptom in self.symptom_columns:
                freq = disease_df[symptom].sum() / len(disease_df)
                self.disease_symptom_freq[disease][symptom] = freq
    
    def _identify_interaction_pairs(self, df: pd.DataFrame, target_col: str, top_k: int = 50):
        """Identify important symptom pairs that frequently occur together"""
        # Score each pair by co-occurrence and discriminative power
        pair_scores = []
        
        for sym1 in self.symptom_columns:
            for sym2 in self.symptom_columns:
                if sym1 >= sym2:  # Avoid duplicates
                    continue
                
                # Co-occurrence count
                cooc_count = self.symptom_cooccurrence[sym1].get(sym2, 0)
                
                if cooc_count > 5:  # Only consider pairs that occur together at least 5 times
                    # Calculate how discriminative this pair is
                    pair_col = df[sym1] * df[sym2]  # Element-wise product
                    if pair_col.sum() > 0:
                        # Variance of this pair across diseases
                        disease_probs = df.groupby(target_col)[sym1].apply(
                            lambda x: (x * df.loc[x.index, sym2]).mean()
                        )
                        variance = disease_probs.var()
                        score = cooc_count * variance
                        pair_scores.append(((sym1, sym2), score))
        
        # Select top_k pairs
        pair_scores.sort(key=lambda x: x[1], reverse=True)
        self.interaction_pairs = [pair for pair, score in pair_scores[:top_k]]
        logger.info(f"Identified {len(self.interaction_pairs)} important interaction pairs")
    
    def transform(self, df: pd.DataFrame, user_severity: Optional[Dict[str, int]] = None) -> pd.DataFrame:
        """
        Transform symptoms dataframe with advanced features
        
        Args:
            df: Dataframe with symptom columns
            user_severity: Optional dict mapping symptom names to severity scores (1-10)
        
        Returns:
            Enhanced dataframe with additional features
        """
        # Store original index to maintain alignment
        original_index = df.index
        original_len = len(df)
        
        df_enhanced = df.copy()
        
        # 1. Severity-weighted features
        for symptom in self.symptom_columns:
            if symptom in df_enhanced.columns:
                weight = self.symptom_severity_weights.get(symptom, 1.0)
                
                # Apply user severity if provided
                if user_severity and symptom in user_severity:
                    severity_multiplier = user_severity[symptom] / 5.0  # Normalize to ~1.0
                    df_enhanced[symptom] = df_enhanced[symptom] * weight * severity_multiplier
                else:
                    df_enhanced[symptom] = df_enhanced[symptom] * weight
        
        # 2. Add interaction features (symptom pairs)
        for sym1, sym2 in self.interaction_pairs:
            if sym1 in df_enhanced.columns and sym2 in df_enhanced.columns:
                interaction_col = f"{sym1}_{sym2}_interaction"
                df_enhanced[interaction_col] = df_enhanced[sym1] * df_enhanced[sym2]
        
        # 3. Add aggregate features
        if len(self.symptom_columns) > 0:
            symptom_cols = [col for col in self.symptom_columns if col in df_enhanced.columns]
            
            # Total symptom count
            df_enhanced['symptom_count'] = df_enhanced[symptom_cols].sum(axis=1)
            
            # Average severity (weighted)
            df_enhanced['avg_severity'] = df_enhanced[symptom_cols].mean(axis=1)
            
            # Max severity
            df_enhanced['max_severity'] = df_enhanced[symptom_cols].max(axis=1)
            
            # Symptom diversity (how spread out the symptoms are)
            df_enhanced['symptom_std'] = df_enhanced[symptom_cols].std(axis=1).fillna(0)
        
        # Verify no row count change occurred
        if len(df_enhanced) != original_len:
            logger.error(f"Transform changed row count from {original_len} to {len(df_enhanced)}")
            raise ValueError(f"Feature engineering altered row count!")
        
        # Ensure index alignment
        df_enhanced.index = original_index
        
        return df_enhanced
    
    def get_feature_importance(self, symptoms: List[str]) -> List[Tuple[str, float]]:
        """Get importance scores for given symptoms"""
        importance_scores = []
        
        for symptom in symptoms:
            weight = self.symptom_severity_weights.get(symptom, 0.5)
            idf = self.symptom_idf.get(symptom, 1.0)
            combined_score = weight * idf
            importance_scores.append((symptom, combined_score))
        
        # Sort by importance (highest first)
        importance_scores.sort(key=lambda x: x[1], reverse=True)
        return importance_scores
    
    def get_related_symptoms(self, symptom: str, top_k: int = 5) -> List[Tuple[str, int]]:
        """Get symptoms that commonly co-occur with the given symptom"""
        if symptom not in self.symptom_cooccurrence:
            return []
        
        cooc = self.symptom_cooccurrence[symptom]
        related = sorted(cooc.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return related
    
    def fit_transform(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """
        Fit the feature engineer and transform the training data
        
        Args:
            X: Training features (symptoms)
            y: Training target (diseases)
        
        Returns:
            Enhanced features
        """
        # Combine X and y for fitting
        df_combined = X.copy()
        df_combined['Disease'] = y.values if isinstance(y, pd.Series) else y
        
        # Fit the feature engineer
        self.fit(df_combined, target_col='Disease')
        
        # Transform X only (without the Disease column)
        X_transformed = self.transform(X)
        
        # Store feature names for later use
        self.feature_names = list(X_transformed.columns)
        
        logger.info(f"fit_transform: Input shape {X.shape} -> Output shape {X_transformed.shape}")
        
        # Verify row count hasn't changed
        if len(X_transformed) != len(X):
            logger.error(f"Row count mismatch! Input: {len(X)}, Output: {len(X_transformed)}")
            raise ValueError(f"Feature engineering changed row count from {len(X)} to {len(X_transformed)}")
        
        return X_transformed
