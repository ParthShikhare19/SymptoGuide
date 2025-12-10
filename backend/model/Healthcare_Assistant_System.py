import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier, ExtraTreesClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from difflib import SequenceMatcher
import pickle
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Import feature engineering
from Feature_Engineering import SymptomFeatureEngineer, engineer_features, augment_training_data

# Get the directory where this script is located
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class HealthcareAssistant:
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.feature_engineer = None
        self.symptom_columns = []
        self.all_symptoms = set()
        self.all_symptoms_list = []
        self.severity_map = {}
        self.disease_info = {}
        self.precautions_map = {}
        self.medications_map = {}
        self.diets_map = {}
        self.workouts_map = {}
        self.description_map = {}
        self.disease_column = None
        self.disease_symptom_map = {}
        self.symptom_disease_map = {}
        self.symptom_idf = {}
        self.df_severity = None
        
    def load_cleaned_data(self):
        """Load all cleaned datasets"""
        folder = os.path.join(_SCRIPT_DIR, "..", "data", "cleaned_datasets")
        
        print("📂 Loading cleaned datasets...")
        
        # Load main disease-symptom dataset
        try:
            self.df_main = pd.read_csv(f"{folder}/diseases_symptoms_cleaned.csv")
            print(f"   ✅ Loaded diseases_symptoms: {self.df_main.shape}")
            
            possible_disease_cols = ['Disease', 'diseases', 'disease', 'DISEASE', 'Disease_clean']
            for col in possible_disease_cols:
                if col in self.df_main.columns:
                    self.disease_column = col
                    print(f"   📋 Disease column detected: '{self.disease_column}'")
                    break
            
            if not self.disease_column:
                print(f"   ❌ Could not find disease column")
                return False
                
        except Exception as e:
            print(f"   ❌ Error loading diseases_symptoms: {e}")
            return False
        
        # Load symptom severity
        try:
            self.df_severity = pd.read_csv(f"{folder}/symptom_severity_cleaned.csv")
            print(f"   ✅ Loaded symptom_severity: {self.df_severity.shape}")
            
            if 'Symptom' in self.df_severity.columns:
                severity_col = [col for col in self.df_severity.columns 
                              if 'weight' in col.lower() or 'severity' in col.lower()]
                if severity_col:
                    self.severity_map = dict(zip(
                        self.df_severity['Symptom'].str.lower().str.replace(' ', '_'),
                        self.df_severity[severity_col[0]]
                    ))
        except Exception as e:
            print(f"   ⚠️ Warning: Could not load symptom_severity: {e}")
            self.df_severity = None
        
        # Load disease descriptions
        try:
            self.df_description = pd.read_csv(f"{folder}/disease_description_cleaned.csv")
            print(f"   ✅ Loaded disease_description: {self.df_description.shape}")
            
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
    
    def _normalize_symptom(self, symptom):
        """Normalize symptom string"""
        if pd.isna(symptom) or symptom == '':
            return None
        symptom = str(symptom).lower().strip()
        symptom = symptom.replace(' ', '_').replace('-', '_')
        symptom = ''.join(c for c in symptom if c.isalnum() or c == '_')
        return symptom if symptom else None
    
    def _find_best_symptom_match(self, user_symptom, threshold=0.55):
        """Find best matching symptom with improved fuzzy matching"""
        user_symptom = self._normalize_symptom(user_symptom)
        if not user_symptom:
            return None, 0
        
        # Exact match
        if user_symptom in self.all_symptoms:
            return user_symptom, 1.0
        
        best_match = None
        best_score = 0
        
        for known_symptom in self.all_symptoms:
            # Direct substring match
            if user_symptom in known_symptom:
                score = len(user_symptom) / len(known_symptom) * 0.95
                if score > best_score:
                    best_score = score
                    best_match = known_symptom
                continue
            
            if known_symptom in user_symptom:
                score = len(known_symptom) / len(user_symptom) * 0.95
                if score > best_score:
                    best_score = score
                    best_match = known_symptom
                continue
            
            # Token overlap
            user_tokens = set(user_symptom.split('_'))
            known_tokens = set(known_symptom.split('_'))
            overlap = len(user_tokens & known_tokens)
            if overlap > 0:
                token_score = overlap / max(len(user_tokens), len(known_tokens))
                if token_score > best_score:
                    best_score = token_score
                    best_match = known_symptom
            
            # Sequence matching
            score = SequenceMatcher(None, user_symptom, known_symptom).ratio()
            if score > best_score:
                best_score = score
                best_match = known_symptom
        
        if best_score >= threshold:
            return best_match, best_score
        return None, 0
    
    def prepare_training_data(self):
        """Prepare training data with advanced feature engineering"""
        print("\n🔨 Preparing training data with feature engineering...")
        
        # Identify symptom columns
        exclude_cols = [self.disease_column, 'Disease_clean', 'diseases', 'Disease', 'disease']
        self.symptom_columns = [col for col in self.df_main.columns if col not in exclude_cols]
        
        print(f"   Found {len(self.symptom_columns)} symptom columns")
        
        # Collect symptoms and build mappings
        for _, row in self.df_main.iterrows():
            if pd.isna(row[self.disease_column]):
                continue
            
            disease = str(row[self.disease_column]).lower().strip()
            symptoms_for_disease = set()
            
            for col in self.symptom_columns:
                val = row[col]
                symptom = None
                
                if isinstance(val, str) and val.strip():
                    symptom = self._normalize_symptom(val)
                elif isinstance(val, (int, float, np.integer, np.floating)) and val == 1:
                    symptom = self._normalize_symptom(col)
                
                if symptom:
                    self.all_symptoms.add(symptom)
                    symptoms_for_disease.add(symptom)
                    
                    if symptom not in self.symptom_disease_map:
                        self.symptom_disease_map[symptom] = set()
                    self.symptom_disease_map[symptom].add(disease)
            
            if symptoms_for_disease:
                if disease not in self.disease_symptom_map:
                    self.disease_symptom_map[disease] = set()
                self.disease_symptom_map[disease].update(symptoms_for_disease)
        
        self.all_symptoms_list = sorted(self.all_symptoms)
        
        print(f"   Total unique symptoms: {len(self.all_symptoms)}")
        print(f"   Total diseases: {len(self.disease_symptom_map)}")
        
        # Initialize feature engineer
        self.feature_engineer = engineer_features(
            self.df_main, 
            self.df_severity, 
            self.disease_column, 
            self.symptom_columns
        )
        
        # Create augmented training data
        self.X, self.y = augment_training_data(
            self.disease_symptom_map,
            self.feature_engineer,
            self.all_symptoms_list,
            augmentation_factor=8  # More augmentation for better generalization
        )
        
        # Scale features
        self.X = self.scaler.fit_transform(self.X)
        
        print(f"   Training data shape: {self.X.shape}")
        print(f"   Features per sample: {self.X.shape[1]}")
        
        return self.X, self.y
    
    def train_model(self):
        """Train enhanced ensemble model"""
        print("\n🤖 Training enhanced ensemble model...")
        
        if len(self.y) == 0:
            print("   ❌ No training data!")
            return 0
        
        y_encoded = self.label_encoder.fit_transform(self.y)
        unique_classes = len(set(y_encoded))
        
        print(f"   Classes: {unique_classes}, Samples: {len(y_encoded)}")
        
        # Enhanced ensemble with more diverse models
        rf_clf = RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            max_features='sqrt',
            bootstrap=True,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
        
        et_clf = ExtraTreesClassifier(
            n_estimators=200,
            max_depth=None,
            min_samples_split=2,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
        
        gb_clf = GradientBoostingClassifier(
            n_estimators=150,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            random_state=42
        )
        
        knn_clf = KNeighborsClassifier(
            n_neighbors=5,
            weights='distance',
            metric='euclidean',
            n_jobs=-1
        )
        
        svm_clf = SVC(
            kernel='rbf',
            C=10,
            gamma='scale',
            probability=True,
            random_state=42,
            class_weight='balanced'
        )
        
        # Weighted voting ensemble
        self.model = VotingClassifier(
            estimators=[
                ('rf', rf_clf),
                ('et', et_clf),
                ('gb', gb_clf),
                ('knn', knn_clf),
                ('svm', svm_clf)
            ],
            voting='soft',
            weights=[3, 2, 2, 1, 2]  # RF gets highest weight
        )
        
        # Cross-validation
        if len(y_encoded) >= 10 and unique_classes >= 2:
            try:
                min_class_count = min(np.bincount(y_encoded))
                n_splits = min(5, min_class_count)
                if n_splits >= 2:
                    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
                    cv_scores = cross_val_score(self.model, self.X, y_encoded, cv=skf, scoring='accuracy')
                    print(f"   📊 Cross-validation scores: {cv_scores}")
                    print(f"   📊 Mean CV accuracy: {cv_scores.mean():.2%} (+/- {cv_scores.std() * 2:.2%})")
            except Exception as e:
                print(f"   ⚠️ CV error: {e}")
        
        # Train on full data
        self.model.fit(self.X, y_encoded)
        
        # Training accuracy
        y_pred = self.model.predict(self.X)
        accuracy = accuracy_score(y_encoded, y_pred)
        
        print(f"   ✅ Model trained!")
        print(f"   📊 Training Accuracy: {accuracy:.2%}")
        
        return accuracy
    
    def predict_disease(self, user_symptoms):
        """Predict with improved matching and scoring"""
        matched_symptoms = []
        unmatched = []
        
        for symptom in user_symptoms:
            matched, score = self._find_best_symptom_match(symptom)
            if matched:
                matched_symptoms.append(matched)
                if score < 1.0:
                    print(f"   📍 '{symptom}' → '{matched}' ({score:.0%})")
            else:
                unmatched.append(symptom)
        
        if unmatched:
            print(f"   ⚠️ Unmatched: {unmatched}")
        
        if not matched_symptoms:
            matched_symptoms = [self._normalize_symptom(s) for s in user_symptoms if self._normalize_symptom(s)]
        
        # Create enhanced feature vector
        features = self.feature_engineer.create_enhanced_features(
            set(matched_symptoms), 
            self.all_symptoms_list
        )
        features = self.scaler.transform(features.reshape(1, -1))
        
        # Predict
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        
        disease = self.label_encoder.inverse_transform([prediction])[0]
        confidence = probabilities[prediction]
        
        # Get top predictions
        top_n = min(5, len(probabilities))
        top_n_idx = np.argsort(probabilities)[-top_n:][::-1]
        top_n_diseases = self.label_encoder.inverse_transform(top_n_idx)
        top_n_probs = probabilities[top_n_idx]
        
        # Rerank with symptom overlap
        reranked = self._rerank_predictions(matched_symptoms, list(zip(top_n_diseases, top_n_probs)))
        
        return reranked[0][0], reranked[0][1], reranked[:3]
    
    def _rerank_predictions(self, user_symptoms, predictions):
        """Rerank based on symptom overlap and disease-symptom match"""
        reranked = []
        user_set = set(user_symptoms)
        
        for disease, prob in predictions:
            disease_symptoms = self.disease_symptom_map.get(disease.lower(), set())
            
            if disease_symptoms and user_set:
                # Jaccard similarity
                overlap = len(user_set & disease_symptoms)
                union = len(user_set | disease_symptoms)
                jaccard = overlap / union if union > 0 else 0
                
                # Precision: how many user symptoms match disease
                precision = overlap / len(user_set) if user_set else 0
                
                # Recall: how many disease symptoms were mentioned
                recall = overlap / len(disease_symptoms) if disease_symptoms else 0
                
                # F1 score
                f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
                
                # Combined score
                combined = (prob * 0.5) + (jaccard * 0.15) + (precision * 0.2) + (f1 * 0.15)
            else:
                combined = prob
            
            reranked.append((disease, combined))
        
        reranked.sort(key=lambda x: x[1], reverse=True)
        
        # Normalize scores
        max_score = max(r[1] for r in reranked) if reranked else 1
        reranked = [(d, min(s/max_score, 1.0)) for d, s in reranked]
        
        return reranked
    
    def calculate_severity(self, symptoms):
        """Calculate severity with enhanced weights"""
        severity_score = 0
        symptom_severities = []
        
        for symptom in symptoms:
            matched, _ = self._find_best_symptom_match(symptom)
            if matched and self.feature_engineer:
                severity = self.feature_engineer.get_combined_weight(matched)
            elif matched:
                severity = self.severity_map.get(matched, 1)
            else:
                severity = 1
            severity_score += severity
            symptom_severities.append((symptom, severity))
        
        avg_severity = severity_score / len(symptoms) if symptoms else 0
        return severity_score, avg_severity, symptom_severities
    
    def is_emergency(self, symptoms, severity_score):
        """Check for emergency symptoms"""
        emergency_symptoms = [
            'chest_pain', 'difficulty_breathing', 'severe_headache',
            'sudden_numbness', 'confusion', 'severe_bleeding',
            'unconsciousness', 'heart_attack', 'stroke', 'seizure',
            'high_fever', 'severe_abdominal_pain', 'blurred_vision',
            'slurred_speech', 'weakness', 'paralysis', 'shortness_of_breath',
            'fainting', 'severe_chest_pain', 'coughing_blood'
        ]
        
        user_symptoms_clean = [self._normalize_symptom(s) for s in symptoms]
        has_emergency = any(es in user_symptoms_clean for es in emergency_symptoms)
        high_severity = severity_score > 20
        
        return has_emergency or high_severity
    
    def get_specialist_recommendation(self, disease):
        """Get specialist recommendation"""
        specialist_map = {
            'fungal': 'Dermatologist', 'allergy': 'Allergist',
            'gerd': 'Gastroenterologist', 'diabetes': 'Endocrinologist',
            'migraine': 'Neurologist', 'arthritis': 'Rheumatologist',
            'hypertension': 'Cardiologist', 'pneumonia': 'Pulmonologist',
            'hepatitis': 'Hepatologist', 'jaundice': 'Hepatologist',
            'malaria': 'Infectious Disease Specialist',
            'dengue': 'Infectious Disease Specialist',
            'typhoid': 'Infectious Disease Specialist',
            'tuberculosis': 'Pulmonologist', 'asthma': 'Pulmonologist',
            'heart': 'Cardiologist', 'kidney': 'Nephrologist',
            'liver': 'Hepatologist', 'stomach': 'Gastroenterologist',
            'skin': 'Dermatologist', 'brain': 'Neurologist',
            'bone': 'Orthopedist', 'blood': 'Hematologist',
            'mental': 'Psychiatrist', 'eye': 'Ophthalmologist',
            'ear': 'ENT Specialist', 'cold': 'General Physician',
            'flu': 'General Physician', 'anxiety': 'Psychiatrist',
            'depression': 'Psychiatrist', 'panic': 'Psychiatrist'
        }
        
        disease_lower = disease.lower()
        for keyword, specialist in specialist_map.items():
            if keyword in disease_lower:
                return specialist
        return 'General Physician'
    
    def get_comprehensive_assessment(self, symptoms):
        """Get complete assessment"""
        print(f"\n🔍 Processing {len(symptoms)} symptom(s)...")
        
        disease, confidence, top_3 = self.predict_disease(symptoms)
        severity_score, avg_severity, symptom_severities = self.calculate_severity(symptoms)
        emergency = self.is_emergency(symptoms, severity_score)
        specialist = self.get_specialist_recommendation(disease)
        
        description = self.description_map.get(disease.lower(), "No description available")
        precautions = self.precautions_map.get(disease.lower(), [])
        medications = self.medications_map.get(disease.lower(), "Consult a doctor")
        diet = self.diets_map.get(disease.lower(), "Maintain a balanced diet")
        workout = self.workouts_map.get(disease.lower(), "Consult a doctor before exercising")
        
        return {
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
    
    def save_model(self, filename=None):
        """Save model"""
        if filename is None:
            filename = os.path.join(_SCRIPT_DIR, '..', 'healthcare_model.pkl')
        
        model_data = {
            'model': self.model,
            'label_encoder': self.label_encoder,
            'scaler': self.scaler,
            'feature_engineer': self.feature_engineer,
            'all_symptoms': self.all_symptoms,
            'all_symptoms_list': self.all_symptoms_list,
            'severity_map': self.severity_map,
            'description_map': self.description_map,
            'precautions_map': self.precautions_map,
            'medications_map': self.medications_map,
            'diets_map': self.diets_map,
            'workouts_map': self.workouts_map,
            'symptom_columns': self.symptom_columns,
            'disease_column': self.disease_column,
            'disease_symptom_map': self.disease_symptom_map,
            'symptom_disease_map': self.symptom_disease_map,
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\n💾 Model saved to {filename}")
    
    def load_model(self, filename=None):
        """Load model"""
        if filename is None:
            filename = os.path.join(_SCRIPT_DIR, '..', 'healthcare_model.pkl')
        
        with open(filename, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.label_encoder = model_data['label_encoder']
        self.scaler = model_data.get('scaler', StandardScaler())
        self.feature_engineer = model_data.get('feature_engineer')
        self.all_symptoms = model_data['all_symptoms']
        self.all_symptoms_list = model_data.get('all_symptoms_list', sorted(self.all_symptoms))
        self.severity_map = model_data['severity_map']
        self.description_map = model_data['description_map']
        self.precautions_map = model_data['precautions_map']
        self.medications_map = model_data['medications_map']
        self.diets_map = model_data['diets_map']
        self.workouts_map = model_data['workouts_map']
        self.symptom_columns = model_data['symptom_columns']
        self.disease_column = model_data.get('disease_column', 'diseases')
        self.disease_symptom_map = model_data.get('disease_symptom_map', {})
        self.symptom_disease_map = model_data.get('symptom_disease_map', {})
        
        print(f"\n✅ Model loaded from {filename}")


def print_assessment(assessment):
    """Print formatted assessment"""
    print("\n" + "="*80)
    print("🏥 HEALTHCARE ASSESSMENT REPORT")
    print("="*80)
    
    print(f"\n🎯 PREDICTED DISEASE: {assessment['predicted_disease'].upper()}")
    print(f"   Confidence: {assessment['confidence']:.1%}")
    
    print(f"\n📊 TOP 3 POSSIBLE CONDITIONS:")
    for i, (disease, prob) in enumerate(assessment['top_3_predictions'], 1):
        bar = "█" * int(prob * 20) + "░" * (20 - int(prob * 20))
        print(f"   {i}. {disease}: {bar} {prob:.1%}")
    
    print(f"\n⚠️  SEVERITY ASSESSMENT:")
    print(f"   Total Severity Score: {assessment['severity_score']:.1f}")
    print(f"   Average Severity: {assessment['average_severity']:.2f}")
    
    if assessment['is_emergency']:
        print(f"\n🚨 {'='*60} 🚨")
        print(f"   EMERGENCY ALERT: Seek immediate medical attention!")
        print(f"🚨 {'='*60} 🚨")
    
    print(f"\n👨‍⚕️ RECOMMENDED SPECIALIST: {assessment['recommended_specialist']}")
    
    print(f"\n📝 DESCRIPTION:")
    desc = assessment['description'][:200] + "..." if len(assessment['description']) > 200 else assessment['description']
    print(f"   {desc}")
    
    if assessment['precautions']:
        print(f"\n🛡️  PRECAUTIONS:")
        for i, precaution in enumerate(assessment['precautions'][:5], 1):
            print(f"   {i}. {precaution}")
    
    print(f"\n💊 MEDICATIONS: {assessment['medications']}")
    print(f"\n🍽️  DIET: {assessment['diet_recommendations']}")
    print(f"\n🏃 WORKOUT: {assessment['workout_recommendations']}")
    
    print("\n" + "="*80)
    print("⚠️  DISCLAIMER: This is a preliminary assessment only.")
    print("   Please consult a qualified healthcare professional.")
    print("="*80)


def main():
    """Train and test"""
    print("="*80)
    print("🏥 HEALTHCARE ASSISTANCE SYSTEM - ENHANCED TRAINING")
    print("="*80)
    
    assistant = HealthcareAssistant()
    
    if not assistant.load_cleaned_data():
        print("\n❌ Failed to load data.")
        return
    
    assistant.prepare_training_data()
    assistant.train_model()
    assistant.save_model()
    
    print("\n" + "="*80)
    print("🧪 TESTING")
    print("="*80)
    
    test_cases = [
        ['fever', 'headache', 'fatigue'],
        ['itching', 'skin rash', 'nodal skin eruptions'],
        ['chest pain', 'shortness of breath', 'sweating'],
        ['stomach pain', 'vomiting', 'diarrhea'],
        ['anxiety', 'depression', 'insomnia']
    ]
    
    for symptoms in test_cases:
        print(f"\n📋 Symptoms: {symptoms}")
        assessment = assistant.get_comprehensive_assessment(symptoms)
        print(f"   → {assessment['predicted_disease']} ({assessment['confidence']:.1%})")
    
    print("\n✅ System ready!")


if __name__ == "__main__":
    main()