/**
 * StatisticsBanner component for displaying text statistics in a horizontal banner
 */

import React from 'react';
import { FileText, Type, Hash, Scroll } from 'lucide-react';
import type { AnalysisMetadata } from '../types/analysis';

interface StatisticsBannerProps {
  metadata: AnalysisMetadata;
}

export const StatisticsBanner: React.FC<StatisticsBannerProps> = ({ metadata }) => {
  return (
    <div className="statistics-banner">
      <div className="statistics-content">
        <div className="statistic-item">
          <div className="statistic-icon">
            <Hash size={16} />
          </div>
          <div className="statistic-info">
            <span className="statistic-label">Characters</span>
            <span className="statistic-value">{metadata.text_length.toLocaleString()}</span>
          </div>
        </div>
        
        <div className="statistic-divider"></div>
        
        <div className="statistic-item">
          <div className="statistic-icon">
            <Type size={16} />
          </div>
          <div className="statistic-info">
            <span className="statistic-label">Words</span>
            <span className="statistic-value">{metadata.word_count?.toLocaleString() || 'N/A'}</span>
          </div>
        </div>
        
        <div className="statistic-divider"></div>
        
        <div className="statistic-item">
          <div className="statistic-icon">
            <FileText size={16} />
          </div>
          <div className="statistic-info">
            <span className="statistic-label">Sentences</span>
            <span className="statistic-value">{metadata.sentence_count}</span>
          </div>
        </div>
        
        <div className="statistic-divider"></div>
        
        <div className="statistic-item">
          <div className="statistic-icon">
            <Scroll size={16} />
          </div>
          <div className="statistic-info">
            <span className="statistic-label">Paragraphs</span>
            <span className="statistic-value">{metadata.paragraph_count}</span>
          </div>
        </div>
      </div>
    </div>
  );
};