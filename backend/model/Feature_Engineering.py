import pandas as pd
import numpy as np
from collections import defaultdict
from itertools import combinations
import os

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def nested_dict():
    """Helper function for nested defaultdict (pickle-safe)"""
    return defaultdict(int)


class SymptomFeatureEngineer:
    """Advanced feature engineering for symptom-disease prediction"""
    
    def __init__(self):
        self.symptom_weights = {}
        self.symptom_cooccurrence = {}  # Changed from defaultdict
        self.symptom_disease_freq = {}  # Changed from defaultdict
        self.disease_symptom_count = {}  # Changed from defaultdict
        self.symptom_rarity = {}
        self.symptom_discriminative_power = {}
        self.symptom_clusters = {}
        
    def calculate_symptom_weights(self, df_main, df_severity, disease_col, symptom_cols):
        """Calculate comprehensive symptom weights"""
        print("📊 Calculating symptom weights...")
        
        # 1. Base severity from dataset
        if df_severity is not None and 'Symptom' in df_severity.columns:
            weight_col = [c for c in df_severity.columns if 'weight' in c.lower() or 'severity' in c.lower()]
            if weight_col:
                for _, row in df_severity.iterrows():
                    symptom = str(row['Symptom']).lower().strip().replace(' ', '_')
                    self.symptom_weights[symptom] = {
                        'base_severity': float(row[weight_col[0]]),
                        'idf': 1.0,
                        'discriminative': 1.0,
                        'rarity': 1.0
                    }
        
        # 2. Calculate IDF (Inverse Document Frequency)
        total_diseases = df_main[disease_col].nunique()
        symptom_doc_freq = {}
        
        for _, row in df_main.iterrows():
            disease = str(row[disease_col]).lower().strip()
            seen_symptoms = set()
            
            for col in symptom_cols:
                val = row[col]
                if pd.notna(val):
                    if isinstance(val, str):
                        symptom = val.lower().strip().replace(' ', '_')
                    elif val == 1:
                        symptom = col.lower().replace(' ', '_')
                    else:
                        continue
                    
                    if symptom and symptom not in seen_symptoms:
                        # Update symptom_doc_freq
                        if symptom not in symptom_doc_freq:
                            symptom_doc_freq[symptom] = 0
                        symptom_doc_freq[symptom] += 1
                        seen_symptoms.add(symptom)
                        
                        # Update symptom_disease_freq
                        if symptom not in self.symptom_disease_freq:
                            self.symptom_disease_freq[symptom] = {}
                        if disease not in self.symptom_disease_freq[symptom]:
                            self.symptom_disease_freq[symptom][disease] = 0
                        self.symptom_disease_freq[symptom][disease] += 1
                        
                        # Update disease_symptom_count
                        if disease not in self.disease_symptom_count:
                            self.disease_symptom_count[disease] = 0
                        self.disease_symptom_count[disease] += 1
        
        # Calculate IDF and rarity scores
        for symptom, doc_freq in symptom_doc_freq.items():
            idf = np.log((total_diseases + 1) / (doc_freq + 1)) + 1
            rarity = 1 / (doc_freq + 1)
            
            if symptom not in self.symptom_weights:
                self.symptom_weights[symptom] = {
                    'base_severity': 1.0,
                    'idf': idf,
                    'discriminative': 1.0,
                    'rarity': rarity
                }
            else:
                self.symptom_weights[symptom]['idf'] = idf
                self.symptom_weights[symptom]['rarity'] = rarity
        
        # 3. Calculate discriminative power
        for symptom, disease_freq in self.symptom_disease_freq.items():
            if len(disease_freq) == 1:
                discriminative = 3.0
            elif len(disease_freq) <= 3:
                discriminative = 2.0
            elif len(disease_freq) <= 5:
                discriminative = 1.5
            else:
                discriminative = 1.0
            
            if symptom in self.symptom_weights:
                self.symptom_weights[symptom]['discriminative'] = discriminative
        
        print(f"   ✅ Calculated weights for {len(self.symptom_weights)} symptoms")
        return self.symptom_weights
    
    def calculate_cooccurrence(self, df_main, disease_col, symptom_cols):
        """Calculate symptom co-occurrence matrix"""
        print("🔗 Calculating symptom co-occurrence...")
        
        for _, row in df_main.iterrows():
            symptoms_in_row = []
            
            for col in symptom_cols:
                val = row[col]
                if pd.notna(val):
                    if isinstance(val, str):
                        symptom = val.lower().strip().replace(' ', '_')
                    elif val == 1:
                        symptom = col.lower().replace(' ', '_')
                    else:
                        continue
                    if symptom:
                        symptoms_in_row.append(symptom)
            
            for s1, s2 in combinations(symptoms_in_row, 2):
                # Update co-occurrence for s1 -> s2
                if s1 not in self.symptom_cooccurrence:
                    self.symptom_cooccurrence[s1] = {}
                if s2 not in self.symptom_cooccurrence[s1]:
                    self.symptom_cooccurrence[s1][s2] = 0
                self.symptom_cooccurrence[s1][s2] += 1
                
                # Update co-occurrence for s2 -> s1
                if s2 not in self.symptom_cooccurrence:
                    self.symptom_cooccurrence[s2] = {}
                if s1 not in self.symptom_cooccurrence[s2]:
                    self.symptom_cooccurrence[s2][s1] = 0
                self.symptom_cooccurrence[s2][s1] += 1
        
        print(f"   ✅ Built co-occurrence matrix for {len(self.symptom_cooccurrence)} symptoms")
        return self.symptom_cooccurrence
    
    def get_combined_weight(self, symptom):
        """Get combined weight for a symptom"""
        if symptom not in self.symptom_weights:
            return 1.0
        
        weights = self.symptom_weights[symptom]
        combined = (
            weights['base_severity'] * 0.3 +
            weights['idf'] * 0.3 +
            weights['discriminative'] * 0.25 +
            weights['rarity'] * 10 * 0.15
        )
        return combined
    
    def get_cooccurrence_score(self, s1, s2):
        """Get co-occurrence score between two symptoms"""
        if s1 in self.symptom_cooccurrence:
            return self.symptom_cooccurrence[s1].get(s2, 0)
        return 0
    
    def create_enhanced_features(self, symptoms, all_symptoms_list):
        """Create enhanced feature vector for given symptoms"""
        features = []
        
        # 1. Weighted symptom presence
        for symptom in all_symptoms_list:
            if symptom in symptoms:
                weight = self.get_combined_weight(symptom)
                features.append(weight)
            else:
                features.append(0)
        
        # 2. Symptom count feature
        features.append(len(symptoms))
        
        # 3. Average severity feature
        avg_severity = np.mean([self.get_combined_weight(s) for s in symptoms]) if symptoms else 0
        features.append(avg_severity)
        
        # 4. Co-occurrence score
        cooc_score = 0
        symptom_list = list(symptoms)
        for i, s1 in enumerate(symptom_list):
            for s2 in symptom_list[i+1:]:
                cooc_score += self.get_cooccurrence_score(s1, s2)
        features.append(cooc_score)
        
        # 5. Max severity
        max_severity = max([self.get_combined_weight(s) for s in symptoms]) if symptoms else 0
        features.append(max_severity)
        
        return np.array(features)


