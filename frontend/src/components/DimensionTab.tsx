/**
 * DimensionTab component for displaying individual dimension analysis results
 * Shows top 10 evidences for each dimension
 */

import React from 'react';
import { EvidenceDisplay } from './EvidenceDisplay';
import { 
  Brain, 
  Shuffle, 
  Network, 
  RotateCcw, 
  BookOpen, 
  PenTool, 
  FileText,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react';
import { getScoreLevel, getScoreDescription } from '../utils/colorUtils';
import type { DimensionAnalysisResult, GlobalScores } from '../types/analysis';

interface DimensionTabProps {
  dimensionId: keyof GlobalScores;
  result: DimensionAnalysisResult;
  dimensionName: string;
  description: string;
  scoreInterpretation: string;
  atomicLevel: string;
}

const getDimensionIcon = (dimensionId: keyof GlobalScores) => {
  switch (dimensionId) {
    case 'perplexity': return Brain;
    case 'burstiness': return Shuffle;
    case 'semantic_coherence': return Network;
    case 'ngram_repetition': return RotateCcw;
    case 'lexical_richness': return BookOpen;
    case 'stylistic_markers': return PenTool;
    case 'readability': return FileText;
    default: return Brain;
  }
};



const getScoreIcon = (score: number) => {
  if (score <= 0.3) return TrendingDown;
  if (score <= 0.6) return Minus;
  return TrendingUp;
};



export const DimensionTab: React.FC<DimensionTabProps> = ({
  dimensionId,
  result,
  dimensionName,
  description,
  scoreInterpretation,
  atomicLevel
}) => {
  const Icon = getDimensionIcon(dimensionId);
  const ScoreIcon = getScoreIcon(result.score);
  const scoreLevel = getScoreLevel(result.score);
  
  return (
    <div className="dimension-tab">
      {/* Dimension Header */}
      <div className="dimension-tab-header">
        <div className="dimension-info">
          <div className="dimension-title">
            <Icon size={28} className={`dimension-icon ${scoreLevel}`} />
            <h2>{dimensionName}</h2>
          </div>
          <p className="dimension-description">{description}</p>
        </div>
        
        <div className="dimension-score-summary">
          <div className={`score-badge ${scoreLevel}`}>
            <ScoreIcon size={20} />
            <span className="score-value">{Math.round(result.score * 100)}%</span>
          </div>
          <div className="score-description">
            {getScoreDescription(result.score)}
          </div>
        </div>
      </div>

      {/* Dimension Stats */}
      <div className="dimension-stats">
        <div className="stat-grid">
          <div className="stat-item">
            <span className="stat-label">Analysis Level</span>
            <span className="stat-value">{atomicLevel}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Weight Applied</span>
            <span className="stat-value">{Math.round(result.weight * 100)}%</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Contribution</span>
            <span className="stat-value">
              {Math.round(result.score * result.weight * 100)}%
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Total Evidences</span>
            <span className="stat-value">{result.totalEvidences}</span>
          </div>
        </div>
      </div>

      {/* Score Interpretation */}
      <div className="score-interpretation">
        <h4>Score Interpretation</h4>
        <p>{scoreInterpretation}</p>
      </div>

      {/* Evidence Display */}
      <div className="dimension-evidences">
        <EvidenceDisplay
          evidences={result.topEvidences}
          title={`Top ${Math.min(result.topEvidences.length, 10)} Evidence${result.topEvidences.length !== 1 ? 's' : ''}`}
          maxLength={300}
        />
        
        {result.totalEvidences > result.topEvidences.length && (
          <div className="additional-evidences-notice">
            <p>
              <strong>{result.totalEvidences - result.topEvidences.length} additional evidence(s)</strong> 
              {' '}available in the complete analysis. 
              Export the full report to view all findings.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};