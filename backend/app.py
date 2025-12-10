"""
Flask API Backend for SymptoGuide Healthcare Assistant
Provides REST endpoints for symptom analysis and disease prediction
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'api_server.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SymptoGuide.API')

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from model.Healthcare_Assistant_System import HealthcareAssistant
    from model.Interract import SymptomExtractor, SYMPTOM_PHRASES, SINGLE_WORD_SYMPTOMS
    ML_MODEL_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ ML Model not available: {e}")
    ML_MODEL_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the healthcare assistant
assistant = None
symptom_extractor = None

def initialize_assistant():
    """Initialize and load the ML model"""
    global assistant, symptom_extractor
    if not ML_MODEL_AVAILABLE:
        return False
    try:
        logger.info("Initializing Healthcare Assistant...")
        assistant = HealthcareAssistant()
        assistant.load_model()
        
        # Initialize symptom extractor with known symptoms
        symptom_extractor = SymptomExtractor(assistant.all_symptoms)
        
        logger.info(f"✅ Model loaded successfully with {len(assistant.all_symptoms)} symptoms")
        return True
    except FileNotFoundError as e:
        logger.error(f"❌ Model file not found: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return False

@app.route('/', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'backend',
        'model_loaded': assistant is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/symptoms', methods=['GET'])
def get_all_symptoms():
    """Get all available symptoms in the system"""
    if not assistant:
        logger.warning("API called but model not loaded")
        return jsonify({'error': 'Model not loaded', 'message': 'Please wait for model initialization'}), 503
    
    # Convert symptoms to readable format
    symptoms_list = sorted([
        symptom.replace('_', ' ').title() 
        for symptom in assistant.all_symptoms
    ])
    
    return jsonify({
        'success': True,
        'symptoms': symptoms_list,
        'total': len(symptoms_list)
    })

@app.route('/api/symptom-keywords', methods=['GET'])
def get_symptom_keywords():
    """Get symptom keywords for NLP matching"""
    if not ML_MODEL_AVAILABLE:
        return jsonify({'error': 'ML model not available'}), 500
    
    # Get unique base symptoms from phrase and single word mappings
    phrases = list(SYMPTOM_PHRASES.keys())
    single_words = list(SINGLE_WORD_SYMPTOMS.keys())
    all_keywords = sorted(set(phrases + single_words))
    
    return jsonify({
        'success': True,
        'keywords': [kw.replace('_', ' ').title() for kw in all_keywords],
        'phrases': phrases,
        'single_words': single_words,
        'total': len(all_keywords)
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_symptoms():
    """
    Analyze symptoms and provide comprehensive health assessment using ML model
    
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
        logger.error("Analyze called but model not initialized")
        return jsonify({'error': 'Model not initialized', 'message': 'Please wait for model initialization'}), 503
    
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("No data provided in request")
            return jsonify({'error': 'No data provided', 'message': 'Please provide symptoms data'}), 400
        
        # Extract symptoms
        symptoms = data.get('symptoms', [])
        description = data.get('description', '')
        
        # Validate input
        if not symptoms and not description:
            return jsonify({
                'success': False,
                'error': 'No symptoms provided',
                'message': 'Please provide at least one symptom or description'
            }), 400
        
        # Process symptoms list
        processed_symptoms = []
        for symptom in symptoms:
            # Convert to lowercase and replace spaces with underscores
            processed_symptom = symptom.lower().strip().replace(' ', '_')
            if processed_symptom:
                processed_symptoms.append(processed_symptom)
        
        # If description provided, extract additional symptoms using NLP
        if description and symptom_extractor:
            nlp_symptoms, _ = symptom_extractor.extract_symptoms(description)
            # Merge with existing symptoms
            for sym in nlp_symptoms:
                if sym not in processed_symptoms:
                    processed_symptoms.append(sym)
        
        if not processed_symptoms:
            return jsonify({
                'success': False,
                'error': 'No valid symptoms identified',
                'message': 'Could not identify any symptoms from your input. Please try being more specific.',
                'suggestions': [
                    'Try describing specific symptoms like "fever", "headache", "cough"',
                    'Example: "I have a fever and headache"',
                    'Example: "stomach pain with nausea"'
                ]
            }), 400
        
        logger.info(f"Processing symptoms: {processed_symptoms}")
        
        # Get comprehensive assessment
        assessment = assistant.get_comprehensive_assessment(processed_symptoms)
        
        # Add input metadata to response
        assessment['input'] = {
            'symptoms': symptoms,
            'processed_symptoms': processed_symptoms,
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
                'confidence_level': assessment.get('confidence_level', 'unknown'),
                'confidence_warning': assessment.get('confidence_warning'),
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
        
        logger.info(f"Analysis complete: {assessment['predicted_disease']} ({assessment['confidence']:.2%})")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Analysis failed',
            'message': str(e)
        }), 500

