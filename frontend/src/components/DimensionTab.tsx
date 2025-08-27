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
  FileText
} from 'lucide-react';
import { getScoreLevel } from '../utils/colorUtils';

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

// Helper function to extract score from evidence




export const DimensionTab: React.FC<DimensionTabProps> = ({
  dimensionId,
  result,
  dimensionName,
  description,
  scoreInterpretation
}) => {
  const Icon = getDimensionIcon(dimensionId);

  const scoreLevel = getScoreLevel(result.score);
  
  // Ora il backend filtra già le evidenze, quindi usiamo direttamente quelle ricevute
  
  return (
    <div className="dimension-tab">
      {/* Dimension Header */}
      <div className="dimension-tab-header">
        <div className="dimension-info">
          <div className="dimension-title">
            <Icon size={28} className={`dimension-icon ${scoreLevel}`} />
            <h2>{dimensionName}</h2>
          </div>
          <div className="dimension-evidence-count">
            Evidences found: <strong>{(result.evidences || []).length}</strong>
          </div>
          <p className="dimension-description">{description}</p>
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
          evidences={result.evidences || []}
          maxLength={300}
        />
      </div>
    </div>
  );
};