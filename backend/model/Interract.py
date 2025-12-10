import pickle
import re
import sys
import os
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
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    nltk.download('punkt_tab', quiet=True)
except:
    pass

# Initialize lemmatizer
wl = WordNetLemmatizer()

# Comprehensive symptom dictionary for NLP matching
SYMPTOM_KEYWORDS = {
    # Fever and temperature related
    'fever': ['fever', 'temperature', 'hot', 'burning', 'feverish', 'pyrexia'],
    'high_fever': ['high fever', 'very hot', 'burning up', 'extremely hot'],
    'chills': ['chills', 'shivering', 'cold', 'freezing', 'shaking'],
    'sweating': ['sweating', 'sweaty', 'perspiring', 'perspiration', 'night sweats'],
    
    # Head related
    'headache': ['headache', 'head pain', 'head ache', 'head hurts', 'migraine', 'head pounding'],
    'dizziness': ['dizzy', 'dizziness', 'lightheaded', 'vertigo', 'spinning', 'unsteady', 'giddy'],
    'confusion': ['confused', 'confusion', 'disoriented', 'foggy', 'unclear thinking'],
    
    # Respiratory
    'cough': ['cough', 'coughing', 'dry cough', 'wet cough', 'hacking'],
    'shortness_of_breath': ['shortness of breath', 'breathless', 'breathing difficulty', 'cant breathe', 
                            'hard to breathe', 'difficulty breathing', 'breath short', 'gasping'],
    'runny_nose': ['runny nose', 'running nose', 'nasal discharge', 'stuffy nose', 'blocked nose', 'congestion'],
    'sore_throat': ['sore throat', 'throat pain', 'throat hurts', 'painful throat', 'scratchy throat'],
    'chest_pain': ['chest pain', 'chest hurts', 'chest tightness', 'chest discomfort', 'heart pain'],
    
    # Digestive
    'nausea': ['nausea', 'nauseous', 'feel sick', 'queasy', 'want to vomit', 'sick feeling'],
    'vomiting': ['vomiting', 'vomit', 'throwing up', 'puking', 'puke'],
    'diarrhea': ['diarrhea', 'loose stools', 'watery stool', 'frequent bowel', 'loose motion'],
    'constipation': ['constipation', 'constipated', 'hard stool', 'cant poop', 'difficulty passing stool'],
    'abdominal_pain': ['stomach pain', 'abdominal pain', 'belly pain', 'tummy ache', 'stomach ache', 
                       'stomach hurts', 'abdomen pain', 'gut pain'],
    'loss_of_appetite': ['no appetite', 'loss of appetite', 'not hungry', 'dont want to eat', 'appetite loss'],
    'indigestion': ['indigestion', 'heartburn', 'acid reflux', 'acidity', 'burning stomach'],
    
    # Skin
    'skin_rash': ['rash', 'skin rash', 'red spots', 'skin eruption', 'bumps on skin', 'hives'],
    'itching': ['itching', 'itchy', 'scratching', 'itch', 'irritation'],
    'skin_peeling': ['skin peeling', 'peeling skin', 'flaky skin'],
    
    # Musculoskeletal
    'muscle_pain': ['muscle pain', 'body ache', 'muscle ache', 'sore muscles', 'body pain', 'myalgia'],
    'joint_pain': ['joint pain', 'joint ache', 'painful joints', 'arthritis', 'stiff joints'],
    'back_pain': ['back pain', 'backache', 'back hurts', 'lower back pain', 'spine pain'],
    'neck_pain': ['neck pain', 'stiff neck', 'neck hurts', 'neck ache'],
    'weakness': ['weakness', 'weak', 'tired', 'no energy', 'lack of strength', 'feeble'],
    
    # Fatigue
    'fatigue': ['fatigue', 'tired', 'exhausted', 'no energy', 'worn out', 'lethargic', 'sleepy', 'drowsy'],
    'malaise': ['malaise', 'unwell', 'not feeling well', 'generally sick', 'feeling bad'],
    
    # Weight
    'weight_loss': ['weight loss', 'losing weight', 'lost weight', 'getting thin'],
    'weight_gain': ['weight gain', 'gaining weight', 'getting fat', 'putting on weight'],
    
    # Eyes
    'blurred_vision': ['blurred vision', 'blurry vision', 'cant see clearly', 'vision problem', 'fuzzy vision'],
    'watery_eyes': ['watery eyes', 'teary eyes', 'eyes watering', 'eye discharge'],
    'eye_pain': ['eye pain', 'eyes hurt', 'painful eyes'],
    
    # Mental health
    'anxiety': ['anxiety', 'anxious', 'nervous', 'worried', 'panic', 'stressed', 'restless'],
    'depression': ['depression', 'depressed', 'sad', 'hopeless', 'low mood', 'feeling down'],
    'insomnia': ['insomnia', 'cant sleep', 'sleepless', 'trouble sleeping', 'difficulty sleeping'],
    
    # Other common symptoms
    'swelling': ['swelling', 'swollen', 'puffiness', 'bloated', 'edema'],
    'numbness': ['numbness', 'numb', 'tingling', 'pins and needles'],
    'bleeding': ['bleeding', 'blood', 'hemorrhage'],
    'bruising': ['bruising', 'bruise', 'black and blue'],
    'yellow_skin': ['yellow skin', 'jaundice', 'yellowish', 'yellow eyes'],
    'pale_skin': ['pale', 'pallor', 'white skin', 'colorless'],
    'frequent_urination': ['frequent urination', 'peeing a lot', 'urinating often', 'bathroom frequently'],
    'painful_urination': ['painful urination', 'burning urination', 'hurts to pee', 'burning pee'],
    'thirst': ['thirsty', 'excessive thirst', 'always thirsty', 'dry mouth'],
    'hunger': ['hungry', 'excessive hunger', 'always hungry', 'increased appetite'],
}

