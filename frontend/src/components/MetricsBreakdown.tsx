/**
 * MetricsBreakdown component for displaying individual analysis metrics
 */

import React from 'react';
import { Brain, Zap, Repeat, Link } from 'lucide-react';
import { ScoreDisplay } from './ScoreDisplay';
import type { GlobalScores } from '../types/analysis';

interface MetricsBreakdownProps {
  scores: GlobalScores;
}

export const MetricsBreakdown: React.FC<MetricsBreakdownProps> = ({ scores }) => {
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

  return (
    <div className="metrics-breakdown">
      <h4 className="breakdown-title">Component Scores</h4>
      <div className="metrics-list">
        {Object.entries(scores).map(([metric, score]) => (
          <div key={metric} className="metric-item">
            <div className="metric-header">
              <div className="metric-info">
                <div className="metric-icon">
                  {getMetricIcon(metric)}
                </div>
                <div className="metric-details">
                  <h5 className="metric-title">{getMetricTitle(metric)}</h5>
                  <p className="metric-explanation">{getMetricExplanation(metric)}</p>
                </div>
              </div>
              <div className="metric-score">
                <ScoreDisplay score={score} size="small" showPercentage={false} />
              </div>
            </div>
            
            {/* Progress bar */}
            <div className="metric-progress-bar">
              <div 
                className={`progress-fill ${score >= 0.7 ? 'high' : score >= 0.4 ? 'medium' : 'low'}`}
                style={{ width: `${score * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};