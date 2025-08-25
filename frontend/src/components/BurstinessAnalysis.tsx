/**
 * BurstinessAnalysisModal component for displaying burstiness analysis insights
 */

import React from 'react';
import type { EnhancedAnalysisDetails } from '../types/analysis';

interface BurstinessAnalysisProps {
  burstinessData: EnhancedAnalysisDetails;
  onClose: () => void;
}

export const BurstinessAnalysisModal: React.FC<BurstinessAnalysisProps> = ({ burstinessData, onClose }) => {
  const getScoreColor = (score: number): string => {
    if (score >= 0.7) return 'high';
    if (score >= 0.6) return 'medium';
    return 'low';
  };

  // Extract sentence clusters from backend analysis
  const sentenceClusters = burstinessData.sentence_clusters?.clusters || [];
  const clusterSummary = burstinessData.sentence_clusters?.summary || {
    total_clusters: 0,
    clustering_rate: 0,
    uniformity_score: 0,
    ai_likelihood: 0,
    dominant_patterns: []
  };

  return (
    <div className="analysis-modal">
      <div className="modal-overlay" onClick={onClose}></div>
      <div className="modal-content">
        <div className="modal-header">
          <h3>Burstiness Analysis Insights</h3>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <p className="modal-description">
            Clusters of sentences with similar structures and lengths. Uniform patterns may indicate AI generation.
          </p>
          
          <div className="clusters-list">
            {sentenceClusters.length > 0 ? (
              sentenceClusters.map((cluster, index) => (
                <div key={index} className="cluster-item">
                  <div className="cluster-header">
                    <h4>{cluster.id} ({cluster.sentence_count} sentences)</h4>
                    <div className={`score-circle ${getScoreColor(cluster.ai_likelihood)}`}>
                      <span className={`score-percentage ${getScoreColor(cluster.ai_likelihood)}`}>
                        {Math.round(cluster.ai_likelihood * 100)}%
                      </span>
                    </div>
                  </div>
                  <div className="cluster-pattern">
                    <strong>Pattern:</strong> {cluster.structure_signature}
                  </div>
                  <div className="cluster-statistics">
                    <div className="stat-item">
                      <strong>Avg Length:</strong> {cluster.statistics.avg_length.toFixed(1)} words
                    </div>
                    <div className="stat-item">
                      <strong>Length Variance:</strong> {(cluster.statistics.length_variance * 100).toFixed(1)}%
                    </div>
                    <div className="stat-item">
                      <strong>Start Pattern:</strong> {cluster.statistics.dominant_start_pattern}
                    </div>
                    <div className="stat-item">
                      <strong>Pattern Repetition:</strong> {(cluster.statistics.pattern_repetition_rate * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div className="cluster-sentences">
                    <strong>Sample sentences:</strong>
                    {cluster.sentences.slice(0, 3).map((sentence, sentIndex) => (
                      <div key={sentIndex} className={`sentence-example ${getScoreColor(cluster.ai_likelihood)}`}>
                        {sentence.text.length > 120 ? sentence.text.substring(0, 120) + '...' : sentence.text}
                        <span className="sentence-stats">
                          ({sentence.length} words, complexity: {sentence.complexity.toFixed(2)})
                        </span>
                      </div>
                    ))}
                    {cluster.sentences.length > 3 && (
                      <div className="more-sentences">
                        ...and {cluster.sentences.length - 3} more sentences
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="no-clusters">
                <div className="cluster-item">
                  <div className="cluster-header">
                    <h4>Sentence Structure Analysis</h4>
                    <div className={`score-circle ${getScoreColor(burstinessData.overall_score)}`}>
                      <span className={`score-percentage ${getScoreColor(burstinessData.overall_score)}`}>
                        {Math.round(burstinessData.overall_score * 100)}%
                      </span>
                    </div>
                  </div>
                  <div className="cluster-pattern">
                    <strong>Pattern:</strong> Analysis of sentence length and complexity variations
                  </div>
                  <div className="cluster-sentences">
                    <div className={`sentence-example ${getScoreColor(burstinessData.overall_score)}`}>
                      Text shows variation in sentence structure and length patterns
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <div className="analysis-summary">
            <strong>Overall Burstiness Score:</strong> {Math.round(burstinessData.overall_score * 100)}%
            {clusterSummary.total_clusters > 0 && (
              <>
                <br />
                <strong>Clustering Analysis:</strong> {clusterSummary.total_clusters} clusters found, 
                {(clusterSummary.clustering_rate * 100).toFixed(1)}% clustering rate, 
                {(clusterSummary.uniformity_score * 100).toFixed(1)}% uniformity
              </>
            )}
            <br />
            <small>Higher scores indicate more uniform patterns typical of AI-generated text.</small>
          </div>
        </div>
      </div>
    </div>
  );
};