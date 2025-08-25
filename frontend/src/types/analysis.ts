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
  ngram_breakdown?: {
    bigram_score: number;
    trigram_score: number;
    fourgram_score: number;
  };
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

// Enhanced N-gram analysis structures
export interface NgramItem {
  text: string;
  frequency: number;
  score: number;
  frequency_ratio: number;
}

export interface NgramAnalysisDetails {
  score: number;
  details: NgramItem[];
}

export interface NgramAnalysis {
  bigrams: NgramAnalysisDetails;
  trigrams: NgramAnalysisDetails;
  fourgrams: NgramAnalysisDetails;
}

// Pattern analysis structures
export interface FormattingAnalysis {
  overall_score: number;
  component_scores: {
    quote_abuse: number;
    formatting_abuse: number;
    icon_abuse: number;
    reader_question_abuse: number;
  };
  details: {
    quotes: { count: number; ratio: number };
    formatting: { count: number; ratio: number };
    icons: { count: number; ratio: number };
    reader_questions: { count: number; ratio: number };
  };
}

export interface ParagraphPatternAnalysis {
  overall_score: number;
  component_scores: {
    uniform_length: number;
    excessive_short: number;
    repetitive_starts: number;
  };
  details: {
    paragraph_count: number;
    avg_length: number;
    length_variance: number;
    short_paragraph_ratio: number;
  };
}

export interface PatternAnalysis {
  formatting: FormattingAnalysis;
  paragraphs: ParagraphPatternAnalysis;
}

// Enhanced analysis details
export interface EnhancedAnalysisDetails {
  overall_score: number;
  ngram_analysis?: NgramAnalysis;
  pattern_analysis?: PatternAnalysis;
  components?: Record<string, number>;
  text_stats?: Record<string, any>;
}

export interface UniqueWord {
  word: string;
  average_score: number;
  count: number;
  category?: string;
}

export interface WordAnalysisResult {
  unique_words: UniqueWord[];
  suspicious_words_found?: number;
  total_unique_words?: number;
}

export interface AnalysisMetadata {
  text_length: number;
  word_count: number;
  sentence_count: number;
  paragraph_count: number;
  weights_used?: Record<string, number>;
  parallel_processing_enabled?: boolean;
  enhanced_features_enabled?: {
    stylistic_analysis: boolean;
    register_analysis: boolean;
    structural_analysis: boolean;
  };
  error?: string;
}

export interface AnalysisResult {
  overall_score: number;
  global_scores: GlobalScores;
  enhanced_analysis?: {
    perplexity_details: EnhancedAnalysisDetails;
    burstiness_details: EnhancedAnalysisDetails;
    ngram_details: EnhancedAnalysisDetails;
    semantic_details: EnhancedAnalysisDetails;
  };
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