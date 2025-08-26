/**
 * DimensionCard component for displaying individual analysis dimension
 * Used in the main 7x1 grid layout
 */

import React from 'react';
import { 
  Brain, 
  Shuffle, 
  Network, 
  RotateCcw, 
  BookOpen, 
  PenTool, 
  FileText,
  ToggleLeft,
  ToggleRight
} from 'lucide-react';
import { getScoreLevel, getScoreLabel } from '../utils/colorUtils';
import type { AnalysisDimension, DimensionAnalysisResult, DimensionToggleSettings } from '../types/analysis';

interface DimensionCardProps {
  dimension: AnalysisDimension;
  result?: DimensionAnalysisResult;
  onToggle: (dimensionId: keyof DimensionToggleSettings, enabled: boolean) => void;
  onCardClick?: (dimensionId: string) => void;
  isClickable?: boolean;
}

const getIcon = (iconName: string) => {
  switch (iconName) {
    case 'Brain': return Brain;
    case 'Shuffle': return Shuffle;
    case 'Network': return Network;
    case 'RotateCcw': return RotateCcw;
    case 'BookOpen': return BookOpen;
    case 'PenTool': return PenTool;
    case 'FileText': return FileText;
    default: return Brain;
  }
};



const getIconLevelClass = (atomicLevel: string): string => {
  switch (atomicLevel) {
    case 'sentence': return 'sentence-level';
    case 'paragraph': return 'paragraph-level';
    case 'global': return 'global-level';
    default: return 'sentence-level';
  }
};

const getClearDescription = (dimensionId: string): string => {
  const descriptions: Record<string, string> = {
    perplexity: 'Measures how predictable your text is. Natural human writing tends to be less predictable.',
    burstiness: 'Checks if sentence lengths vary naturally. Humans write with more variation than AI.',
    semantic_coherence: 'Analyzes if ideas flow logically from one sentence to the next.',
    ngram_repetition: 'Looks for repetitive word patterns that AI systems often produce.',
    lexical_richness: 'Measures vocabulary diversity - how many different words you use.',
    stylistic_markers: 'Detects unusual writing patterns in punctuation and word choices.',
    readability: 'Evaluates if the text reads naturally and is appropriately complex.'
  };
  return descriptions[dimensionId] || 'Analysis dimension for AI detection.';
};

export const DimensionCard: React.FC<DimensionCardProps> = ({
  dimension,
  result,
  onToggle,
  onCardClick,
  isClickable = false
}) => {
  const Icon = getIcon(dimension.icon);
  const isActive = dimension.enabled;
  const hasResult = result && isActive;
  const score = hasResult ? result.score : 0;
  const weight = hasResult ? result.weight : dimension.weight;
  const evidenceCount = hasResult ? result.totalEvidences : 0;
  const scoreLevel = hasResult ? getScoreLevel(score) : 'low';

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    onToggle(dimension.id as keyof DimensionToggleSettings, !dimension.enabled);
  };

  const handleCardClick = () => {
    if (isClickable && onCardClick && hasResult) {
      onCardClick(dimension.id);
    }
  };

  return (
    <div className="dimension-card-wrapper">
      {/* Toggle button positioned outside and to the left of dimension container */}
      <div className="dimension-toggle-external">
        <button 
          className={`toggle-button-external ${isActive ? 'active' : 'inactive'}`}
          onClick={handleToggle}
          title={`${isActive ? 'Disable' : 'Enable'} ${dimension.name} analysis`}
        >
          {isActive ? <ToggleRight size={24} /> : <ToggleLeft size={24} />}
        </button>
      </div>
      
      {/* Dimension container - compact and reduced height */}
      <div 
        className={`dimension-card-compact ${isActive ? 'active' : 'inactive'} ${isClickable && hasResult ? 'clickable' : ''}`}
        onClick={handleCardClick}
      >
        <div className="dimension-compact-content">
          {/* Left: Icon and Name */}
          <div className="dimension-left-compact">
            <div className={`dimension-icon-small ${getIconLevelClass(dimension.atomicLevel)}`}>
              <Icon size={40} className={`dimension-icon ${isActive ? 'active' : 'inactive'}`} />
            </div>
            <h4 className="dimension-name-compact">{dimension.name}</h4>
          </div>
          
          {/* Center: Description */}
          <div className="dimension-center-compact">
            <p className="dimension-description-compact">{getClearDescription(dimension.id)}</p>
            
            {hasResult && (
              <div className="dimension-score-inline">
                <span className={`score-value-small ${scoreLevel}`}>
                  {Math.round(score * 100)}%
                </span>
                <span className={`score-label-small ${scoreLevel}`}>
                  {getScoreLabel(score)}
                </span>
              </div>
            )}
          </div>
          
          {/* Right: Compact Labels */}
          <div className="dimension-labels-inline">
            <span className={`dimension-label-mini granularity-label ${getIconLevelClass(dimension.atomicLevel)}`}>
              {dimension.atomicLevel}
            </span>
            <span className="dimension-label-mini weight-label">
              {Math.round(weight * 100)}%
            </span>
            {hasResult && evidenceCount > 0 && (
              <span className="dimension-label-mini evidence-label">
                {evidenceCount}
              </span>
            )}
          </div>
        </div>
        
        {isClickable && hasResult && evidenceCount > 0 && (
          <div className="dimension-click-hint">
            Click for details →
          </div>
        )}
      </div>
    </div>
  );
};