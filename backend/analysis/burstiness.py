"""
Burstiness Analysis Module for Origo
Analyzes variation in sentence length and structure to detect AI patterns
AI-generated text often shows more uniform patterns (lower burstiness)
"""

import logging
import numpy as np
from typing import List, Dict, Any
from utils.sentence_splitter import sentence_splitter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BurstinessAnalyzer:
    """
    Analyzes burstiness: variation in sentence length and structural patterns
    Low burstiness (uniform patterns) suggests AI generation
    """
    
    def __init__(self):
        pass
    
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
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive burstiness analysis
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
        
        # Combined burstiness score (weighted average)
        overall_burstiness = (
            length_variation * 0.3 +
            complexity_variation * 0.3 +
            start_variation * 0.2 +
            punctuation_variation * 0.2
        )
        
        # Invert for AI detection (lower burstiness = higher AI probability)
        ai_probability = 1.0 - overall_burstiness
        
        return {
            'overall_score': ai_probability,
            'components': {
                'length_variation': length_variation,
                'complexity_variation': complexity_variation,
                'start_variation': start_variation,
                'punctuation_variation': punctuation_variation
            },
            'sentence_count': len(sentences),
            'analysis_details': {
                'avg_sentence_length': np.mean([len(s.split()) for s in sentences]) if sentences else 0,
                'sentence_length_range': np.ptp([len(s.split()) for s in sentences]) if sentences else 0
            }
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