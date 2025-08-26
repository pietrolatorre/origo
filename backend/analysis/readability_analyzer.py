"""
Readability Analyzer - Sentence Level Analysis

=== CONTEXT AND PURPOSE ===
This module is part of Origo's 7-dimension AI text detection system.
Readability analysis measures natural text complexity and flow.
Human writing typically shows balanced readability patterns,
while AI-generated text may be too simplistic or unnaturally complex.

=== ANALYSIS APPROACH ===
- ATOMIC LEVEL: Sentence-by-sentence readability calculation
- PRIMARY METRIC: Flesch Reading Ease score
- ADDITIONAL METRICS: Sentence complexity, syllable patterns, word difficulty
- AGGREGATION: Paragraph = mean(sentence scores), Global = mean(paragraphs)

=== READABILITY METRICS ===
1. **Flesch Reading Ease Formula**:
   206.835 - (1.015 × ASL) - (84.6 × ASW)
   Where: ASL = Average Sentence Length, ASW = Average Syllables per Word

2. **Complexity Indicators**:
   - Long word ratios (>6 characters)
   - Subordinating conjunctions frequency
   - Complex punctuation patterns
   - Sentence length variation

3. **Readability Levels**:
   - 90-100: Very Easy (5th grade)
   - 80-90: Easy (6th grade)
   - 70-80: Fairly Easy (7th grade)
   - 60-70: Standard (8th-9th grade)
   - 50-60: Fairly Difficult (10th-12th grade)
   - 30-50: Difficult (College level)
   - 0-30: Very Difficult (Graduate level)

=== SCORING INTERPRETATION ===
- Very high readability (90+): Too simplistic → May indicate AI oversimplification
- Very low readability (<30): Too complex → May indicate AI overcomplexity
- Balanced readability (30-90): Natural complexity → Human-like patterns

=== REAL IMPLEMENTATION REQUIREMENTS ===
To implement comprehensive readability analysis:
1. Accurate syllable counting algorithms
2. Advanced sentence parsing and clause identification
3. Vocabulary difficulty assessment
4. Multiple readability formulas (Flesch-Kincaid, SMOG, ARI)
5. Language-specific readability norms

=== ADDITIONAL READABILITY FORMULAS ===
- **Flesch-Kincaid Grade Level**: 0.39 × ASL + 11.8 × ASW - 15.59
- **SMOG Index**: 1.043 × √(polysyllables × 30/sentences) + 3.1291
- **Automated Readability Index**: 4.71 × (characters/words) + 0.5 × (words/sentences) - 21.43

=== INTEGRATION POINTS ===
- Inherits from BaseAnalyzer for standardized interface
- Sentence-level analysis like Perplexity and Lexical Richness
- Called by AnalysisCoordinator during comprehensive analysis
- Weight: 14.2% (1/7, slightly less to sum to 1.0) of total score
- Evidence: Sentences with extreme readability scores

=== CURRENT STATUS ===
Simulated implementation using basic sentence length and word complexity
with approximated Flesch Reading Ease calculations.
"""

import random
import re
from typing import List
from .base_analyzer import BaseAnalyzer, DimensionResult, Evidence, AnalysisLevel

