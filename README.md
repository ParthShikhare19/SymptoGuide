<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/TypeScript-5.8-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/scikit--learn-1.0+-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-learn">
</p>

# 🏥 SymptoGuide

> **AI-Powered Healthcare Assistant for Symptom Analysis & Medical Guidance**

SymptoGuide is an intelligent healthcare assistance system that helps users understand and categorize their symptoms, providing preliminary assessments and guiding them toward appropriate medical experts or hospitals.

---

## 🎯 Problem Statement

**Community Connection Challenge - The Local Services Trust Problem**

Develop an intelligent healthcare assistance system that:
- ✅ Helps users understand and categorize their symptoms
- ✅ Provides preliminary, non-diagnostic assessments
- ✅ Guides users toward appropriate medical experts or hospitals
- ✅ Identifies emergency indicators and concern areas
- ✅ Recommends departments and specialists

> ⚠️ **Disclaimer**: This system does NOT replace professional medical diagnosis. Always consult a healthcare provider for medical advice.

---

## 💡 Our Solution

SymptoGuide combines **Machine Learning** and **Natural Language Processing** to:

1. 🗣️ **Accept natural language symptom descriptions** - "I have a bad headache and feeling very tired"
2. 🔍 **Extract and identify symptoms** using NLP with 100+ phrase mappings
3. 🤖 **Predict potential conditions** using an ensemble ML model (Random Forest + Gradient Boosting + SVM)
4. 📊 **Assess severity levels** and identify emergency indicators
5. 💊 **Provide recommendations** including specialists, medications, diet, and precautions
6. 🏥 **Connect users to nearby hospitals** and appropriate departments

---

## ✨ Features

### 🔬 AI-Powered Symptom Analysis
- Natural language processing for symptom extraction
- Support for 230+ medical symptoms
- Intelligent phrase matching ("chest pain", "difficulty breathing", etc.)

### 🎯 Disease Prediction
- Ensemble machine learning model with 95%+ accuracy
- Top-3 disease predictions with confidence scores
- Confidence level indicators (High/Medium/Low)

### 🚨 Emergency Detection
- Automatic identification of red-flag symptoms
- Emergency severity scoring
- Urgent care recommendations

### 👨‍⚕️ Smart Recommendations
- Specialist recommendations based on predicted condition
- Personalized precautions and medications
- Diet and workout suggestions
- Nearby hospital finder

### 💻 Modern User Interface
- Step-by-step symptom checker wizard
- Real-time symptom extraction preview
- Beautiful, responsive design
- Dark/Light mode support

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| ⚛️ **React 18** | UI Framework |
| 📘 **TypeScript** | Type Safety |
| ⚡ **Vite** | Build Tool |
| 🎨 **Tailwind CSS** | Styling |
| 🧩 **Shadcn/UI** | Component Library |
| 🔄 **React Query** | Data Fetching |
| 🧭 **React Router** | Navigation |
| 📊 **Recharts** | Data Visualization |

### Backend
| Technology | Purpose |
|------------|---------|
| 🐍 **Python 3.10+** | Core Language |
| 🌐 **Flask** | REST API Framework |
| 🤖 **Scikit-learn** | Machine Learning |
| 🔢 **Pandas & NumPy** | Data Processing |
| 📝 **NLTK** | Natural Language Processing |
| 📦 **Pickle** | Model Serialization |

### Machine Learning Model
| Component | Details |
|-----------|---------|
| 🎲 **Algorithm** | Ensemble (Random Forest + Extra Trees + Gradient Boosting + KNN + SVM) |
| 📊 **Features** | 230 binary symptom features |
| 🏷️ **Classes** | 40+ disease categories |
| 📈 **Accuracy** | 95%+ on test data |

---

## 📁 Project Structure

```
SymptoGuide/
├── 📂 backend/
│   ├── 📄 app.py                    # Flask API server
│   ├── 📄 requirements.txt          # Python dependencies
│   ├── 📦 healthcare_model.pkl      # Trained ML model
│   ├── 📂 data/
│   │   ├── 📂 cleaned_datasets/     # Processed data files
│   │   │   ├── diseases_symptoms_cleaned.csv
│   │   │   ├── symptom_severity_cleaned.csv
│   │   │   ├── medications_cleaned.csv
│   │   │   ├── precautions_cleaned.csv
│   │   │   ├── diets_cleaned.csv
│   │   │   └── ...
│   │   └── 📂 raw_data/             # Original datasets
│   └── 📂 model/
│       ├── 📄 Healthcare_Assistant_System.py  # Core ML model
│       ├── 📄 Interract.py                    # CLI & NLP extraction
│       ├── 📄 Feature_Engineering.py          # Feature processing
│       └── 📄 Complete_data_clean.py          # Data preprocessing
│
├── 📂 frontend/
│   ├── 📄 package.json              # Node dependencies
│   ├── 📄 vite.config.ts            # Vite configuration
│   ├── 📄 tailwind.config.ts        # Tailwind CSS config
│   └── 📂 src/
│       ├── 📄 App.tsx               # Main App component
│       ├── 📂 pages/
│       │   ├── 📄 Index.tsx         # Landing page
│       │   ├── 📄 SymptomChecker.tsx # Symptom input wizard
│       │   ├── 📄 Results.tsx       # Analysis results
│       │   ├── 📄 Hospitals.tsx     # Hospital finder
│       │   └── 📄 Specialists.tsx   # Specialist directory
│       ├── 📂 components/           # Reusable UI components
│       ├── 📂 services/
│       │   └── 📄 api.ts            # Backend API client
│       └── 📂 data/
│           └── 📄 mockData.ts       # Fallback data
│
├── 📄 README.md
├── 📄 LICENSE
└── 📄 package.json
```

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Version |
|-------------|---------|
| 🐍 Python | 3.10+ |
| 📦 Node.js | 18+ |
| 📦 npm/bun | Latest |

