"""
Flask API Backend for SymptoGuide Healthcare Assistant
Provides REST endpoints for symptom analysis and disease prediction
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging
from datetime import datetime
from math import radians, sin, cos, sqrt, asin
import requests

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
    ML_IMPORT_ERROR = None
except ImportError as e:
    print(f"⚠️ ML Model not available: {e}")
    import traceback
    traceback.print_exc()
    ML_MODEL_AVAILABLE = False
    ML_IMPORT_ERROR = str(e)

app = Flask(__name__)

GEOAPIFY_KEY = os.environ.get("GEOAPIFY_KEY")


def haversine_distance_km(lat1, lon1, lat2, lon2):
    """
    Compute great-circle distance between two points (lat/lon) in kilometers.
    """
    try:
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        R = 6371  # Earth radius in km
        return R * c
    except Exception:
        return None

# Configure CORS properly for production
CORS(app, 
     origins=["https://yoursymptoguide.vercel.app", "http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True)

# Initialize the healthcare assistant
assistant = None
symptom_extractor = None
_initialized = False
_init_error = None  # Track initialization errors for debugging

def initialize_assistant():
    """Initialize and load the ML model"""
    global assistant, symptom_extractor, _initialized, _init_error
    if _initialized:
        return assistant is not None
    _initialized = True
    
    if not ML_MODEL_AVAILABLE:
        _init_error = f"ML model imports not available: {ML_IMPORT_ERROR}"
        return False
    try:
        logger.info("Initializing Healthcare Assistant...")
        assistant = HealthcareAssistant()
        assistant.load_model()
        
        # Initialize symptom extractor with known symptoms
        symptom_extractor = SymptomExtractor(assistant.all_symptoms)
        
        logger.info(f"✅ Model loaded successfully with {len(assistant.all_symptoms)} symptoms")
        _init_error = None
        return True
    except FileNotFoundError as e:
        _init_error = f"Model file not found: {e}"
        logger.error(f"❌ {_init_error}")
        return False
    except Exception as e:
        _init_error = f"Error loading model: {e}"
        logger.error(f"❌ {_init_error}")
        import traceback
        traceback.print_exc()
        return False

# Initialize model on first request (works with Gunicorn)
@app.before_request
def ensure_model_loaded():
    """Ensure model is loaded before handling requests"""
    if not _initialized:
        initialize_assistant()

@app.route('/', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with debug info"""
    return jsonify({
        'status': 'healthy',
        'service': 'backend',
        'model_loaded': assistant is not None,
        'initialized': _initialized,
        'init_error': _init_error,
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

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
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
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 204
    
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

@app.route('/api/assess', methods=['POST', 'OPTIONS'])
def assess():
    """
    Simple triage-style assessment endpoint (fallback when ML model not available)
    """
    if request.method == 'OPTIONS':
        return '', 204
    
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

    lower_symptoms = {s.lower() for s in symptoms}

    if lower_symptoms & red_flag_symptoms:
        concern = "high"
    elif severity == "severe":
        concern = "high"
    elif severity == "moderate" or duration in {"week", "weeks", "month", "chronic"}:
        concern = "moderate"
    elif len(symptoms) >= 3:
        concern = "moderate"

    dept = "Primary Care"

    if any(
        k in lower_symptoms
        for k in ["stomach pain", "abdominal pain", "nausea", "vomiting", "diarrhea", "bloating"]
    ):
        dept = "Gastroenterology"
    elif any(k in lower_symptoms for k in ["chest pain", "palpitations", "heart"]):
        dept = "Cardiology"
    elif any(
        k in lower_symptoms
        for k in ["shortness of breath", "breathlessness", "cough", "wheezing"]
    ):
        dept = "Pulmonology"
    elif any(k in lower_symptoms for k in ["headache", "migraine", "dizziness", "numbness", "seizure"]):
        dept = "Neurology"
    elif any(k in lower_symptoms for k in ["rash", "itching", "skin", "hives"]):
        dept = "Dermatology"

    recommended_departments = []

    if concern == "high":
        recommended_departments.append("Emergency")

    if dept != "Primary Care":
        recommended_departments.append(dept)

    if not recommended_departments:
        if concern == "moderate":
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

@app.route('/api/extract-symptoms', methods=['POST', 'OPTIONS'])
def extract_symptoms_endpoint():
    """
    Extract symptoms from natural language text
    
    Expected JSON payload:
    {
        "text": "I have a headache and feeling very tired"
    }
    """
    if request.method == 'OPTIONS':
        return '', 204
    
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

# ----------------- Geoapify-based nearby hospitals -----------------
@app.route("/api/nearby-hospitals", methods=["GET"])
def nearby_hospitals():
    """
    Query Geoapify for healthcare places around (lat, lng) within radius_m.
    Accepts optional ?department=Orthopedics (case-insensitive).
    Returns hospitals sorted by distance and pre-filtered by department when possible.
    """
    try:
        lat = float(request.args.get("lat"))
        lng = float(request.args.get("lng"))
    except (TypeError, ValueError):
        return jsonify({"error": "lat and lng query params required"}), 400

    department_raw = (request.args.get("department") or "").strip()
    department = department_raw.lower()

    # radius in meters (default 20 km)
    radius_m = int(request.args.get("radius_m") or 20000)

    if not GEOAPIFY_KEY:
        print("Geoapify key missing or empty")
        return jsonify({"error": "Geoapify API key not configured"}), 500

    # Map friendly department name -> Geoapify category
    # Use only safe, supported categories:
    #   healthcare, healthcare.hospital, healthcare.dentist [web:211]
    dept_map = {
        # for all specialties, just search general healthcare places
        "cardiology": "healthcare",
        "neurology": "healthcare",
        "dermatology": "healthcare",
        "orthopedics": "healthcare",
        "gastroenterology": "healthcare",
        "pulmonology": "healthcare",
        "ent": "healthcare",
        # specific categories that are supported
        "dental": "healthcare.dentist",
        "dentistry": "healthcare.dentist",
        "emergency": "healthcare.hospital",
        "general medicine": "healthcare",
        "primary care": "healthcare",
    }

    # pick a category param if we have a mapping; otherwise use broad healthcare query
    geo_category = "healthcare"
    dept_key = department.strip().lower()
    if dept_key in dept_map:
        geo_category = dept_map[dept_key]

    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": geo_category,
        "filter": f"circle:{lng},{lat},{radius_m}",
        "limit": 100,
        "apiKey": GEOAPIFY_KEY,
    }

    try:
        resp = requests.get(url, params=params, timeout=8)
        print("Geoapify status:", resp.status_code)
        print("Geoapify body preview:", resp.text[:300])
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("Geoapify error:", e)
        return jsonify(
            {
                "error": "Failed to fetch hospitals from Geoapify",
                "details": str(e),
            }
        ), 500

    features = data.get("features", [])

    hospitals_all = []
    for i, feat in enumerate(features):
        props = feat.get("properties", {}) or {}
        geom = feat.get("geometry", {}) or {}
        coords = geom.get("coordinates") or [None, None]
        lng_res, lat_res = (coords[0], coords[1]) if len(coords) >= 2 else (None, None)

        name = props.get("name") or ""
        if not name:
            continue

        address = (
            props.get("formatted")
            or props.get("address_line1")
            or "Address not available"
        )
        categories = props.get("categories") or []
        cats_lower = [c.lower() for c in categories]
        name_lower = name.lower()
        inferred_specialties = []

        # Infer specialties using name + categories (loose matching)
        if any("cardio" in c or "heart" in c for c in cats_lower) or "cardio" in name_lower or "heart" in name_lower:
            inferred_specialties.append("Cardiology")
        if any("gastro" in c for c in cats_lower) or "gastro" in name_lower:
            inferred_specialties.append("Gastroenterology")
        if any("neuro" in c for c in cats_lower) or "neuro" in name_lower:
            inferred_specialties.append("Neurology")
        if any("dermatology" in c for c in cats_lower) or "derma" in name_lower or "skin" in name_lower:
            inferred_specialties.append("Dermatology")
        if "ent" in name_lower or "ear nose throat" in name_lower:
            inferred_specialties.append("ENT")
        if any("ortho" in c for c in cats_lower) or "ortho" in name_lower or "bone" in name_lower:
            inferred_specialties.append("Orthopedics")
        if "dent" in name_lower or "dental" in name_lower or "dentist" in name_lower:
            inferred_specialties.append("Dental")
        if "surgical" in name_lower:
            inferred_specialties.append("Surgery")

        emergency = (
            "emergency" in name_lower
            or "er" in name_lower
            or "24/7" in (props.get("opening_hours") or "")
        )

        distance_km = None
        if lat_res is not None and lng_res is not None:
            try:
                distance_km = haversine_distance_km(
                    lat, lng, float(lat_res), float(lng_res)
                )
            except Exception:
                distance_km = None

        hospitals_all.append(
            {
                "id": str(props.get("place_id", i)),
                "name": name,
                "address": address,
                "lat": lat_res,
                "lng": lng_res,
                "emergency": bool(emergency),
                "phone": props.get("contact:phone") or "Not available",
                "specialties": inferred_specialties,
                "has_specialties": bool(inferred_specialties),
                "rating": props.get("rate", 4.5) or 4.5,
                "distance_km": distance_km if distance_km is not None else None,
            }
        )

    # Normalize: sort by distance (unknown distances come last)
    hospitals_all.sort(
        key=lambda h: (
            h["distance_km"] is None,
            h["distance_km"] if h["distance_km"] is not None else 99999,
        )
    )

    # Filter by requested department (server-side)
    def matches_department(h, dept):
        if not dept:
            return True
        dept_norm = dept.lower()
        if dept_norm == "emergency":
            return h["emergency"] is True or any(
                "emergency" in s.lower() for s in (h.get("specialties") or [])
            )
        specialties_lower = [(s or "").lower() for s in (h.get("specialties") or [])]
        if any(dept_norm in s for s in specialties_lower):
            return True
        synonyms = {
            "dental": ["dental", "dentist"],
            "orthopedics": ["ortho", "orthopedics", "bone"],
            "cardiology": ["cardio", "cardiology", "heart"],
            "neurology": ["neuro", "neurology"],
            "dermatology": ["derma", "dermatology", "skin"],
            "gastroenterology": ["gastro", "gastroenterology"],
            "ent": ["ent", "ear", "nose", "throat"],
            "primary care": ["general", "primary", "family"],
            "general medicine": ["general", "medicine", "gp", "general medicine"],
        }
        for key, vals in synonyms.items():
            if dept_norm == key:
                name_addr_lower = (
                    (h.get("name", "") or "") + " " + (h.get("address", "") or "")
                ).lower()
                if any(v in name_addr_lower for v in vals):
                    return True
        return False

    filtered = [h for h in hospitals_all if matches_department(h, department)]

    # Fallback: if nothing matched and a department was requested, return nearest general hospitals
    fallback_used = False
    if department and len(filtered) == 0:
        fallback_used = True
        filtered = hospitals_all[:15]

    def format_distance(h):
        dk = h.get("distance_km")
        if dk is None:
            return ""
        if dk < 1:
            return f"{int(dk * 1000)} m"
        else:
            return f"{dk:.1f} km"

    results = []
    for h in filtered:
        results.append(
            {
                "id": h["id"],
                "name": h["name"],
                "address": h["address"],
                "lat": h["lat"],
                "lng": h["lng"],
                "emergency": h["emergency"],
                "phone": h["phone"],
                "specialties": h["specialties"],
                "has_specialties": h["has_specialties"],
                "rating": round(
                    float(h.get("rating", 4.5)) if h.get("rating") else 4.5, 1
                ),
                "distance": format_distance(h),
            }
        )

    return jsonify({"hospitals": results, "fallback_used": fallback_used})


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
        print("   GET  /api/nearby-hospitals    - Find nearby hospitals")
    else:
        print("\n⚠️ Running in basic mode (ML model not available)")
        print("📍 API Endpoints:")
        print("   GET  /api/health              - Health check")
        print("   POST /api/assess              - Simple triage assessment")
    
    # Get port from environment variable (required for Render)
    port = int(os.environ.get('PORT', 5000))
    
    print(f"\n🚀 Starting Flask server on port {port}...")
    print("="*80 + "\n")
    
    # Run the server (debug=False for production)
    app.run(host='0.0.0.0', port=port, debug=False)
