import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import re
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

# Get the directory where this script is located
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
except:
    pass

# Initialize lemmatizer
wl = WordNetLemmatizer()

def clean_text(text):
    """Clean text data for symptom/disease names"""
    if pd.isna(text) or text == '':
        return ""
    
    text = str(text).lower()
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    try:
        # Tokenize
        tokens = word_tokenize(text)
        # Remove stopwords
        tokens = [t for t in tokens if t not in stopwords.words("english")]
        # Lemmatize
        tokens = [wl.lemmatize(t) for t in tokens]
        return " ".join(tokens)
    except:
        return text

def clean_symptom_column(text):
    """Clean symptom names - keep underscores, convert to lowercase"""
    if pd.isna(text) or text == '':
        return ""
    text = str(text).strip().lower()
    text = text.replace(' ', '_')
    return text

def create_cleaned_folder():
    """Create folder for cleaned datasets"""
    cleaned_folder = os.path.join(_SCRIPT_DIR, "..", "data", "cleaned_datasets")
    if not os.path.exists(cleaned_folder):
        os.makedirs(cleaned_folder)
    return cleaned_folder

def clean_diseases_symptoms(filepath, output_folder):
    """Clean disease-symptom dataset"""
    try:
        df = pd.read_csv(filepath)
        print(f"\n🔍 Cleaning: {filepath}")
        print(f"   Original shape: {df.shape}")
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Clean disease names if 'Disease' column exists
        if 'Disease' in df.columns:
            df['Disease'] = df['Disease'].str.strip()
            df['Disease_clean'] = df['Disease'].apply(clean_text)
        
        # Clean all symptom columns
        symptom_cols = [col for col in df.columns if 'Symptom' in col or col.startswith('S')]
        for col in symptom_cols:
            if col != 'Disease':
                df[col] = df[col].apply(clean_symptom_column)
                # Replace empty strings with NaN
                df[col] = df[col].replace('', np.nan)
        
        # Save cleaned dataset
        output_path = os.path.join(output_folder, "diseases_symptoms_cleaned.csv")
        df.to_csv(output_path, index=False)
        print(f"   ✅ Cleaned shape: {df.shape}")
        print(f"   ✅ Saved to: {output_path}")
        return df
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def clean_symptom_description(filepath, output_folder):
    """Clean symptom description dataset"""
    try:
        df = pd.read_csv(filepath)
        print(f"\n🔍 Cleaning: {filepath}")
        print(f"   Original shape: {df.shape}")
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Clean symptom names
        if 'Symptom' in df.columns:
            df['Symptom'] = df['Symptom'].str.strip()
            df['Symptom_clean'] = df['Symptom'].apply(clean_symptom_column)
        
        # Clean description
        if 'Description' in df.columns:
            df['Description'] = df['Description'].fillna('')
            df['Description'] = df['Description'].str.strip()
        
        # Remove rows with empty descriptions
        if 'Description' in df.columns:
            df = df[df['Description'] != '']
        
        # Save cleaned dataset
        output_path = os.path.join(output_folder, "symptom_description_cleaned.csv")
        df.to_csv(output_path, index=False)
        print(f"   ✅ Cleaned shape: {df.shape}")
        print(f"   ✅ Saved to: {output_path}")
        return df
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def clean_symptom_severity(filepath, output_folder):
    """Clean symptom severity dataset"""
    try:
        df = pd.read_csv(filepath)
        print(f"\n🔍 Cleaning: {filepath}")
        print(f"   Original shape: {df.shape}")
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Clean symptom names
        if 'Symptom' in df.columns:
            df['Symptom'] = df['Symptom'].str.strip()
            df['Symptom_clean'] = df['Symptom'].apply(clean_symptom_column)
        
        # Clean weight/severity column
        severity_col = [col for col in df.columns if 'weight' in col.lower() or 'severity' in col.lower()]
        if severity_col:
            df[severity_col[0]] = pd.to_numeric(df[severity_col[0]], errors='coerce')
            df = df.dropna(subset=severity_col)
        
        # Remove duplicates based on symptom
        if 'Symptom' in df.columns:
            df = df.drop_duplicates(subset=['Symptom'], keep='first')
        
        # Save cleaned dataset
        output_path = os.path.join(output_folder, "symptom_severity_cleaned.csv")
        df.to_csv(output_path, index=False)
        print(f"   ✅ Cleaned shape: {df.shape}")
        print(f"   ✅ Saved to: {output_path}")
        return df
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def clean_precautions(filepath, output_folder):
    """Clean precautions dataset"""
    try:
        df = pd.read_csv(filepath)
        print(f"\n🔍 Cleaning: {filepath}")
        print(f"   Original shape: {df.shape}")
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Clean disease names
        if 'Disease' in df.columns:
            df['Disease'] = df['Disease'].str.strip()
            df['Disease_clean'] = df['Disease'].apply(clean_text)
        
        # Clean precaution columns
        precaution_cols = [col for col in df.columns if 'Precaution' in col]
        for col in precaution_cols:
            df[col] = df[col].fillna('')
            df[col] = df[col].str.strip()
        
        # Save cleaned dataset
        output_path = os.path.join(output_folder, "precautions_cleaned.csv")
        df.to_csv(output_path, index=False)
        print(f"   ✅ Cleaned shape: {df.shape}")
        print(f"   ✅ Saved to: {output_path}")
        return df
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def clean_disease_description(filepath, output_folder):
    """Clean disease description dataset"""
    try:
        df = pd.read_csv(filepath)
        print(f"\n🔍 Cleaning: {filepath}")
        print(f"   Original shape: {df.shape}")
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Clean disease names
        if 'Disease' in df.columns:
            df['Disease'] = df['Disease'].str.strip()
            df['Disease_clean'] = df['Disease'].apply(clean_text)
        
        # Clean description
        if 'Description' in df.columns:
            df['Description'] = df['Description'].fillna('')
            df['Description'] = df['Description'].str.strip()
        
        # Save cleaned dataset
        output_path = os.path.join(output_folder, "disease_description_cleaned.csv")
        df.to_csv(output_path, index=False)
        print(f"   ✅ Cleaned shape: {df.shape}")
        print(f"   ✅ Saved to: {output_path}")
        return df
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def clean_generic_dataset(filepath, output_folder, output_name):
    """Clean generic datasets (medications, diets, workouts)"""
    try:
        df = pd.read_csv(filepath)
        print(f"\n🔍 Cleaning: {filepath}")
        print(f"   Original shape: {df.shape}")
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Clean disease column if exists
        if 'Disease' in df.columns:
            df['Disease'] = df['Disease'].str.strip()
            df['Disease_clean'] = df['Disease'].apply(clean_text)
        
        # Clean all text columns
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('')
                df[col] = df[col].str.strip()
        
        # Save cleaned dataset
        output_path = os.path.join(output_folder, output_name)
        df.to_csv(output_path, index=False)
        print(f"   ✅ Cleaned shape: {df.shape}")
        print(f"   ✅ Saved to: {output_path}")
        return df
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None

