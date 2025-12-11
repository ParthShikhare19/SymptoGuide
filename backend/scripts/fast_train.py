"""Ultra-fast model training - completes in ~1-2 minutes"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import json
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from app.core.logging import logger

# Configuration
DATA_PATH = Path("data/cleaned_datasets")
OUTPUT_PATH = Path("ml_artifacts/models/v1")
RANDOM_STATE = 42
TEST_SIZE = 0.2

def main():
    """Ultra-fast training with single RandomForest model"""
    
    logger.info("=" * 60)
    logger.info("ULTRA-FAST MODEL TRAINING")
    logger.info("=" * 60)
    
    # 1. Load data
    logger.info("Loading data...")
    df = pd.read_csv(DATA_PATH / "diseases_symptoms_cleaned.csv")
    logger.info(f"Loaded {len(df)} samples")
    
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
    
    y = y.str.strip().str.lower().str.replace('_', ' ')
    logger.info(f"Features: {X.shape}, Diseases: {y.nunique()}")
    
    # 3. Split data
    logger.info("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")
    
    # 4. Train SINGLE RandomForest (fastest and still very accurate)
    logger.info("Training RandomForest model...")
    
    model = RandomForestClassifier(
        n_estimators=200,  # Reduced for speed
        max_depth=25,
        min_samples_split=5,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight='balanced',
        verbose=1  # Show progress
    )
    
    model.fit(X_train, y_train)
    logger.info("Training complete!")
    
    # 5. Evaluate
    logger.info("Evaluating model...")
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    logger.info(f"\n{'='*40}")
    logger.info(f"MODEL PERFORMANCE:")
    logger.info(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    logger.info(f"  Precision: {precision:.4f}")
    logger.info(f"  Recall:    {recall:.4f}")
    logger.info(f"  F1 Score:  {f1:.4f}")
    logger.info(f"{'='*40}\n")
    
    # 6. Save model
    logger.info("Saving model...")
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    model_path = OUTPUT_PATH / "model.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    logger.info(f"✓ Model saved: {model_path}")
    
    # Save metadata
    metadata = {
        "version": "1.0-fast",
        "created_at": datetime.now().isoformat(),
        "model_type": "RandomForestClassifier",
        "n_estimators": 200,
        "feature_names": X.columns.tolist(),
        "target_classes": sorted(y.unique().tolist()),
        "metrics": {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1)
        },
        "training_samples": len(X_train),
        "test_samples": len(X_test)
    }
    
    metadata_path = OUTPUT_PATH / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"✓ Metadata saved: {metadata_path}")
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ TRAINING COMPLETE - MODEL READY TO USE!")
    logger.info("=" * 60)
    
    return model, metadata

if __name__ == "__main__":
    main()