def engineer_features(df_main, df_severity, disease_col, symptom_cols):
    """Main function to engineer features"""
    engineer = SymptomFeatureEngineer()
    engineer.calculate_symptom_weights(df_main, df_severity, disease_col, symptom_cols)
    engineer.calculate_cooccurrence(df_main, disease_col, symptom_cols)
    return engineer


def augment_training_data(disease_symptom_map, engineer, all_symptoms_list, augmentation_factor=5):
    """Create augmented training data with variations"""
    print("🔄 Augmenting training data...")
    
    X_augmented = []
    y_augmented = []
    
    for disease, symptoms in disease_symptom_map.items():
        symptoms_list = list(symptoms)
        
        if len(symptoms_list) < 2:
            features = engineer.create_enhanced_features(symptoms, all_symptoms_list)
            X_augmented.append(features)
            y_augmented.append(disease)
            continue
        
        # Original sample
        features = engineer.create_enhanced_features(symptoms, all_symptoms_list)
        X_augmented.append(features)
        y_augmented.append(disease)
        
        # Augmented samples
        for aug_idx in range(augmentation_factor):
            ratio = 0.5 + (aug_idx / augmentation_factor) * 0.5
            n_symptoms = max(2, int(len(symptoms_list) * ratio))
            
            np.random.seed(hash(disease) % (2**32) + aug_idx)
            selected = np.random.choice(symptoms_list, n_symptoms, replace=False)
            
            features = engineer.create_enhanced_features(set(selected), all_symptoms_list)
            X_augmented.append(features)
            y_augmented.append(disease)
        
        # Noise samples
        for noise_idx in range(2):
            np.random.seed(hash(disease) % (2**32) + augmentation_factor + noise_idx)
            noise_symptoms = set(np.random.choice(all_symptoms_list, min(2, len(all_symptoms_list)), replace=False))
            noisy_symptoms = symptoms | noise_symptoms
            
            features = engineer.create_enhanced_features(noisy_symptoms, all_symptoms_list)
            X_augmented.append(features)
            y_augmented.append(disease)
    
    print(f"   ✅ Created {len(X_augmented)} training samples")
    return np.array(X_augmented), np.array(y_augmented)