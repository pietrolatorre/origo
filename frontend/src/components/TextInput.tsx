/**
 * TextInput component for text input and analysis controls
 */

import React, { useState, useCallback, useEffect } from 'react';
import { Send, Trash2, Loader2, ClipboardPaste, Globe } from 'lucide-react';
import { AnalysisDimensions } from './AnalysisDimensions';
import type { DimensionToggleSettings } from '../types/analysis';

interface TextInputProps {
  onAnalyze: (text: string) => void;
  onClear: () => void;
  isAnalyzing: boolean;
  error: string | null;
  dimensions: DimensionToggleSettings;
  onDimensionToggle: (dimensionId: keyof DimensionToggleSettings, enabled: boolean) => void;
}

export const TextInput: React.FC<TextInputProps> = ({
  onAnalyze,
  onClear,
  isAnalyzing,
  error,
  dimensions,
  onDimensionToggle
}) => {
  const [text, setText] = useState('');
  const [showPasteButton, setShowPasteButton] = useState(false);

  // Sample text for demonstration
  const sampleText = `Artificial intelligence has revolutionized numerous industries and transformed how we approach complex problems. Machine learning algorithms can now process vast amounts of data with unprecedented accuracy and speed. These systems demonstrate remarkable capabilities in pattern recognition, natural language processing, and predictive analytics. The integration of AI technologies continues to expand across various sectors, including healthcare, finance, and transportation. As these systems become more sophisticated, they enable innovative solutions that were previously unimaginable. The potential applications seem limitless, offering exciting possibilities for the future.`;

  // Initialize with sample text if no text is provided
  useEffect(() => {
    if (!text) {
      setText(sampleText);
    }
  }, [sampleText]);

  const handleTextChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value;
    setText(newText);
  }, []);

  const handleAnalyze = useCallback(() => {
    if (text.trim() && text.length >= 10) {
      onAnalyze(text);
    }
  }, [text, onAnalyze]);

  const handleClear = useCallback(() => {
    setText('');
    onClear();
  }, [onClear]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.ctrlKey && e.key === 'Enter') {
      e.preventDefault();
      handleAnalyze();
    }
  }, [handleAnalyze]);

  const handlePaste = useCallback(async () => {
    try {
      const clipboardText = await navigator.clipboard.readText();
      setText(clipboardText);
    } catch (err) {
      console.error('Failed to read clipboard:', err);
    }
  }, []);

  const handleMouseEnter = useCallback(() => {
    setShowPasteButton(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setShowPasteButton(false);
  }, []);

  const isDisabled = text.length < 10 || isAnalyzing;
  const isOverLimit = text.length > 50000;

  return (
    <div className="text-input-section">
      <div className="input-header">
        <h2>Input text</h2>
        <div className="language-tabs">
          <div className={`language-tab active`}>
            <Globe size={14} />
            EN
          </div>
          <div className="language-tab coming-soon">
            <Globe size={14} />
            IT
            <span className="coming-soon-badge">coming soon</span>
          </div>
        </div>
      </div>

      <div className="input-container">
        <div 
          className="textarea-wrapper"
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          <textarea
            className={`text-input ${error ? 'error' : ''} ${isOverLimit ? 'over-limit' : ''}`}
            placeholder="Sample text loaded for demonstration. Replace with your own text for AI detection analysis...\n\nMinimum 10 characters required. The analysis will examine:\n• Perplexity patterns using GPT-2\n• Sentence structure and variation\n• N-gram repetition and similarity\n• Semantic coherence patterns\n\nPress Ctrl+Enter to analyze quickly."
            value={text}
            onChange={handleTextChange}
            onKeyDown={handleKeyDown}
            disabled={isAnalyzing}
            rows={12}
            maxLength={50000}
          />
          
          {showPasteButton && (
            <button
              className="floating-paste-btn"
              onClick={handlePaste}
              title="Paste from clipboard"
              type="button"
            >
              <ClipboardPaste size={16} />
              Paste
            </button>
          )}
        </div>
        
        <AnalysisDimensions 
          dimensions={dimensions}
          onDimensionToggle={onDimensionToggle}
        />
        
        <div className="input-controls">
          <div className="control-buttons">
            <button
              className="btn btn-secondary"
              onClick={handleClear}
              disabled={!text || isAnalyzing}
              title="Clear text"
            >
              <Trash2 size={16} />
              Clear
            </button>
            
            <button
              className="btn btn-primary"
              onClick={handleAnalyze}
              disabled={isDisabled || isOverLimit}
              title={isDisabled ? 'Enter at least 10 characters' : 'Launch analysis (Ctrl+Enter)'}
            >
              {isAnalyzing ? (
                <>
                  <Loader2 size={16} className="spinning" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Send size={16} />
                  Launch analysis
                </>
              )}
            </button>
          </div>
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          {isOverLimit && (
            <div className="error-message">
              Text exceeds maximum length of 50,000 characters
            </div>
          )}
        </div>
      </div>
    </div>
  );
};