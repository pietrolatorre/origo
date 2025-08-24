/**
 * TextInput component for text input and analysis controls
 */

import React, { useState, useCallback, useEffect } from 'react';
import { Send, Trash2, Loader2 } from 'lucide-react';

interface TextInputProps {
  onAnalyze: (text: string) => void;
  onClear: () => void;
  isAnalyzing: boolean;
  error: string | null;
}

export const TextInput: React.FC<TextInputProps> = ({
  onAnalyze,
  onClear,
  isAnalyzing,
  error
}) => {
  const [text, setText] = useState('');

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

  const isDisabled = text.length < 10 || isAnalyzing;
  const isOverLimit = text.length > 50000;

  return (
    <div className="text-input-section">
      <div className="input-header">
        <h2>Text Analysis</h2>
      </div>

      <div className="input-container">
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
              title={isDisabled ? 'Enter at least 10 characters' : 'Analyze text (Ctrl+Enter)'}
            >
              {isAnalyzing ? (
                <>
                  <Loader2 size={16} className="spinning" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Send size={16} />
                  Analyze Text
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