@app.route('/api/assess', methods=['POST'])
def assess():
    """
    Simple triage-style assessment endpoint (fallback when ML model not available)
    """
    data = request.get_json(silent=True) or {}

    symptoms = data.get("symptoms", [])
    severity = data.get("severity", "")
    duration = data.get("duration", "")

    # basic triage-style rules: low / moderate / high concern
    concern = "low"

    red_flag_symptoms = {
        "chest pain",
        "difficulty breathing",
        "shortness of breath",
        "loss of consciousness",
        "severe bleeding",
        "sudden weakness",
    }

    # normalize symptoms to lowercase for matching
    lower_symptoms = {s.lower() for s in symptoms}

    if lower_symptoms & red_flag_symptoms:
        concern = "high"
    elif severity == "severe":
        concern = "high"
    elif severity == "moderate" or duration in {"week", "weeks", "month", "chronic"}:
        concern = "moderate"
    elif len(symptoms) >= 3:
        concern = "moderate"

    if concern == "high":
        recommended_departments = ["Emergency", "General Medicine"]
    elif concern == "moderate":
        recommended_departments = ["General Medicine"]
    else:
        recommended_departments = ["Primary Care"]

    return jsonify(
        {
            "concern_level": concern,
            "suggestions": [
                "This is a preliminary assessment and not a diagnosis.",
                "If concern is high, seek emergency care.",
            ],
            "recommended_departments": recommended_departments,
        }
    )

@app.route('/api/extract-symptoms', methods=['POST'])
def extract_symptoms_endpoint():
    """
    Extract symptoms from natural language text
    
    Expected JSON payload:
    {
        "text": "I have a headache and feeling very tired"
    }
    """
    if not assistant or not symptom_extractor:
        logger.error("Extract symptoms called but model not initialized")
        return jsonify({'error': 'Model not initialized', 'message': 'Please wait for model initialization'}), 503
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'No text provided',
                'message': 'Please provide text to analyze'
            }), 400
        
        if len(text) < 3:
            return jsonify({
                'success': False,
                'error': 'Text too short',
                'message': 'Please provide a longer description'
            }), 400
        
        # Extract symptoms using NLP
        symptoms, matched_phrases = symptom_extractor.extract_symptoms(text)
        
        # Convert to readable format
        readable_symptoms = [
            symptom.replace('_', ' ').title() 
            for symptom in symptoms
        ]
        
        logger.info(f"Extracted {len(symptoms)} symptoms from: '{text[:50]}...'")
        
        return jsonify({
            'success': True,
            'extracted_symptoms': readable_symptoms,
            'raw_symptoms': symptoms,
            'matched_phrases': matched_phrases,
            'total': len(symptoms),
            'message': 'No symptoms identified' if not symptoms else None
        })
    
    except Exception as e:
        logger.error(f"Error extracting symptoms: {e}")
        return jsonify({
            'success': False,
            'error': 'Extraction failed',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

@app.errorhandler(503)
def service_unavailable(error):
    return jsonify({
        'success': False,
        'error': 'Service unavailable',
        'message': 'Model is still loading, please try again in a moment'
    }), 503

if __name__ == '__main__':
    print("="*80)
    print("🏥 SYMPTOGUIDE HEALTHCARE API SERVER")
    print("="*80)
    
    # Initialize the assistant
    if ML_MODEL_AVAILABLE and initialize_assistant():
        print("\n✅ Server ready with ML model")
        print("📍 API Endpoints:")
        print("   GET  /api/health              - Health check")
        print("   GET  /api/symptoms            - Get all symptoms")
        print("   GET  /api/symptom-keywords    - Get symptom keywords")
        print("   POST /api/analyze             - Analyze symptoms (ML-powered)")
        print("   POST /api/assess              - Simple triage assessment")
        print("   POST /api/extract-symptoms    - Extract symptoms from text")
    else:
        print("\n⚠️ Running in basic mode (ML model not available)")
        print("📍 API Endpoints:")
        print("   GET  /api/health              - Health check")
        print("   POST /api/assess              - Simple triage assessment")
    
    print("\n🚀 Starting Flask server...")
    print("="*80 + "\n")
    
    # Run the server
    app.run(host='0.0.0.0', port=5000, debug=True)
