/**
 * NgramAnalysisModal component for displaying N-gram frequency analysis results
 */

import React, { useState } from 'react';
import type { NgramAnalysis, NgramItem } from '../types/analysis';

interface NgramAnalysisProps {
  ngramData: NgramAnalysis;
  onClose: () => void;
}

export const NgramAnalysisModal: React.FC<NgramAnalysisProps> = ({ ngramData, onClose }) => {
  const [activeNgramTab, setActiveNgramTab] = useState<'bigrams' | 'trigrams' | 'fourgrams'>('bigrams');

  const getScoreColor = (score: number): string => {
    if (score >= 0.7) return 'high';
    if (score >= 0.6) return 'medium';
    return 'low';
  };

  const renderNgramTable = (items: NgramItem[], title: string) => {
    // Filter and sort items, showing only top 10
    const significantItems = items
      .filter(item => item.score >= 0.6) // Only show yellow/red scores
      .sort((a, b) => b.score - a.score)
      .slice(0, 10);

    if (significantItems.length === 0) {
      return (
        <div className="no-significant-elements">
          No significant {title.toLowerCase()} patterns show evidence of AI-generated content.
        </div>
      );
    }

    return (
      <div className="ngram-table">
        <table>
          <thead>
            <tr>
              <th>Pattern</th>
              <th>Frequency</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {significantItems.map((item, index) => (
              <tr key={index}>
                <td className="ngram-text">{item.text}</td>
                <td className="ngram-frequency">{item.frequency}</td>
                <td>
                  <div className={`score-circle ${getScoreColor(item.score)}`}>
                    <span className={`score-percentage ${getScoreColor(item.score)}`}>
                      {Math.round(item.score * 100)}%
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {significantItems.length === 10 && (
          <div className="results-limit-notice">
            Showing top 10 results. Export report for complete analysis.
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="ngram-analysis-modal">
      <div className="ngram-modal-overlay" onClick={onClose}></div>
      <div className="ngram-modal-content">
        <div className="ngram-modal-header">
          <h3>N-gram Frequency Analysis</h3>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="ngram-tabs">
          <div className="ngram-tab-buttons">
            <button
              className={`tab-button ${activeNgramTab === 'bigrams' ? 'active' : ''}`}
              onClick={() => setActiveNgramTab('bigrams')}
            >
              2-grams
              <span className={`score-badge ${getScoreColor(ngramData.bigrams.score)}`}>
                {Math.round(ngramData.bigrams.score * 100)}%
              </span>
            </button>
            <button
              className={`tab-button ${activeNgramTab === 'trigrams' ? 'active' : ''}`}
              onClick={() => setActiveNgramTab('trigrams')}
            >
              3-grams
              <span className={`score-badge ${getScoreColor(ngramData.trigrams.score)}`}>
                {Math.round(ngramData.trigrams.score * 100)}%
              </span>
            </button>
            <button
              className={`tab-button ${activeNgramTab === 'fourgrams' ? 'active' : ''}`}
              onClick={() => setActiveNgramTab('fourgrams')}
            >
              4-grams
              <span className={`score-badge ${getScoreColor(ngramData.fourgrams.score)}`}>
                {Math.round(ngramData.fourgrams.score * 100)}%
              </span>
            </button>
          </div>

          <div className="ngram-tab-content">
            {activeNgramTab === 'bigrams' && (
              <div className="ngram-tab-panel">
                <h4>2-gram Pattern Analysis</h4>
                <p className="ngram-description">
                  Two-word sequences that appear frequently. High repetition may indicate AI-generated text.
                </p>
                {renderNgramTable(ngramData.bigrams.details, '2-gram')}
              </div>
            )}

            {activeNgramTab === 'trigrams' && (
              <div className="ngram-tab-panel">
                <h4>3-gram Pattern Analysis</h4>
                <p className="ngram-description">
                  Three-word sequences that appear frequently. More suspicious than 2-grams when repeated.
                </p>
                {renderNgramTable(ngramData.trigrams.details, '3-gram')}
              </div>
            )}

            {activeNgramTab === 'fourgrams' && (
              <div className="ngram-tab-panel">
                <h4>4-gram Pattern Analysis</h4>
                <p className="ngram-description">
                  Four-word sequences that appear frequently. Highly suspicious when repeated, as natural text rarely contains identical 4-word patterns.
                </p>
                {renderNgramTable(ngramData.fourgrams.details, '4-gram')}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};