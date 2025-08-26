/**
 * AnalysisResults component for displaying comprehensive analysis results
 * Now uses dimension-based tabs (7 dimensions + overview)
 */

import React, { useState } from 'react';
import { 
  BarChart3, 
  Brain, 
  Shuffle, 
  Network, 
  RotateCcw, 
  BookOpen, 
  PenTool, 
  FileText 
} from 'lucide-react';
import { OverviewTab } from './OverviewTab';
import { DimensionTab } from './DimensionTab';
import type { AnalysisResult, DimensionToggleSettings, GlobalScores } from '../types/analysis';

interface AnalysisResultsProps {
  result: AnalysisResult;
  enabledDimensions: DimensionToggleSettings;
}

type TabType = 'overview' | keyof GlobalScores;

const DIMENSION_INFO = {
  perplexity: {
    name: 'Perplexity',
    description: 'Analyzes text predictability using language model patterns to detect statistical likelihood',
    icon: Brain,
    atomicLevel: 'sentence',
    scoreInterpretation: 'Low = more natural, High = more likely artificial'
  },
  burstiness: {
    name: 'Burstiness',
    description: 'Measures variability in sentence lengths within paragraphs using coefficient of variation',
    icon: Shuffle,
    atomicLevel: 'paragraph',
    scoreInterpretation: 'Very low = monotonous, Very high = unnatural oscillation'
  },
  semantic_coherence: {
    name: 'Semantic Coherence',
    description: 'Evaluates logical flow between text segments using sentence embeddings and cosine similarity',
    icon: Network,
    atomicLevel: 'paragraph',
    scoreInterpretation: 'High = coherent flow, Low = abrupt topic shifts'
  },
  ngram_repetition: {
    name: 'N-gram Repetition',
    description: 'Detects unusual repetition of word sequences and analyzes diversity patterns',
    icon: RotateCcw,
    atomicLevel: 'global',
    scoreInterpretation: 'High repetition = suspicious of artificiality'
  },
  lexical_richness: {
    name: 'Lexical Richness',
    description: 'Measures vocabulary variety using Type-Token Ratio analysis',
    icon: BookOpen,
    atomicLevel: 'sentence',
    scoreInterpretation: 'Low = repetitive/poor vocabulary, High = rich'
  },
  stylistic_markers: {
    name: 'Stylistic Markers',
    description: 'Identifies unusual stylistic patterns in punctuation, POS tags, and word usage',
    icon: PenTool,
    atomicLevel: 'sentence',
    scoreInterpretation: 'Deviations from balanced style = possible artificial generation'
  },
  readability: {
    name: 'Readability',
    description: 'Measures natural readability using Flesch Reading Ease and complexity metrics',
    icon: FileText,
    atomicLevel: 'sentence',
    scoreInterpretation: 'Very high = too simplistic, Very low = too complex'
  }
} as const;

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ 
  result, 
  enabledDimensions
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  // Get all available dimension tabs (not just active ones)
  const allDimensionTabs: (keyof GlobalScores)[] = [
    'perplexity', 'burstiness', 'semantic_coherence', 'ngram_repetition', 
    'lexical_richness', 'stylistic_markers', 'readability'
  ];

  // Function removed - dimension clicking is handled directly in tab buttons

  const generatePDFReport = async () => {
    try {
      // Prepare complete analysis data for PDF export
      const reportData = {
        overview: {
          overall_score: result.overall_score,
          global_scores: result.global_scores,
          dimension_results: result.dimension_results,
          metadata: result.analysis_metadata
        },
        dimensions: result.dimension_results || {},
        weights_applied: result.weights_applied || {},
        active_dimensions: result.active_dimensions || []
      };

      // Call backend API to generate PDF
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/export-pdf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(reportData),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `origo-analysis-report-${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        console.error('Failed to generate PDF report');
        alert('Failed to generate PDF report. Please try again.');
      }
    } catch (error) {
      console.error('Error generating PDF report:', error);
      alert('Error generating PDF report. Please try again.');
    }
  };

  return (
    <div className="analysis-results-container">
      <div className="analysis-results">
        {/* Analysis Tabs */}
        <div className="analysis-tabs">
          <div className="tab-buttons">
            {/* Overview Tab */}
            <div className="tab-button-wrapper">
              <div className="overview-score-above">
                {Math.round(result.overall_score * 100)}%
              </div>
              <button
                className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                <BarChart3 size={16} />
                <span className="tab-text">Overview</span>
              </button>
            </div>
            
            {/* All Dimension Tabs */}
            {allDimensionTabs.map((dimensionId) => {
              const dimensionInfo = DIMENSION_INFO[dimensionId];
              const Icon = dimensionInfo.icon;
              const dimensionResult = result.dimension_results?.[dimensionId];
              const evidenceCount = dimensionResult?.totalEvidences || 0;
              const isEnabled = enabledDimensions[dimensionId];
              const dimensionScore = result.global_scores?.[dimensionId] || 0;
              const getScoreLevel = (score: number) => {
                if (score <= 0.3) return 'score-low';
                if (score <= 0.6) return 'score-medium';
                return 'score-high';
              };
              const scoreLevel = getScoreLevel(dimensionScore);
              
              return (
                <div key={dimensionId} className="tab-button-wrapper">
                  {/* Dimension score above tab */}
                  <div className={`dimension-score-above ${scoreLevel} ${!isEnabled ? 'disabled' : ''}`}>
                    {isEnabled ? `${Math.round(dimensionScore * 100)}%` : '--'}
                  </div>
                  <button
                    className={`tab-button ${activeTab === dimensionId ? 'active' : ''} ${!isEnabled ? 'disabled' : ''}`}
                    onClick={() => setActiveTab(dimensionId)}
                    title={`${dimensionInfo.name}${!isEnabled ? ' (disabled)' : ''}`}
                    disabled={!isEnabled}
                  >
                    <Icon size={16} />
                    <span className="tab-text">{dimensionInfo.name}</span>
                    {isEnabled && evidenceCount > 0 && (
                      <span className="evidence-badge">{evidenceCount}</span>
                    )}
                  </button>
                </div>
              );
            })}
            
          </div>

          <div className="tab-content">
            {activeTab === 'overview' ? (
              <OverviewTab
                result={result}
                onExportReport={generatePDFReport}
              />
            ) : (
              // Render dimension-specific tab
              (() => {
                const dimensionResult = result.dimension_results?.[activeTab as keyof GlobalScores];
                const dimensionInfo = DIMENSION_INFO[activeTab as keyof GlobalScores];
                const isEnabled = enabledDimensions[activeTab as keyof GlobalScores];
                
                if (!isEnabled) {
                  return (
                    <div className="dimension-disabled">
                      <h3>Dimension Disabled</h3>
                      <p>This dimension was not included in the analysis. Enable it in the configuration to see results.</p>
                    </div>
                  );
                }
                
                if (!dimensionResult || !dimensionInfo) {
                  return (
                    <div className="dimension-error">
                      <h3>No Data Available</h3>
                      <p>Analysis data for this dimension is not available.</p>
                    </div>
                  );
                }
                
                return (
                  <DimensionTab
                    dimensionId={activeTab as keyof GlobalScores}
                    result={dimensionResult}
                    dimensionName={dimensionInfo.name}
                    description={dimensionInfo.description}
                    scoreInterpretation={dimensionInfo.scoreInterpretation}
                    atomicLevel={dimensionInfo.atomicLevel}
                  />
                );
              })()
            )}
          </div>
        </div>
      </div>
    </div>
  );
};