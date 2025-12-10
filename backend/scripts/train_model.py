"""
Advanced model training pipeline with:
- SMOTE for class balancing
- Hyperparameter optimization with Optuna
- Advanced feature engineering
- Cross-validation
- Model persistence
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import json
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    VotingClassifier
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
from imblearn.over_sampling import SMOTE
from imblearn.combine import SMOTETomek
import optuna

from app.services.ml.feature_engine import AdvancedFeatureEngineer
from app.core.logging import logger

# Configuration
DATA_PATH = Path("data/cleaned_datasets")
OUTPUT_PATH = Path("ml_artifacts/models/v1")
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 3
USE_SMOTE = False  # Disable SMOTE for faster training initially
OPTUNA_TRIALS = 10  # Reduced for faster training
ENABLE_HYPERPARAM_TUNING = False  # Use default params for faster initial training


class ImprovedModelTrainer:
    """Improved model trainer with SMOTE and hyperparameter tuning"""
    
    def __init__(self):
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.feature_engineer = None
        self.best_model = None
        self.best_params = {}
        self.metrics = {}
    
    def load_data(self):
        """Load and prepare training data"""
        
        logger.info("Loading training data...")
        
        # Load diseases and symptoms dataset
        df = pd.read_csv(DATA_PATH / "diseases_symptoms_cleaned.csv")
        
        logger.info(f"Loaded {len(df)} samples with {len(df.columns)} columns")
        
        # Separate features and target
        if 'Disease' in df.columns:
            y = df['Disease']
            X = df.drop('Disease', axis=1)
        elif 'disease' in df.columns:
            y = df['disease']
            X = df.drop('disease', axis=1)
        else:
            # Assume first column is disease
            y = df.iloc[:, 0]
            X = df.iloc[:, 1:]
        
        # Clean target labels
        y = y.str.strip().str.lower().str.replace('_', ' ')
        
        logger.info(f"Features shape: {X.shape}")
        logger.info(f"Number of unique diseases: {y.nunique()}")
        logger.info(f"Class distribution:\n{y.value_counts()}")
        
        return X, y
    
    def split_data(self, X, y):
        """Split data into train and test sets"""
        
        logger.info("Splitting data...")
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=y
        )
        
        # Reset indices to ensure alignment
        self.X_train = self.X_train.reset_index(drop=True)
        self.X_test = self.X_test.reset_index(drop=True)
        self.y_train = self.y_train.reset_index(drop=True) if isinstance(self.y_train, pd.Series) else pd.Series(self.y_train).reset_index(drop=True)
        self.y_test = self.y_test.reset_index(drop=True) if isinstance(self.y_test, pd.Series) else pd.Series(self.y_test).reset_index(drop=True)
        
        logger.info(f"Train size: {len(self.X_train)}")
        logger.info(f"Test size: {len(self.X_test)}")
    
    def engineer_features(self):
        """Apply advanced feature engineering"""
        
        logger.info("Engineering features...")
        
        # Create and fit feature engineer
        self.feature_engineer = AdvancedFeatureEngineer()
        self.X_train = self.feature_engineer.fit_transform(self.X_train, self.y_train)
        self.X_test = self.feature_engineer.transform(self.X_test)
        
        # Handle NaN values - fill with 0 (no symptom/feature)
        logger.info("Handling missing values...")
        self.X_train = self.X_train.fillna(0)
        self.X_test = self.X_test.fillna(0)
        
        # Handle infinite values
        self.X_train = self.X_train.replace([np.inf, -np.inf], 0)
        self.X_test = self.X_test.replace([np.inf, -np.inf], 0)
        
        # Verify no NaN or inf values remain
        nan_count = self.X_train.isna().sum().sum()
        inf_count = np.isinf(self.X_train).sum().sum()
        
        if nan_count > 0 or inf_count > 0:
            logger.warning(f"Found {nan_count} NaN and {inf_count} inf values after cleaning")
        
        logger.info(f"Engineered features shape: {self.X_train.shape}")
        logger.info(f"Number of features: {len(self.feature_engineer.feature_names)}")
    
    def balance_classes(self):
        """Balance classes using SMOTE"""
        
        if not USE_SMOTE:
            logger.info("Skipping SMOTE (disabled)")
            return
        
        logger.info("Applying SMOTE for class balancing...")
        
        # Ensure X_train and y_train have same length before SMOTE
        logger.info(f"Before SMOTE - X_train: {len(self.X_train)}, y_train: {len(self.y_train)}")
        
        # Convert to numpy arrays if they're DataFrames/Series
        if isinstance(self.X_train, pd.DataFrame):
            X_train_array = self.X_train.values
        else:
            X_train_array = self.X_train
            
        if isinstance(self.y_train, pd.Series):
            y_train_array = self.y_train.values
        else:
            y_train_array = self.y_train
        
        # Use SMOTETomek for better results (SMOTE + Tomek links removal)
        try:
            smote_tomek = SMOTETomek(random_state=RANDOM_STATE, n_jobs=-1)
            X_resampled, y_resampled = smote_tomek.fit_resample(
                X_train_array,
                y_train_array
            )
            
            # Convert back to DataFrame with proper column names
            if isinstance(self.X_train, pd.DataFrame):
                self.X_train = pd.DataFrame(X_resampled, columns=self.X_train.columns)
            else:
                self.X_train = X_resampled
                
            self.y_train = y_resampled
            
            logger.info(f"After SMOTE - Train size: {len(self.X_train)}")
            logger.info(f"Class distribution:\n{pd.Series(self.y_train).value_counts().head(10)}")
            
        except Exception as e:
            logger.warning(f"SMOTE failed: {e}. Using original data.")
    
    def optimize_hyperparameters(self):
        """Optimize hyperparameters using Optuna"""
        
        if not ENABLE_HYPERPARAM_TUNING:
            logger.info("Using default hyperparameters")
            return self._get_default_params()
        
        logger.info("Optimizing hyperparameters with Optuna...")
        
        def objective(trial):
            """Optuna objective function"""
            
            # Random Forest parameters
            rf_n_estimators = trial.suggest_int('rf_n_estimators', 100, 500)
            rf_max_depth = trial.suggest_int('rf_max_depth', 10, 50)
            rf_min_samples_split = trial.suggest_int('rf_min_samples_split', 2, 20)
            
            # Extra Trees parameters
            et_n_estimators = trial.suggest_int('et_n_estimators', 100, 400)
            et_max_depth = trial.suggest_int('et_max_depth', 10, 40)
            
            # Gradient Boosting parameters
            gb_n_estimators = trial.suggest_int('gb_n_estimators', 50, 200)
            gb_learning_rate = trial.suggest_float('gb_learning_rate', 0.01, 0.3)
            gb_max_depth = trial.suggest_int('gb_max_depth', 3, 10)
            
            # Create ensemble
            rf = RandomForestClassifier(
                n_estimators=rf_n_estimators,
                max_depth=rf_max_depth,
                min_samples_split=rf_min_samples_split,
                random_state=RANDOM_STATE,
                n_jobs=-1,
                class_weight='balanced'
            )
            
            et = ExtraTreesClassifier(
                n_estimators=et_n_estimators,
                max_depth=et_max_depth,
                random_state=RANDOM_STATE,
                n_jobs=-1,
                class_weight='balanced'
            )
            
            gb = GradientBoostingClassifier(
                n_estimators=gb_n_estimators,
                learning_rate=gb_learning_rate,
                max_depth=gb_max_depth,
                random_state=RANDOM_STATE
            )
            
            ensemble = VotingClassifier(
                estimators=[('rf', rf), ('et', et), ('gb', gb)],
                voting='soft',
                weights=[3, 2, 2],
                n_jobs=-1
            )
            
            # Convert to numpy arrays if needed
            X_cv = self.X_train.values if isinstance(self.X_train, pd.DataFrame) else self.X_train
            y_cv = self.y_train if isinstance(self.y_train, (list, np.ndarray)) else self.y_train.values
            
            # Verify shape consistency
            if len(X_cv) != len(y_cv):
                logger.error(f"Shape mismatch: X={len(X_cv)}, y={len(y_cv)}")
                return 0.0
            
            # Cross-validation score
            cv_scores = cross_val_score(
                ensemble,
                X_cv,
                y_cv,
                cv=min(3, CV_FOLDS),  # Use fewer folds for speed
                scoring='f1_weighted',
                n_jobs=-1
            )
            
            return cv_scores.mean()
        
        # Create study
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=OPTUNA_TRIALS, show_progress_bar=True)
        
        logger.info(f"Best trial: {study.best_trial.value}")
        logger.info(f"Best params: {study.best_trial.params}")
        
        self.best_params = study.best_trial.params
        return self.best_params
    
    def _get_default_params(self):
        """Get default parameters"""
        return {
            'rf_n_estimators': 300,
            'rf_max_depth': 30,
            'rf_min_samples_split': 5,
            'et_n_estimators': 200,
            'et_max_depth': 25,
            'gb_n_estimators': 150,
            'gb_learning_rate': 0.1,
            'gb_max_depth': 5
        }
    
    def train_model(self, params=None):
        """Train final model with best parameters"""
        
        if params is None:
            params = self.best_params if self.best_params else self._get_default_params()
        
        logger.info("Training final model...")
        
        # Create models with best parameters
        rf = RandomForestClassifier(
            n_estimators=params.get('rf_n_estimators', 300),
            max_depth=params.get('rf_max_depth', 30),
            min_samples_split=params.get('rf_min_samples_split', 5),
            random_state=RANDOM_STATE,
            n_jobs=-1,
            class_weight='balanced'
        )
        
        et = ExtraTreesClassifier(
            n_estimators=params.get('et_n_estimators', 200),
            max_depth=params.get('et_max_depth', 25),
            random_state=RANDOM_STATE,
            n_jobs=-1,
            class_weight='balanced'
        )
        
        gb = GradientBoostingClassifier(
            n_estimators=params.get('gb_n_estimators', 150),
            learning_rate=params.get('gb_learning_rate', 0.1),
            max_depth=params.get('gb_max_depth', 5),
            random_state=RANDOM_STATE
        )
        
        knn = KNeighborsClassifier(
            n_neighbors=5,
            n_jobs=-1
        )
        
        svc = SVC(
            kernel='rbf',
            probability=True,
            random_state=RANDOM_STATE,
            class_weight='balanced'
        )
        
        # Create voting ensemble
        self.best_model = VotingClassifier(
            estimators=[
                ('rf', rf),
                ('et', et),
                ('gb', gb),
                ('knn', knn),
                ('svc', svc)
            ],
            voting='soft',
            weights=[3, 2, 2, 1, 2],
            n_jobs=-1
        )
        
        # Train model
        self.best_model.fit(self.X_train, self.y_train)
        
        logger.info("Model training completed")
    
    def evaluate_model(self):
        """Evaluate model on test set"""
        
        logger.info("Evaluating model...")
        
        # Predictions
        y_pred = self.best_model.predict(self.X_test)
        y_pred_proba = self.best_model.predict_proba(self.X_test)
        
        # Calculate metrics
        self.metrics = {
            'accuracy': accuracy_score(self.y_test, y_pred),
            'precision_macro': precision_score(self.y_test, y_pred, average='macro', zero_division=0),
            'recall_macro': recall_score(self.y_test, y_pred, average='macro', zero_division=0),
            'f1_macro': f1_score(self.y_test, y_pred, average='macro', zero_division=0),
            'precision_weighted': precision_score(self.y_test, y_pred, average='weighted', zero_division=0),
            'recall_weighted': recall_score(self.y_test, y_pred, average='weighted', zero_division=0),
            'f1_weighted': f1_score(self.y_test, y_pred, average='weighted', zero_division=0),
        }
        
        logger.info(f"\n=== Model Performance ===")
        logger.info(f"Accuracy: {self.metrics['accuracy']:.4f}")
        logger.info(f"Precision (macro): {self.metrics['precision_macro']:.4f}")
        logger.info(f"Recall (macro): {self.metrics['recall_macro']:.4f}")
        logger.info(f"F1 Score (macro): {self.metrics['f1_macro']:.4f}")
        logger.info(f"Precision (weighted): {self.metrics['precision_weighted']:.4f}")
        logger.info(f"Recall (weighted): {self.metrics['recall_weighted']:.4f}")
        logger.info(f"F1 Score (weighted): {self.metrics['f1_weighted']:.4f}")
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.best_model,
            self.X_train,
            self.y_train,
            cv=CV_FOLDS,
            scoring='accuracy',
            n_jobs=-1
        )
        
        logger.info(f"\nCross-Validation Scores: {cv_scores}")
        logger.info(f"CV Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        self.metrics['cv_scores'] = cv_scores.tolist()
        self.metrics['cv_mean'] = cv_scores.mean()
        self.metrics['cv_std'] = cv_scores.std()
        
        return self.metrics
    
    def save_model(self):
        """Save model and artifacts"""
        
        logger.info("Saving model artifacts...")
        
        # Create output directory
        OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
        
        # Save model
        model_file = OUTPUT_PATH / "model.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump(self.best_model, f)
        logger.info(f"Model saved to {model_file}")
        
        # Save feature engineer
        feature_file = OUTPUT_PATH / "feature_engineer.pkl"
        with open(feature_file, 'wb') as f:
            pickle.dump(self.feature_engineer, f)
        logger.info(f"Feature engineer saved to {feature_file}")
        
        # Save metadata
        metadata = {
            'version': 'v1',
            'created_at': datetime.now().isoformat(),
            'training_samples': len(self.X_train),
            'test_samples': len(self.X_test),
            'num_features': self.X_train.shape[1],
            'num_classes': len(self.best_model.classes_),
            'classes': self.best_model.classes_.tolist(),
            'metrics': self.metrics,
            'hyperparameters': self.best_params,
            'use_smote': USE_SMOTE,
            'random_state': RANDOM_STATE
        }
        
        metadata_file = OUTPUT_PATH / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Metadata saved to {metadata_file}")
        
        logger.info("All artifacts saved successfully!")
    
    def run_pipeline(self):
        """Run complete training pipeline"""
        
        logger.info("=" * 60)
        logger.info("Starting model training pipeline")
        logger.info("=" * 60)
        
        # Load data
        X, y = self.load_data()
        
        # Split data
        self.split_data(X, y)
        
        # Engineer features
        self.engineer_features()
        
        # Balance classes
        self.balance_classes()
        
        # Optimize hyperparameters
        params = self.optimize_hyperparameters()
        
        # Train model
        self.train_model(params)
        
        # Evaluate model
        self.evaluate_model()
        
        # Save model
        self.save_model()
        
        logger.info("=" * 60)
        logger.info("Training pipeline completed successfully!")
        logger.info("=" * 60)


if __name__ == "__main__":
    trainer = ImprovedModelTrainer()
    trainer.run_pipeline()
