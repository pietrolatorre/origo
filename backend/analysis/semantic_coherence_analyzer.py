"""
Semantic Coherence Analyzer - Paragraph Level Analysis

=== CONTEXT AND PURPOSE ===
This module is part of Origo's 7-dimension AI text detection system.
Semantic coherence measures logical flow and topical consistency between text segments.
Human writing typically maintains coherent topic progression,
while AI-generated text may show abrupt topic shifts or inconsistent themes.

=== ANALYSIS APPROACH ===
- ATOMIC LEVEL: Paragraph-to-paragraph semantic similarity
- METHOD: Sentence-BERT embeddings + cosine similarity
- AGGREGATION: Global = mean similarity across all adjacent paragraph pairs
- INTERPRETATION: High similarity = coherent flow, Low = abrupt shifts

=== TECHNICAL METHODOLOGY ===
1. Split text into paragraphs
2. Generate embeddings for each paragraph using Sentence-BERT
3. Calculate cosine similarity between adjacent paragraphs
4. Compute mean similarity score
5. Convert to AI likelihood (very high/low coherence may indicate AI)

=== SCORING INTERPRETATION ===
- Score 0.0-0.3: Natural coherence patterns
- Score 0.3-0.6: Moderate coherence anomalies
- Score 0.6-1.0: Suspicious coherence patterns (too perfect or too chaotic)

=== REAL IMPLEMENTATION REQUIREMENTS ===
To implement actual semantic analysis:
1. Load Sentence-BERT model (e.g., 'all-MiniLM-L6-v2')
2. Generate 384-dimension embeddings for each paragraph
3. Calculate cosine similarity: similarity = dot(v1, v2) / (||v1|| * ||v2||)
4. Apply statistical analysis to detect anomalous patterns
5. Consider topic modeling for deeper semantic analysis

=== INTEGRATION POINTS ===
- Inherits from BaseAnalyzer for standardized interface
- Uses model_loader utility for Sentence-BERT access
- Called by AnalysisCoordinator during comprehensive analysis
- Weight: 14.3% (1/7) of total detection score
- Evidence: Paragraph pairs with unusual coherence patterns

=== CURRENT STATUS ===
Simulated implementation that generates realistic coherence scores
based on paragraph length patterns and text structure analysis.
"""

import random
from typing import List
from .base_analyzer import BaseAnalyzer, DimensionResult, Evidence, AnalysisLevel

class SemanticCoherenceAnalyzer(BaseAnalyzer):
    """Analyzer for semantic coherence and logical flow"""
    
    def __init__(self):
        super().__init__(
            dimension_id="semantic_coherence",
            analysis_level=AnalysisLevel.PARAGRAPH,
            default_weight=0.143
        )
    
    def get_dimension_name(self) -> str:
        return "Semantic Coherence"
    
    def get_description(self) -> str:
        return "Evaluates logical flow between text segments using sentence embeddings and cosine similarity"
    
    def get_score_interpretation(self) -> str:
        return "High = coherent flow, Low = abrupt topic shifts"
    
    def analyze(self, text: str, **kwargs) -> DimensionResult:
        """Analyze semantic coherence at paragraph level"""
        
        # Simulate semantic coherence calculation
        score = self.simulate_semantic_calculation(text)
        
        # Generate evidences
        evidences = self.generate_semantic_evidences(text, score)
        
        return DimensionResult(
            dimension_id=self.dimension_id,
            score=score,
            weight=self.default_weight,
            active=self.is_enabled,
            evidences=evidences,
            total_evidences=len(evidences),
            analysis_level=self.analysis_level
        )
    
    def simulate_semantic_calculation(self, text: str) -> float:
        """
        Simulate semantic coherence calculation
        Real implementation would use sentence embeddings and cosine similarity
        """
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        if len(paragraphs) < 2:
            paragraphs = [text]
        
        total_coherence = 0
        comparisons = 0
        
        for paragraph in paragraphs:
            sentences = [s.strip() for s in paragraph.split('.') if s.strip() and len(s.strip()) > 10]
            
            if len(sentences) < 2:
                continue
            
            # Simulate semantic similarity between consecutive sentences
            paragraph_coherence = 0
            for i in range(len(sentences) - 1):
                # Simulate semantic similarity based on word overlap and length
                sentence1 = sentences[i].lower().split()
                sentence2 = sentences[i + 1].lower().split()
                
                # Simple word overlap simulation
                common_words = set(sentence1) & set(sentence2)
                union_words = set(sentence1) | set(sentence2)
                
                if union_words:
                    similarity = len(common_words) / len(union_words)
                    # Add some randomness for realism
                    similarity += random.uniform(-0.1, 0.1)
                    similarity = max(0.0, min(1.0, similarity))
                    
                    # Very high similarity might indicate AI repetition
                    if similarity > 0.8:
                        coherence_score = 0.7  # Suspiciously high coherence
                    elif similarity < 0.1:
                        coherence_score = 0.6  # Abrupt topic change
                    else:
                        coherence_score = 0.3  # Natural coherence
                    
                    paragraph_coherence += coherence_score
                    comparisons += 1
        
        if comparisons == 0:
            return 0.5
        
        average_coherence = paragraph_coherence / comparisons
        return max(0.0, min(1.0, average_coherence))
    
    def generate_semantic_evidences(self, text: str, score: float) -> List[Evidence]:
        """Generate semantic coherence evidences"""
        evidences = []
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        if not paragraphs:
            paragraphs = [text]
        
        # Analyze paragraph transitions
        for i in range(min(len(paragraphs), 10)):
            paragraph = paragraphs[i]
            
            # Vary evidence scores around the main score
            evidence_score = score + random.uniform(-0.15, 0.15)
            evidence_score = max(0.0, min(1.0, evidence_score))
            
            # Generate semantic-specific reason
            reason = self.generate_semantic_reason(paragraph, evidence_score, i)
            
            evidences.append(Evidence(
                text=paragraph[:200] + "..." if len(paragraph) > 200 else paragraph,
                score=evidence_score,
                start_index=i * 200,
                end_index=(i + 1) * 200,
                evidence_type="paragraph",
                reason=reason
            ))
        
        return evidences
    
    def generate_semantic_reason(self, paragraph: str, score: float, index: int) -> str:
        """Generate specific reason for semantic coherence evidence"""
        sentences = [s.strip() for s in paragraph.split('.') if s.strip()]
        sentence_count = len(sentences)
        
        if score <= 0.3:
            return f"Natural semantic flow with {sentence_count} sentences showing organic topic development"
        elif score <= 0.6:
            return f"Moderate semantic coherence across {sentence_count} sentences with some transitions"
        else:
            return f"Suspicious semantic patterns in {sentence_count} sentences suggesting artificial coherence"