import { useState, useCallback } from 'react';
import './App.css';
import { TextInput } from './components/TextInput';
import { AnalysisResults } from './components/AnalysisResults';
import { AnalysisDimensions } from './components/AnalysisDimensions';
import { Header } from './components/Header';
import { Disclaimer } from './components/Disclaimer';
import { analyzeText } from './services/api';
import type { AnalysisResult, DimensionToggleSettings } from './types/analysis';

function App() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dimensions, setDimensions] = useState<DimensionToggleSettings>({
    perplexity: true,
    burstiness: true,
    semantic_coherence: true,
    ngram_similarity: true
  });

  const handleAnalyze = useCallback(async (text: string) => {
    if (!text.trim() || text.length < 10) {
      setError('Text must be at least 10 characters long');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);

    try {
      const result = await analyzeText(text, dimensions);
      setAnalysisResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during analysis');
    } finally {
      setIsAnalyzing(false);
    }
  }, [dimensions]);

  const handleDimensionToggle = useCallback((dimensionId: keyof DimensionToggleSettings, enabled: boolean) => {
    setDimensions(prev => ({
      ...prev,
      [dimensionId]: enabled
    }));
  }, []);

  const handleClear = useCallback(() => {
    setAnalysisResult(null);
    setError(null);
  }, []);

  return (
    <div className="app">
      <Header />
      
      <main className="main-content">
        <div className="container">
          <TextInput 
            onAnalyze={handleAnalyze}
            onClear={handleClear}
            isAnalyzing={isAnalyzing}
            error={error}
          />
          
          <AnalysisDimensions 
            dimensions={dimensions}
            onDimensionToggle={handleDimensionToggle}
          />
          
          {analysisResult && (
            <AnalysisResults 
              result={analysisResult} 
              enabledDimensions={dimensions}
            />
          )}
        </div>
      </main>
      
      <Disclaimer />
    </div>
  );
}

export default App;
