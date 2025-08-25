/**
 * SemanticAnalysisModal component for displaying semantic coherence analysis insights
 */

import React from 'react';
import type { EnhancedAnalysisDetails } from '../types/analysis';

interface SemanticAnalysisProps {
  semanticData: EnhancedAnalysisDetails;
  onClose: () => void;
}

export const SemanticAnalysisModal: React.FC<SemanticAnalysisProps> = ({ semanticData, onClose }) => {
  const getScoreColor = (score: number): string => {
    if (score >= 0.7) return 'high';
    if (score >= 0.6) return 'medium';
    return 'low';
  };

  // Extract detailed evidence from backend analysis
  const detailedEvidence = semanticData.detailed_evidence || {
    coherence_patterns: [],
    flow_analysis: { flow_uniformity: 0.5, transitions: [], avg_consecutive_similarity: 0.5 },
    topic_clusters: [],
    repetition_evidence: [],
    summary: { overall_coherence: 0.5, ai_likelihood: 0.5, analysis_confidence: 'low', evidence_count: 0, primary_indicators: [] }
  };
  const coherencePatterns = detailedEvidence.coherence_patterns || [];
  const flowAnalysis = detailedEvidence.flow_analysis || { flow_uniformity: 0.5, transitions: [], avg_consecutive_similarity: 0.5 };
  const topicClusters = detailedEvidence.topic_clusters || [];
  const repetitionEvidence = detailedEvidence.repetition_evidence || [];
  const summary = detailedEvidence.summary || { overall_coherence: 0.5, ai_likelihood: 0.5, analysis_confidence: 'low', evidence_count: 0, primary_indicators: [] };

  return (
    <div className="analysis-modal">
      <div className="modal-overlay" onClick={onClose}></div>
      <div className="modal-content">
        <div className="modal-header">
          <h3>Semantic Coherence Analysis</h3>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <p className="modal-description">
            Semantic coherence analysis using advanced NLP techniques. Evidence of patterns that may indicate artificial generation.
          </p>
          
          <div className="semantic-insights-list">
            {/* Coherence Patterns */}
            {coherencePatterns.length > 0 && (
              <div className="semantic-section">
                <h4>High Coherence Segments</h4>
                {coherencePatterns.map((pattern: any, index: number) => (
                  <div key={index} className="semantic-insight-item">
                    <div className="insight-header">
                      <div className="insight-title">
                        Sentences {pattern.start_sentence + 1}-{pattern.end_sentence + 1}
                      </div>
                      <div className={`score-circle ${getScoreColor(pattern.ai_likelihood)}`}>
                        <span className={`score-percentage ${getScoreColor(pattern.ai_likelihood)}`}>
                          {Math.round(pattern.ai_likelihood * 100)}%
                        </span>
                      </div>
                    </div>
                    <div className="insight-content">
                      <div className="insight-evidence">{pattern.evidence}</div>
                      <div className="insight-sentences">
                        {pattern.sentences.map((sentence: string, sentIndex: number) => (
                          <div key={sentIndex} className="evidence-sentence">
                            {sentence.length > 150 ? sentence.substring(0, 150) + '...' : sentence}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Topic Clusters */}
            {topicClusters.length > 0 && (
              <div className="semantic-section">
                <h4>Topic Clusters</h4>
                {topicClusters.map((cluster: any, index: number) => (
                  <div key={index} className="semantic-insight-item">
                    <div className="insight-header">
                      <div className="insight-title">
                        {cluster.id} ({cluster.size} sentences)
                      </div>
                      <div className={`score-circle ${getScoreColor(cluster.ai_likelihood)}`}>
                        <span className={`score-percentage ${getScoreColor(cluster.ai_likelihood)}`}>
                          {Math.round(cluster.ai_likelihood * 100)}%
                        </span>
                      </div>
                    </div>
                    <div className="insight-content">
                      <div className="insight-evidence">{cluster.evidence}</div>
                      <div className="cluster-stats">
                        <strong>Avg Similarity:</strong> {(cluster.avg_similarity * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Semantic Repetitions */}
            {repetitionEvidence.length > 0 && (
              <div className="semantic-section">
                <h4>Semantic Repetitions</h4>
                {repetitionEvidence.map((repetition: any, index: number) => (
                  <div key={index} className="semantic-insight-item">
                    <div className="insight-header">
                      <div className="insight-title">
                        Similar Ideas Detected
                      </div>
                      <div className={`score-circle ${getScoreColor(repetition.ai_likelihood)}`}>
                        <span className={`score-percentage ${getScoreColor(repetition.ai_likelihood)}`}>
                          {Math.round(repetition.similarity * 100)}%
                        </span>
                      </div>
                    </div>
                    <div className="insight-content">
                      <div className="insight-evidence">{repetition.evidence}</div>
                      <div className="repetition-sentences">
                        <div className="evidence-sentence">
                          <strong>Sentence {repetition.sentence_1_index + 1}:</strong> {repetition.sentence_1}
                        </div>
                        <div className="evidence-sentence">
                          <strong>Sentence {repetition.sentence_2_index + 1}:</strong> {repetition.sentence_2}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Flow Analysis */}
            {flowAnalysis.transitions && flowAnalysis.transitions.length > 0 && (
              <div className="semantic-section">
                <h4>Semantic Flow Analysis</h4>
                <div className="semantic-insight-item">
                  <div className="insight-header">
                    <div className="insight-title">
                      Flow Uniformity: {(flowAnalysis.flow_uniformity * 100).toFixed(1)}%
                    </div>
                    <div className={`score-circle ${getScoreColor(flowAnalysis.flow_uniformity)}`}>
                      <span className={`score-percentage ${getScoreColor(flowAnalysis.flow_uniformity)}`}>
                        {Math.round(flowAnalysis.flow_uniformity * 100)}%
                      </span>
                    </div>
                  </div>
                  <div className="insight-content">
                    <div className="flow-transitions">
                      {flowAnalysis.transitions && flowAnalysis.transitions.slice(0, 3).map((transition: any, index: number) => (
                        <div key={index} className="transition-item">
                          <div className="transition-evidence">{transition.evidence}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Default fallback */}
            {coherencePatterns.length === 0 && topicClusters.length === 0 && repetitionEvidence.length === 0 && (
              <div className="semantic-insight-item">
                <div className="insight-header">
                  <h4>Overall Semantic Coherence</h4>
                  <div className={`score-circle ${getScoreColor(semanticData.overall_score)}`}>
                    <span className={`score-percentage ${getScoreColor(semanticData.overall_score)}`}>
                      {Math.round(semanticData.overall_score * 100)}%
                    </span>
                  </div>
                </div>
                
                <div className="insight-content">
                  <div className="insight-description">
                    <strong>Analysis:</strong> Combined semantic analysis using Sentence-BERT embeddings
                  </div>
                  
                  <div className="insight-interpretation">
                    <strong>Interpretation:</strong> Measures overall semantic consistency and coherence patterns
                  </div>
                  
                  <div className={`insight-analysis ${getScoreColor(semanticData.overall_score)}`}>
                    <strong>Result:</strong> Text shows {semanticData.overall_score > 0.7 ? 'high' : semanticData.overall_score > 0.4 ? 'moderate' : 'low'} semantic coherence
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <div className="analysis-summary">
            <strong>Overall Semantic Score:</strong> {Math.round(semanticData.overall_score * 100)}%
            {summary.analysis_confidence && (
              <>
                <br />
                <strong>Analysis Confidence:</strong> {summary.analysis_confidence}
                {summary.evidence_count && (
                  <>, {summary.evidence_count} evidence items found</>
                )}
              </>
            )}
            <br />
            <small>Higher scores may indicate artificial coherence patterns typical of AI models.</small>
          </div>
        </div>
      </div>
    </div>
  );
};