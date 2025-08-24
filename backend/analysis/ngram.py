"""
N-gram Similarity Analysis Module for Origo
Analyzes repetitive patterns and n-gram similarities to detect AI-generated text
AI text often shows repetitive patterns and predictable n-gram sequences
"""

import logging
import numpy as np
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
from utils.sentence_splitter import sentence_splitter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NgramAnalyzer:
    """
    Analyzes n-gram patterns and repetitions to detect AI-generated text
    High repetition and predictable patterns suggest AI generation
    """
    
    def __init__(self):
        pass
    
    def extract_ngrams(self, text: str, n: int) -> List[Tuple[str, ...]]:
        """
        Extract n-grams from text
        Args:
            text: Input text
            n: N-gram size (2 for bigrams, 3 for trigrams, etc.)
        Returns:
            List of n-gram tuples
        """
        words = sentence_splitter.tokenize_words(text)
        
        if len(words) < n:
            return []
        
        ngrams = []
        for i in range(len(words) - n + 1):
            ngrams.append(tuple(words[i:i + n]))
        
        return ngrams
    
    def calculate_ngram_repetition(self, text: str, n: int) -> float:
        """
        Calculate repetition rate for n-grams
        Args:
            text: Text to analyze
            n: N-gram size
        Returns:
            Repetition score (0-1, higher = more repetitive/AI-like)
        """
        ngrams = self.extract_ngrams(text, n)
        
        if len(ngrams) < 2:
            return 0.0
        
        # Count n-gram frequencies
        ngram_counts = Counter(ngrams)
        
        # Calculate repetition metrics
        total_ngrams = len(ngrams)
        unique_ngrams = len(ngram_counts)
        
        if total_ngrams == 0:
            return 0.0
        
        # Repetition ratio (lower unique/total = higher repetition)
        repetition_ratio = 1.0 - (unique_ngrams / total_ngrams)
        
        # Weight by frequency of most common n-grams
        most_common = ngram_counts.most_common(5)
        frequency_weight = sum(count for _, count in most_common) / total_ngrams
        
        # Combined repetition score
        repetition_score = (repetition_ratio * 0.7) + (frequency_weight * 0.3)
        
        return min(1.0, repetition_score)
    
    def calculate_phrase_repetition(self, text: str) -> float:
        """
        Detect repetitive phrases and expressions
        Args:
            text: Text to analyze
        Returns:
            Phrase repetition score (0-1, higher = more AI-like)
        """
        sentences = sentence_splitter.split_into_sentences(text)
        
        if len(sentences) < 2:
            return 0.0
        
        # Extract phrases (3-5 word sequences)
        all_phrases = []
        
        for sentence in sentences:
            words = sentence_splitter.tokenize_words(sentence)
            
            # Extract phrases of different lengths
            for phrase_len in range(3, 6):
                if len(words) >= phrase_len:
                    for i in range(len(words) - phrase_len + 1):
                        phrase = ' '.join(words[i:i + phrase_len])
                        all_phrases.append(phrase)
        
        if len(all_phrases) < 2:
            return 0.0
        
        # Count phrase frequencies
        phrase_counts = Counter(all_phrases)
        
        # Calculate repetition metrics
        total_phrases = len(all_phrases)
        repeated_phrases = sum(count for count in phrase_counts.values() if count > 1)
        
        repetition_rate = repeated_phrases / total_phrases if total_phrases > 0 else 0.0
        
        return min(1.0, repetition_rate * 2)  # Scale up for visibility
    
    def calculate_transition_predictability(self, text: str) -> float:
        """
        Analyze predictability of word transitions
        Args:
            text: Text to analyze
        Returns:
            Predictability score (0-1, higher = more predictable/AI-like)
        """
        words = sentence_splitter.tokenize_words(text)
        
        if len(words) < 3:
            return 0.0
        
        # Build transition dictionary (word -> next words)
        transitions = defaultdict(list)
        
        for i in range(len(words) - 1):
            current_word = words[i]
            next_word = words[i + 1]
            transitions[current_word].append(next_word)
        
        # Calculate predictability
        predictability_scores = []
        
        for word, next_words in transitions.items():
            if len(next_words) > 1:
                # Count frequency of each next word
                next_word_counts = Counter(next_words)
                total_transitions = len(next_words)
                
                # Calculate entropy (lower entropy = more predictable)
                probabilities = [count / total_transitions for count in next_word_counts.values()]
                entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
                
                # Convert to predictability (lower entropy = higher predictability)
                max_entropy = np.log2(len(next_word_counts))
                if max_entropy > 0:
                    predictability = 1.0 - (entropy / max_entropy)
                else:
                    predictability = 1.0
                
                predictability_scores.append(predictability)
        
        if predictability_scores:
            return np.mean(predictability_scores)
        
        return 0.5
    
    def calculate_lexical_diversity(self, text: str) -> float:
        """
        Calculate lexical diversity (Type-Token Ratio variations)
        Args:
            text: Text to analyze
        Returns:
            Diversity score (0-1, lower = less diverse/more AI-like)
        """
        words = sentence_splitter.tokenize_words(text)
        
        if len(words) < 5:
            return 0.5
        
        # Basic Type-Token Ratio
        unique_words = len(set(words))
        total_words = len(words)
        basic_ttr = unique_words / total_words
        
        # Moving Average Type-Token Ratio (MATTR)
        window_size = min(50, total_words)
        mattr_scores = []
        
        for i in range(len(words) - window_size + 1):
            window_words = words[i:i + window_size]
            window_unique = len(set(window_words))
            window_ttr = window_unique / window_size
            mattr_scores.append(window_ttr)
        
        mattr = np.mean(mattr_scores) if mattr_scores else basic_ttr
        
        # Combine metrics (invert for AI detection)
        diversity_score = (basic_ttr + mattr) / 2
        ai_score = 1.0 - diversity_score
        
        return ai_score
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive n-gram and repetition analysis
        Args:
            text: Text to analyze
        Returns:
            Dictionary with analysis results
        """
        # Calculate different n-gram metrics
        bigram_repetition = self.calculate_ngram_repetition(text, 2)
        trigram_repetition = self.calculate_ngram_repetition(text, 3)
        phrase_repetition = self.calculate_phrase_repetition(text)
        transition_predictability = self.calculate_transition_predictability(text)
        lexical_diversity_score = self.calculate_lexical_diversity(text)
        
        # Combined score (weighted average)
        overall_score = (
            bigram_repetition * 0.2 +
            trigram_repetition * 0.2 +
            phrase_repetition * 0.2 +
            transition_predictability * 0.2 +
            lexical_diversity_score * 0.2
        )
        
        return {
            'overall_score': overall_score,
            'components': {
                'bigram_repetition': bigram_repetition,
                'trigram_repetition': trigram_repetition,
                'phrase_repetition': phrase_repetition,
                'transition_predictability': transition_predictability,
                'lexical_diversity': lexical_diversity_score
            },
            'text_stats': sentence_splitter.get_text_statistics(text)
        }
    
    def analyze_sentences(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze n-gram patterns for individual sentences
        Args:
            sentences: List of sentences
        Returns:
            List of sentence analyses
        """
        sentence_analysis = []
        
        for sentence in sentences:
            # Analyze sentence-level patterns
            analysis = self.analyze_text(sentence)
            
            sentence_analysis.append({
                'text': sentence,
                'score': analysis['overall_score'],
                'words': []  # Individual word analysis not as relevant for n-grams
            })
        
        return sentence_analysis
    
    def get_repetitive_patterns(self, text: str) -> Dict[str, Any]:
        """
        Identify specific repetitive patterns in text
        Args:
            text: Text to analyze
        Returns:
            Dictionary with repetitive patterns found
        """
        # Find most common n-grams
        bigrams = self.extract_ngrams(text, 2)
        trigrams = self.extract_ngrams(text, 3)
        
        bigram_counts = Counter(bigrams)
        trigram_counts = Counter(trigrams)
        
        # Find repeated phrases
        sentences = sentence_splitter.split_into_sentences(text)
        phrases = []
        
        for sentence in sentences:
            words = sentence_splitter.tokenize_words(sentence)
            for i in range(len(words) - 2):
                phrase = ' '.join(words[i:i + 3])
                phrases.append(phrase)
        
        phrase_counts = Counter(phrases)
        
        return {
            'common_bigrams': [
                {'pattern': ' '.join(bigram), 'count': count}
                for bigram, count in bigram_counts.most_common(10) if count > 1
            ],
            'common_trigrams': [
                {'pattern': ' '.join(trigram), 'count': count}
                for trigram, count in trigram_counts.most_common(10) if count > 1
            ],
            'repeated_phrases': [
                {'pattern': phrase, 'count': count}
                for phrase, count in phrase_counts.most_common(10) if count > 1
            ]
        }

# Global n-gram analyzer instance
ngram_analyzer = NgramAnalyzer()