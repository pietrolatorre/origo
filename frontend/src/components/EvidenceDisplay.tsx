/**
 * EvidenceDisplay component for showing analysis evidences
 * Supports different evidence types with appropriate styling
 */

import React from 'react';
import { AlertTriangle, Info } from 'lucide-react';
import { getScoreLevel } from '../utils/colorUtils';
import type { Evidence } from '../types/analysis';

interface EvidenceDisplayProps {
  evidences: Evidence[];
  title: string;
  maxLength?: number;
}

const formatEvidenceText = (text: string, maxLength: number = 200): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

const renderEvidenceContent = (evidence: Evidence, maxLength: number) => {
  switch (evidence.type) {
    case 'sentence':
      if ('score' in evidence) {
        return (
          <div className="evidence-content-simplified">
            <div className="evidence-text-main">
              {formatEvidenceText(evidence.text, maxLength)}
            </div>
            <div className={`evidence-score-prominent ${getScoreLevel(evidence.score)}`}>
              {Math.round(evidence.score * 100)}%
            </div>
          </div>
        );
      }
      break;
      
    case 'paragraph':
      if ('score' in evidence) {
        return (
          <div className="evidence-content-simplified">
            <div className="evidence-text-main">
              {formatEvidenceText(evidence.text, maxLength)}
            </div>
            <div className={`evidence-score-prominent ${getScoreLevel(evidence.score)}`}>
              {Math.round(evidence.score * 100)}%
            </div>
          </div>
        );
      }
      break;
      
    case 'paragraph_pair':
      if ('similarity' in evidence) {
        return (
          <div className="evidence-content-simplified">
            <div className="evidence-text-main">
              <div className="paragraph-part">
                <strong>Paragraph 1:</strong> {formatEvidenceText(evidence.paragraph1, maxLength / 2)}
              </div>
              <div className="paragraph-part">
                <strong>Paragraph 2:</strong> {formatEvidenceText(evidence.paragraph2, maxLength / 2)}
              </div>
            </div>
            <div className={`evidence-score-prominent ${getScoreLevel(1 - evidence.similarity)}`}>
              {Math.round((1 - evidence.similarity) * 100)}%
            </div>
          </div>
        );
      }
      break;
      
    case 'ngram':
      if ('frequency' in evidence) {
        return (
          <div className="evidence-content-simplified">
            <div className="evidence-text-main">
              <span className="ngram-text-highlighted">"{evidence.text}"</span>
              <span className="ngram-frequency">({evidence.frequency} times)</span>
            </div>
            <div className={`evidence-score-prominent ${getScoreLevel(evidence.repetitionRate)}`}>
              {Math.round(evidence.repetitionRate * 100)}%
            </div>
          </div>
        );
      }
      break;
      
    default:
      return (
        <div className="evidence-content-simplified">
          <div className="evidence-text-main">
            {JSON.stringify(evidence, null, 2)}
          </div>
        </div>
      );
  }
  
  return null;
};

export const EvidenceDisplay: React.FC<EvidenceDisplayProps> = ({
  evidences,
  title,
  maxLength = 200
}) => {
  if (!evidences || evidences.length === 0) {
    return (
      <div className="evidence-display empty">
        <div className="empty-state">
          <Info size={32} className="empty-icon" />
          <h4>No Evidence Found</h4>
          <p>This dimension shows no significant patterns suggesting AI generation.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="evidence-display">
      <div className="evidence-header-section">
        <h3 className="evidence-title">
          {title.replace(/\s*\(\d+\s+evidences?\)$/, '')}
        </h3>
        
        {evidences.length === 10 && (
          <div className="evidence-notice">
            <AlertTriangle size={16} />
            <span>Showing top 10 results. Export report for complete analysis.</span>
          </div>
        )}
      </div>

      <div className="evidence-list">
        {evidences.map((evidence, index) => (
          <div 
            key={index}
            className={`evidence-item ${evidence.type}`}
          >
            <div className="evidence-rank">
              #{index + 1}
            </div>
            {renderEvidenceContent(evidence, maxLength)}
          </div>
        ))}
      </div>
    </div>
  );
};