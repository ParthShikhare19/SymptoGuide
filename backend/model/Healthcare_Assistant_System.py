import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Get the directory where this script is located
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class HealthcareAssistant:
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.symptom_columns = []
        self.all_symptoms = set()
        self.severity_map = {}
        self.disease_info = {}
        self.precautions_map = {}
        self.medications_map = {}
        self.diets_map = {}
        self.workouts_map = {}
        self.description_map = {}
        self.disease_column = None  # Will detect automatically
        
    def load_cleaned_data(self):
        """Load all cleaned datasets"""
        # Path relative to model/ folder - using absolute path based on script location
        folder = os.path.join(_SCRIPT_DIR, "..", "data", "cleaned_datasets")
        
        print("📂 Loading cleaned datasets...")
        
        # Load main disease-symptom dataset
        try:
            self.df_main = pd.read_csv(f"{folder}/diseases_symptoms_cleaned.csv")
            print(f"   ✅ Loaded diseases_symptoms: {self.df_main.shape}")
            print(f"   Sample columns: {list(self.df_main.columns[:5])}")
            
            # Detect disease column name
            possible_disease_cols = ['Disease', 'diseases', 'disease', 'DISEASE', 'Disease_clean']
            for col in possible_disease_cols:
                if col in self.df_main.columns:
                    self.disease_column = col
                    print(f"   📋 Disease column detected: '{self.disease_column}'")
                    break
            
            if not self.disease_column:
                print(f"   ❌ Could not find disease column in: {list(self.df_main.columns[:10])}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error loading diseases_symptoms: {e}")
            return False
        
        # Load symptom severity
        try:
            self.df_severity = pd.read_csv(f"{folder}/symptom_severity_cleaned.csv")
            print(f"   ✅ Loaded symptom_severity: {self.df_severity.shape}")
            
            # Create severity map
            if 'Symptom' in self.df_severity.columns:
                severity_col = [col for col in self.df_severity.columns 
                              if 'weight' in col.lower() or 'severity' in col.lower()][0]
                self.severity_map = dict(zip(
                    self.df_severity['Symptom'].str.lower().str.replace(' ', '_'),
                    self.df_severity[severity_col]
                ))
        except Exception as e:
            print(f"   ⚠️ Warning: Could not load symptom_severity: {e}")
        
        # Load disease descriptions
        try:
            self.df_description = pd.read_csv(f"{folder}/disease_description_cleaned.csv")
            print(f"   ✅ Loaded disease_description: {self.df_description.shape}")
            
            # Find disease column in description
            desc_disease_col = None
            for col in ['Disease', 'diseases', 'disease']:
                if col in self.df_description.columns:
                    desc_disease_col = col
                    break
            
            if desc_disease_col and 'Description' in self.df_description.columns:
                self.description_map = dict(zip(
                    self.df_description[desc_disease_col].str.strip().str.lower(),
                    self.df_description['Description']
                ))
        except Exception as e:
            print(f"   ⚠️ Warning: Could not load disease_description: {e}")
        
        # Load precautions
        try:
            self.df_precautions = pd.read_csv(f"{folder}/precautions_cleaned.csv")
            print(f"   ✅ Loaded precautions: {self.df_precautions.shape}")
            
            # Find disease column
            prec_disease_col = None
            for col in ['Disease', 'diseases', 'disease']:
                if col in self.df_precautions.columns:
                    prec_disease_col = col
                    break
            
            if prec_disease_col:
                precaution_cols = [col for col in self.df_precautions.columns if 'Precaution' in col]
                for _, row in self.df_precautions.iterrows():
                    disease = row[prec_disease_col]
                    precautions = [row[col] for col in precaution_cols if pd.notna(row[col]) and row[col] != '']
                    self.precautions_map[disease.lower()] = precautions
        except Exception as e:
            print(f"   ⚠️ Warning: Could not load precautions: {e}")
        
        # Load medications
        try:
            self.df_medications = pd.read_csv(f"{folder}/medications_cleaned.csv")
            print(f"   ✅ Loaded medications: {self.df_medications.shape}")
            
            # Find disease column
            med_disease_col = None
            for col in ['Disease', 'diseases', 'disease']:
                if col in self.df_medications.columns:
                    med_disease_col = col
                    break
            
            if med_disease_col:
                med_cols = [col for col in self.df_medications.columns if col not in ['Disease', 'diseases', 'disease', 'Disease_clean']]
                if med_cols:
                    self.medications_map = dict(zip(
                        self.df_medications[med_disease_col].str.lower(),
                        self.df_medications[med_cols[0]]
                    ))
        except Exception as e:
            print(f"   ⚠️ Warning: Could not load medications: {e}")
        
        # Load diets
        try:
            self.df_diets = pd.read_csv(f"{folder}/diets_cleaned.csv")
            print(f"   ✅ Loaded diets: {self.df_diets.shape}")
            
            # Find disease column
            diet_disease_col = None
            for col in ['Disease', 'diseases', 'disease']:
                if col in self.df_diets.columns:
                    diet_disease_col = col
                    break
            
            if diet_disease_col:
                diet_cols = [col for col in self.df_diets.columns if col not in ['Disease', 'diseases', 'disease', 'Disease_clean']]
                if diet_cols:
                    self.diets_map = dict(zip(
                        self.df_diets[diet_disease_col].str.lower(),
                        self.df_diets[diet_cols[0]]
                    ))
        except Exception as e:
            print(f"   ⚠️ Warning: Could not load diets: {e}")
        
        # Load workouts
        try:
            self.df_workouts = pd.read_csv(f"{folder}/workouts_cleaned.csv")
            print(f"   ✅ Loaded workouts: {self.df_workouts.shape}")
            
            # Find disease column
            workout_disease_col = None
            for col in ['Disease', 'diseases', 'disease']:
                if col in self.df_workouts.columns:
                    workout_disease_col = col
                    break
            
            if workout_disease_col:
                workout_cols = [col for col in self.df_workouts.columns if col not in ['Disease', 'diseases', 'disease', 'Disease_clean']]
                if workout_cols:
                    self.workouts_map = dict(zip(
                        self.df_workouts[workout_disease_col].str.lower(),
                        self.df_workouts[workout_cols[0]]
                    ))
        except Exception as e:
            print(f"   ⚠️ Warning: Could not load workouts: {e}")
        
        return True
    
    def prepare_training_data(self):
        """Prepare data for model training"""
        print("\n🔨 Preparing training data...")
        
        # Identify symptom columns (exclude Disease and Disease_clean)
        exclude_cols = [self.disease_column, 'Disease_clean', 'diseases', 'Disease', 'disease']
        self.symptom_columns = [col for col in self.df_main.columns if col not in exclude_cols]
        
        print(f"   Found {len(self.symptom_columns)} symptom columns")
        
        # Inspect data type
        sample_values = []
        for col in self.symptom_columns[:5]:
            sample_val = self.df_main[col].iloc[0]
            sample_values.append(f"{col}: {type(sample_val).__name__} = {sample_val}")
        print(f"   Sample values: {sample_values[:2]}")
        
        # Collect all unique symptoms
        for col in self.symptom_columns:
            # Handle both string and numeric data
            unique_vals = self.df_main[col].dropna().unique()
            for val in unique_vals:
                if val != '' and not pd.isna(val):
                    # Convert to string and process
                    if isinstance(val, (int, float, np.integer, np.floating)):
                        # If numeric, use column name as symptom
                        symptom = col.lower().replace(' ', '_')
                    else:
                        # If string, use the value
                        symptom = str(val).lower().replace(' ', '_')
                    
                    self.all_symptoms.add(symptom)
        
        print(f"   Total unique symptoms: {len(self.all_symptoms)}")
        
        # Create binary feature matrix
        X = []
        y = []
        
        for _, row in self.df_main.iterrows():
            if pd.isna(row[self.disease_column]):
                continue
                
            disease = row[self.disease_column]
            
            # Get symptoms for this disease
            symptoms = []
            for col in self.symptom_columns:
                val = row[col]
                if pd.notna(val) and val != '':
                    # Check if value indicates presence of symptom
                    if isinstance(val, (int, float, np.integer, np.floating)):
                        if val == 1 or val > 0:  # Binary indicator
                            symptom = col.lower().replace(' ', '_')
                            symptoms.append(symptom)
                    else:
                        symptom = str(val).lower().replace(' ', '_')
                        symptoms.append(symptom)
            
            if len(symptoms) == 0:
                continue
            
            # Create binary vector
            feature_vector = [1 if symptom in symptoms else 0 for symptom in sorted(self.all_symptoms)]
            
            X.append(feature_vector)
            y.append(disease)
        
        self.X = np.array(X)
        self.y = np.array(y)
        
        print(f"   Training data shape: {self.X.shape}")
        print(f"   Number of diseases: {len(set(self.y))}")
        print(f"   Number of samples: {len(self.y)}")
        
        return self.X, self.y
    
    def train_model(self):
        """Train the disease prediction model"""
        print("\n🤖 Training model...")
        
        if len(self.y) == 0:
            print("   ❌ No training data available!")
            return 0
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(self.y)
        
        # Check if we have enough samples for train-test split
        unique_classes = len(set(y_encoded))
        if len(y_encoded) < 10 or unique_classes < 2:
            print(f"   ⚠️ Warning: Limited data - {len(y_encoded)} samples, {unique_classes} classes")
            # Train on all data
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(self.X, y_encoded)
            print(f"   ✅ Model trained on all data (no test split due to limited samples)")
            return 1.0
        
        # Split data
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                self.X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )
        except ValueError:
            # If stratify fails, try without it
            X_train, X_test, y_train, y_test = train_test_split(
                self.X, y_encoded, test_size=0.2, random_state=42
            )
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"   ✅ Model trained successfully!")
        print(f"   Accuracy: {accuracy:.2%}")
        
        return accuracy
    
    def predict_disease(self, user_symptoms):
        """Predict disease from user symptoms"""
        # Convert symptoms to lowercase and replace spaces
        user_symptoms = [s.lower().strip().replace(' ', '_') for s in user_symptoms]
        
        # Create feature vector
        feature_vector = [1 if symptom in user_symptoms else 0 for symptom in sorted(self.all_symptoms)]
        feature_vector = np.array(feature_vector).reshape(1, -1)
        
        # Predict
        prediction = self.model.predict(feature_vector)[0]
        probabilities = self.model.predict_proba(feature_vector)[0]
        
        # Get disease name
        disease = self.label_encoder.inverse_transform([prediction])[0]
        confidence = probabilities[prediction]
        
        # Get top 3 predictions
        top_n = min(3, len(probabilities))
        top_n_idx = np.argsort(probabilities)[-top_n:][::-1]
        top_n_diseases = self.label_encoder.inverse_transform(top_n_idx)
        top_n_probs = probabilities[top_n_idx]
        
        return disease, confidence, list(zip(top_n_diseases, top_n_probs))
    
    def calculate_severity(self, symptoms):
        """Calculate severity score from symptoms"""
        severity_score = 0
        symptom_severities = []
        
        for symptom in symptoms:
            symptom_clean = symptom.lower().strip().replace(' ', '_')
            severity = self.severity_map.get(symptom_clean, 1)  # Default severity = 1
            severity_score += severity
            symptom_severities.append((symptom, severity))
        
        avg_severity = severity_score / len(symptoms) if symptoms else 0
        
        return severity_score, avg_severity, symptom_severities
    
    def is_emergency(self, symptoms, severity_score):
        """Determine if symptoms indicate emergency"""
        emergency_symptoms = [
            'chest_pain', 'difficulty_breathing', 'severe_headache',
            'sudden_numbness', 'confusion', 'severe_bleeding',
            'unconsciousness', 'heart_attack', 'stroke', 'seizure',
            'high_fever', 'severe_abdominal_pain', 'blurred_vision',
            'slurred_speech', 'weakness', 'paralysis'
        ]
        
        # Check for emergency symptoms
        user_symptoms_clean = [s.lower().strip().replace(' ', '_') for s in symptoms]
        has_emergency_symptom = any(es in user_symptoms_clean for es in emergency_symptoms)
        
        # High severity score
        high_severity = severity_score > 20
        
        return has_emergency_symptom or high_severity
    
    def get_specialist_recommendation(self, disease):
        """Recommend medical specialist based on disease"""
        specialist_map = {
            'fungal': 'Dermatologist',
            'allergy': 'Allergist',
            'gerd': 'Gastroenterologist',
            'diabetes': 'Endocrinologist',
            'migraine': 'Neurologist',
            'arthritis': 'Rheumatologist',
            'hypertension': 'Cardiologist',
            'pneumonia': 'Pulmonologist',
            'hepatitis': 'Hepatologist',
            'jaundice': 'Hepatologist',
            'malaria': 'Infectious Disease Specialist',
            'dengue': 'Infectious Disease Specialist',
            'typhoid': 'Infectious Disease Specialist',
            'tuberculosis': 'Pulmonologist',
            'asthma': 'Pulmonologist',
            'heart': 'Cardiologist',
            'kidney': 'Nephrologist',
            'liver': 'Hepatologist',
            'stomach': 'Gastroenterologist',
            'skin': 'Dermatologist',
            'brain': 'Neurologist',
            'bone': 'Orthopedist',
            'blood': 'Hematologist',
            'mental': 'Psychiatrist',
            'eye': 'Ophthalmologist',
            'ear': 'ENT Specialist',
            'infection': 'Infectious Disease Specialist',
            'cold': 'General Physician',
            'flu': 'General Physician',
            'panic': 'Psychiatrist',
            'depression': 'Psychiatrist',
            'anxiety': 'Psychiatrist'
        }
        
        disease_lower = disease.lower()
        for keyword, specialist in specialist_map.items():
            if keyword in disease_lower:
                return specialist
        
        return 'General Physician'
    
    def get_comprehensive_assessment(self, symptoms):
        """Get comprehensive health assessment"""
        # Predict disease
        disease, confidence, top_3 = self.predict_disease(symptoms)
        
        # Calculate severity
        severity_score, avg_severity, symptom_severities = self.calculate_severity(symptoms)
        
        # Check for emergency
        emergency = self.is_emergency(symptoms, severity_score)
        
        # Get recommendations (use lowercase for lookups)
        specialist = self.get_specialist_recommendation(disease)
        description = self.description_map.get(disease.lower(), "No description available")
        precautions = self.precautions_map.get(disease.lower(), [])
        medications = self.medications_map.get(disease.lower(), "Consult a doctor")
        diet = self.diets_map.get(disease.lower(), "Maintain a balanced diet")
        workout = self.workouts_map.get(disease.lower(), "Consult a doctor before exercising")
        
        # Compile assessment
        assessment = {
            'predicted_disease': disease,
            'confidence': confidence,
            'top_3_predictions': top_3,
            'severity_score': severity_score,
            'average_severity': avg_severity,
            'symptom_severities': symptom_severities,
            'is_emergency': emergency,
            'recommended_specialist': specialist,
            'description': description,
            'precautions': precautions,
            'medications': medications,
            'diet_recommendations': diet,
            'workout_recommendations': workout
        }
        
        return assessment
    
    def save_model(self, filename=None):
        """Save trained model and mappings"""
        if filename is None:
            filename = os.path.join(_SCRIPT_DIR, '..', 'healthcare_model.pkl')
        elif not os.path.isabs(filename):
            filename = os.path.join(_SCRIPT_DIR, filename)
            
        model_data = {
            'model': self.model,
            'label_encoder': self.label_encoder,
            'all_symptoms': self.all_symptoms,
            'severity_map': self.severity_map,
            'description_map': self.description_map,
            'precautions_map': self.precautions_map,
            'medications_map': self.medications_map,
            'diets_map': self.diets_map,
            'workouts_map': self.workouts_map,
            'symptom_columns': self.symptom_columns,
            'disease_column': self.disease_column
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\n💾 Model saved to {filename}")
    
    def load_model(self, filename=None):
        """Load trained model and mappings"""
        if filename is None:
            filename = os.path.join(_SCRIPT_DIR, '..', 'healthcare_model.pkl')
        elif not os.path.isabs(filename):
            filename = os.path.join(_SCRIPT_DIR, filename)
            
        with open(filename, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.label_encoder = model_data['label_encoder']
        self.all_symptoms = model_data['all_symptoms']
        self.severity_map = model_data['severity_map']
        self.description_map = model_data['description_map']
        self.precautions_map = model_data['precautions_map']
        self.medications_map = model_data['medications_map']
        self.diets_map = model_data['diets_map']
        self.workouts_map = model_data['workouts_map']
        self.symptom_columns = model_data['symptom_columns']
        self.disease_column = model_data.get('disease_column', 'diseases')
        
        print(f"\n✅ Model loaded from {filename}")

def print_assessment(assessment):
    """Print formatted assessment"""
    print("\n" + "="*80)
    print("HEALTHCARE ASSESSMENT REPORT")
    print("="*80)
    
    print(f"\n🏥 PREDICTED DISEASE: {assessment['predicted_disease']}")
    print(f"   Confidence: {assessment['confidence']:.2%}")
    
    print(f"\n📊 TOP 3 POSSIBLE CONDITIONS:")
    for i, (disease, prob) in enumerate(assessment['top_3_predictions'], 1):
        print(f"   {i}. {disease}: {prob:.2%}")
    
    print(f"\n⚠️  SEVERITY ASSESSMENT:")
    print(f"   Total Severity Score: {assessment['severity_score']}")
    print(f"   Average Severity: {assessment['average_severity']:.2f}")
    
    if assessment['is_emergency']:
        print(f"\n🚨 EMERGENCY ALERT: Please seek immediate medical attention!")
    
    print(f"\n👨‍⚕️ RECOMMENDED SPECIALIST: {assessment['recommended_specialist']}")
    
    print(f"\n📝 DESCRIPTION:")
    print(f"   {assessment['description']}")
    
    if assessment['precautions']:
        print(f"\n🛡️  PRECAUTIONS:")
        for i, precaution in enumerate(assessment['precautions'], 1):
            print(f"   {i}. {precaution}")
    
    print(f"\n💊 MEDICATIONS:")
    print(f"   {assessment['medications']}")
    
    print(f"\n🍽️  DIET RECOMMENDATIONS:")
    print(f"   {assessment['diet_recommendations']}")
    
    print(f"\n🏃 WORKOUT RECOMMENDATIONS:")
    print(f"   {assessment['workout_recommendations']}")
    
    print("\n" + "="*80)
    print("⚠️  DISCLAIMER: This is a preliminary assessment only.")
    print("   Please consult a qualified healthcare professional for proper diagnosis.")
    print("="*80)

def main():
    """Main function to train and test the system"""
    print("="*80)
    print("HEALTHCARE ASSISTANCE SYSTEM - TRAINING")
    print("="*80)
    
    # Initialize assistant
    assistant = HealthcareAssistant()
    
    # Load data
    if not assistant.load_cleaned_data():
        print("\n❌ Failed to load data. Please run clean_datasets.py first.")
        return
    
    # Prepare training data
    assistant.prepare_training_data()
    
    # Train model
    assistant.train_model()
    
    # Save model
    assistant.save_model()
    
    # Test with sample symptoms
    print("\n" + "="*80)
    print("TESTING WITH SAMPLE SYMPTOMS")
    print("="*80)
    
    test_symptoms = ['anxiety_and_nervousness', 'depression', 'shortness_of_breath']
    print(f"\nTest Symptoms: {test_symptoms}")
    
    assessment = assistant.get_comprehensive_assessment(test_symptoms)
    print_assessment(assessment)
    
    print("\n✅ System ready for use!")

if __name__ == "__main__":
    main()