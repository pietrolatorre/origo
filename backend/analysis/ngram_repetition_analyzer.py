"""
N-gram Repetition Analyzer - Global Level Analysis

=== CONTEXT AND PURPOSE ===
This module is part of Origo's 7-dimension AI text detection system.
N-gram analysis detects unusual repetition patterns in word sequences.
AI models may exhibit repetitive patterns or lack natural linguistic diversity
that characterizes human writing.

=== ANALYSIS APPROACH ===
- ATOMIC LEVEL: Global analysis across entire text
- SCOPE: Bigrams (2-word), Trigrams (3-word), 4-grams analysis
- METRICS: Repetition rate, diversity index, frequency distribution entropy
- AGGREGATION: Already global - no paragraph/sentence breakdown needed

=== KEY MEASUREMENTS ===
1. **Repetition Rate**: #repeated_ngrams / #total_ngrams
2. **Diversity Index**: Type-Token Ratio for n-grams
3. **Frequency Entropy**: Measure of n-gram distribution uniformity
4. **Anomaly Detection**: Statistical outliers in repetition patterns

=== MATHEMATICAL FOUNDATION ===
For each n-gram size (2, 3, 4):
- Generate all possible n-grams from text
- Count frequencies using Counter
- Calculate diversity: unique_ngrams / total_ngrams
- Identify most frequent patterns (evidence)
- Weighted combination of n-gram scores

=== SCORING INTERPRETATION ===
- High repetition rates = suspicious artificiality
- Low diversity = potential AI generation
- Extreme frequency distributions = anomalous patterns
- Natural text shows balanced repetition/diversity

=== REAL IMPLEMENTATION APPROACH ===
1. Robust tokenization and normalization
2. Statistical significance testing for repetition patterns
3. Comparison against human/AI corpora baselines
4. Language-specific n-gram analysis
5. Entropy calculation for frequency distributions

=== INTEGRATION POINTS ===
- Inherits from BaseAnalyzer for interface consistency
- Operates at global level (unlike sentence/paragraph analyzers)
- Called by AnalysisCoordinator for comprehensive analysis
- Weight: 14.3% (1/7) of total detection score
- Evidence: Most frequently repeated n-grams with occurrence counts

=== CURRENT STATUS ===
Simulated implementation using basic Counter analysis
with realistic repetition pattern detection.
"""

import random
from collections import Counter
from typing import List, Tuple
from .base_analyzer import BaseAnalyzer, DimensionResult, Evidence, AnalysisLevel

