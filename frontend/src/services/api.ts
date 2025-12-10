/**
 * API Service for SymptoGuide
 * Handles all communication with the Flask backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

export interface SymptomAnalysisRequest {
  symptoms: string[];
  description?: string;
  age?: string;
  gender?: string;
  duration?: string;
  severity?: string;
  medicalHistory?: string;
  currentMedications?: string;
  allergies?: string;
  followUpAnswers?: Record<string, string>;
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
    confidence_level?: string;
    confidence_warning?: string | null;
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
    processed_symptoms?: string[];
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
  matched_phrases?: string[];
  total: number;
  message?: string | null;
}

export interface HealthCheckResponse {
  status: string;
  model_loaded: boolean;
  timestamp?: string;
}

export interface SymptomsListResponse {
  success?: boolean;
  symptoms: string[];
  total: number;
}

export interface ApiError {
  success: false;
  error: string;
  message?: string;
  suggestions?: string[];
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  /**
   * Helper method to handle fetch with retry logic
   */
  private async fetchWithRetry(
    url: string,
    options?: RequestInit,
    retries: number = MAX_RETRIES
  ): Promise<Response> {
    try {
      const response = await fetch(url, options);
      
      // Retry on 503 (service unavailable - model loading)
      if (response.status === 503 && retries > 0) {
        console.log(`Service unavailable, retrying in ${RETRY_DELAY}ms...`);
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
        return this.fetchWithRetry(url, options, retries - 1);
      }
      
      return response;
    } catch (error) {
      if (retries > 0) {
        console.log(`Request failed, retrying in ${RETRY_DELAY}ms...`);
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
        return this.fetchWithRetry(url, options, retries - 1);
      }
      throw error;
    }
  }

  /**
   * Helper to parse error response
   */
  private async parseError(response: Response): Promise<ApiError> {
    try {
      const errorData = await response.json();
      return {
        success: false,
        error: errorData.error || 'Unknown error',
        message: errorData.message,
        suggestions: errorData.suggestions,
      };
    } catch {
      return {
        success: false,
        error: `HTTP ${response.status}`,
        message: response.statusText,
      };
    }
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    try {
      const response = await this.fetchWithRetry(`${this.baseUrl}/health`);
      if (!response.ok) {
        throw new Error('Health check failed');
      }
      return response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      return { status: 'unhealthy', model_loaded: false };
    }
  }

  /**
   * Get all available symptoms
   */
  async getAllSymptoms(): Promise<SymptomsListResponse> {
    const response = await this.fetchWithRetry(`${this.baseUrl}/symptoms`);
    if (!response.ok) {
      const error = await this.parseError(response);
      throw new Error(error.message || error.error);
    }
    return response.json();
  }

  /**
   * Get symptom keywords for NLP matching
   */
  async getSymptomKeywords(): Promise<SymptomsListResponse> {
    const response = await this.fetchWithRetry(`${this.baseUrl}/symptom-keywords`);
    if (!response.ok) {
      const error = await this.parseError(response);
      throw new Error(error.message || error.error);
    }
    return response.json();
  }

  /**
   * Analyze symptoms and get comprehensive health assessment
   */
  async analyzeSymptoms(
    data: SymptomAnalysisRequest
  ): Promise<SymptomAnalysisResponse> {
    const response = await this.fetchWithRetry(`${this.baseUrl}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await this.parseError(response);
      throw new Error(error.message || error.error);
    }

    const result = await response.json();
    
    // Log confidence warning if present
    if (result.prediction?.confidence_warning) {
      console.warn('Confidence warning:', result.prediction.confidence_warning);
    }

    return result;
  }

  /**
   * Extract symptoms from natural language text
   */
  async extractSymptoms(
    text: string
  ): Promise<ExtractSymptomsResponse> {
    if (!text || text.trim().length < 3) {
      return {
        success: false,
        extracted_symptoms: [],
        raw_symptoms: [],
        total: 0,
        message: 'Please provide a longer description',
      };
    }

    const response = await this.fetchWithRetry(`${this.baseUrl}/extract-symptoms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: text.trim() }),
    });

    if (!response.ok) {
      const error = await this.parseError(response);
      throw new Error(error.message || error.error);
    }

    return response.json();
  }

  /**
   * Check if the API is available and model is loaded
   */
  async isReady(): Promise<boolean> {
    try {
      const health = await this.healthCheck();
      return health.status === 'healthy' && health.model_loaded;
    } catch {
      return false;
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export default for convenience
export default apiService;
