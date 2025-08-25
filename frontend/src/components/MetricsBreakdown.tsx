/**
 * MetricsBreakdown component for displaying individual analysis metrics
 */

import React from 'react';
import { Brain, Zap, Repeat, Link } from 'lucide-react';
import type { GlobalScores, EnhancedAnalysisDetails, DimensionToggleSettings } from '../types/analysis';

interface MetricsBreakdownProps {
  scores: GlobalScores;
  enhancedAnalysis?: {
    perplexity_details: EnhancedAnalysisDetails;
    burstiness_details: EnhancedAnalysisDetails;
    ngram_details: EnhancedAnalysisDetails;
    semantic_details: EnhancedAnalysisDetails;
  };
  enabledDimensions?: DimensionToggleSettings;
  onDimensionClick?: (dimension: string, details: EnhancedAnalysisDetails) => void;
}

// Default weights for analysis components (should match backend)
const DEFAULT_WEIGHTS: Record<string, number> = {
  perplexity: 0.4,
  burstiness: 0.2,
  ngram_similarity: 0.2,
  semantic_coherence: 0.2
};

export const MetricsBreakdown: React.FC<MetricsBreakdownProps> = ({ 
  scores, 
  enhancedAnalysis, 
  enabledDimensions,
  onDimensionClick 
}) => {
  const getMetricIcon = (metric: string) => {
    switch (metric) {
      case 'perplexity':
        return <Brain size={20} />;
      case 'burstiness':
        return <Zap size={20} />;
      case 'semantic_coherence':
        return <Link size={20} />;
      case 'ngram_similarity':
        return <Repeat size={20} />;
      default:
        return <Brain size={20} />;
    }
  };

  const getMetricTitle = (metric: string): string => {
    const titles: Record<string, string> = {
      perplexity: 'Perplexity',
      burstiness: 'Burstiness',
      semantic_coherence: 'Semantic Coherence',
      ngram_similarity: 'N-gram Similarity'
    };
    return titles[metric] || metric;
  };

  const getMetricExplanation = (metric: string): string => {
    const explanations: Record<string, string> = {
      perplexity: 'How predictable the text is according to GPT-2. Lower perplexity suggests AI generation.',
      burstiness: 'Variation in sentence structure and length. Uniform patterns may indicate AI.',
      semantic_coherence: 'Consistency of semantic meaning. Extreme coherence might suggest AI.',
      ngram_similarity: 'Repetitive word patterns and phrases. High similarity common in AI text.'
    };
    return explanations[metric] || 'Analysis metric for AI detection.';
  };

  const getScoreColor = (score: number): string => {
    if (score >= 0.7) return 'high';
    if (score >= 0.6) return 'medium'; // Changed from 0.4 to 0.6
    return 'low';
  };

  const isDimensionEnabled = (metric: string): boolean => {
    if (!enabledDimensions) return true;
    const dimensionMap: Record<string, keyof DimensionToggleSettings> = {
      'perplexity': 'perplexity',
      'burstiness': 'burstiness',
      'semantic_coherence': 'semantic_coherence',
      'ngram_similarity': 'ngram_similarity'
    };
    return enabledDimensions[dimensionMap[metric]] !== false;
  };

  const handleDimensionClick = (metric: string) => {
    // Only allow clicks on enabled dimensions
    if (!isDimensionEnabled(metric)) return;
    
    if (onDimensionClick && enhancedAnalysis) {
      const detailsMap: Record<string, EnhancedAnalysisDetails> = {
        perplexity: enhancedAnalysis.perplexity_details,
        burstiness: enhancedAnalysis.burstiness_details,
        ngram_similarity: enhancedAnalysis.ngram_details,
        semantic_coherence: enhancedAnalysis.semantic_details
      };
      
      const details = detailsMap[metric];
      if (details) {
        onDimensionClick(metric, details);
      }
    }
  };

  return (
    <div className="metrics-breakdown">
      <div className="metrics-grid-2x2">
        {Object.entries(scores).map(([metric, score]) => {
          const weight = DEFAULT_WEIGHTS[metric] || 0.25;
          const isEnabled = score !== null && isDimensionEnabled(metric);
          const scoreValue = score ?? 0;
          const scoreColor = getScoreColor(scoreValue);
          const isClickable = onDimensionClick && isEnabled;
          
          return (
            <div 
              key={metric} 
              className={`metric-dimension-2x2 ${
                isClickable ? 'clickable' : ''
              } ${
                !isEnabled ? 'disabled' : ''
              }`}
              onClick={() => handleDimensionClick(metric)}
              title={
                !isEnabled 
                  ? 'This dimension is disabled' 
                  : isClickable 
                    ? 'Click to view detailed insights' 
                    : undefined
              }
            >
              <div className="metric-header-row">
                <div className="metric-icon">
                  {getMetricIcon(metric)}
                </div>
                <h5 className="metric-title">{getMetricTitle(metric)}</h5>
              </div>
              <div className="metric-content-below">
                <div className="metric-description">
                  <p>{getMetricExplanation(metric)}</p>
                  {!isEnabled && (
                    <p className="disabled-notice">This dimension was excluded from analysis</p>
                  )}
                </div>
                <div className="metric-score-weight">
                  <div className={`score-circle ${isEnabled ? scoreColor : 'disabled'}`}>
                    <span className={`score-percentage ${isEnabled ? scoreColor : 'disabled'}`}>
                      {isEnabled ? Math.round(scoreValue * 100) : '--'}%
                    </span>
                  </div>
                  <span className="metric-weight">Weight: {Math.round(weight * 100)}%</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};