def main():
    """Main function to clean all datasets"""
    print("=" * 80)
    print("HEALTHCARE DATASET CLEANING PROCESS")
    print("=" * 80)
    
    # Create output folder
    output_folder = create_cleaned_folder()
    print(f"\n📂 Output folder created: {output_folder}")
    
    # Clean all datasets
    datasets_cleaned = {}
    
    # Define raw data path - using absolute path based on script location
    raw_data = os.path.join(_SCRIPT_DIR, "..", "data", "raw_data")
    
    # 1. Clean Diseases and Symptoms (from raw_data)
    if os.path.exists(f"{raw_data}/Diseases_and_Symptoms_dataset.csv"):
        datasets_cleaned['diseases_symptoms'] = clean_diseases_symptoms(
            f"{raw_data}/Diseases_and_Symptoms_dataset.csv", output_folder
        )
    
    # 2. Clean Symptom Description
    if os.path.exists(f"{raw_data}/symptom_Description.csv"):
        datasets_cleaned['symptom_description'] = clean_symptom_description(
            f"{raw_data}/symptom_Description.csv", output_folder
        )
    
    # 3. Clean Symptom Severity
    if os.path.exists(f"{raw_data}/Symptom-severity.csv"):
        datasets_cleaned['symptom_severity'] = clean_symptom_severity(
            f"{raw_data}/Symptom-severity.csv", output_folder
        )
    
    # 4. Clean Precautions
    if os.path.exists(f"{raw_data}/symptom_precaution.csv"):
        datasets_cleaned['precautions'] = clean_precautions(
            f"{raw_data}/symptom_precaution.csv", output_folder
        )
    
    # 5. Clean Disease Description
    if os.path.exists(f"{raw_data}/description.csv"):
        datasets_cleaned['disease_description'] = clean_disease_description(
            f"{raw_data}/description.csv", output_folder
        )
    
    # 6. Clean Medications
    if os.path.exists(f"{raw_data}/medications.csv"):
        datasets_cleaned['medications'] = clean_generic_dataset(
            f"{raw_data}/medications.csv", output_folder, "medications_cleaned.csv"
        )
    
    # 7. Clean Diets
    if os.path.exists(f"{raw_data}/diets.csv"):
        datasets_cleaned['diets'] = clean_generic_dataset(
            f"{raw_data}/diets.csv", output_folder, "diets_cleaned.csv"
        )
    
    # 8. Clean Workouts
    if os.path.exists(f"{raw_data}/workout.csv"):
        datasets_cleaned['workouts'] = clean_generic_dataset(
            f"{raw_data}/workout.csv", output_folder, "workouts_cleaned.csv"
        )
    
    # Clean from Dataset 3 folder (if precautions.csv exists there)
    if os.path.exists(f"{raw_data}/Dataset 3/precautions.csv"):
        datasets_cleaned['precautions_d3'] = clean_precautions(
            f"{raw_data}/Dataset 3/precautions.csv", output_folder
        )
    
    # Clean Disease symptom and patient profile dataset
    if os.path.exists(f"{raw_data}/Dataset 2/Disease_symptom_and_patient_profile_dataset.csv"):
        datasets_cleaned['patient_profile'] = clean_generic_dataset(
            f"{raw_data}/Dataset 2/Disease_symptom_and_patient_profile_dataset.csv", 
            output_folder, 
            "patient_profile_cleaned.csv"
        )
    
    print("\n" + "=" * 80)
    print("CLEANING SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for v in datasets_cleaned.values() if v is not None)
    total = len(datasets_cleaned)
    
    print(f"\n✅ Successfully cleaned: {successful}/{total} datasets")
    print(f"📂 All cleaned files saved in: {output_folder}/")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()