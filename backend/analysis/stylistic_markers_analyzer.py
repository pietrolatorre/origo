"""
Stylistic Markers Analyzer - Sentence Level Analysis

=== CONTEXT AND PURPOSE ===
This module is part of Origo's 7-dimension AI text detection system.
Stylistic analysis identifies unusual patterns in writing style that may
indicate artificial generation. Human writers have consistent personal style,
while AI may exhibit anomalous stylistic patterns or inconsistencies.

=== ANALYSIS APPROACH ===
- ATOMIC LEVEL: Sentence-by-sentence stylistic feature analysis
- FEATURES: Punctuation patterns, POS tag distributions, syntactic structures
- AGGREGATION: Paragraph = mean(sentence anomalies), Global = mean(paragraphs)
- INTERPRETATION: Deviations from balanced style = possible AI generation

=== KEY STYLISTIC FEATURES ===
1. **Punctuation Analysis**:
   - Comma frequency and placement patterns
   - Semicolon, colon, exclamation usage
   - Quotation mark and parenthesis patterns
   - Ellipsis and dash usage

2. **Part-of-Speech Patterns**:
   - Noun/verb/adjective/adverb ratios
   - Function word vs content word distribution
   - Sentence structure complexity
   - Dependency parsing patterns

3. **Syntactic Features**:
   - Sentence length variation
   - Clause structure complexity
   - Passive vs active voice usage
   - Subordinate clause frequency

4. **Register Consistency**:
   - Formal vs informal language mixing
   - Technical vs colloquial vocabulary
   - Consistent tone and voice

=== REAL IMPLEMENTATION REQUIREMENTS ===
To implement comprehensive stylistic analysis:
1. POS tagging using NLTK or spaCy
2. Dependency parsing for syntactic analysis
3. Statistical analysis of feature distributions
4. Baseline comparison against human/AI style corpora
5. Machine learning models for style classification

=== SCORING METHODOLOGY ===
- Calculate feature vectors for each sentence
- Compare against expected distributions
- Identify statistical anomalies and outliers
- Weight different features by importance
- Aggregate sentence-level anomalies

=== INTEGRATION POINTS ===
- Inherits from BaseAnalyzer for interface consistency
- Sentence-level analysis similar to Perplexity and Readability
- May utilize external NLP libraries (NLTK, spaCy)
- Called by AnalysisCoordinator during comprehensive analysis
- Weight: 14.3% (1/7) of total detection score
- Evidence: Sentences with extreme stylistic anomalies

=== CURRENT STATUS ===
Simulated implementation using basic punctuation and word pattern analysis
with realistic stylistic anomaly detection.
"""

import random
import re
from typing import List, Dict
from .base_analyzer import BaseAnalyzer, DimensionResult, Evidence, AnalysisLevel

