/**
 * TypeScript type definitions for Origo text analysis
 */

export interface WordAnalysis {
  word: string;
  score: number;
}

export interface SentenceAnalysis {
  text: string;
  score: number;
  words: WordAnalysis[];
}

export interface ParagraphAnalysis {
  text: string;
  score: number;
  sentences: SentenceAnalysis[];
}

export interface GlobalScores {
  perplexity: number;
  burstiness: number;
  semantic_coherence: number;
  ngram_similarity: number;
}

export interface UniqueWord {
  word: string;
  average_score: number;
  count: number;
}

export interface WordAnalysisResult {
  unique_words: UniqueWord[];
}

export interface AnalysisMetadata {
  text_length: number;
  sentence_count: number;
  paragraph_count: number;
  weights_used?: Record<string, number>;
  error?: string;
}

export interface AnalysisResult {
  overall_score: number;
  global_scores: GlobalScores;
  paragraphs: ParagraphAnalysis[];
  word_analysis: WordAnalysisResult;
  analysis_metadata?: AnalysisMetadata;
}

export interface TextAnalysisRequest {
  text: string;
}

export interface HighlightInfo {
  start: number;
  end: number;
  score: number;
  type: 'word' | 'sentence' | 'paragraph';
  text: string;
}