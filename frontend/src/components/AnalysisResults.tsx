/**
 * AnalysisResults component for displaying comprehensive analysis results
 */

import React, { useState } from 'react';
import { BarChart3, FileText, List, Type, User, Bot } from 'lucide-react';
import type { AnalysisResult } from '../types/analysis';
import WordTable from './WordTable';
import { MetricsBreakdown } from './MetricsBreakdown';
import { StatisticsBanner } from './StatisticsBanner';

interface AnalysisResultsProps {
  result: AnalysisResult;
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ result }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'paragraph' | 'sentence' | 'words'>('overview');

  const getScoreColor = (score: number): string => {
    if (score >= 0.7) return 'high';
    if (score >= 0.4) return 'medium';
    return 'low';
  };

  const isSignificantScore = (score: number): boolean => score >= 0.4;

  // Filter paragraphs with significant scores (yellow/red)
  const significantParagraphs = result.paragraphs.filter(p => isSignificantScore(p.score));

  // Get all sentences with significant scores, sorted by score descending
  const significantSentences = result.paragraphs
    .flatMap(p => p.sentences || [])
    .filter(s => isSignificantScore(s.score))
    .sort((a, b) => b.score - a.score);

  // Filter words with significant scores
  const significantWords = (result.word_analysis?.unique_words || [])
    .filter(w => isSignificantScore(w.average_score))
    .sort((a, b) => b.average_score - a.average_score);

  return (
    <>
      {/* Statistics Banner */}
      {result.analysis_metadata && (
        <StatisticsBanner metadata={result.analysis_metadata} />
      )}
      
      <div className="analysis-results">
        {/* Analysis Tabs */}
        <div className="analysis-tabs">
          <div className="tab-buttons">
            <button
              className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              <BarChart3 size={16} />
              Overview
            </button>
            <button
              className={`tab-button ${activeTab === 'paragraph' ? 'active' : ''}`}
              onClick={() => setActiveTab('paragraph')}
            >
              <FileText size={16} />
              Paragraph
            </button>
            <button
              className={`tab-button ${activeTab === 'sentence' ? 'active' : ''}`}
              onClick={() => setActiveTab('sentence')}
            >
              <Type size={16} />
              Sentence
            </button>
            <button
              className={`tab-button ${activeTab === 'words' ? 'active' : ''}`}
              onClick={() => setActiveTab('words')}
            >
              <List size={16} />
              Word
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'overview' && (
              <div className="overview-tab">
                {/* Visual Score Representation */}
                <div className="score-visualization">
                  <div className="score-bar-container">
                    <h3 className="score-title">Origin Likelihood</h3>
                    <div className="score-endpoints">
                      <div className="human-endpoint">
                        <User size={32} className="human-icon" />
                        <span>Human</span>
                      </div>
                      <div className="ai-endpoint">
                        <Bot size={32} className="ai-icon" />
                        <span>AI</span>
                      </div>
                    </div>
                    <div className="score-bar">
                      <div 
                        className={`score-fill ${getScoreColor(result.overall_score)}`}
                        style={{ width: `${result.overall_score * 100}%` }}
                      ></div>
                      <div className="score-percentage">
                        {Math.round(result.overall_score * 100)}%
                      </div>
                    </div>
                  </div>
                </div>
                
                <MetricsBreakdown scores={result.global_scores} />
              </div>
            )}

            {activeTab === 'paragraph' && (
              <div className="paragraph-tab">
                {significantParagraphs.length === 0 ? (
                  <div className="no-significant-elements">
                    No significant elements in this analysis dimension show evidence of AI-generated content.
                  </div>
                ) : (
                  <div className="paragraph-analysis">
                    {significantParagraphs.map((paragraph, paragraphIndex) => (
                      <div key={paragraphIndex} className="sentence-item-new">
                        <div className={`sentence-background ${getScoreColor(paragraph.score)}`}>
                          <div className="sentence-text-new">{paragraph.text}</div>
                        </div>
                        <div className={`score-circle ${getScoreColor(paragraph.score)}`}>
                          <span className={`score-percentage ${getScoreColor(paragraph.score)}`}>{Math.round(paragraph.score * 100)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'sentence' && (
              <div className="sentence-tab">
                {significantSentences.length === 0 ? (
                  <div className="no-significant-elements">
                    No significant elements in this analysis dimension show evidence of AI-generated content.
                  </div>
                ) : (
                  <div className="sentence-analysis">
                    {significantSentences.map((sentence, sentIndex) => (
                      <div key={sentIndex} className="sentence-item-new">
                        <div className={`sentence-background ${getScoreColor(sentence.score)}`}>
                          <div className="sentence-text-new">{sentence.text}</div>
                        </div>
                        <div className={`score-circle ${getScoreColor(sentence.score)}`}>
                          <span className={`score-percentage ${getScoreColor(sentence.score)}`}>{Math.round(sentence.score * 100)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'words' && (
              <div className="words-tab">
                {significantWords.length === 0 ? (
                  <div className="no-significant-elements">
                    No significant elements in this analysis dimension show evidence of AI-generated content.
                  </div>
                ) : (
                  <WordTable words={significantWords.slice(0, 10)} hideControls={true} />
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};