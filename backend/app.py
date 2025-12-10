from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "backend"}), 200


@app.route("/api/assess", methods=["POST"])
def assess():
    data = request.get_json(silent=True) or {}

    symptoms = data.get("symptoms", [])
    severity = data.get("severity", "")
    duration = data.get("duration", "")

    # basic triage-style rules: low / moderate / high concern [web:15][web:89]
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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
