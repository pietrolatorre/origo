/**
 * AnalysisDimensions component for controlling which analysis dimensions to include
 */

import React from 'react';
import { Brain, Shuffle, Network, RotateCcw } from 'lucide-react';
import type { AnalysisDimension, DimensionToggleSettings } from '../types/analysis';

interface AnalysisDimensionsProps {
  dimensions: DimensionToggleSettings;
  onDimensionToggle: (dimensionId: keyof DimensionToggleSettings, enabled: boolean) => void;
}

const ANALYSIS_DIMENSIONS: AnalysisDimension[] = [
  {
    id: 'perplexity',
    name: 'Perplexity',
    description: 'Analyzes text predictability using GPT-2 language model patterns',
    icon: 'Brain',
    enabled: true
  },
  {
    id: 'burstiness',
    name: 'Burstiness',
    description: 'Examines sentence structure variation and linguistic diversity',
    icon: 'Shuffle',
    enabled: true
  },
  {
    id: 'semantic_coherence',
    name: 'Semantic Coherence',
    description: 'Evaluates meaning consistency and topic flow throughout text',
    icon: 'Network',
    enabled: true
  },
  {
    id: 'ngram_similarity',
    name: 'N-gram Similarity',
    description: 'Detects repetitive patterns and phrase frequency anomalies',
    icon: 'RotateCcw',
    enabled: true
  }
];

const getIcon = (iconName: string) => {
  switch (iconName) {
    case 'Brain': return Brain;
    case 'Shuffle': return Shuffle;
    case 'Network': return Network;
    case 'RotateCcw': return RotateCcw;
    default: return Brain;
  }
};

export const AnalysisDimensions: React.FC<AnalysisDimensionsProps> = ({
  dimensions,
  onDimensionToggle
}) => {
  return (
    <div className="analysis-dimensions">
      <div className="dimensions-grid">
        {ANALYSIS_DIMENSIONS.map((dimension) => {
          const Icon = getIcon(dimension.icon);
          const isEnabled = dimensions[dimension.id];
          
          return (
            <div 
              key={dimension.id}
              className={`dimension-card ${isEnabled ? 'enabled' : 'disabled'}`}
            >
              <div className="dimension-toggle">
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={isEnabled}
                    onChange={(e) => onDimensionToggle(dimension.id, e.target.checked)}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>
              
              <div className="dimension-content">
                <div className="dimension-header">
                  <div className="dimension-icon">
                    <Icon size={20} />
                  </div>
                  <h4 className="dimension-name">{dimension.name}</h4>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};