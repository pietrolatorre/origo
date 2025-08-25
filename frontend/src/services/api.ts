/**
 * API service for Origo backend communication
 */

import axios from 'axios';
import type { AnalysisResult, TextAnalysisRequest, DimensionToggleSettings } from '../types/analysis';

// Configure axios defaults
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes timeout for analysis
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
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
 * @param text - Text to analyze
 * @param enabledDimensions - Which analysis dimensions to include
 * @returns Promise with analysis results
 */
export const analyzeText = async (text: string, enabledDimensions?: DimensionToggleSettings): Promise<AnalysisResult> => {
  if (!text || text.trim().length < 10) {
    throw new Error('Text must be at least 10 characters long');
  }

  if (text.length > 50000) {
    throw new Error('Text must be less than 50,000 characters');
  }

  const request: TextAnalysisRequest = { 
    text: text.trim(),
    enabled_dimensions: enabledDimensions
  };
  
  try {
    const response = await apiClient.post<AnalysisResult>('/analyze', request);
    return response.data;
  } catch (error) {
    console.error('Analysis request failed:', error);
    throw error;
  }
};

/**
 * Check backend health status
 * @returns Promise with health status
 */
export const checkHealth = async (): Promise<any> => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

/**
 * Get API information
 * @returns Promise with API info
 */
export const getApiInfo = async (): Promise<any> => {
  try {
    const response = await apiClient.get('/');
    return response.data;
  } catch (error) {
    console.error('API info request failed:', error);
    throw error;
  }
};

export default apiClient;