def clean_text(text):
    """Clean and preprocess text using NLP"""
    text = text.lower()
    text = text.replace(".", " ")
    text = text.replace(",", " ")
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    try:
        tokens = word_tokenize(text)
        tokens = [t for t in tokens if t not in punctuation]
        tokens = [t for t in tokens if t not in stopwords.words("english")]
        tokens = [wl.lemmatize(t) for t in tokens]
        return tokens
    except:
        return text.split()

def extract_symptoms_from_text(user_input, known_symptoms):
    """Extract symptoms from natural language using NLP"""
    user_input_lower = user_input.lower()
    extracted_symptoms = set()
    
    # Step 1: Direct matching with symptom keywords dictionary
    for symptom, keywords in SYMPTOM_KEYWORDS.items():
        for keyword in keywords:
            if keyword in user_input_lower:
                extracted_symptoms.add(symptom)
                break
    
    # Step 2: Clean and tokenize user input
    tokens = clean_text(user_input)
    
    # Step 3: Match against known symptoms from the trained model
    for known_symptom in known_symptoms:
        # Convert known symptom to comparable format
        symptom_words = known_symptom.lower().replace('_', ' ').split()
        
        # Check if any token matches symptom words
        for token in tokens:
            lemmatized_token = wl.lemmatize(token)
            for symptom_word in symptom_words:
                lemmatized_symptom = wl.lemmatize(symptom_word)
                if lemmatized_token == lemmatized_symptom or token in symptom_word or symptom_word in token:
                    extracted_symptoms.add(known_symptom)
                    break
    
    # Step 4: Fuzzy matching for common phrases
    phrase_patterns = [
        (r'feel(ing)?\s+(sick|unwell|bad|terrible|awful)', ['malaise', 'fatigue']),
        (r'(can\'?t|cannot|unable to)\s+breathe', ['shortness_of_breath']),
        (r'(can\'?t|cannot|unable to)\s+sleep', ['insomnia']),
        (r'throwing\s+up', ['vomiting']),
        (r'running\s+(a\s+)?temperature', ['fever']),
        (r'(body|all over)\s+(ache|pain|hurts)', ['muscle_pain', 'fatigue']),
        (r'(head|brain)\s+(is\s+)?(spinning|pounding)', ['headache', 'dizziness']),
        (r'(stomach|tummy)\s+(upset|problem|issue)', ['abdominal_pain', 'nausea']),
        (r'skin\s+(problem|issue|irritation)', ['skin_rash', 'itching']),
        (r'(feel|feeling)\s+(anxious|nervous|worried|stressed)', ['anxiety']),
        (r'(feel|feeling)\s+(sad|down|depressed|hopeless)', ['depression']),
        (r'losing\s+(my\s+)?appetite', ['loss_of_appetite']),
        (r'(no|lack of|without)\s+energy', ['fatigue', 'weakness']),
    ]
    
    for pattern, symptoms in phrase_patterns:
        if re.search(pattern, user_input_lower):
            extracted_symptoms.update(symptoms)
    
    return list(extracted_symptoms)

