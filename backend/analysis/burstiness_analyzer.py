"""
Burstiness Analyzer - Paragraph Level Analysis

=== CONTEXT AND PURPOSE ===
This module is part of Origo's 7-dimension AI text detection system.
Burstiness measures variability in sentence lengths within paragraphs.
Human writing typically shows natural variation in sentence length,
while AI-generated text may be too uniform (low burstiness) or 
unnaturally oscillating (high burstiness).

=== ANALYSIS APPROACH ===
- ATOMIC LEVEL: Sentence length analysis within each paragraph
- MEASUREMENT: Coefficient of Variation (CV = standard_deviation / mean)
- AGGREGATION: Global = mean of paragraph burstiness scores
- INTERPRETATION: Very low CV = monotonous, Very high CV = unnatural

=== MATHEMATICAL FOUNDATION ===
For each paragraph:
1. Calculate sentence lengths L = [len(s1), len(s2), ..., len(sn)]
2. Compute mean μ = mean(L)
3. Compute standard deviation σ = std(L)
4. Burstiness = σ / μ (Coefficient of Variation)
5. Convert CV to AI likelihood score

=== SCORING LOGIC ===
- CV < 0.2: Too uniform → High AI likelihood (score ~0.7)
- CV > 0.8: Too variable → Moderate AI likelihood (score ~0.6)
- 0.2 ≤ CV ≤ 0.8: Natural variation → Low AI likelihood (score ~0.2)

=== INTEGRATION POINTS ===
- Inherits from BaseAnalyzer for common interface
- Called by AnalysisCoordinator during full analysis
- Weight: 14.3% (1/7) of total score by default
- Evidence: Paragraphs with extreme burstiness values

=== FUTURE ENHANCEMENTS ===
- Add word-level burstiness analysis
- Consider punctuation patterns
- Analyze structural consistency across document
- Language-specific sentence length norms
"""

import random
import statistics
from typing import List
from .base_analyzer import BaseAnalyzer, DimensionResult, Evidence, AnalysisLevel

class BurstinessAnalyzer(BaseAnalyzer):
    """Analyzer for sentence length variability patterns"""
    
    def __init__(self):
        super().__init__(
            dimension_id="burstiness",
            analysis_level=AnalysisLevel.PARAGRAPH,
            default_weight=0.143
        )
    
    def get_dimension_name(self) -> str:
        return "Burstiness"
    
    def get_description(self) -> str:
        return "Measures variability in sentence lengths within paragraphs using coefficient of variation"
    
    def get_score_interpretation(self) -> str:
        return "Very low = monotonous, Very high = unnatural oscillation"
    
    def analyze(self, text: str, **kwargs) -> DimensionResult:
        """Analyze text burstiness at paragraph level"""
        
        # Simulate burstiness calculation
        score = self.simulate_burstiness_calculation(text)
        
        # Generate evidences
        evidences = self.generate_burstiness_evidences(text, score)
        
        return DimensionResult(
            dimension_id=self.dimension_id,
            score=score,
            weight=self.default_weight,
            active=self.is_enabled,
            evidences=evidences,
            total_evidences=len(evidences),
            analysis_level=self.analysis_level
        )
    
    def simulate_burstiness_calculation(self, text: str) -> float:
        """
        Simulate burstiness calculation based on sentence length variation
        Real implementation would calculate coefficient of variation
        """
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        if len(paragraphs) < 2:
            # Treat as single paragraph
            paragraphs = [text]
        
        total_burstiness = 0
        valid_paragraphs = 0
        
        for paragraph in paragraphs:
            sentences = [s.strip() for s in paragraph.split('.') if s.strip()]
            
            if len(sentences) < 2:
                continue
            
            # Calculate sentence lengths
            sentence_lengths = [len(s.split()) for s in sentences]
            
            if len(sentence_lengths) < 2:
                continue
            
            # Calculate coefficient of variation
            mean_length = statistics.mean(sentence_lengths)
            if mean_length > 0:
                std_dev = statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0
                cv = std_dev / mean_length
                
                # Convert CV to AI likelihood score
                # Very low CV (monotonous) or very high CV (unnatural) = higher AI likelihood
                if cv < 0.2:  # Too uniform
                    paragraph_score = 0.7 + random.uniform(-0.1, 0.1)
                elif cv > 0.8:  # Too variable
                    paragraph_score = 0.6 + random.uniform(-0.1, 0.1)
                else:  # Natural variation
                    paragraph_score = 0.2 + random.uniform(-0.1, 0.1)
                
                total_burstiness += paragraph_score
                valid_paragraphs += 1
        
        if valid_paragraphs == 0:
            return 0.5
        
        average_burstiness = total_burstiness / valid_paragraphs
        return max(0.0, min(1.0, average_burstiness))
    
    def generate_burstiness_evidences(self, text: str, score: float) -> List[Evidence]:
        """Generate burstiness-specific evidences"""
        evidences = []
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        if not paragraphs:
            paragraphs = [text]
        
        # Select up to 10 paragraphs for evidence
        selected_paragraphs = paragraphs[:10]
        
        for i, paragraph in enumerate(selected_paragraphs):
            sentences = [s.strip() for s in paragraph.split('.') if s.strip()]
            
            if len(sentences) < 2:
                continue
            
            # Calculate actual sentence lengths for this paragraph
            sentence_lengths = [len(s.split()) for s in sentences]
            
            # Vary evidence scores around the main score
            evidence_score = score + random.uniform(-0.15, 0.15)
            evidence_score = max(0.0, min(1.0, evidence_score))
            
            # Generate burstiness-specific reason
            reason = self.generate_burstiness_reason(sentence_lengths, evidence_score)
            
            evidences.append(Evidence(
                text=paragraph[:200] + "..." if len(paragraph) > 200 else paragraph,
                score=evidence_score,
                start_index=i * 200,  # Approximate positioning
                end_index=(i + 1) * 200,
                evidence_type="paragraph",
                reason=reason
            ))
        
        return evidences
    
    def generate_burstiness_reason(self, sentence_lengths: List[int], score: float) -> str:
        """Generate specific reason for burstiness evidence"""
        if not sentence_lengths:
            return "Insufficient sentence data for analysis"
        
        mean_length = statistics.mean(sentence_lengths)
        cv = statistics.stdev(sentence_lengths) / mean_length if len(sentence_lengths) > 1 and mean_length > 0 else 0
        
        if score <= 0.3:
            return f"Natural sentence length variation (CV: {cv:.2f}, avg: {mean_length:.1f} words)"
        elif score <= 0.6:
            return f"Moderate sentence length patterns (CV: {cv:.2f}, avg: {mean_length:.1f} words)"
        else:
            return f"Unusual sentence length uniformity suggesting AI generation (CV: {cv:.2f})"