/**
 * Color coding utilities for Origo analysis results
 * Implements the green-yellow-red scale based on score ranges
 */

export type ScoreLevel = 'low' | 'medium' | 'high';

/**
 * Get color level based on score
 * @param score - Score between 0 and 1
 * @returns Color level: 'low' (green), 'medium' (yellow), 'high' (red)
 */
export const getScoreLevel = (score: number): ScoreLevel => {
  if (score <= 0.5) return 'low';      // Green - Natural range (0-50%)
  if (score <= 0.7) return 'medium';   // Yellow - Moderate suspicion (51-70%)
  return 'high';                       // Red - High suspicion (71-100%)
};

/**
 * Get color class name for CSS styling
 * @param score - Score between 0 and 1
 * @returns CSS class name
 */
export const getScoreColorClass = (score: number): string => {
  return `score-${getScoreLevel(score)}`;
};

/**
 * Get human-readable label for score
 * @param score - Score between 0 and 1
 * @returns Human-readable label
 */
export const getScoreLabel = (score: number): string => {
  const level = getScoreLevel(score);
  switch (level) {
    case 'low': return 'Natural';
    case 'medium': return 'Moderate';
    case 'high': return 'Suspicious';
  }
};

/**
 * Get detailed description for score
 * @param score - Score between 0 and 1
 * @returns Detailed description
 */
export const getScoreDescription = (score: number): string => {
  const level = getScoreLevel(score);
  switch (level) {
    case 'low': return 'Shows natural human-like patterns';
    case 'medium': return 'Shows some suspicious patterns';
    case 'high': return 'Shows strong AI-like patterns';
  }
};

/**
 * Get color hex values for direct styling
 * @param score - Score between 0 and 1
 * @returns Object with color hex values
 */
export const getScoreColors = (score: number) => {
  const level = getScoreLevel(score);
  switch (level) {
    case 'low':
      return {
        primary: '#22c55e',      // green-500
        background: '#dcfce7',   // green-100
        border: '#16a34a',       // green-600
        text: '#15803d'          // green-700
      };
    case 'medium':
      return {
        primary: '#eab308',      // yellow-500
        background: '#fef3c7',   // yellow-100
        border: '#ca8a04',       // yellow-600
        text: '#a16207'          // yellow-700
      };
    case 'high':
      return {
        primary: '#ef4444',      // red-500
        background: '#fee2e2',   // red-100
        border: '#dc2626',       // red-600
        text: '#b91c1c'          // red-700
      };
  }
};

/**
 * Get score range boundaries
 */
export const SCORE_THRESHOLDS = {
  LOW_UPPER: 0.3,     // 0-30% = Natural (Green)
  MEDIUM_UPPER: 0.6,  // 31-60% = Moderate (Yellow)
  HIGH_LOWER: 0.6     // 61-100% = Suspicious (Red)
} as const;

/**
 * Validate if score is in valid range
 * @param score - Score to validate
 * @returns True if score is between 0 and 1
 */
export const isValidScore = (score: number): boolean => {
  return typeof score === 'number' && score >= 0 && score <= 1;
};

/**
 * Format score as percentage string
 * @param score - Score between 0 and 1
 * @param decimals - Number of decimal places (default: 0)
 * @returns Formatted percentage string
 */
export const formatScoreAsPercentage = (score: number, decimals: number = 0): string => {
  if (!isValidScore(score)) return 'N/A';
  return `${(score * 100).toFixed(decimals)}%`;
};

/**
 * Get appropriate icon name for score level
 * @param score - Score between 0 and 1
 * @returns Icon identifier
 */
export const getScoreIcon = (score: number): string => {
  const level = getScoreLevel(score);
  switch (level) {
    case 'low': return 'trending-down';
    case 'medium': return 'minus';
    case 'high': return 'trending-up';
  }
};