/**
 * API Service for SymptoGuide
 * Handles all communication with the Flask backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export interface SymptomAnalysisRequest {
  symptoms: string[];
  description?: string;
  age?: string;
  gender?: string;
  duration?: string;
  severity?: string;
}

export interface DiseaseAlt {
  disease: string;
  probability: number;
}

export interface SymptomAnalysisResponse {
  success: boolean;
  prediction: {
    disease: string;
    confidence: number;
    alternatives: DiseaseAlt[];
  };
  severity: {
    score: number;
    average: number;
    is_emergency: boolean;
    symptom_details: Record<string, number>;
  };
  recommendations: {
    specialist: string;
    description: string;
    precautions: string[];
    medications: string;
    diet: string;
    workout: string;
  };
  input_metadata: {
    symptoms: string[];
    description: string;
    age?: string;
    gender?: string;
    duration?: string;
    severity?: string;
  };
}

export interface ExtractSymptomsRequest {
  text: string;
}

export interface ExtractSymptomsResponse {
  success: boolean;
  extracted_symptoms: string[];
  raw_symptoms: string[];
  total: number;
}

export interface HealthCheckResponse {
  status: string;
  model_loaded: boolean;
}

export interface SymptomsListResponse {
  symptoms: string[];
  total: number;
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return response.json();
  }

  /**
   * Get all available symptoms
   */
  async getAllSymptoms(): Promise<SymptomsListResponse> {
    const response = await fetch(`${this.baseUrl}/symptoms`);
    if (!response.ok) {
      throw new Error('Failed to fetch symptoms');
    }
    return response.json();
  }

  /**
   * Get symptom keywords for NLP matching
   */
  async getSymptomKeywords(): Promise<SymptomsListResponse> {
    const response = await fetch(`${this.baseUrl}/symptom-keywords`);
    if (!response.ok) {
      throw new Error('Failed to fetch symptom keywords');
    }
    return response.json();
  }

  /**
   * Analyze symptoms and get comprehensive health assessment
   */
  async analyzeSymptoms(
    data: SymptomAnalysisRequest
  ): Promise<SymptomAnalysisResponse> {
    const response = await fetch(`${this.baseUrl}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Analysis failed');
    }

    return response.json();
  }

  /**
   * Extract symptoms from natural language text
   */
  async extractSymptoms(
    text: string
  ): Promise<ExtractSymptomsResponse> {
    const response = await fetch(`${this.baseUrl}/extract-symptoms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Extraction failed');
    }

    return response.json();
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export default for convenience
export default apiService;
