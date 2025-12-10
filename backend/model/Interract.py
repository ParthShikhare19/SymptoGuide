import os
import sys
from string import punctuation

# Add the current directory to Python path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Healthcare_Assistant_System import HealthcareAssistant, print_assessment

# Import NLP libraries
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('punkt_tab', quiet=True)

# Initialize lemmatizer
wl = WordNetLemmatizer()

# Comprehensive symptom dictionary for NLP matching
SYMPTOM_PHRASES = {
    # Urinary symptoms
    'difficulty in urination': ['difficult_urination', 'painful_urination'],
    'difficulty urinating': ['difficult_urination', 'painful_urination'],
    'painful urination': ['painful_urination', 'burning_micturition'],
    'burning urination': ['burning_micturition'],
    'frequent urination': ['frequent_urination', 'polyuria'],
    'blood in urine': ['blood_in_urine'],
    'cant pee': ['difficult_urination'],
    'hard to urinate': ['difficult_urination'],
    
    # Fever related
    'high fever': ['high_fever', 'fever'],
    'mild fever': ['mild_fever', 'fever'],
    'fever': ['fever'],
    'temperature': ['fever'],
    'feeling hot': ['fever'],
    
    # Headache related
    'bad headache': ['headache', 'severe_headache'],
    'severe headache': ['severe_headache', 'headache'],
    'headache': ['headache'],
    'head hurts': ['headache'],
    'head pain': ['headache'],
    'migraine': ['headache', 'migraine'],
    
    # Fatigue related
    'very tired': ['fatigue', 'weakness'],
    'feeling tired': ['fatigue'],
    'exhausted': ['fatigue', 'weakness'],
    'no energy': ['fatigue', 'weakness'],
    'weakness': ['weakness'],
    'fatigue': ['fatigue'],
    'lethargic': ['lethargy', 'fatigue'],
    
    # Stomach/Digestive
    'stomach pain': ['stomach_pain', 'abdominal_pain'],
    'stomach ache': ['stomach_pain', 'abdominal_pain'],
    'belly pain': ['abdominal_pain'],
    'abdominal pain': ['abdominal_pain'],
    'nausea': ['nausea'],
    'feeling sick': ['nausea'],
    'want to vomit': ['nausea', 'vomiting'],
    'vomiting': ['vomiting'],
    'throwing up': ['vomiting'],
    'diarrhea': ['diarrhoea'],
    'loose motion': ['diarrhoea'],
    'loose stool': ['diarrhoea'],
    'constipation': ['constipation'],
    'acidity': ['acidity', 'heartburn'],
    'heartburn': ['heartburn', 'acidity'],
    'indigestion': ['indigestion'],
    'bloating': ['bloating', 'stomach_bloating'],
    'gas': ['gas', 'bloating'],
    
    # Respiratory
    'cough': ['cough'],
    'coughing': ['cough'],
    'dry cough': ['cough'],
    'wet cough': ['cough', 'phlegm'],
    'cold': ['cold', 'common_cold'],
    'runny nose': ['runny_nose'],
    'blocked nose': ['congestion', 'nasal_congestion'],
    'stuffy nose': ['congestion', 'nasal_congestion'],
    'sneezing': ['sneezing', 'continuous_sneezing'],
    'shortness of breath': ['shortness_of_breath', 'breathlessness'],
    'difficulty breathing': ['breathlessness', 'shortness_of_breath'],
    'hard to breathe': ['breathlessness'],
    'cant breathe': ['breathlessness'],
    'wheezing': ['wheezing'],
    'chest congestion': ['congestion_in_chest'],
    
    # Chest/Heart
    'chest pain': ['chest_pain'],
    'chest hurts': ['chest_pain'],
    'heart pain': ['chest_pain'],
    'palpitations': ['palpitations', 'fast_heart_rate'],
    'heart racing': ['palpitations', 'fast_heart_rate'],
    'sweating': ['sweating', 'excessive_sweating'],
    
    # Skin
    'skin rash': ['skin_rash', 'rash'],
    'rash': ['skin_rash', 'rash'],
    'itching': ['itching'],
    'itchy skin': ['itching'],
    'red skin': ['redness', 'skin_rash'],
    'acne': ['acne', 'pimples'],
    'pimples': ['acne', 'pimples'],
    'yellow skin': ['yellowish_skin', 'jaundice'],
    'skin peeling': ['skin_peeling'],
    'dry skin': ['dry_skin'],
    
    # Pain
    'body pain': ['body_pain', 'muscle_pain'],
    'body ache': ['body_pain', 'muscle_pain'],
    'muscle pain': ['muscle_pain'],
    'joint pain': ['joint_pain'],
    'knee pain': ['joint_pain', 'knee_pain'],
    'back pain': ['back_pain'],
    'neck pain': ['neck_pain'],
    'leg pain': ['leg_pain'],
    
    # Mental/Neurological
    'anxiety': ['anxiety'],
    'feeling anxious': ['anxiety'],
    'depression': ['depression'],
    'feeling sad': ['depression'],
    'cant sleep': ['insomnia', 'sleeplessness'],
    'insomnia': ['insomnia'],
    'sleeplessness': ['insomnia', 'sleeplessness'],
    'dizziness': ['dizziness'],
    'feeling dizzy': ['dizziness'],
    'vertigo': ['dizziness', 'vertigo'],
    'confusion': ['confusion', 'altered_sensorium'],
    'mood swings': ['mood_swings'],
    'irritability': ['irritability'],
    'stress': ['anxiety', 'stress'],
    
    # Eye
    'blurred vision': ['blurred_vision'],
    'blurry vision': ['blurred_vision'],
    'eye pain': ['pain_in_eye'],
    'red eyes': ['redness_in_eye'],
    'watery eyes': ['watering_from_eyes'],
    
    # Throat/Mouth
    'sore throat': ['sore_throat'],
    'throat pain': ['sore_throat'],
    'difficulty swallowing': ['difficulty_swallowing'],
    'hard to swallow': ['difficulty_swallowing'],
    
    # Weight
    'weight loss': ['weight_loss'],
    'losing weight': ['weight_loss'],
    'weight gain': ['weight_gain'],
    'gaining weight': ['weight_gain'],
    'loss of appetite': ['loss_of_appetite'],
    'not hungry': ['loss_of_appetite'],
    'excessive hunger': ['excessive_hunger'],
    'always hungry': ['excessive_hunger'],
    'increased thirst': ['excessive_thirst', 'polydipsia'],
    'very thirsty': ['excessive_thirst'],
    
    # Others
    'swelling': ['swelling'],
    'swollen': ['swelling'],
    'chills': ['chills'],
    'shivering': ['shivering', 'chills'],
    'night sweats': ['night_sweats'],
    'dehydration': ['dehydration'],
}

