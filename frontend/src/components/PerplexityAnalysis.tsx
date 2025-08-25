/**
 * PerplexityAnalysisModal component for displaying perplexity analysis insights
 */

import React from 'react';
import type { EnhancedAnalysisDetails } from '../types/analysis';

interface PerplexityAnalysisProps {
  perplexityData: EnhancedAnalysisDetails;
  onClose: () => void;
}

export const PerplexityAnalysisModal: React.FC<PerplexityAnalysisProps> = ({ perplexityData, onClose }) => {
  const getScoreColor = (score: number): string => {
    if (score >= 0.7) return 'high';
    if (score >= 0.6) return 'medium';
    return 'low';
  };

  // Extract detailed sentences from backend analysis
  const detailedSentences = perplexityData.detailed_sentences || [];
  const topSentences = detailedSentences.slice(0, 10); // Top 10 sentences

  return (
    <div className="analysis-modal">
      <div className="modal-overlay" onClick={onClose}></div>
      <div className="modal-content">
        <div className="modal-header">
          <h3>Perplexity Analysis Insights</h3>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <p className="modal-description">
            Top 10 sentences that most contributed to high predictability. Lower perplexity indicates more predictable text patterns typical of AI generation.
          </p>
          
          <div className="insights-list">
            {topSentences.length > 0 ? (
              topSentences.map((sentence, index) => (
                <div key={index} className="insight-item">
                  <div className="insight-content">
                    <div className="insight-text">{sentence.text}</div>
                    <div className="insight-impact">
                      <strong>Perplexity Score:</strong> {Math.round(sentence.perplexity_score * 100)}% | 
                      <strong> Stylistic Score:</strong> {Math.round(sentence.stylistic_score * 100)}% | 
                      <strong> Register Score:</strong> {Math.round(sentence.register_score * 100)}%
                    </div>
                    {sentence.impactful_parts && sentence.impactful_parts.length > 0 && (
                      <div className="impactful-parts">
                        <strong>Key Indicators:</strong>
                        {sentence.impactful_parts.map((part, partIndex) => (
                          <span key={partIndex} className={`highlighted-part ${getScoreColor(part.score)}`} title={part.explanation}>
                            {part.text}
                          </span>
                        ))}
                      </div>
                    )}
                    {sentence.evidence && (
                      <div className="evidence-details">
                        {sentence.evidence.suspicious_words && sentence.evidence.suspicious_words.length > 0 && (
                          <div className="evidence-item">
                            <strong>Suspicious words:</strong> {sentence.evidence.suspicious_words.join(', ')}
                          </div>
                        )}
                        {sentence.evidence.formulaic_phrases && sentence.evidence.formulaic_phrases.length > 0 && (
                          <div className="evidence-item">
                            <strong>Formulaic phrases:</strong> {sentence.evidence.formulaic_phrases.join(', ')}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className={`score-circle ${getScoreColor(sentence.score)}`}>
                    <span className={`score-percentage ${getScoreColor(sentence.score)}`}>
                      {Math.round(sentence.score * 100)}%
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-evidence">
                <div className="insight-item">
                  <div className="insight-content">
                    <div className="insight-text">GPT-2 Model Perplexity Analysis</div>
                    <div className="insight-impact">
                      <strong>Impact:</strong> Text predictability based on language model expectations
                    </div>
                  </div>
                  <div className={`score-circle ${getScoreColor(perplexityData.overall_score)}`}>
                    <span className={`score-percentage ${getScoreColor(perplexityData.overall_score)}`}>
                      {Math.round(perplexityData.overall_score * 100)}%
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <div className="analysis-summary">
            <strong>Overall Perplexity Score:</strong> {Math.round(perplexityData.overall_score * 100)}%
            <br />
            <small>Higher scores indicate more predictable, potentially AI-generated patterns.</small>
          </div>
        </div>
      </div>
    </div>
  );
};