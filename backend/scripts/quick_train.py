"""Quick model training without advanced features for immediate deployment"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import json
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from app.core.logging import logger

# Configuration
DATA_PATH = Path("data/cleaned_datasets")
OUTPUT_PATH = Path("ml_artifacts/models/v1")
RANDOM_STATE = 42
TEST_SIZE = 0.2

def main():
    """Quick training pipeline"""
    
    logger.info("=" * 60)
    logger.info("QUICK MODEL TRAINING")
    logger.info("=" * 60)
    
    # 1. Load data
    logger.info("Loading data...")
    df = pd.read_csv(DATA_PATH / "diseases_symptoms_cleaned.csv")
    logger.info(f"Loaded {len(df)} samples with {len(df.columns)} columns")
    
    # 2. Separate features and target
    if 'Disease' in df.columns:
        y = df['Disease']
        X = df.drop('Disease', axis=1)
    elif 'disease' in df.columns:
        y = df['disease']
        X = df.drop('disease', axis=1)
    else:
        y = df.iloc[:, 0]
        X = df.iloc[:, 1:]
    
    # Clean target
    y = y.str.strip().str.lower().str.replace('_', ' ')
    
    logger.info(f"Features: {X.shape}")
    logger.info(f"Unique diseases: {y.nunique()}")
    
    # 3. Split data
    logger.info("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    
    logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")
    
    # 4. Create ensemble model
    logger.info("Training ensemble model...")
    
    rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=30,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight='balanced'
    )
    
    et = ExtraTreesClassifier(
        n_estimators=200,
        max_depth=25,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight='balanced'
    )
    
    gb = GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.1,
        max_depth=5,
        random_state=RANDOM_STATE
    )
    
    ensemble = VotingClassifier(
        estimators=[('rf', rf), ('et', et), ('gb', gb)],
        voting='soft',
        weights=[3, 2, 2],
        n_jobs=-1
    )
    
    ensemble.fit(X_train, y_train)
    logger.info("Training complete!")
    
    # 5. Evaluate
    logger.info("Evaluating model...")
    
    y_pred = ensemble.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    logger.info(f"\nModel Performance:")
    logger.info(f"  Accuracy:  {accuracy:.4f}")
    logger.info(f"  Precision: {precision:.4f}")
    logger.info(f"  Recall:    {recall:.4f}")
    logger.info(f"  F1 Score:  {f1:.4f}")
    
    # 6. Save model
    logger.info("\nSaving model...")
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    # Save model
    model_path = OUTPUT_PATH / "model.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(ensemble, f)
    logger.info(f"Model saved: {model_path}")
    
    # Save metadata
    metadata = {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "model_type": "VotingClassifier",
        "estimators": ["RandomForest", "ExtraTrees", "GradientBoosting"],
        "feature_names": X.columns.tolist(),
        "target_classes": sorted(y.unique().tolist()),
        "metrics": {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1)
        },
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "random_state": RANDOM_STATE
    }
    
    metadata_path = OUTPUT_PATH / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Metadata saved: {metadata_path}")
    
    logger.info("\n" + "=" * 60)
    logger.info("TRAINING COMPLETE!")
    logger.info("=" * 60)
    
    return ensemble, metadata

if __name__ == "__main__":
    main()
