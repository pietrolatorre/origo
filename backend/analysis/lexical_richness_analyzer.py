"""
Lexical Richness Analyzer - Sentence Level Analysis

=== CONTEXT AND PURPOSE ===
This module is part of Origo's 7-dimension AI text detection system.
Lexical richness measures vocabulary variety and linguistic diversity.
Human writing typically shows rich vocabulary usage,
while AI-generated text may exhibit repetitive word choices or
unnatural vocabulary patterns.

=== ANALYSIS APPROACH ===
- ATOMIC LEVEL: Sentence-by-sentence vocabulary analysis
- PRIMARY METRIC: Type-Token Ratio (TTR = unique_words / total_words)
- AGGREGATION: Paragraph = mean(sentence TTR), Global = mean(paragraph TTR)
- INTERPRETATION: Low TTR = repetitive/poor vocabulary, High TTR = rich vocabulary

=== MATHEMATICAL FOUNDATION ===
For each sentence:
1. Tokenize into individual words
2. Count total words (tokens)
3. Count unique words (types)
4. Calculate TTR = unique_words / total_words
5. Convert TTR to AI likelihood score

=== ADDITIONAL METRICS (Future Implementation) ===
- **Moving Average TTR (MATTR)**: TTR calculated over moving windows
- **Measure of Textual Lexical Diversity (MTLD)**: Advanced diversity measure
- **Hapax Legomena**: Words appearing only once in text
- **Vocabulary Sophistication**: Average word length, syllable count

=== SCORING LOGIC ===
- Very low TTR (< 0.3): High repetition → High AI likelihood
- Very high TTR (> 0.9): Unnatural diversity → Moderate AI likelihood
- Balanced TTR (0.4-0.8): Natural vocabulary → Low AI likelihood

=== LINGUISTIC CONSIDERATIONS ===
- Function words vs content words
- Word frequency distributions
- Semantic field diversity
- Register consistency

=== INTEGRATION POINTS ===
- Inherits from BaseAnalyzer for standardized interface
- Sentence-level analysis like Perplexity and Readability
- Called by AnalysisCoordinator during full text analysis
- Weight: 14.3% (1/7) of total detection score
- Evidence: Sentences with extreme lexical richness patterns

=== CURRENT STATUS ===
Simulated implementation using basic word counting
with realistic vocabulary diversity scoring.
"""

import random
from typing import List, Set
from .base_analyzer import BaseAnalyzer, DimensionResult, Evidence, AnalysisLevel

class LexicalRichnessAnalyzer(BaseAnalyzer):
    """Analyzer for vocabulary diversity and lexical richness"""
    
    def __init__(self):
        super().__init__(
            dimension_id="lexical_richness",
            analysis_level=AnalysisLevel.SENTENCE,
            default_weight=0.143
        )
    
    def get_dimension_name(self) -> str:
        return "Lexical Richness"
    
    def get_description(self) -> str:
        return "Measures vocabulary variety using Type-Token Ratio analysis"
    
    def get_score_interpretation(self) -> str:
        return "Low = repetitive/poor vocabulary, High = rich"
    
    def analyze(self, text: str, **kwargs) -> DimensionResult:
        """Analyze lexical richness at sentence level"""
        
        # Simulate lexical richness calculation
        score = self.simulate_lexical_calculation(text)
        
        # Generate evidences
        evidences = self.generate_lexical_evidences(text, score)
        
        return DimensionResult(
            dimension_id=self.dimension_id,
            score=score,
            weight=self.default_weight,
            active=self.is_enabled,
            evidences=evidences,
            total_evidences=len(evidences),
            analysis_level=self.analysis_level
        )
    
    def simulate_lexical_calculation(self, text: str) -> float:
        """
        Simulate lexical richness calculation using Type-Token Ratio
        Real implementation would use more sophisticated lexical diversity metrics
        """
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if not sentences:
            return 0.5
        
        total_richness = 0
        valid_sentences = 0
        
        for sentence in sentences:
            words = [w.lower() for w in sentence.split() if w.isalpha()]
            
            if len(words) < 3:  # Skip very short sentences
                continue
            
            # Calculate Type-Token Ratio
            unique_words = len(set(words))
            total_words = len(words)
            
            if total_words > 0:
                ttr = unique_words / total_words
                
                # Convert TTR to AI likelihood score
                # Very low TTR (repetitive) = higher AI likelihood
                # Very high TTR (overly diverse for short text) might also suggest AI
                if ttr < 0.5:  # Low diversity
                    sentence_score = 0.7 + random.uniform(-0.1, 0.1)
                elif ttr > 0.95:  # Suspiciously high diversity
                    sentence_score = 0.6 + random.uniform(-0.1, 0.1)
                else:  # Natural diversity
                    sentence_score = 0.3 + random.uniform(-0.1, 0.1)
                
                total_richness += sentence_score
                valid_sentences += 1
        
        if valid_sentences == 0:
            return 0.5
        
        average_richness = total_richness / valid_sentences
        return max(0.0, min(1.0, average_richness))
    
    def calculate_ttr(self, words: List[str]) -> float:
        """Calculate Type-Token Ratio"""
        if not words:
            return 0.0
        
        unique_words = len(set(words))
        total_words = len(words)
        
        return unique_words / total_words if total_words > 0 else 0.0
    
    def generate_lexical_evidences(self, text: str, score: float) -> List[Evidence]:
        """Generate lexical richness evidences"""
        evidences = []
        sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
        
        # Select up to 15 sentences for evidence
        selected_sentences = sentences[:15]
        
        for i, sentence in enumerate(selected_sentences):
            words = [w.lower() for w in sentence.split() if w.isalpha()]
            
            if len(words) < 3:
                continue
            
            # Calculate TTR for this sentence
            ttr = self.calculate_ttr(words)
            
            # Vary evidence scores around the main score
            evidence_score = score + random.uniform(-0.15, 0.15)
            evidence_score = max(0.0, min(1.0, evidence_score))
            
            # Generate lexical-specific reason
            reason = self.generate_lexical_reason(words, ttr, evidence_score)
            
            evidences.append(Evidence(
                text=sentence,
                score=evidence_score,
                start_index=i * len(sentence),
                end_index=(i + 1) * len(sentence),
                evidence_type="sentence",
                reason=reason
            ))
        
        return evidences
    
    def generate_lexical_reason(self, words: List[str], ttr: float, score: float) -> str:
        """Generate specific reason for lexical richness evidence"""
        unique_count = len(set(words))
        total_count = len(words)
        
        if score <= 0.3:
            return f"Natural vocabulary diversity: {unique_count}/{total_count} unique words (TTR: {ttr:.2f})"
        elif score <= 0.6:
            return f"Moderate lexical variety: {unique_count}/{total_count} unique words (TTR: {ttr:.2f})"
        else:
            if ttr < 0.5:
                return f"Low vocabulary diversity suggesting repetitive patterns: {unique_count}/{total_count} words (TTR: {ttr:.2f})"
            else:
                return f"Unusual lexical patterns: {unique_count}/{total_count} unique words (TTR: {ttr:.2f})"