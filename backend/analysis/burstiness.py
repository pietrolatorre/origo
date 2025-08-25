"""
Burstiness Analysis Module for Origo
Analyzes variation in sentence length and structure to detect AI patterns
AI-generated text often shows more uniform patterns (lower burstiness)
"""

import logging
import numpy as np
import json
import os
from typing import List, Dict, Any
from utils.sentence_splitter import sentence_splitter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BurstinessAnalyzer:
    """
    Analyzes burstiness: variation in sentence length and structural patterns
    Low burstiness (uniform patterns) suggests AI generation
    Enhanced with structural consistency analysis
    """
    
    def __init__(self):
        # Load configuration files
        self.config_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.structural_patterns = self._load_config('burstiness/structural_patterns.json')
        self.weights_config = self._load_config('weights_config.json')
    
    def _load_config(self, filename: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            config_path = os.path.join(self.config_dir, filename)
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config {filename}: {e}")
            return {}
    
    def calculate_sentence_length_variation(self, sentences: List[str]) -> float:
        """
        Calculate variation in sentence lengths
        Args:
            sentences: List of sentences
        Returns:
            Burstiness score based on length variation (0-1, higher = more human-like)
        """
        if len(sentences) < 2:
            return 0.5
        
        # Calculate sentence lengths
        lengths = [len(sentence.split()) for sentence in sentences]
        
        if len(set(lengths)) == 1:  # All sentences same length
            return 0.0  # Very uniform = AI-like
        
        # Calculate coefficient of variation (std/mean)
        mean_length = np.mean(lengths)
        std_length = np.std(lengths)
        
        if mean_length == 0:
            return 0.0
        
        coefficient_of_variation = std_length / mean_length
        
        # Normalize to 0-1 scale (higher = more human-like)
        # Typical human writing has CoV between 0.3-0.8
        normalized_score = min(1.0, coefficient_of_variation / 0.8)
        
        return normalized_score
    
    def calculate_syntactic_complexity_variation(self, sentences: List[str]) -> float:
        """
        Analyze variation in syntactic complexity
        Args:
            sentences: List of sentences
        Returns:
            Complexity variation score (0-1, higher = more human-like)
        """
        if len(sentences) < 2:
            return 0.5
        
        complexity_scores = []
        
        for sentence in sentences:
            # Simple complexity metrics
            words = sentence.split()
            
            # Count complexity indicators
            complex_words = sum(1 for word in words if len(word) > 6)
            punctuation_count = sum(1 for char in sentence if char in '.,;:!?')
            subordinate_conjunctions = sum(1 for word in words if word.lower() in 
                                         ['although', 'because', 'since', 'while', 'whereas', 'if', 'unless'])
            
            # Calculate complexity score
            if len(words) > 0:
                complexity = (
                    (complex_words / len(words)) * 0.4 +
                    (punctuation_count / len(words)) * 0.3 +
                    (subordinate_conjunctions / len(words)) * 0.3
                )
            else:
                complexity = 0.0
            
            complexity_scores.append(complexity)
        
        # Calculate variation in complexity
        if len(complexity_scores) > 1:
            mean_complexity = np.mean(complexity_scores)
            std_complexity = np.std(complexity_scores)
            
            if mean_complexity > 0:
                variation = std_complexity / mean_complexity
                return min(1.0, variation)
        
        return 0.5
    
    def calculate_sentence_start_variation(self, sentences: List[str]) -> float:
        """
        Analyze variation in sentence starting patterns
        Args:
            sentences: List of sentences
        Returns:
            Start pattern variation score (0-1, higher = more human-like)
        """
        if len(sentences) < 3:
            return 0.5
        
        # Extract first words (normalized)
        first_words = []
        for sentence in sentences:
            words = sentence.strip().split()
            if words:
                first_word = words[0].lower().rstrip('.,!?;:')
                first_words.append(first_word)
        
        if len(first_words) < 2:
            return 0.5
        
        # Calculate repetition patterns
        unique_starts = len(set(first_words))
        total_starts = len(first_words)
        
        # Higher ratio = more variety = more human-like
        variety_ratio = unique_starts / total_starts
        
        return variety_ratio
    
    def calculate_punctuation_patterns(self, text: str) -> float:
        """
        Analyze punctuation usage patterns
        Args:
            text: Full text to analyze
        Returns:
            Punctuation pattern score (0-1, higher = more human-like)
        """
        sentences = sentence_splitter.split_into_sentences(text)
        
        if len(sentences) < 2:
            return 0.5
        
        # Count different punctuation types per sentence
        punctuation_patterns = []
        
        for sentence in sentences:
            pattern = {
                'periods': sentence.count('.'),
                'commas': sentence.count(','),
                'semicolons': sentence.count(';'),
                'colons': sentence.count(':'),
                'exclamations': sentence.count('!'),
                'questions': sentence.count('?'),
                'dashes': sentence.count('-') + sentence.count('—'),
                'quotes': sentence.count('"') + sentence.count("'")
            }
            
            # Calculate pattern diversity
            total_punct = sum(pattern.values())
            unique_types = sum(1 for count in pattern.values() if count > 0)
            
            if total_punct > 0:
                pattern_score = unique_types / len(pattern)
            else:
                pattern_score = 0.0
            
            punctuation_patterns.append(pattern_score)
        
        # Calculate variation in punctuation patterns
        if len(punctuation_patterns) > 1:
            return min(1.0, np.std(punctuation_patterns) * 2)
        
        return 0.5
    
    def analyze_structural_consistency(self, text: str) -> Dict[str, Any]:
        """
        Analyze structural consistency patterns that indicate AI generation
        Args:
            text: Input text to analyze
        Returns:
            Dictionary with structural consistency analysis
        """
        if not self.structural_patterns:
            return {'overall_score': 0.5, 'details': {}}
        
        paragraphs = sentence_splitter.split_into_paragraphs(text)
        sentences = sentence_splitter.split_into_sentences(text)
        words = sentence_splitter.tokenize_words(text)
        
        scores = {}
        
        # Analyze paragraph length uniformity
        paragraph_score = self._analyze_paragraph_uniformity(paragraphs)
        scores['paragraph_uniformity'] = paragraph_score
        
        # Analyze sentence symmetry patterns
        sentence_score = self._analyze_sentence_symmetry(sentences)
        scores['sentence_symmetry'] = sentence_score
        
        # Analyze section balance
        section_score = self._analyze_section_balance(paragraphs)
        scores['section_balance'] = section_score
        
        # Analyze mechanical patterns
        mechanical_score = self._analyze_mechanical_patterns(text, words)
        scores['mechanical_patterns'] = mechanical_score
        
        # Analyze rhythmic patterns
        rhythmic_score = self._analyze_rhythmic_patterns(sentences)
        scores['rhythmic_patterns'] = rhythmic_score
        
        # Analyze formatting consistency
        formatting_score = self._analyze_formatting_consistency(text)
        scores['formatting_consistency'] = formatting_score
        
        # Calculate overall structural consistency score with safe numeric handling
        score_values = []
        for key, value in scores.items():
            try:
                # Ensure all values are converted to float scalars
                if isinstance(value, (int, float)):
                    score_values.append(float(value))
                elif isinstance(value, (list, tuple)) and len(value) > 0:
                    # If it's a list/tuple, take the first numeric value
                    score_values.append(float(value[0]))
                else:
                    # Fallback to neutral score
                    score_values.append(0.5)
            except (ValueError, TypeError, IndexError):
                # If conversion fails, use neutral score
                score_values.append(0.5)
        
        # Calculate overall score safely
        if score_values:
            overall_score = sum(score_values) / len(score_values)  # Use standard mean instead of np.mean
        else:
            overall_score = 0.5
        
        return {
            'overall_score': min(1.0, max(0.0, overall_score)),
            'details': scores
        }
    
    def _analyze_paragraph_uniformity(self, paragraphs: List[str]) -> float:
        """Analyze paragraph length uniformity"""
        if len(paragraphs) < 3:
            return 0.5
        
        uniformity_config = self.structural_patterns.get('uniformity_detectors', {}).get('paragraph_length', {})
        
        # Calculate paragraph lengths in words
        paragraph_lengths = [len(para.split()) for para in paragraphs]
        
        if len(set(paragraph_lengths)) == 1:
            return 1.0  # Perfect uniformity = AI-like
        
        mean_length = np.mean(paragraph_lengths)
        std_length = np.std(paragraph_lengths)
        
        if mean_length == 0:
            return 0.5
        
        coefficient_of_variation = std_length / mean_length
        
        # Check against thresholds
        variance_threshold = uniformity_config.get('variance_threshold', 0.1)
        suspicious_consistency = uniformity_config.get('suspicious_consistency', 0.05)
        
        if coefficient_of_variation < suspicious_consistency:
            return 1.0  # Very suspicious uniformity
        elif coefficient_of_variation < variance_threshold:
            return 0.7  # Moderate uniformity
        else:
            return 0.2  # Natural variation
    
    def _analyze_sentence_symmetry(self, sentences: List[str]) -> float:
        """Analyze sentence structure symmetry"""
        if len(sentences) < 5:
            return 0.5
        
        symmetry_config = self.structural_patterns.get('uniformity_detectors', {}).get('sentence_symmetry', {})
        repetition_threshold = symmetry_config.get('repetition_threshold', 0.3)
        
        # Analyze sentence starting patterns
        first_words = []
        for sentence in sentences:
            words = sentence.strip().split()
            if words:
                first_word = words[0].lower().rstrip('.,!?;:')
                first_words.append(first_word)
        
        # Calculate repetition ratio
        if first_words:
            unique_starts = len(set(first_words))
            total_starts = len(first_words)
            repetition_ratio = 1.0 - (unique_starts / total_starts)
            
            if repetition_ratio > repetition_threshold:
                return repetition_ratio  # High repetition = AI-like
        
        return 0.5
    
    def _analyze_section_balance(self, paragraphs: List[str]) -> float:
        """Analyze artificial section balance"""
        if len(paragraphs) < 3:
            return 0.5
        
        section_config = self.structural_patterns.get('uniformity_detectors', {}).get('section_balance', {})
        expected_ratio = section_config.get('intro_body_conclusion_ratio', [0.15, 0.70, 0.15])
        tolerance = section_config.get('tolerance', 0.05)
        
        # Calculate word counts for each paragraph
        word_counts = [len(para.split()) for para in paragraphs]
        total_words = sum(word_counts)
        
        if total_words == 0 or len(paragraphs) < 3:
            return 0.5
        
        # Assume first paragraph is intro, last is conclusion, middle are body
        intro_ratio = word_counts[0] / total_words
        conclusion_ratio = word_counts[-1] / total_words
        body_ratio = sum(word_counts[1:-1]) / total_words if len(paragraphs) > 2 else 0
        
        actual_ratios = [intro_ratio, body_ratio, conclusion_ratio]
        
        # Calculate deviation from expected ratios
        deviations = [abs(actual - expected) for actual, expected in zip(actual_ratios, expected_ratio)]
        max_deviation = max(deviations)
        
        if max_deviation < tolerance:
            return 0.8  # Too perfectly balanced = suspicious
        else:
            return max_deviation  # Natural deviation
    
    def _analyze_mechanical_patterns(self, text: str, words: List[str]) -> float:
        """Analyze mechanical transition and formatting patterns"""
        mechanical_config = self.structural_patterns.get('mechanical_patterns', {})
        
        text_lower = text.lower()
        word_count = len(words)
        
        if word_count == 0:
            return 0.5
        
        # Check transition phrases
        transition_config = mechanical_config.get('transition_phrases', {})
        transition_patterns = transition_config.get('patterns', [])
        transition_count = sum(1 for pattern in transition_patterns if pattern.lower() in text_lower)
        
        overuse_threshold = transition_config.get('overuse_threshold', 0.15)
        transition_density = transition_count / max(1, len(sentence_splitter.split_into_sentences(text)))
        
        if transition_density > overuse_threshold:
            return min(1.0, transition_density / overuse_threshold)
        else:
            return 0.0
    
    def _analyze_rhythmic_patterns(self, sentences: List[str]) -> float:
        """Analyze rhythmic consistency in sentence patterns"""
        if len(sentences) < 5:
            return 0.5
        
        # Simplified rhythmic analysis through sentence length patterns
        lengths = [len(sentence.split()) for sentence in sentences]
        
        if lengths:
            mean_length = np.mean(lengths)
            std_length = np.std(lengths)
            
            if mean_length > 0:
                length_variance = std_length / mean_length
                
                # Low variance indicates mechanical rhythm
                if length_variance < 0.15:
                    return 0.8  # Too consistent = AI-like
                else:
                    return length_variance
        
        return 0.5
    
    def _analyze_formatting_consistency(self, text: str) -> float:
        """Analyze formatting consistency patterns"""
        # Check comma spacing consistency
        import re
        comma_patterns = re.findall(r',\s*', text)
        if comma_patterns:
            consistent_spacing = sum(1 for pattern in comma_patterns if pattern == ', ')
            consistency_ratio = consistent_spacing / len(comma_patterns)
            
            if consistency_ratio > 0.95:
                return 0.7  # Too perfect = suspicious
        
        return 0.3  # Normal formatting variation
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive burstiness analysis including structural consistency
        Args:
            text: Text to analyze
        Returns:
            Dictionary with burstiness analysis results
        """
        sentences = sentence_splitter.split_into_sentences(text)
        
        # Calculate different burstiness metrics
        length_variation = self.calculate_sentence_length_variation(sentences)
        complexity_variation = self.calculate_syntactic_complexity_variation(sentences)
        start_variation = self.calculate_sentence_start_variation(sentences)
        punctuation_variation = self.calculate_punctuation_patterns(text)
        
        # Calculate structural consistency analysis
        structural_analysis = self.analyze_structural_consistency(text)
        
        # Get component weights from configuration
        burstiness_weights = self.weights_config.get('burstiness_components', {
            'base_burstiness': 0.6,
            'structural_consistency': 0.4
        })
        
        # Combined base burstiness score (weighted average)
        base_burstiness = (
            length_variation * 0.3 +
            complexity_variation * 0.3 +
            start_variation * 0.2 +
            punctuation_variation * 0.2
        )
        
        # Invert for AI detection (lower burstiness = higher AI probability)
        base_ai_probability = 1.0 - base_burstiness
        
        # Calculate overall score with structural consistency
        overall_score = (
            base_ai_probability * burstiness_weights['base_burstiness'] +
            structural_analysis['overall_score'] * burstiness_weights['structural_consistency']
        )
        
        overall_score = min(1.0, max(0.0, overall_score))
        
        return {
            'overall_score': round(overall_score, 3),
            'base_burstiness': round(base_ai_probability, 3),
            'structural_consistency': structural_analysis,
            'components': {
                'length_variation': round(length_variation, 3),
                'complexity_variation': round(complexity_variation, 3),
                'start_variation': round(start_variation, 3),
                'punctuation_variation': round(punctuation_variation, 3)
            },
            'sentence_count': len(sentences),
            'analysis_details': {
                'avg_sentence_length': round(np.mean([len(s.split()) for s in sentences]), 2) if sentences else 0,
                'sentence_length_range': int(np.ptp([len(s.split()) for s in sentences])) if sentences else 0
            } if sentences else {
                'avg_sentence_length': 0,
                'sentence_length_range': 0
            },
            'component_weights': burstiness_weights
        }
    
    def analyze_sentences(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze burstiness for individual sentences in context
        Args:
            sentences: List of sentences
        Returns:
            List of sentence analyses
        """
        sentence_analysis = []
        
        for i, sentence in enumerate(sentences):
            # Analyze sentence in context of surrounding sentences
            context_start = max(0, i - 2)
            context_end = min(len(sentences), i + 3)
            context_sentences = sentences[context_start:context_end]
            
            # Calculate local burstiness
            context_analysis = self.analyze_text(' '.join(context_sentences))
            
            sentence_analysis.append({
                'text': sentence,
                'score': context_analysis['overall_score'],
                'words': []  # Individual word analysis not applicable for burstiness
            })
        
        return sentence_analysis

# Global burstiness analyzer instance
burstiness_analyzer = BurstinessAnalyzer()