class StylisticMarkersAnalyzer(BaseAnalyzer):
    """Analyzer for stylistic patterns and writing markers"""
    
    def __init__(self):
        super().__init__(
            dimension_id="stylistic_markers",
            analysis_level=AnalysisLevel.SENTENCE,
            default_weight=0.143
        )
    
    def get_dimension_name(self) -> str:
        return "Stylistic Markers"
    
    def get_description(self) -> str:
        return "Identifies unusual stylistic patterns in punctuation, POS tags, and word usage"
    
    def get_score_interpretation(self) -> str:
        return "Deviations from balanced style = possible artificial generation"
    
    def analyze(self, text: str, **kwargs) -> DimensionResult:
        """Analyze stylistic markers at sentence level"""
        
        # Simulate stylistic analysis calculation
        score = self.simulate_stylistic_calculation(text)
        
        # Generate evidences
        evidences = self.generate_stylistic_evidences(text, score)
        
        return DimensionResult(
            dimension_id=self.dimension_id,
            score=score,
            weight=self.default_weight,
            active=self.is_enabled,
            evidences=evidences,
            total_evidences=len(evidences),
            analysis_level=self.analysis_level
        )
    
    def simulate_stylistic_calculation(self, text: str) -> float:
        """
        Simulate stylistic markers calculation
        Real implementation would analyze POS patterns, punctuation, and stylistic features
        """
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if not sentences:
            return 0.5
        
        total_stylistic_score = 0
        valid_sentences = 0
        
        for sentence in sentences:
            if len(sentence.strip()) < 5:
                continue
            
            # Analyze various stylistic features
            punctuation_score = self.analyze_punctuation(sentence)
            word_pattern_score = self.analyze_word_patterns(sentence)
            structure_score = self.analyze_sentence_structure(sentence)
            
            # Combine scores
            sentence_score = (punctuation_score + word_pattern_score + structure_score) / 3
            
            total_stylistic_score += sentence_score
            valid_sentences += 1
        
        if valid_sentences == 0:
            return 0.5
        
        average_score = total_stylistic_score / valid_sentences
        return max(0.0, min(1.0, average_score))
    
    def analyze_punctuation(self, sentence: str) -> float:
        """Analyze punctuation patterns"""
        # Count different punctuation types
        commas = sentence.count(',')
        semicolons = sentence.count(';')
        exclamations = sentence.count('!')
        questions = sentence.count('?')
        quotes = sentence.count('"') + sentence.count("'")
        
        word_count = len(sentence.split())
        
        if word_count == 0:
            return 0.5
        
        # Calculate punctuation density
        total_punctuation = commas + semicolons + exclamations + questions + quotes
        punctuation_density = total_punctuation / word_count
        
        # Unusual punctuation patterns might indicate AI generation
        if punctuation_density > 0.3:  # Too much punctuation
            return 0.7 + random.uniform(-0.1, 0.1)
        elif punctuation_density < 0.02:  # Too little punctuation
            return 0.6 + random.uniform(-0.1, 0.1)
        else:  # Normal range
            return 0.3 + random.uniform(-0.1, 0.1)
    
    def analyze_word_patterns(self, sentence: str) -> float:
        """Analyze word usage patterns"""
        words = sentence.lower().split()
        
        if len(words) < 3:
            return 0.5
        
        # Analyze word characteristics
        avg_word_length = sum(len(word) for word in words) / len(words)
        long_words = sum(1 for word in words if len(word) > 7)
        short_words = sum(1 for word in words if len(word) <= 3)
        
        long_word_ratio = long_words / len(words)
        short_word_ratio = short_words / len(words)
        
        # Analyze patterns that might indicate AI generation
        if avg_word_length > 8:  # Unusually long words
            return 0.6 + random.uniform(-0.1, 0.1)
        elif long_word_ratio > 0.4:  # Too many long words
            return 0.7 + random.uniform(-0.1, 0.1)
        elif short_word_ratio > 0.7:  # Too many short words
            return 0.6 + random.uniform(-0.1, 0.1)
        else:  # Balanced word usage
            return 0.3 + random.uniform(-0.1, 0.1)
    
    def analyze_sentence_structure(self, sentence: str) -> float:
        """Analyze sentence structure patterns"""
        # Simple structural analysis
        words = sentence.split()
        
        if len(words) < 3:
            return 0.5
        
        # Check for repetitive patterns
        first_words = [word.lower() for word in words[:3]]
        repeated_starts = len(first_words) - len(set(first_words))
        
        # Check capitalization patterns
        capitalized_words = sum(1 for word in words if word and word[0].isupper())
        cap_ratio = capitalized_words / len(words)
        
        # Unusual structural patterns
        if repeated_starts > 1:  # Repetitive sentence starts
            return 0.7 + random.uniform(-0.1, 0.1)
        elif cap_ratio > 0.3:  # Too many capitalized words
            return 0.6 + random.uniform(-0.1, 0.1)
        else:  # Normal structure
            return 0.3 + random.uniform(-0.1, 0.1)
    
    def generate_stylistic_evidences(self, text: str, score: float) -> List[Evidence]:
        """Generate stylistic markers evidences"""
        evidences = []
        sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
        
        # Select up to 15 sentences for evidence
        selected_sentences = sentences[:15]
        
        for i, sentence in enumerate(selected_sentences):
            if len(sentence.strip()) < 5:
                continue
            
            # Analyze stylistic features for this sentence
            features = self.extract_stylistic_features(sentence)
            
            # Vary evidence scores around the main score
            evidence_score = score + random.uniform(-0.15, 0.15)
            evidence_score = max(0.0, min(1.0, evidence_score))
            
            # Generate stylistic-specific reason
            reason = self.generate_stylistic_reason(features, evidence_score)
            
            evidences.append(Evidence(
                text=sentence,
                score=evidence_score,
                start_index=i * len(sentence),
                end_index=(i + 1) * len(sentence),
                evidence_type="sentence",
                reason=reason
            ))
        
        return evidences
    
    def extract_stylistic_features(self, sentence: str) -> Dict[str, float]:
        """Extract stylistic features from a sentence"""
        words = sentence.split()
        word_count = len(words)
        
        if word_count == 0:
            return {}
        
        features = {
            'avg_word_length': sum(len(word) for word in words) / word_count,
            'punctuation_density': len(re.findall(r'[,.;!?"\']', sentence)) / word_count,
            'capitalization_ratio': sum(1 for word in words if word and word[0].isupper()) / word_count,
            'word_count': word_count
        }
        
        return features
    
    def generate_stylistic_reason(self, features: Dict[str, float], score: float) -> str:
        """Generate specific reason for stylistic evidence"""
        if not features:
            return "Insufficient stylistic data for analysis"
        
        avg_length = features.get('avg_word_length', 0)
        punct_density = features.get('punctuation_density', 0)
        cap_ratio = features.get('capitalization_ratio', 0)
        word_count = features.get('word_count', 0)
        
        if score <= 0.3:
            return f"Natural stylistic patterns: avg word length {avg_length:.1f}, punctuation density {punct_density:.2f}"
        elif score <= 0.6:
            return f"Moderate stylistic characteristics: {word_count} words, capitalization ratio {cap_ratio:.2f}"
        else:
            if punct_density > 0.3:
                return f"Unusual punctuation density ({punct_density:.2f}) suggesting artificial generation"
            elif avg_length > 8:
                return f"Atypical word length patterns (avg: {avg_length:.1f}) indicating possible AI origin"
            else:
                return f"Stylistic anomalies detected in {word_count}-word sentence"