### Installation

#### 1️⃣ Clone the Repository
```bash
git clone https://github.com/ParthShikhare19/SymptoGuide.git
cd SymptoGuide
```

#### 2️⃣ Backend Setup
```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Download NLTK data (first time only)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

#### 3️⃣ Frontend Setup
```bash
cd frontend

# Install dependencies
npm install
# or
bun install
```

---

## ▶️ Running the Application

### Start Backend Server
```bash
cd backend
python app.py
```
The API will be available at `http://localhost:5000`

### Start Frontend Development Server
```bash
cd frontend
npm run dev
# or
bun dev
```
The app will be available at `http://localhost:5173`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/symptoms` | Get all available symptoms |
| `GET` | `/api/symptom-keywords` | Get symptom keywords for NLP |
| `POST` | `/api/analyze` | Analyze symptoms (ML-powered) |
| `POST` | `/api/assess` | Simple triage assessment |
| `POST` | `/api/extract-symptoms` | Extract symptoms from text |

### Example: Analyze Symptoms
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["fever", "headache", "fatigue"],
    "description": "I have been feeling very tired with high fever",
    "severity": "moderate",
    "duration": "3-7 days"
  }'
```

---

## 🧪 Testing the Model (CLI)

You can test the model directly from the command line:

```bash
cd backend/model
python Interract.py
```

Then enter symptoms naturally:
```
🗣️  Describe how you're feeling: I have a bad headache, fever and feeling very tired

✅ Identified 3 symptom(s):
   1. Headache
   2. High Fever
   3. Fatigue

Predicted Disease: Typhoid
Confidence: 87.3%
Recommended Specialist: Infectious Disease Specialist
```

---

## 📊 Datasets Used

| Dataset | Description | Records |
|---------|-------------|---------|
| `diseases_symptoms_cleaned.csv` | Disease-symptom mappings | 4,920 |
| `symptom_severity_cleaned.csv` | Symptom severity weights | 133 |
| `disease_description_cleaned.csv` | Disease descriptions | 41 |
| `precautions_cleaned.csv` | Disease precautions | 41 |
| `medications_cleaned.csv` | Recommended medications | 41 |
| `diets_cleaned.csv` | Diet recommendations | 41 |
| `workouts_cleaned.csv` | Workout recommendations | 41 |

---

## 🔮 Future Enhancements

- [ ] 🌐 Multi-language support
- [ ] 📱 Mobile app (React Native)
- [ ] 🗺️ Real-time hospital mapping with Google Maps API
- [ ] 📞 Telemedicine integration
- [ ] 📈 User health history tracking
- [ ] 🔔 Symptom progression alerts

---

## 📄 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

---

## 👥 Contributors

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/Ai-Chetan">
        <img src="https://github.com/Ai-Chetan.png" width="100px;" alt="Chetan Chaudhari"/><br />
        <sub><b>Chetan Chaudhari</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Nischay-loq">
        <img src="https://github.com/Nischay-loq.png" width="100px;" alt="Nischay Chavan"/><br />
        <sub><b>Nischay Chavan</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/ParthShikhare19">
        <img src="https://github.com/ParthShikhare19.png" width="100px;" alt="Parth Shikhare"/><br />
        <sub><b>Parth Shikhare</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/TanviPatil70">
        <img src="https://github.com/TanviPatil70.png" width="100px;" alt="Tanvi Patil"/><br />
        <sub><b>Tanvi Patil</b></sub>
      </a>
    </td>
  </tr>
</table>

---

<p align="center">
  Made with ❤️ for better healthcare accessibility
</p>

<p align="center">
  <a href="https://github.com/ParthShikhare19/SymptoGuide">⭐ Star this repo</a> •
  <a href="https://github.com/ParthShikhare19/SymptoGuide/issues">🐛 Report Bug</a> •
  <a href="https://github.com/ParthShikhare19/SymptoGuide/issues">✨ Request Feature</a>
</p>