# Single word symptom mapping
SINGLE_WORD_SYMPTOMS = {
    'fever': ['fever'],
    'headache': ['headache'],
    'cough': ['cough'],
    'cold': ['cold'],
    'fatigue': ['fatigue'],
    'tired': ['fatigue'],
    'weakness': ['weakness'],
    'nausea': ['nausea'],
    'vomiting': ['vomiting'],
    'diarrhea': ['diarrhoea'],
    'constipation': ['constipation'],
    'acidity': ['acidity'],
    'itching': ['itching'],
    'rash': ['skin_rash'],
    'sweating': ['sweating'],
    'chills': ['chills'],
    'dizziness': ['dizziness'],
    'anxiety': ['anxiety'],
    'depression': ['depression'],
    'insomnia': ['insomnia'],
    'sneezing': ['sneezing'],
    'wheezing': ['wheezing'],
    'bloating': ['bloating'],
    'swelling': ['swelling'],
    'palpitations': ['palpitations'],
}


class SymptomExtractor:
    """Extract symptoms from natural language input"""
    
    def __init__(self, known_symptoms):
        self.known_symptoms = set(known_symptoms)
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
    def extract_symptoms(self, user_input):
        """Extract symptoms from user's natural language input"""
        user_input = user_input.lower().strip()
        extracted_symptoms = set()
        matched_phrases = []
        
        # 1. First try exact phrase matching (most accurate)
        for phrase, symptoms in SYMPTOM_PHRASES.items():
            if phrase in user_input:
                for symptom in symptoms:
                    # Verify symptom exists in known symptoms
                    if symptom in self.known_symptoms:
                        extracted_symptoms.add(symptom)
                        matched_phrases.append(phrase)
                    else:
                        # Try fuzzy match with known symptoms
                        matched = self._fuzzy_match(symptom)
                        if matched:
                            extracted_symptoms.add(matched)
                            matched_phrases.append(phrase)
        
        # 2. Single word matching for remaining words
        words = user_input.split()
        for word in words:
            word_clean = word.strip(punctuation).lower()
            if word_clean in SINGLE_WORD_SYMPTOMS:
                for symptom in SINGLE_WORD_SYMPTOMS[word_clean]:
                    if symptom in self.known_symptoms:
                        extracted_symptoms.add(symptom)
                    else:
                        matched = self._fuzzy_match(symptom)
                        if matched:
                            extracted_symptoms.add(matched)
        
        # 3. If no matches found, try tokenizing and direct matching
        if not extracted_symptoms:
            tokens = word_tokenize(user_input)
            tokens = [t for t in tokens if t not in self.stop_words and t not in punctuation]
            
            for token in tokens:
                lemma = self.lemmatizer.lemmatize(token)
                # Try direct match
                matched = self._fuzzy_match(lemma)
                if matched:
                    extracted_symptoms.add(matched)
        
        return list(extracted_symptoms), matched_phrases
    
    def _fuzzy_match(self, symptom, threshold=0.7):
        """Fuzzy match symptom to known symptoms"""
        symptom_normalized = symptom.lower().replace(' ', '_').replace('-', '_')
        
        # Exact match
        if symptom_normalized in self.known_symptoms:
            return symptom_normalized
        
        # Substring match
        for known in self.known_symptoms:
            if symptom_normalized in known or known in symptom_normalized:
                return known
        
        # Token overlap
        symptom_tokens = set(symptom_normalized.split('_'))
        best_match = None
        best_score = 0
        
        for known in self.known_symptoms:
            known_tokens = set(known.split('_'))
            overlap = len(symptom_tokens & known_tokens)
            if overlap > 0:
                score = overlap / max(len(symptom_tokens), len(known_tokens))
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = known
        
        return best_match


