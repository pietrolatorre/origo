/**
 * AnalysisResults component for displaying comprehensive analysis results
 */

import React, { useState } from 'react';
import { BarChart3, FileText, List, Type, User, Bot, Download } from 'lucide-react';
import type { AnalysisResult, EnhancedAnalysisDetails } from '../types/analysis';
import WordTable from './WordTable';
import { MetricsBreakdown } from './MetricsBreakdown';
import { StatisticsBanner } from './StatisticsBanner';
import { NgramAnalysisModal } from './NgramAnalysis';

interface AnalysisResultsProps {
  result: AnalysisResult;
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ result }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'paragraph' | 'sentence' | 'words'>('overview');
  const [showNgramModal, setShowNgramModal] = useState(false);

  const getScoreColor = (score: number): string => {
    if (score >= 0.7) return 'high';
    if (score >= 0.6) return 'medium'; // Changed from 0.4 to 0.6
    return 'low';
  };

  const isSignificantScore = (score: number): boolean => score >= 0.6;  // Changed from 0.4 to 0.6

  // Filter and sort paragraphs with significant scores (yellow/red) - sorted by score descending
  const significantParagraphs = result.paragraphs
    .filter(p => isSignificantScore(p.score))
    .sort((a, b) => b.score - a.score)
    .slice(0, 10); // Show only top 10

  // Get all sentences with significant scores, sorted by score descending, limited to top 10
  const significantSentences = result.paragraphs
    .flatMap(p => p.sentences || [])
    .filter(s => isSignificantScore(s.score))
    .sort((a, b) => b.score - a.score)
    .slice(0, 10); // Show only top 10

  // Filter words with significant scores, sorted by score descending, limited to top 10
  const significantWords = (result.word_analysis?.unique_words || [])
    .filter(w => isSignificantScore(w.average_score))
    .sort((a, b) => b.average_score - a.average_score)
    .slice(0, 10); // Show only top 10

  const handleDimensionClick = (dimension: string, details: EnhancedAnalysisDetails) => {
    // Handle N-gram dimension specially
    if (dimension === 'ngram_similarity' && details.ngram_analysis) {
      setShowNgramModal(true);
    } else {
      // For other dimensions, show insights in a simple alert for now
      // This can be expanded with more detailed modals later
      alert(`${dimension} insights: Score ${(details.overall_score * 100).toFixed(1)}% - Click export for detailed analysis.`);
    }
  };

  const generatePDFReport = async () => {
    try {
      // Get complete analysis data (not limited to 10)
      const allSignificantParagraphs = result.paragraphs
        .filter(p => isSignificantScore(p.score))
        .sort((a, b) => b.score - a.score);
      
      const allSignificantSentences = result.paragraphs
        .flatMap(p => p.sentences || [])
        .filter(s => isSignificantScore(s.score))
        .sort((a, b) => b.score - a.score);
      
      const allSignificantWords = (result.word_analysis?.unique_words || [])
        .filter(w => isSignificantScore(w.average_score))
        .sort((a, b) => b.average_score - a.average_score);

      const reportData = {
        overview: {
          overall_score: result.overall_score,
          global_scores: result.global_scores,
          metadata: result.analysis_metadata
        },
        paragraphs: allSignificantParagraphs,
        sentences: allSignificantSentences,
        words: allSignificantWords
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
            <button
              className="tab-button export-button"
              onClick={generatePDFReport}
              title="Export complete analysis report as PDF"
            >
              <Download size={16} />
              Export Report
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
                
                <MetricsBreakdown 
                  scores={result.global_scores} 
                  enhancedAnalysis={result.enhanced_analysis}
                  onDimensionClick={handleDimensionClick}
                />
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
                    {significantParagraphs.length === 10 && (
                      <div className="results-limit-notice">
                        Showing top 10 results. Export report for complete analysis.
                      </div>
                    )}
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
                    {significantSentences.length === 10 && (
                      <div className="results-limit-notice">
                        Showing top 10 results. Export report for complete analysis.
                      </div>
                    )}
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
                  <div className="words-tab">
                    <WordTable words={significantWords} hideControls={true} />
                    {significantWords.length === 10 && (
                      <div className="results-limit-notice">
                        Showing top 10 results. Export report for complete analysis.
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
        
        {/* N-gram Analysis Modal */}
        {showNgramModal && result.enhanced_analysis?.ngram_details?.ngram_analysis && (
          <NgramAnalysisModal 
            ngramData={result.enhanced_analysis.ngram_details.ngram_analysis}
            onClose={() => setShowNgramModal(false)}
          />
        )}
      </div>
    </>
  );
};