def get_user_symptoms_nlp(known_symptoms):
    """Get symptoms from user using natural language processing - Direct response without confirmation"""
    print("\n" + "="*80)
    print("🩺 TELL US HOW YOU'RE FEELING")
    print("="*80)
    
    print("\n📝 Describe your symptoms in your own words.")
    print("   Example: 'I have a bad headache, fever and feel very tired'\n")
    
    while True:
        user_input = input("🗣️  Describe how you're feeling: ").strip()
        
        if user_input == '':
            print("⚠️  Please describe your symptoms.\n")
            continue
        
        # Extract symptoms using NLP
        symptoms = extract_symptoms_from_text(user_input, known_symptoms)
        
        if len(symptoms) == 0:
            print("\n⚠️  I couldn't identify specific symptoms. Please try again with more details.\n")
            continue
        
        # Show extracted symptoms and immediately return (no confirmation)
        print(f"\n✅ Identified {len(symptoms)} symptom(s): {', '.join([s.replace('_', ' ').title() for s in symptoms])}")
        
        return symptoms

def get_user_symptoms_manual():
    """Fallback: Get symptoms manually one by one"""
    print("\n" + "="*80)
    print("MANUAL SYMPTOM ENTRY")
    print("="*80)
    
    print("\nEnter your symptoms one by one.")
    print("Type 'done' when finished.\n")
    
    symptoms = []
    
    while True:
        symptom = input(f"Symptom #{len(symptoms)+1} (or 'done'): ").strip().lower()
        
        if symptom == 'done':
            if len(symptoms) == 0:
                print("⚠️  Please enter at least one symptom.")
                continue
            break
        elif symptom == '':
            continue
        else:
            symptoms.append(symptom.replace(' ', '_'))
            print(f"   ✅ Added: {symptom}")
    
    return symptoms

def main():
    """Main interactive application with NLP support"""
    print("="*80)
    print("🏥 INTELLIGENT HEALTHCARE ASSISTANCE SYSTEM")
    print("="*80)
    print("\n⚠️  DISCLAIMER: This system provides preliminary assessments only.")
    print("   It does NOT replace professional medical diagnosis.")
    print("   Always consult a qualified healthcare professional.\n")
    
    # Load trained model
    assistant = HealthcareAssistant()
    
    try:
        # Use default path (relative to Healthcare_Assistant_System.py location)
        assistant.load_model()
        known_symptoms = assistant.all_symptoms
        print(f"✅ System loaded with {len(known_symptoms)} known symptoms.\n")
    except FileNotFoundError:
        print("\n❌ Model not found. Please run Healthcare_Assistant_System.py first to train the model.")
        return
    
    while True:
        # Get symptoms from user using NLP
        symptoms = get_user_symptoms_nlp(known_symptoms)
        
        # Get assessment
        print("\n" + "="*80)
        print("🔍 ANALYZING YOUR SYMPTOMS...")
        print("="*80)
        
        assessment = assistant.get_comprehensive_assessment(symptoms)
        
        # Display assessment
        print_assessment(assessment)
        
        # Ask to continue
        print("\n" + "="*80)
        another = input("Would you like to check another set of symptoms? (yes/no): ").strip().lower()
        if another not in ['yes', 'y']:
            break
    
    print("\n" + "="*80)
    print("Thank you for using the Healthcare Assistance System!")
    print("Stay healthy! 🏥")
    print("="*80)

if __name__ == "__main__":
    main()