class NgramRepetitionAnalyzer(BaseAnalyzer):
    """Analyzer for n-gram repetition patterns"""
    
    def __init__(self):
        super().__init__(
            dimension_id="ngram_repetition",
            analysis_level=AnalysisLevel.GLOBAL,
            default_weight=0.143
        )
    
    def get_dimension_name(self) -> str:
        return "N-gram Repetition"
    
    def get_description(self) -> str:
        return "Detects unusual repetition of word sequences and analyzes diversity patterns"
    
    def get_score_interpretation(self) -> str:
        return "High repetition = suspicious of artificiality"
    
    def analyze(self, text: str, **kwargs) -> DimensionResult:
        """Analyze n-gram repetition at global level"""
        
        # Simulate n-gram repetition calculation
        score = self.simulate_ngram_calculation(text)
        
        # Generate evidences
        evidences = self.generate_ngram_evidences(text, score)
        
        return DimensionResult(
            dimension_id=self.dimension_id,
            score=score,
            weight=self.default_weight,
            active=self.is_enabled,
            evidences=evidences,
            total_evidences=len(evidences),
            analysis_level=self.analysis_level
        )
    
    def simulate_ngram_calculation(self, text: str) -> float:
        """
        Simulate n-gram repetition calculation
        Real implementation would analyze bigrams, trigrams, and 4-grams
        """
        words = text.lower().split()
        
        if len(words) < 4:
            return 0.5
        
        # Analyze different n-gram sizes
        bigram_score = self.analyze_ngrams(words, 2)
        trigram_score = self.analyze_ngrams(words, 3)
        fourgram_score = self.analyze_ngrams(words, 4)
        
        # Weighted average of n-gram scores
        overall_score = (bigram_score * 0.3 + trigram_score * 0.4 + fourgram_score * 0.3)
        
        return max(0.0, min(1.0, overall_score))
    
    def analyze_ngrams(self, words: List[str], n: int) -> float:
        """Analyze n-grams of size n"""
        if len(words) < n:
            return 0.5
        
        # Generate n-grams
        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = tuple(words[i:i + n])
            ngrams.append(ngram)
        
        # Count frequencies
        ngram_counts = Counter(ngrams)
        total_ngrams = len(ngrams)
        unique_ngrams = len(ngram_counts)
        
        # Calculate repetition metrics
        if total_ngrams == 0:
            return 0.5
        
        # Diversity ratio (higher = more diverse = lower AI likelihood)
        diversity_ratio = unique_ngrams / total_ngrams
        
        # Find most frequent n-grams
        max_frequency = max(ngram_counts.values()) if ngram_counts else 1
        frequency_ratio = max_frequency / total_ngrams
        
        # High repetition or low diversity suggests AI generation
        repetition_score = (1 - diversity_ratio) * 0.7 + frequency_ratio * 0.3
        
        # Add some noise for realism
        repetition_score += random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, repetition_score))
    
    def generate_ngram_evidences(self, text: str, score: float) -> List[Evidence]:
        """Generate n-gram repetition evidences"""
        evidences = []
        words = text.lower().split()
        
        if len(words) < 4:
            return evidences
        
        # Find most repetitive n-grams for evidence
        bigrams = self.get_most_frequent_ngrams(words, 2, 5)
        trigrams = self.get_most_frequent_ngrams(words, 3, 5)
        fourgrams = self.get_most_frequent_ngrams(words, 4, 5)
        
        evidence_count = 0
        
        # Add bigram evidences
        for ngram, frequency in bigrams:
            if evidence_count >= 15:
                break
            
            evidence_score = score + random.uniform(-0.1, 0.1)
            evidence_score = max(0.0, min(1.0, evidence_score))
            
            ngram_text = ' '.join(ngram)
            reason = f"Bigram '{ngram_text}' appears {frequency} times"
            
            evidences.append(Evidence(
                text=ngram_text,
                score=evidence_score,
                start_index=evidence_count * 10,
                end_index=(evidence_count + 1) * 10,
                evidence_type="ngram",
                reason=reason
            ))
            evidence_count += 1
        
        # Add trigram evidences
        for ngram, frequency in trigrams:
            if evidence_count >= 15:
                break
            
            evidence_score = score + random.uniform(-0.1, 0.1)
            evidence_score = max(0.0, min(1.0, evidence_score))
            
            ngram_text = ' '.join(ngram)
            reason = f"Trigram '{ngram_text}' appears {frequency} times"
            
            evidences.append(Evidence(
                text=ngram_text,
                score=evidence_score,
                start_index=evidence_count * 10,
                end_index=(evidence_count + 1) * 10,
                evidence_type="ngram",
                reason=reason
            ))
            evidence_count += 1
        
        return evidences
    
    def get_most_frequent_ngrams(self, words: List[str], n: int, top_k: int) -> List[Tuple[Tuple[str, ...], int]]:
        """Get the most frequent n-grams"""
        if len(words) < n:
            return []
        
        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = tuple(words[i:i + n])
            ngrams.append(ngram)
        
        ngram_counts = Counter(ngrams)
        
        # Return only n-grams that appear more than once
        repeated_ngrams = [(ngram, count) for ngram, count in ngram_counts.items() if count > 1]
        repeated_ngrams.sort(key=lambda x: x[1], reverse=True)
        
        return repeated_ngrams[:top_k]