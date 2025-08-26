/**
 * OverviewTab component for displaying overall analysis results
 * Redesigned with improved score visualization and structured statistics
 */

import React from 'react';
import { Download } from 'lucide-react';
import { getScoreLevel } from '../utils/colorUtils';
import type { AnalysisResult } from '../types/analysis';

interface OverviewTabProps {
  result: AnalysisResult;
  onExportReport?: () => void;
}

// Function removed - no longer needed with new design

const formatProcessingTime = (seconds?: number): string => {
  if (!seconds) return 'N/A';
  if (seconds < 1) return `${Math.round(seconds * 1000)}ms`;
  return `${seconds.toFixed(1)}s`;
};

export const OverviewTab: React.FC<OverviewTabProps> = ({
  result,
  onExportReport
}) => {
  const scoreLevel = getScoreLevel(result.overall_score);

  return (
    <div className="overview-tab-redesigned">
      {/* Ultra Prominent Global Score Section */}
      <div className="global-score-ultra-prominent">
        <div className="score-display-ultra-large">
          <div className={`score-number-massive ${scoreLevel}`}>
            {Math.round(result.overall_score * 100)}<span className="percent-sign-large">%</span>
          </div>
          <div className="score-label-ultra-large">AI Likelihood</div>
        </div>
        
        <div className="score-bar-ultra-minimal">
          <div className="score-track-ultra-minimal">
            <div 
              className={`score-fill-ultra-minimal ${scoreLevel}`}
              style={{ width: `${result.overall_score * 100}%` }}
            />
            <div 
              className="score-indicator-point"
              style={{ left: `${result.overall_score * 100}%` }}
            />
          </div>
          <div className="score-percentage-below">
            <div 
              className={`percentage-marker ${scoreLevel}`}
              style={{ left: `${result.overall_score * 100}%` }}
            >
              {Math.round(result.overall_score * 100)}%
            </div>
          </div>
        </div>
      </div>

      {/* Ultra Compact Horizontal Statistics Section */}
      <div className="text-statistics-ultra-horizontal">
        <div className="stats-grid-horizontal">
          <div className="stat-item-ultra-horizontal">
            <div className="stat-value-ultra-horizontal">{result.analysis_metadata?.paragraph_count || 0}</div>
            <div className="stat-label-ultra-horizontal">Paragraphs</div>
          </div>
          <div className="stat-item-ultra-horizontal">
            <div className="stat-value-ultra-horizontal">{result.analysis_metadata?.sentence_count || 0}</div>
            <div className="stat-label-ultra-horizontal">Sentences</div>
          </div>
          <div className="stat-item-ultra-horizontal">
            <div className="stat-value-ultra-horizontal">{result.analysis_metadata?.word_count || 0}</div>
            <div className="stat-label-ultra-horizontal">Words</div>
          </div>
          <div className="stat-item-ultra-horizontal">
            <div className="stat-value-ultra-horizontal">{result.analysis_metadata?.text_length || 0}</div>
            <div className="stat-label-ultra-horizontal">Characters</div>
          </div>
          <div className="stat-item-ultra-horizontal">
            <div className="stat-value-ultra-horizontal">{formatProcessingTime(result.analysis_metadata?.processing_time_seconds)}</div>
            <div className="stat-label-ultra-horizontal">Processing</div>
          </div>
        </div>
      </div>

      {/* Prominent Export Report Section */}
      <div className="export-report-section">
        <button 
          className="export-report-prominent"
          onClick={onExportReport}
        >
          <Download size={20} />
          Export Report
        </button>
        <p className="export-description">Download complete analysis with all dimension details</p>
      </div>
    </div>
  );
};