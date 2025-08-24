/**
 * HighlightedText component for displaying text with color-coded highlights
 */

import React, { useState, useMemo } from 'react';
import { ChevronDown, ChevronUp, Info } from 'lucide-react';
import type { ParagraphAnalysis, SentenceAnalysis, WordAnalysis } from '../types/analysis';

interface HighlightedTextProps {
  paragraphs: ParagraphAnalysis[];
}

interface TooltipInfo {
  score: number;
  type: 'word' | 'sentence' | 'paragraph';
  text: string;
}

export const HighlightedText: React.FC<HighlightedTextProps> = ({ paragraphs }) => {
  const [highlightLevel, setHighlightLevel] = useState<'paragraph' | 'sentence' | 'word'>('sentence');
  const [expandedParagraphs, setExpandedParagraphs] = useState<Set<number>>(new Set([0]));
  const [tooltip, setTooltip] = useState<{ visible: boolean; x: number; y: number; info: TooltipInfo | null }>({ 
    visible: false, x: 0, y: 0, info: null 
  });

  const toggleParagraph = (index: number) => {
    const newExpanded = new Set(expandedParagraphs);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedParagraphs(newExpanded);
  };

  const getHighlightClass = (score: number): string => {
    if (score >= 0.7) return 'highlight-high';
    if (score >= 0.4) return 'highlight-medium';
    return 'highlight-low';
  };

  const showTooltip = (e: React.MouseEvent, info: TooltipInfo) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setTooltip({
      visible: true,
      x: rect.left + rect.width / 2,
      y: rect.top - 10,
      info
    });
  };

  const hideTooltip = () => {
    setTooltip({ visible: false, x: 0, y: 0, info: null });
  };

  const renderHighlightedSentence = (sentence: SentenceAnalysis, sentenceIndex: number) => {
    if (highlightLevel === 'word' && sentence.words.length > 0) {
      // Word-level highlighting
      let highlightedText = sentence.text;
      const sortedWords = [...sentence.words].sort((a, b) => b.word.length - a.word.length);
      
      sortedWords.forEach(wordInfo => {
        const regex = new RegExp(`\\\\b${wordInfo.word}\\\\b`, 'gi');
        highlightedText = highlightedText.replace(regex, (match) => 
          `<mark class=\"word-highlight ${getHighlightClass(wordInfo.score)}\" data-score=\"${wordInfo.score}\" data-word=\"${wordInfo.word}\">${match}</mark>`
        );
      });
      
      return (
        <span 
          className={`sentence ${getHighlightClass(sentence.score)}`}
          onMouseEnter={(e) => showTooltip(e, { score: sentence.score, type: 'sentence', text: sentence.text })}
          onMouseLeave={hideTooltip}
          dangerouslySetInnerHTML={{ __html: highlightedText }}
        />
      );
    } else {
      // Sentence-level highlighting
      return (
        <span
          className={`sentence ${getHighlightClass(sentence.score)}`}
          onMouseEnter={(e) => showTooltip(e, { score: sentence.score, type: 'sentence', text: sentence.text })}
          onMouseLeave={hideTooltip}
        >
          {sentence.text}
        </span>
      );
    }
  };

  return (
    <div className=\"highlighted-text\">
      {/* Controls */}
      <div className=\"highlight-controls\">
        <div className=\"control-group\">
          <label htmlFor=\"highlight-level\">Highlight Level:</label>
          <select 
            id=\"highlight-level\"
            value={highlightLevel} 
            onChange={(e) => setHighlightLevel(e.target.value as 'paragraph' | 'sentence' | 'word')}
            className=\"highlight-select\"
          >
            <option value=\"paragraph\">Paragraphs</option>
            <option value=\"sentence\">Sentences</option>
            <option value=\"word\">Words</option>
          </select>
        </div>
        
        <div className=\"legend\">
          <div className=\"legend-item\">
            <span className=\"legend-color highlight-low\"></span>
            <span>Low AI Probability</span>
          </div>
          <div className=\"legend-item\">
            <span className=\"legend-color highlight-medium\"></span>
            <span>Medium AI Probability</span>
          </div>
          <div className=\"legend-item\">
            <span className=\"legend-color highlight-high\"></span>
            <span>High AI Probability</span>
          </div>
        </div>
      </div>

      {/* Text content */}
      <div className=\"text-content\">
        {paragraphs.map((paragraph, pIndex) => (
          <div key={pIndex} className=\"paragraph-container\">
            <div 
              className={`paragraph-header ${expandedParagraphs.has(pIndex) ? 'expanded' : ''}`}
              onClick={() => toggleParagraph(pIndex)}
            >
              <div className=\"paragraph-info\">
                <span className=\"paragraph-label\">Paragraph {pIndex + 1}</span>
                <span className={`paragraph-score ${getHighlightClass(paragraph.score)}`}>
                  AI Probability: {Math.round(paragraph.score * 100)}%
                </span>
              </div>
              {expandedParagraphs.has(pIndex) ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </div>
            
            {expandedParagraphs.has(pIndex) && (
              <div className={`paragraph-content ${highlightLevel === 'paragraph' ? getHighlightClass(paragraph.score) : ''}`}>
                {highlightLevel === 'paragraph' ? (
                  <div 
                    className=\"paragraph-text\"
                    onMouseEnter={(e) => showTooltip(e, { score: paragraph.score, type: 'paragraph', text: paragraph.text })}
                    onMouseLeave={hideTooltip}
                  >
                    {paragraph.text}
                  </div>
                ) : (
                  <div className=\"sentences-container\">
                    {paragraph.sentences.map((sentence, sIndex) => (
                      <span key={sIndex}>
                        {renderHighlightedSentence(sentence, sIndex)}
                        {sIndex < paragraph.sentences.length - 1 && ' '}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Tooltip */}
      {tooltip.visible && tooltip.info && (
        <div 
          className=\"highlight-tooltip\"
          style={{
            position: 'fixed',
            left: tooltip.x,
            top: tooltip.y,
            transform: 'translate(-50%, -100%)'
          }}
        >
          <div className=\"tooltip-header\">
            <Info size={14} />
            <span className=\"tooltip-type\">{tooltip.info.type} Analysis</span>
          </div>
          <div className=\"tooltip-content\">
            <div className=\"tooltip-score\">
              AI Probability: <strong>{Math.round(tooltip.info.score * 100)}%</strong>
            </div>
            {tooltip.info.text.length > 100 && (
              <div className=\"tooltip-text\">
                {tooltip.info.text.substring(0, 100)}...
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};