def interactive_session():
    """Run interactive symptom checker"""
    print("=" * 80)
    print("🏥 SYMPTOGUIDE - AI HEALTHCARE ASSISTANT")
    print("=" * 80)
    print("\nLoading model...")
    
    assistant = HealthcareAssistant()
    
    try:
        assistant.load_model()
        print("✅ Model loaded successfully!")
    except FileNotFoundError:
        print("❌ Model not found. Training new model...")
        if not assistant.load_cleaned_data():
            print("❌ Could not load data. Exiting.")
            return
        assistant.prepare_training_data()
        assistant.train_model()
        assistant.save_model()
        print("✅ Model trained and saved!")
    
    # Initialize symptom extractor
    extractor = SymptomExtractor(assistant.all_symptoms)
    
    print("\n" + "=" * 80)
    print("💬 SYMPTOM CHECKER")
    print("=" * 80)
    print("\nDescribe your symptoms in your own words.")
    print("Examples:")
    print("  - 'I have a bad headache, fever and feel very tired'")
    print("  - 'difficulty in urination and burning sensation'")
    print("  - 'skin rash with itching'")
    print("  - 'chest pain and shortness of breath'")
    print("\nType 'quit' or 'exit' to end the session.")
    print("Type 'list' to see available symptoms.")
    print("=" * 80)
    
    while True:
        print("\n🗣️  Describe how you're feeling: ", end="")
        user_input = input().strip()
        
        if not user_input:
            print("⚠️  Please describe your symptoms.")
            continue
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Thank you for using SymptoGuide. Take care!")
            break
        
        if user_input.lower() == 'list':
            print("\n📋 Available symptoms (sample):")
            symptoms_list = sorted(list(assistant.all_symptoms))[:50]
            for i, s in enumerate(symptoms_list, 1):
                print(f"   {i}. {s.replace('_', ' ').title()}")
            print(f"   ... and {len(assistant.all_symptoms) - 50} more")
            continue
        
        if user_input.lower() == 'help':
            print("\n📖 How to use:")
            print("   1. Describe your symptoms in plain English")
            print("   2. Be specific (e.g., 'burning urination' not just 'pain')")
            print("   3. Mention multiple symptoms if you have them")
            continue
        
        # Extract symptoms
        symptoms, matched_phrases = extractor.extract_symptoms(user_input)
        
        if not symptoms:
            print("\n⚠️  Could not identify specific symptoms from your description.")
            print("   Please try being more specific. Examples:")
            print("   - 'fever with headache'")
            print("   - 'stomach pain and vomiting'")
            print("   - 'skin rash and itching'")
            continue
        
        # Display identified symptoms
        print(f"\n✅ Identified {len(symptoms)} symptom(s):")
        for i, symptom in enumerate(symptoms, 1):
            print(f"   {i}. {symptom.replace('_', ' ').title()}")
        
        # Confirm with user
        print("\n❓ Are these symptoms correct? (yes/no/add more): ", end="")
        confirm = input().strip().lower()
        
        if confirm in ['no', 'n']:
            print("   Please try describing your symptoms differently.")
            continue
        
        if confirm in ['add', 'more', 'add more']:
            print("   Enter additional symptoms (comma-separated): ", end="")
            additional = input().strip()
            if additional:
                add_symptoms, _ = extractor.extract_symptoms(additional)
                symptoms.extend(add_symptoms)
                symptoms = list(set(symptoms))
                print(f"   Updated symptoms: {len(symptoms)} total")
        
        # Get assessment
        print("\n" + "=" * 80)
        print("🔍 ANALYZING YOUR SYMPTOMS...")
        print("=" * 80)
        
        assessment = assistant.get_comprehensive_assessment(symptoms)
        print_assessment(assessment)
        
        # Ask for another check
        print("\n" + "=" * 80)


def main():
    """Main entry point"""
    interactive_session()


if __name__ == "__main__":
    main()