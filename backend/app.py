"""
Flask API Backend for SymptoGuide Healthcare Assistant
Provides REST endpoints for symptom analysis and disease prediction
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model.Healthcare_Assistant_System import HealthcareAssistant
from model.Interract import extract_symptoms_from_text, SYMPTOM_KEYWORDS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the healthcare assistant
assistant = None

def initialize_assistant():
    """Initialize and load the ML model"""
    global assistant
    try:
        assistant = HealthcareAssistant()
        assistant.load_model()
        print(f"✅ Model loaded successfully with {len(assistant.all_symptoms)} symptoms")
        return True
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': assistant is not None
    })

@app.route('/api/symptoms', methods=['GET'])
def get_all_symptoms():
    """Get all available symptoms in the system"""
    if not assistant:
        return jsonify({'error': 'Model not loaded'}), 500
    
    # Convert symptoms to readable format
    symptoms_list = sorted([
        symptom.replace('_', ' ').title() 
        for symptom in assistant.all_symptoms
    ])
    
    return jsonify({
        'symptoms': symptoms_list,
        'total': len(symptoms_list)
    })

@app.route('/api/symptom-keywords', methods=['GET'])
def get_symptom_keywords():
    """Get symptom keywords for NLP matching"""
    # Get unique base symptoms from SYMPTOM_KEYWORDS
    keywords = list(SYMPTOM_KEYWORDS.keys())
    return jsonify({
        'keywords': sorted([kw.replace('_', ' ').title() for kw in keywords]),
        'total': len(keywords)
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_symptoms():
    """
    Analyze symptoms and provide comprehensive health assessment
    
    Expected JSON payload:
    {
        "symptoms": ["fever", "cough", "headache"],
        "description": "Optional text description of symptoms",
        "age": 25,
        "gender": "male",
        "duration": "3-7 days",
        "severity": "moderate"
    }
    """
    if not assistant:
        return jsonify({'error': 'Model not initialized'}), 500
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract symptoms
        symptoms = data.get('symptoms', [])
        description = data.get('description', '')
        
        # Process symptoms list
        processed_symptoms = []
        for symptom in symptoms:
            # Convert to lowercase and replace spaces with underscores
            processed_symptom = symptom.lower().replace(' ', '_')
            processed_symptoms.append(processed_symptom)
        
        # If description provided, extract additional symptoms using NLP
        if description:
            nlp_symptoms = extract_symptoms_from_text(description, assistant.all_symptoms)
            # Merge with existing symptoms
            for sym in nlp_symptoms:
                if sym not in processed_symptoms:
                    processed_symptoms.append(sym)
        
        if not processed_symptoms:
            return jsonify({'error': 'No valid symptoms provided'}), 400
        
        # Get comprehensive assessment
        assessment = assistant.get_comprehensive_assessment(processed_symptoms)
        
        # Add input metadata to response
        assessment['input'] = {
            'symptoms': symptoms,
            'description': description,
            'age': data.get('age'),
            'gender': data.get('gender'),
            'duration': data.get('duration'),
            'severity': data.get('severity')
        }
        
        # Format response
        response = {
            'success': True,
            'prediction': {
                'disease': assessment['predicted_disease'],
                'confidence': float(assessment['confidence']),
                'alternatives': [
                    {
                        'disease': disease,
                        'probability': float(prob)
                    }
                    for disease, prob in assessment['top_3_predictions']
                ]
            },
            'severity': {
                'score': int(assessment['severity_score']),
                'average': float(assessment['average_severity']),
                'is_emergency': bool(assessment['is_emergency']),
                'symptom_details': assessment['symptom_severities']
            },
            'recommendations': {
                'specialist': assessment['recommended_specialist'],
                'description': assessment['description'],
                'precautions': assessment['precautions'],
                'medications': assessment['medications'],
                'diet': assessment['diet_recommendations'],
                'workout': assessment['workout_recommendations']
            },
            'input_metadata': assessment['input']
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/extract-symptoms', methods=['POST'])
def extract_symptoms():
    """
    Extract symptoms from natural language text
    
    Expected JSON payload:
    {
        "text": "I have a headache and feeling very tired"
    }
    """
    if not assistant:
        return jsonify({'error': 'Model not initialized'}), 500
    
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Extract symptoms using NLP
        symptoms = extract_symptoms_from_text(text, assistant.all_symptoms)
        
        # Convert to readable format
        readable_symptoms = [
            symptom.replace('_', ' ').title() 
            for symptom in symptoms
        ]
        
        return jsonify({
            'success': True,
            'extracted_symptoms': readable_symptoms,
            'raw_symptoms': symptoms,
            'total': len(symptoms)
        })
    
    except Exception as e:
        print(f"Error extracting symptoms: {e}")
        return jsonify({
            'success': False,
            'error': f'Extraction failed: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("="*80)
    print("🏥 SYMPTOGUIDE HEALTHCARE API SERVER")
    print("="*80)
    
    # Initialize the assistant
    if initialize_assistant():
        print("\n✅ Server ready to accept requests")
        print("📍 API Endpoints:")
        print("   GET  /api/health              - Health check")
        print("   GET  /api/symptoms            - Get all symptoms")
        print("   GET  /api/symptom-keywords    - Get symptom keywords")
        print("   POST /api/analyze             - Analyze symptoms")
        print("   POST /api/extract-symptoms    - Extract symptoms from text")
        print("\n🚀 Starting Flask server...")
        print("="*80 + "\n")
        
        # Run the server
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("\n❌ Failed to initialize assistant. Please ensure:")
        print("   1. The model has been trained (run Healthcare_Assistant_System.py)")
        print("   2. healthcare_model.pkl exists in the backend folder")
        print("   3. All required dependencies are installed")
