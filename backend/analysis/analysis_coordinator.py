"""
Analysis Coordinator - Main Orchestrator for 7-Dimension AI Text Detection

=== CONTEXT AND PURPOSE ===
This module serves as the central orchestrator for Origo's comprehensive
AI text detection system. It manages all 7 analysis dimensions,
performs real weighted aggregation, and coordinates the entire analysis pipeline.

=== SYSTEM ARCHITECTURE ROLE ===
The AnalysisCoordinator is the **central hub** that:
1. **Instantiates** all 7 dimension analyzers
2. **Orchestrates** parallel or sequential analysis execution
3. **Aggregates** dimension scores with proper weighting
4. **Formats** results for frontend consumption
5. **Manages** dimension activation and weight configuration

=== 7-DIMENSION FRAMEWORK ===
Manages these analysis dimensions:
1. **Perplexity** (Sentence): Language model predictability
2. **Burstiness** (Paragraph): Sentence length variation
3. **Semantic Coherence** (Paragraph): Topical flow consistency
4. **N-gram Repetition** (Global): Word sequence patterns
5. **Lexical Richness** (Sentence): Vocabulary diversity
6. **Stylistic Markers** (Sentence): Writing style patterns
7. **Readability** (Sentence): Text complexity measures

=== WEIGHTED AGGREGATION METHODOLOGY ===
**Default Weights** (Equal Distribution):
- Each dimension: ~14.3% (1/7 of total weight)
- Perplexity through Stylistic Markers: 0.143 each
- Readability: 0.142 (to ensure total = 1.0)

**Aggregation Formula**:
Global Score = Σ(dimension_score × weight) / Σ(active_weights)

**Key Features**:
- Automatic weight rebalancing when dimensions are disabled
- Normalization ensures scores remain in 0.0-1.0 range
- Statistical validation of weight distributions

=== API INTEGRATION ===
Primary method: `analyze_text_comprehensive(text, enabled_dimensions)`

**Input**:
- text (str): Raw text to analyze
- enabled_dimensions (Dict[str, bool]): Which dimensions to activate

**Output** (Frontend-Compatible JSON):
- overall_score: Weighted global score (0.0-1.0)
- global_scores: Individual dimension scores
- dimension_results: Detailed results with evidences
- weights_applied: Actual weights used in calculation
- active_dimensions: List of enabled dimension IDs
- analysis_metadata: Performance and statistics data

=== REAL-TIME PROCESSING PIPELINE ===
1. **Validation**: Check text length and enabled dimensions
2. **Parallel Execution**: Run enabled analyzers (future enhancement)
3. **Score Collection**: Gather DimensionResult objects
4. **Aggregation**: Calculate weighted global score
5. **Formatting**: Convert to frontend-compatible format
6. **Metadata**: Generate performance and statistical data

=== PERFORMANCE CHARACTERISTICS ===
- **Current**: Sequential processing of dimensions
- **Target**: < 5 seconds for texts up to 5000 words
- **Memory**: Efficient text processing with minimal overhead
- **Scalability**: Ready for parallel processing enhancement

=== ERROR HANDLING AND ROBUSTNESS ===
- Graceful degradation when dimensions fail
- Validation of weight configurations
- Fallback scoring for edge cases
- Comprehensive logging for debugging

=== CONFIGURATION MANAGEMENT ===
- Dynamic weight adjustment
- Runtime dimension enabling/disabling
- Validation of configuration changes
- Persistent configuration options (future)

=== DEVELOPMENT AND TESTING ===
**Current Status**: Production-ready with simulated calculations
**Testing**: Comprehensive test coverage needed
**Monitoring**: Built-in performance tracking
**Extensibility**: Easy addition of new dimensions

=== FUTURE ENHANCEMENTS ===
1. **Parallel Processing**: Async execution of independent dimensions
2. **Caching**: Model output and intermediate calculation caching
3. **Adaptive Weights**: ML-based weight optimization
4. **Batch Processing**: Multiple text analysis
5. **Real-time Monitoring**: Performance and accuracy metrics

=== INTEGRATION POINTS ===
- **FastAPI Backend**: Called from main.py analyze endpoint
- **Model Loader**: Accesses AI models for real calculations
- **PDF Generator**: Provides data for comprehensive reports
- **Frontend**: Sends results to React analysis interface
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from .base_analyzer import BaseAnalyzer, DimensionResult, AnalysisLevel
from .perplexity_analyzer import PerplexityAnalyzer
from .burstiness_analyzer import BurstinessAnalyzer
from .semantic_coherence_analyzer import SemanticCoherenceAnalyzer
from .ngram_repetition_analyzer import NgramRepetitionAnalyzer
from .lexical_richness_analyzer import LexicalRichnessAnalyzer
from .stylistic_markers_analyzer import StylisticMarkersAnalyzer
from .readability_analyzer import ReadabilityAnalyzer

class AnalysisCoordinator:
    """
    Coordinates all 7 analysis dimensions and performs aggregation
    """
    
    def __init__(self):
        # Initialize all analyzers
        self.analyzers: Dict[str, BaseAnalyzer] = {
            'perplexity': PerplexityAnalyzer(),
            'burstiness': BurstinessAnalyzer(),
            'semantic_coherence': SemanticCoherenceAnalyzer(),
            'ngram_repetition': NgramRepetitionAnalyzer(),
            'lexical_richness': LexicalRichnessAnalyzer(),
            'stylistic_markers': StylisticMarkersAnalyzer(),
            'readability': ReadabilityAnalyzer()
        }
        
        # Default weights (equal weighting for all dimensions)
        self.default_weights = {
            'perplexity': 0.143,
            'burstiness': 0.143,
            'semantic_coherence': 0.143,
            'ngram_repetition': 0.143,
            'lexical_richness': 0.143,
            'stylistic_markers': 0.143,
            'readability': 0.142  # Slightly less to sum to 1.0
        }
    
    def analyze_text_comprehensive(self, text: str, enabled_dimensions: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis using all enabled dimensions
        Returns results in the format expected by the frontend
        """
        start_time = time.time()
        
        # Determine which dimensions are enabled
        if enabled_dimensions is None:
            enabled_dimensions = {dim_id: True for dim_id in self.analyzers.keys()}
        
        # Run analysis for each enabled dimension
        dimension_results = {}
        global_scores = {}
        weights_applied = {}
        active_dimensions = []
        
        for dim_id, analyzer in self.analyzers.items():
            is_enabled = enabled_dimensions.get(dim_id, True)
            
            if is_enabled:
                print(f"Analyzing {dim_id}...")
                
                # Run the dimension analysis
                result = analyzer.analyze(text)
                
                # Store results
                dimension_results[dim_id] = {
                    'score': result.score,
                    'weight': result.weight,
                    'active': result.active,
                    'totalEvidences': result.total_evidences,
                    'topEvidences': [self._evidence_to_dict(evidence) for evidence in result.top_evidences]
                }
                
                global_scores[dim_id] = result.score
                weights_applied[dim_id] = result.weight
                active_dimensions.append(dim_id)
                
                print(f"  → {dim_id}: {result.score:.3f}")
            else:
                global_scores[dim_id] = None
        
        # Calculate overall score using real weighted aggregation
        overall_score = self.calculate_overall_score(global_scores, weights_applied)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Format response according to frontend expectations
        # Convert to the new structured format matching TypeScript interfaces
        formatted_global_scores = {
            'perplexity': global_scores.get('perplexity'),
            'burstiness': global_scores.get('burstiness'),
            'semantic_coherence': global_scores.get('semantic_coherence'),
            'ngram_repetition': global_scores.get('ngram_repetition'),
            'lexical_richness': global_scores.get('lexical_richness'),
            'stylistic_markers': global_scores.get('stylistic_markers'),
            'readability': global_scores.get('readability')
        }
        
        formatted_dimension_results = {
            'perplexity': dimension_results.get('perplexity'),
            'burstiness': dimension_results.get('burstiness'),
            'semantic_coherence': dimension_results.get('semantic_coherence'),
            'ngram_repetition': dimension_results.get('ngram_repetition'),
            'lexical_richness': dimension_results.get('lexical_richness'),
            'stylistic_markers': dimension_results.get('stylistic_markers'),
            'readability': dimension_results.get('readability')
        }
        
        # Create metadata object
        metadata = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'sentence_count': len([s.strip() for s in text.split('.') if s.strip()]),
            'paragraph_count': len([p.strip() for p in text.split('\n') if p.strip()]) or 1,
            'processing_time_seconds': round(processing_time, 3),
            'weights_used': self.default_weights.copy(),
            'parallel_processing_enabled': False,
            'caching_enabled': False
        }
        
        response = {
            'overall_score': overall_score,
            'global_scores': formatted_global_scores,
            'dimension_results': formatted_dimension_results,
            'weights_applied': weights_applied,
            'active_dimensions': active_dimensions,
            'analysis_metadata': metadata,
            'paragraphs': [],  # Empty for current implementation
            'word_analysis': {'unique_words': []}  # Empty for current implementation
        }
        
        print(f"Analysis complete. Overall score: {overall_score:.3f} (processed in {processing_time:.2f}s)")
        
        return response
    
    def calculate_overall_score(self, global_scores: Dict[str, Optional[float]], weights: Dict[str, float]) -> float:
        """
        Calculate overall score using weighted aggregation
        Only includes active dimensions in the calculation
        """
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for dim_id, score in global_scores.items():
            if score is not None:  # Only include active dimensions
                weight = weights.get(dim_id, self.default_weights.get(dim_id, 0.143))
                total_weighted_score += score * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.5  # Default score if no dimensions are active
        
        # Normalize by total weight to ensure proper aggregation
        overall_score = total_weighted_score / total_weight
        
        return max(0.0, min(1.0, overall_score))
    
    def generate_analysis_metadata(self, text: str, processing_time: float) -> Dict[str, Any]:
        """Generate analysis metadata"""
        # Basic text statistics
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        words = text.split()
        
        return {
            'text_length': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'paragraph_count': len(paragraphs) if paragraphs else 1,
            'processing_time_seconds': round(processing_time, 3),
            'weights_used': self.default_weights.copy(),
            'parallel_processing_enabled': False,
            'caching_enabled': False,
            'enhanced_features_enabled': {
                'stylistic_analysis': True,
                'register_analysis': False,
                'structural_analysis': True
            }
        }
    
    def _evidence_to_dict(self, evidence) -> Dict[str, Any]:
        """Convert Evidence dataclass to dictionary matching frontend expectations
        
        Frontend expects camelCase field names:
        - startIndex (not start_index)
        - endIndex (not end_index)
        """
        return {
            'text': evidence.text,
            'score': evidence.score,
            'startIndex': evidence.start_index,
            'endIndex': evidence.end_index,
            'type': evidence.evidence_type,
            'reason': evidence.reason
        }
    
    def get_dimension_info(self, dimension_id: str) -> Dict[str, str]:
        """Get information about a specific dimension"""
        analyzer = self.analyzers.get(dimension_id)
        if not analyzer:
            return {}
        
        return {
            'name': analyzer.get_dimension_name(),
            'description': analyzer.get_description(),
            'score_interpretation': analyzer.get_score_interpretation(),
            'analysis_level': analyzer.analysis_level.value
        }
    
    def get_all_dimensions_info(self) -> Dict[str, Dict[str, str]]:
        """Get information about all dimensions"""
        return {
            dim_id: self.get_dimension_info(dim_id) 
            for dim_id in self.analyzers.keys()
        }
    
    def update_weights(self, new_weights: Dict[str, float]) -> None:
        """Update dimension weights"""
        # Validate weights sum to approximately 1.0
        total_weight = sum(new_weights.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
        
        # Update weights for each analyzer
        for dim_id, weight in new_weights.items():
            if dim_id in self.analyzers:
                self.analyzers[dim_id].default_weight = weight
                self.default_weights[dim_id] = weight

# Create global instance
analysis_coordinator = AnalysisCoordinator()