class ReadabilityAnalyzer(BaseAnalyzer):
    """Analyzer for text readability and complexity patterns"""
    
    def __init__(self):
        super().__init__(
            dimension_id="readability",
            analysis_level=AnalysisLevel.SENTENCE,
            default_weight=0.143
        )
    
    def get_dimension_name(self) -> str:
        return "Readability"
    
    def get_description(self) -> str:
        return "Measures natural readability using Flesch Reading Ease and complexity metrics"
    
    def get_score_interpretation(self) -> str:
        return "Very high = too simplistic, Very low = too complex"
    
    def analyze(self, text: str, **kwargs) -> DimensionResult:
        """Analyze readability at sentence level"""
        
        # Simulate readability calculation
        score = self.simulate_readability_calculation(text)
        
        # Generate evidences
        evidences = self.generate_readability_evidences(text, score)
        
        return DimensionResult(
            dimension_id=self.dimension_id,
            score=score,
            weight=self.default_weight,
            active=self.is_enabled,
            evidences=evidences,
            total_evidences=len(evidences),
            analysis_level=self.analysis_level
        )
    
    def simulate_readability_calculation(self, text: str) -> float:
        """
        Simulate readability calculation using Flesch Reading Ease approximation
        Real implementation would use sophisticated readability metrics
        """
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if not sentences:
            return 0.5
        
        total_readability_score = 0
        valid_sentences = 0
        
        for sentence in sentences:
            if len(sentence.strip()) < 5:
                continue
            
            # Calculate readability metrics for this sentence
            flesch_score = self.calculate_flesch_approximation(sentence)
            complexity_score = self.analyze_sentence_complexity(sentence)
            
            # Convert readability to AI likelihood
            # Very high readability (too simple) or very low (too complex) might indicate AI
            if flesch_score > 90:  # Too simple
                sentence_score = 0.6 + random.uniform(-0.1, 0.1)
            elif flesch_score < 30:  # Too complex
                sentence_score = 0.7 + random.uniform(-0.1, 0.1)
            else:  # Natural readability
                sentence_score = 0.3 + random.uniform(-0.1, 0.1)
            
            # Incorporate complexity score
            combined_score = (sentence_score + complexity_score) / 2
            
            total_readability_score += combined_score
            valid_sentences += 1
        
        if valid_sentences == 0:
            return 0.5
        
        average_score = total_readability_score / valid_sentences
        return max(0.0, min(1.0, average_score))
    
    def calculate_flesch_approximation(self, sentence: str) -> float:
        """
        Approximate Flesch Reading Ease score
        Formula: 206.835 - (1.015 × ASL) - (84.6 × ASW)
        ASL = Average Sentence Length (words per sentence)
        ASW = Average Syllables per Word
        """
        words = sentence.split()
        word_count = len(words)
        
        if word_count == 0:
            return 50.0
        
        # Approximate syllable count (very rough estimation)
        total_syllables = 0
        for word in words:
            # Simple syllable estimation
            vowels = len(re.findall(r'[aeiouAEIOU]', word))
            syllables = max(1, vowels)  # At least 1 syllable per word
            total_syllables += syllables
        
        avg_syllables_per_word = total_syllables / word_count
        avg_sentence_length = word_count  # Since we're analyzing one sentence
        
        # Simplified Flesch formula
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Clamp to reasonable range
        return max(0.0, min(100.0, flesch_score))
    
    def analyze_sentence_complexity(self, sentence: str) -> float:
        """Analyze sentence structural complexity"""
        words = sentence.split()
        word_count = len(words)
        
        if word_count == 0:
            return 0.5
        
        # Analyze complexity indicators
        long_words = sum(1 for word in words if len(word) > 6)
        long_word_ratio = long_words / word_count
        
        # Count subordinating conjunctions and complex structures
        complex_words = ['however', 'therefore', 'moreover', 'furthermore', 'consequently', 
                        'nevertheless', 'nonetheless', 'although', 'whereas', 'whereby']
        complex_indicators = sum(1 for word in words if word.lower() in complex_words)
        
        # Punctuation complexity
        commas = sentence.count(',')
        semicolons = sentence.count(';')
        colons = sentence.count(':')
        complex_punct = commas + semicolons * 2 + colons * 2
        
        # Calculate complexity score
        if word_count > 25:  # Very long sentences
            complexity = 0.7 + random.uniform(-0.1, 0.1)
        elif long_word_ratio > 0.5:  # Too many long words
            complexity = 0.6 + random.uniform(-0.1, 0.1)
        elif complex_indicators > 2:  # Too many complex connectors
            complexity = 0.6 + random.uniform(-0.1, 0.1)
        elif complex_punct > word_count * 0.3:  # Too much complex punctuation
            complexity = 0.6 + random.uniform(-0.1, 0.1)
        else:  # Natural complexity
            complexity = 0.3 + random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, complexity))
    
    def generate_readability_evidences(self, text: str, score: float) -> List[Evidence]:
        """Generate readability evidences"""
        evidences = []
        sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
        
        # Select up to 15 sentences for evidence
        selected_sentences = sentences[:15]
        
        for i, sentence in enumerate(selected_sentences):
            if len(sentence.strip()) < 5:
                continue
            
            # Calculate readability metrics for this sentence
            flesch_score = self.calculate_flesch_approximation(sentence)
            word_count = len(sentence.split())
            
            # Vary evidence scores around the main score
            evidence_score = score + random.uniform(-0.15, 0.15)
            evidence_score = max(0.0, min(1.0, evidence_score))
            
            # Generate readability-specific reason
            reason = self.generate_readability_reason(sentence, flesch_score, word_count, evidence_score)
            
            evidences.append(Evidence(
                text=sentence,
                score=evidence_score,
                start_index=i * len(sentence),
                end_index=(i + 1) * len(sentence),
                evidence_type="sentence",
                reason=reason
            ))
        
        return evidences
    
    def get_readability_level(self, flesch_score: float) -> str:
        """Convert Flesch score to readability level"""
        if flesch_score >= 90:
            return "Very Easy"
        elif flesch_score >= 80:
            return "Easy"
        elif flesch_score >= 70:
            return "Fairly Easy"
        elif flesch_score >= 60:
            return "Standard"
        elif flesch_score >= 50:
            return "Fairly Difficult"
        elif flesch_score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def generate_readability_reason(self, sentence: str, flesch_score: float, word_count: int, score: float) -> str:
        """Generate specific reason for readability evidence"""
        readability_level = self.get_readability_level(flesch_score)
        
        if score <= 0.3:
            return f"Natural readability level: {readability_level} (Flesch: {flesch_score:.1f}, {word_count} words)"
        elif score <= 0.6:
            return f"Moderate readability complexity: {readability_level} ({word_count} words)"
        else:
            if flesch_score > 90:
                return f"Suspiciously simple readability ({readability_level}) suggesting artificial simplification"
            elif flesch_score < 30:
                return f"Unnaturally complex readability ({readability_level}) indicating possible AI generation"
            else:
                return f"Readability anomalies detected: {readability_level} level with {word_count} words"