/**
 * API service for Origo backend communication
 * All data is fetched from backend - no simulations
 */

import axios from 'axios';
import type { AnalysisResult, TextAnalysisRequest, DimensionToggleSettings } from '../types/analysis';

// Configure axios defaults
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for analysis requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config: any) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error: any) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: any) => {
    return response;
  },
  (error: any) => {
    console.error('Response error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'Server error';
      throw new Error(`${message} (${error.response.status})`);
    } else if (error.request) {
      // Network error
      throw new Error('Network error - please check if the backend server is running');
    } else {
      // Other error
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

/**
 * Analyze text for AI-generated content detection
 * Fetches all data from backend - no fallback simulations
 * @param text - Text to analyze
 * @param enabledDimensions - Which analysis dimensions to include (all 7 dimensions)
 * @returns Promise with analysis results from backend
 */
export const analyzeText = async (text: string, enabledDimensions?: DimensionToggleSettings): Promise<AnalysisResult> => {
  if (!text || text.trim().length < 10) {
    throw new Error('Text must be at least 10 characters long');
  }

  if (text.length > 50000) {
    throw new Error('Text must be less than 50,000 characters');
  }

  // Convert DimensionToggleSettings to the format expected by backend
  const dimensionsConfig = enabledDimensions ? {
    perplexity: enabledDimensions.perplexity,
    burstiness: enabledDimensions.burstiness,
    semantic_coherence: enabledDimensions.semantic_coherence,
    ngram_repetition: enabledDimensions.ngram_repetition,
    lexical_richness: enabledDimensions.lexical_richness,
    stylistic_markers: enabledDimensions.stylistic_markers,
    readability: enabledDimensions.readability
  } : undefined;

  const request: TextAnalysisRequest = { 
    text: text.trim(),
    enabled_dimensions: dimensionsConfig
  };
  
  // Make request to backend - no fallback simulations
  const response = await apiClient.post<AnalysisResult>('/analyze', request);
  
  // Validate response structure
  if (!response.data) {
    throw new Error('Invalid response from server');
  }

  // Validate required fields
  if (typeof response.data.overall_score !== 'number') {
    throw new Error('Invalid response: missing overall_score');
  }

  if (!response.data.global_scores) {
    throw new Error('Invalid response: missing global_scores');
  }

  if (!response.data.dimension_results) {
    throw new Error('Invalid response: missing dimension_results');
  }
  
  return response.data;
};

/**
 * Check backend health status
 * @returns Promise with health status
 */
export const checkHealth = async (): Promise<any> => {
  const response = await apiClient.get('/health');
  return response.data;
};

/**
 * Get API information
 * @returns Promise with API info
 */
export const getApiInfo = async (): Promise<any> => {
  const response = await apiClient.get('/');
  return response.data;
};

/**
 * Get current analysis weights configuration
 * @returns Promise with weights configuration
 */
export const getAnalysisWeights = async (): Promise<any> => {
  const response = await apiClient.get('/weights');
  return response.data;
};

/**
 * Update analysis weights configuration
 * @param weights - New weights configuration
 * @returns Promise with updated weights
 */
export const updateAnalysisWeights = async (weights: Record<string, number>): Promise<any> => {
  const response = await apiClient.post('/weights', weights);
  return response.data;
};

/**
 * Get comprehensive API framework information
 * @returns Promise with framework documentation
 */
export const getApiFrameworkInfo = async (): Promise<any> => {
  const response = await apiClient.get('/api-info');
  return response.data;
};

export default apiClient;