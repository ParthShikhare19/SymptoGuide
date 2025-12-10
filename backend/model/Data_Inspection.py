import pandas as pd
import os
from pathlib import Path

# Get the directory where this script is located
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def inspect_all_datasets():
    """Inspect all CSV files in the workspace"""
    
    # Base path for raw data - using absolute path based on script location
    raw_data_base = os.path.join(_SCRIPT_DIR, "..", "data", "raw_data")
    
    datasets = {
        'raw_data': [
            'Diseases_and_Symptoms_dataset.csv',
            'symptom_Description.csv',
            'symptom_precaution.csv',
            'Symptom-severity.csv',
            'description.csv',
            'diets.csv',
            'workout.csv',
            'medications.csv',
            'dataset.csv'
        ],
        'raw_data/Dataset 1': [
            'dataset.csv',
            'symptom_Description.csv',
            'symptom_precaution.csv',
            'Symptom-severity.csv'
        ],
        'raw_data/Dataset 2': [
            'Disease_symptom_and_patient_profile_dataset.csv',
            'disease and symptoms.csv'
        ],
        'raw_data/Dataset 3': [
            'Diseases_and_Symptoms_dataset.csv',
            'description.csv',
            'diets.csv',
            'medications.csv',
            'precautions.csv',
            'workout.csv'
        ]
    }
    
    print("=" * 80)
    print("DATASET INSPECTION REPORT")
    print("=" * 80)
    
    for folder, files in datasets.items():
        print(f"\n{'='*80}")
        print(f"FOLDER: {folder}")
        print(f"{'='*80}")
        
        for file in files:
            try:
                if folder == 'raw_data':
                    filepath = os.path.join(_SCRIPT_DIR, "..", "data", "raw_data", file)
                else:
                    filepath = os.path.join(_SCRIPT_DIR, "..", "data", folder, file)
                
                if os.path.exists(filepath):
                    df = pd.read_csv(filepath)
                    print(f"\n📁 File: {filepath}")
                    print(f"   Shape: {df.shape}")
                    print(f"   Columns: {list(df.columns)}")
                    print(f"   Null values:\n{df.isnull().sum()}")
                    print(f"   First row sample:\n{df.head(1)}")
                else:
                    print(f"\n❌ File not found: {filepath}")
            except Exception as e:
                print(f"\n❌ Error reading {filepath}: {str(e)}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    inspect_all_datasets()