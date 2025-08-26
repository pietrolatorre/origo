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
  perplexity: number | null;
  burstiness: number | null;
  semantic_coherence: number | null;
  ngram_repetition: number | null;
  lexical_richness: number | null;
  stylistic_markers: number | null;
  readability: number | null;
}

// Evidence types for each analysis dimension
export interface PerplexityEvidence {
  type: 'sentence';
  text: string;
  score: number;
  reason: string;
}

export interface BurstinessEvidence {
  type: 'paragraph';
  text: string;
  score: number;
  sentenceLengths: number[];
  coefficientOfVariation: number;
  reason: string;
}

export interface SemanticEvidence {
  type: 'paragraph_pair';
  paragraph1: string;
  paragraph2: string;
  similarity: number;
  reason: string;
}

export interface NgramEvidence {
  type: 'ngram';
  text: string;
  frequency: number;
  ngramType: 'bigram' | 'trigram' | 'fourgram';
  repetitionRate: number;
}

export interface LexicalEvidence {
  type: 'sentence';
  text: string;
  typeTokenRatio: number;
  uniqueWords: number;
  totalWords: number;
  reason: string;
}

export interface StylisticEvidence {
  type: 'sentence';
  text: string;
  score: number;
  anomalies: {
    punctuationFreq: number;
    posDistribution: Record<string, number>;
    stopwordRatio: number;
  };
  reason: string;
}

export interface ReadabilityEvidence {
  type: 'sentence';
  text: string;
  readabilityScore: number;
  complexity: 'too_simple' | 'too_complex' | 'normal';
  reason: string;
}

export type Evidence = 
  | PerplexityEvidence 
  | BurstinessEvidence 
  | SemanticEvidence 
  | NgramEvidence 
  | LexicalEvidence 
  | StylisticEvidence 
  | ReadabilityEvidence;

// Dimension analysis results with evidences
export interface DimensionAnalysisResult {
  score: number;
  weight: number;
  active: boolean;
  evidences: Evidence[];
  topEvidences: Evidence[]; // Limited to top 10 for UI
  totalEvidences: number;
}

export interface DimensionResults {
  perplexity: DimensionAnalysisResult;
  burstiness: DimensionAnalysisResult;
  semantic_coherence: DimensionAnalysisResult;
  ngram_repetition: DimensionAnalysisResult;
  lexical_richness: DimensionAnalysisResult;
  stylistic_markers: DimensionAnalysisResult;
  readability: DimensionAnalysisResult;
}


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
  detailed_sentences?: DetailedSentence[];
  sentence_clusters?: SentenceClusterAnalysis;
  detailed_evidence?: SemanticEvidenceDetails;
}

// New interfaces for enhanced modal data
export interface DetailedSentence {
  text: string;
  score: number;
  perplexity_score: number;
  stylistic_score: number;
  register_score: number;
  impactful_parts: ImpactfulPart[];
  evidence: SentenceEvidence;
}

export interface ImpactfulPart {
  text: string;
  start_pos: number;
  end_pos: number;
  impact_type: string;
  score: number;
  explanation: string;
}

export interface SentenceEvidence {
  suspicious_words: string[];
  formulaic_phrases: string[];
  transitions: string[];
  register_issues: Record<string, any>;
}

export interface SentenceClusterAnalysis {
  clusters: SentenceCluster[];
  summary: ClusterSummary;
}

export interface SentenceCluster {
  id: string;
  structure_signature: string;
  sentence_count: number;
  sentences: ClusterSentence[];
  statistics: ClusterStatistics;
  uniformity_score: number;
  ai_likelihood: number;
}

export interface ClusterSentence {
  text: string;
  length: number;
  complexity: number;
  start_pattern: string;
}

export interface ClusterStatistics {
  avg_length: number;
  length_variance: number;
  avg_complexity: number;
  complexity_variance: number;
  dominant_start_pattern: string;
  pattern_repetition_rate: number;
}

export interface ClusterSummary {
  total_clusters: number;
  clustering_rate: number;
  uniformity_score: number;
  ai_likelihood: number;
  dominant_patterns: DominantPattern[];
}

export interface DominantPattern {
  pattern: string;
  sentence_count: number;
  uniformity: number;
}

export interface SemanticEvidenceDetails {
  coherence_patterns: CoherencePattern[];
  flow_analysis: FlowAnalysis;
  topic_clusters: TopicCluster[];
  repetition_evidence: RepetitionEvidence[];
  summary: SemanticSummary;
}

export interface CoherencePattern {
  type: string;
  start_sentence: number;
  end_sentence: number;
  coherence_score: number;
  sentences: string[];
  evidence: string;
  ai_likelihood: number;
}

export interface FlowAnalysis {
  flow_uniformity: number;
  transitions: FlowTransition[];
  avg_consecutive_similarity: number;
}

export interface FlowTransition {
  type: string;
  from_sentence: number;
  to_sentence: number;
  similarity: number;
  evidence: string;
  ai_likelihood: number;
}

export interface TopicCluster {
  id: string;
  sentence_indices: number[];
  sentences: string[];
  avg_similarity: number;
  size: number;
  evidence: string;
  ai_likelihood: number;
}

export interface RepetitionEvidence {
  sentence_1_index: number;
  sentence_2_index: number;
  sentence_1: string;
  sentence_2: string;
  similarity: number;
  evidence: string;
  ai_likelihood: number;
}

export interface SemanticSummary {
  overall_coherence: number;
  ai_likelihood: number;
  analysis_confidence: string;
  evidence_count: number;
  primary_indicators: (string | null)[];
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
  caching_enabled?: boolean;
  processing_time_seconds?: number;
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
  dimension_results: DimensionResults;
  weights_applied: Record<keyof GlobalScores, number>;
  active_dimensions: (keyof GlobalScores)[];
  analysis_metadata?: AnalysisMetadata;
  // Legacy fields for backward compatibility
  enhanced_analysis?: {
    perplexity_details: EnhancedAnalysisDetails;
    burstiness_details: EnhancedAnalysisDetails;
    ngram_details: EnhancedAnalysisDetails;
    semantic_details: EnhancedAnalysisDetails;
  };
  paragraphs: ParagraphAnalysis[];
  word_analysis: WordAnalysisResult;
}

export interface TextAnalysisRequest {
  text: string;
  enabled_dimensions?: {
    perplexity: boolean;
    burstiness: boolean;
    semantic_coherence: boolean;
    ngram_repetition: boolean;
    lexical_richness: boolean;
    stylistic_markers: boolean;
    readability: boolean;
  };
}

export interface AnalysisDimension {
  id: keyof GlobalScores;
  name: string;
  description: string;
  icon: string;
  enabled: boolean;
  weight: number;
  atomicLevel: 'sentence' | 'paragraph' | 'global';
  scoreInterpretation: string;
}

export interface DimensionToggleSettings {
  perplexity: boolean;
  burstiness: boolean;
  semantic_coherence: boolean;
  ngram_repetition: boolean;
  lexical_richness: boolean;
  stylistic_markers: boolean;
  readability: boolean;
}

export interface HighlightInfo {
  start: number;
  end: number;
  score: number;
  type: 'word' | 'sentence' | 'paragraph';
  text: string;
}