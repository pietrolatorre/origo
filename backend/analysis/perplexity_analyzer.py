"""
Perplexity Analyzer - Sentence Level Analysis

=== CONTEXT AND PURPOSE ===
This module is part of Origo's 7-dimension AI text detection system.
Perplexity measures how "predictable" text is from a language model's perspective.
Lower perplexity = more predictable = potentially more AI-generated.
Higher perplexity = less predictable = potentially more human-written.

=== ANALYSIS APPROACH ===
- ATOMIC LEVEL: Sentence-by-sentence analysis
- AGGREGATION: Paragraph = max(sentence scores), Global = mean(paragraph scores)
- REAL IMPLEMENTATION: Would use GPT-2 or similar LM for actual next-word probabilities
- CURRENT STATUS: Simulated calculations with realistic patterns

=== TECHNICAL DETAILS ===
- Input: Raw text string
- Output: DimensionResult with score (0-1), evidences, and metadata
- Score Interpretation: 0.0 = very natural, 1.0 = very artificial
- Evidence Type: Individual sentences with perplexity reasoning

=== INTEGRATION POINTS ===
- Inherits from BaseAnalyzer (defines interface and common functionality)
- Called by AnalysisCoordinator during full text analysis
- Results aggregated with other 6 dimensions for global score
- Weight: 14.3% (1/7) of total analysis by default

=== FUTURE DEVELOPMENT ===
To implement real perplexity calculation:
1. Load GPT-2 model from model_loader utility
2. Tokenize sentences and calculate log probabilities
3. Apply sliding window for long sentences
4. Handle edge cases (very short/long text, special characters)
"""

import random
from typing import List
from .base_analyzer import BaseAnalyzer, DimensionResult, Evidence, AnalysisLevel

class PerplexityAnalyzer(BaseAnalyzer):
    """Analyzer for text perplexity using language model probability"""
    
    def __init__(self):
        super().__init__(
            dimension_id="perplexity",
            analysis_level=AnalysisLevel.SENTENCE,
            default_weight=0.143
        )
    
    def get_dimension_name(self) -> str:
        return "Perplexity"
    
    def get_description(self) -> str:
        return "Analyzes text predictability using language model patterns to detect statistical likelihood"
    
    def get_score_interpretation(self) -> str:
        return "Low = more natural, High = more likely artificial"
    
    def analyze(self, text: str, **kwargs) -> DimensionResult:
        """Analyze text perplexity at sentence level"""
        
        # Simulate perplexity calculation
        score = self.simulate_perplexity_calculation(text)
        
        # Generate evidences
        evidences = self.generate_perplexity_evidences(text, score)
        
        return DimensionResult(
            dimension_id=self.dimension_id,
            score=score,
            weight=self.default_weight,
            active=self.is_enabled,
            evidences=evidences,
            total_evidences=len(evidences),
            analysis_level=self.analysis_level
        )
    
    def simulate_perplexity_calculation(self, text: str) -> float:
        """
        Simulate perplexity calculation based on text characteristics.
        
        === CURRENT IMPLEMENTATION (SIMULATED) ===
        This is a placeholder that generates realistic perplexity-like scores
        based on observable text patterns that correlate with AI generation:
        - Repetitive word usage (high repetition = low perplexity = more AI-like)
        - Sentence length uniformity
        - Vocabulary diversity
        
        === REAL IMPLEMENTATION APPROACH ===
        1. Load pre-trained language model (GPT-2)
        2. Tokenize each sentence
        3. Calculate log probability for each token given previous context
        4. Average log probabilities to get sentence perplexity
        5. Aggregate sentence scores to paragraph/global level
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            float: Perplexity score (0.0 = natural, 1.0 = artificial)
            
        Note:
            Real perplexity formula: perplexity = exp(-1/N * sum(log P(w_i|context)))
            Lower perplexity = more predictable = potentially AI-generated
        """
        sentences = text.split('.')
        valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        if not valid_sentences:
            return 0.5
        
        # Simulate perplexity based on sentence characteristics
        total_perplexity = 0
        for sentence in valid_sentences:
            # Simulate factors that affect perplexity
            word_count = len(sentence.split())
            unique_words = len(set(sentence.lower().split()))
            repetition_ratio = 1.0 - (unique_words / max(word_count, 1))
            
            # Higher repetition and shorter sentences tend to be more predictable (higher AI likelihood)
            sentence_perplexity = 0.3 + (repetition_ratio * 0.4) + random.uniform(-0.1, 0.1)
            total_perplexity += sentence_perplexity
        
        average_perplexity = total_perplexity / len(valid_sentences)
        return max(0.0, min(1.0, average_perplexity))
    
    def generate_perplexity_evidences(self, text: str, score: float) -> List[Evidence]:
        """Generate perplexity-specific evidences"""
        evidences = []
        sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
        
        # Select up to 15 sentences for evidence
        selected_sentences = sentences[:15]
        
        for i, sentence in enumerate(selected_sentences):
            # Vary evidence scores around the main score
            evidence_score = score + random.uniform(-0.15, 0.15)
            evidence_score = max(0.0, min(1.0, evidence_score))
            
            # Generate perplexity-specific reason
            reason = self.generate_perplexity_reason(sentence, evidence_score)
            
            evidences.append(Evidence(
                text=sentence,
                score=evidence_score,
                start_index=i * len(sentence),  # Approximate positioning
                end_index=(i + 1) * len(sentence),
                evidence_type="sentence",
                reason=reason
            ))
        
        return evidences
    
    def generate_perplexity_reason(self, sentence: str, score: float) -> str:
        """Generate specific reason for perplexity evidence"""
        word_count = len(sentence.split())
        
        if score <= 0.3:
            return f"Natural language patterns with varied word choices ({word_count} words)"
        elif score <= 0.6:
            return f"Moderate predictability in sentence structure ({word_count} words)"
        else:
            return f"High predictability suggesting potential AI generation ({word_count} words)"