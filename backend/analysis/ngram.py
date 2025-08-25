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
    
    def calculate_ngram_frequency_score(self, text: str, n: int, threshold_percent: float = 0.05) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calculate n-gram frequency score with improved thresholding for repetitive text detection
        Args:
            text: Text to analyze
            n: N-gram size
            threshold_percent: Frequency threshold as percentage (lowered for better detection)
        Returns:
            Tuple of (score, suspicious_ngrams_list)
        """
        ngrams = self.extract_ngrams(text, n)
        
        if len(ngrams) < 2:
            return 0.0, []
        
        # Count n-gram frequencies
        ngram_counts = Counter(ngrams)
        total_ngrams = len(ngrams)
        
        # Improved threshold calculation - use minimum of 2 or percentage-based threshold
        threshold = max(2, int(total_ngrams * threshold_percent))
        
        # Find ALL n-grams with their frequencies for analysis
        all_ngrams = []
        for ngram, count in ngram_counts.items():
            frequency_ratio = count / total_ngrams
            
            # Enhanced scoring system - more sensitive to repetition and aggressive for high repetition
            if count >= 3:  # 3 or more occurrences are suspicious
                if frequency_ratio >= 0.15:  # Red: very frequent (15%+) - reduced threshold
                    score = 0.85 + min(0.15, (frequency_ratio - 0.15) * 2.0)  # More aggressive scoring
                elif frequency_ratio >= 0.08:  # Yellow: moderately frequent (8%+) - reduced threshold
                    score = 0.6 + (frequency_ratio - 0.08) * 5.0
                elif frequency_ratio >= 0.04:  # Light yellow: somewhat frequent (4%+) - reduced threshold
                    score = 0.4 + (frequency_ratio - 0.04) * 8.0
                else:
                    score = frequency_ratio * 10.0  # Increased scale for visibility
            elif count == 2:  # Exactly 2 occurrences
                score = frequency_ratio * 5.0  # Increased moderate scoring
            else:
                score = 0.0  # Single occurrence, not suspicious
            
            # Only include if score > 0 for cleaner display
            if score > 0:
                all_ngrams.append({
                    'text': ' '.join(ngram),
                    'frequency': count,
                    'score': min(1.0, score),
                    'frequency_ratio': frequency_ratio
                })
        
        # Sort by score then by frequency
        all_ngrams.sort(key=lambda x: (x['score'], x['frequency']), reverse=True)
        
        # Calculate overall score for this n-gram length
        if all_ngrams:
            # Weight by both frequency and score - emphasize high repetition
            total_weight = 0
            weighted_score_sum = 0
            
            for item in all_ngrams:
                # Give more weight to higher frequency items with enhanced weighting
                weight = (item['frequency'] ** 1.5) * item['frequency_ratio']  # Exponential frequency weight
                weighted_score_sum += item['score'] * weight
                total_weight += weight
            
            if total_weight > 0:
                overall_score = min(1.0, weighted_score_sum / total_weight)
            else:
                overall_score = 0.0
                
            # Enhanced boost for multiple suspicious n-grams with higher multiplier
            repetition_bonus = min(0.4, len(all_ngrams) * 0.08)  # Increased from 0.3 and 0.05
            overall_score = min(1.0, overall_score + repetition_bonus)
        else:
            overall_score = 0.0
        
        return overall_score, all_ngrams[:15]  # Top 15 for better coverage
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Enhanced comprehensive n-gram analysis with improved scoring for repetitive text detection
        Args:
            text: Text to analyze
        Returns:
            Dictionary with analysis results
        """
        # Calculate separate n-gram analysis with optimized thresholds
        # Lower thresholds for better detection of repetitive patterns
        bigram_score, bigram_details = self.calculate_ngram_frequency_score(text, 2, 0.03)  # 3% threshold
        trigram_score, trigram_details = self.calculate_ngram_frequency_score(text, 3, 0.02)  # 2% threshold
        fourgram_score, fourgram_details = self.calculate_ngram_frequency_score(text, 4, 0.01)  # 1% threshold
        
        # Legacy analysis for compatibility
        phrase_repetition = self.calculate_phrase_repetition(text)
        transition_predictability = self.calculate_transition_predictability(text)
        lexical_diversity_score = self.calculate_lexical_diversity(text)
        
        # Enhanced weighting - longer n-grams are much more suspicious
        ngram_weights = {
            'bigram': 0.15,   # 2-grams are common, lower weight
            'trigram': 0.35,  # 3-grams more significant
            'fourgram': 0.5   # 4-grams most suspicious (increased weight)
        }
        
        # Calculate weighted n-gram score
        weighted_ngram_score = (
            bigram_score * ngram_weights['bigram'] +
            trigram_score * ngram_weights['trigram'] +
            fourgram_score * ngram_weights['fourgram']
        ) / sum(ngram_weights.values())
        
        # Enhanced overall score calculation - give more weight to n-gram patterns
        overall_score = (
            weighted_ngram_score * 0.6 +  # Increased from 0.5
            phrase_repetition * 0.1 +     # Reduced from 0.15
            transition_predictability * 0.2 +
            lexical_diversity_score * 0.1  # Reduced from 0.15
        )
        
        return {
            'overall_score': overall_score,
            'ngram_analysis': {
                'bigrams': {
                    'score': bigram_score,
                    'details': bigram_details
                },
                'trigrams': {
                    'score': trigram_score,
                    'details': trigram_details
                },
                'fourgrams': {
                    'score': fourgram_score,
                    'details': fourgram_details
                }
            },
            'components': {
                'weighted_ngram_score': weighted_ngram_score,
                'phrase_repetition': phrase_repetition,
                'transition_predictability': transition_predictability,
                'lexical_diversity': lexical_diversity_score
            },
            'text_stats': sentence_splitter.get_text_statistics(text)
        }
    
    def analyze_sentences(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze n-gram patterns for individual sentences with enhanced detail
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
                'ngram_breakdown': {
                    'bigram_score': analysis['ngram_analysis']['bigrams']['score'],
                    'trigram_score': analysis['ngram_analysis']['trigrams']['score'],
                    'fourgram_score': analysis['ngram_analysis']['fourgrams']['score']
                },
                'words': []  # Individual word analysis not as relevant for n-grams
            })
        
        return sentence_analysis
        
    def detect_formatting_abuse(self, text: str) -> Dict[str, Any]:
        """
        Detect excessive use of formatting elements that may indicate AI text
        Args:
            text: Text to analyze
        Returns:
            Dictionary with formatting abuse scores and details
        """
        import re
        
        # Count various formatting elements
        quote_patterns = re.findall(r'["''][^"'']*["'']', text)
        bold_patterns = re.findall(r'\*\*([^*]+)\*\*|__([^_]+)__', text)
        italic_patterns = re.findall(r'\*([^*]+)\*|_([^_]+)_', text)
        icon_patterns = re.findall(r'[📝🔍💡📊⚡🎯🚀📈💪👍✅❌⭐🌟]', text)
        
        # Count reader-directed questions
        question_patterns = re.findall(r'\b(?:do you|have you|can you|would you|are you|will you|did you)\b[^.]*\?', text, re.IGNORECASE)
        rhetorical_questions = re.findall(r'\?', text)
        
        # Calculate text metrics for normalization
        word_count = len(text.split())
        sentence_count = len(sentence_splitter.split_into_sentences(text))
        
        if word_count == 0:
            return {'overall_score': 0.0, 'details': {}}
        
        # Score each pattern type
        scores = {}
        details = {}
        
        # Quote abuse (normalize by word count)
        quote_ratio = len(quote_patterns) / word_count * 100
        if quote_ratio > 15:  # More than 15% of words in quotes is suspicious
            scores['quote_abuse'] = min(1.0, quote_ratio / 20)
        else:
            scores['quote_abuse'] = 0.0
        details['quotes'] = {'count': len(quote_patterns), 'ratio': quote_ratio}
        
        # Bold/italic abuse
        formatting_count = len(bold_patterns) + len(italic_patterns)
        formatting_ratio = formatting_count / word_count * 100
        if formatting_ratio > 10:  # More than 10% formatted is suspicious
            scores['formatting_abuse'] = min(1.0, formatting_ratio / 15)
        else:
            scores['formatting_abuse'] = 0.0
        details['formatting'] = {'count': formatting_count, 'ratio': formatting_ratio}
        
        # Icon abuse
        icon_ratio = len(icon_patterns) / word_count * 100
        if icon_ratio > 5:  # More than 5% is excessive
            scores['icon_abuse'] = min(1.0, icon_ratio / 8)
        else:
            scores['icon_abuse'] = 0.0
        details['icons'] = {'count': len(icon_patterns), 'ratio': icon_ratio}
        
        # Reader question abuse
        reader_question_ratio = len(question_patterns) / sentence_count if sentence_count > 0 else 0
        if reader_question_ratio > 0.3:  # More than 30% reader-directed questions
            scores['reader_question_abuse'] = min(1.0, reader_question_ratio / 0.5)
        else:
            scores['reader_question_abuse'] = 0.0
        details['reader_questions'] = {'count': len(question_patterns), 'ratio': reader_question_ratio}
        
        # Overall formatting abuse score
        overall_score = sum(scores.values()) / len(scores) if scores else 0.0
        
        return {
            'overall_score': overall_score,
            'component_scores': scores,
            'details': details
        }
    
    def detect_paragraph_patterns(self, text: str) -> Dict[str, Any]:
        """
        Analyze paragraph structure including line-break detection
        Args:
            text: Text to analyze
        Returns:
            Dictionary with paragraph pattern analysis
        """
        import re
        
        # Split by different paragraph indicators
        empty_line_paragraphs = text.split('\n\n')
        line_break_paragraphs = text.split('\n')
        
        # Remove empty entries
        empty_line_paragraphs = [p.strip() for p in empty_line_paragraphs if p.strip()]
        line_break_paragraphs = [p.strip() for p in line_break_paragraphs if p.strip()]
        
        # Analyze paragraph characteristics
        if not line_break_paragraphs:
            return {'overall_score': 0.0, 'details': {}}
        
        # Calculate paragraph length statistics
        paragraph_lengths = [len(p.split()) for p in line_break_paragraphs]
        avg_length = sum(paragraph_lengths) / len(paragraph_lengths)
        length_variance = np.var(paragraph_lengths) if len(paragraph_lengths) > 1 else 0
        
        # Detect patterns suspicious of AI
        scores = {}
        
        # Very uniform paragraph lengths (AI tends to generate similar-length paragraphs)
        if length_variance < 10 and len(paragraph_lengths) > 3:
            scores['uniform_length'] = 0.7
        else:
            scores['uniform_length'] = 0.0
        
        # Excessive short paragraphs (single sentences)
        short_paragraphs = sum(1 for length in paragraph_lengths if length < 15)
        short_ratio = short_paragraphs / len(paragraph_lengths)
        if short_ratio > 0.7:  # More than 70% short paragraphs
            scores['excessive_short'] = short_ratio
        else:
            scores['excessive_short'] = 0.0
        
        # Pattern regularity in paragraph starts
        paragraph_starts = [p.split()[0].lower() if p.split() else '' for p in line_break_paragraphs]
        start_counter = Counter(paragraph_starts)
        most_common_start_ratio = start_counter.most_common(1)[0][1] / len(paragraph_starts) if paragraph_starts else 0
        if most_common_start_ratio > 0.5:  # More than 50% start with same word
            scores['repetitive_starts'] = most_common_start_ratio
        else:
            scores['repetitive_starts'] = 0.0
        
        overall_score = sum(scores.values()) / len(scores) if scores else 0.0
        
        return {
            'overall_score': min(1.0, overall_score),
            'component_scores': scores,
            'details': {
                'paragraph_count': len(line_break_paragraphs),
                'avg_length': avg_length,
                'length_variance': length_variance,
                'short_paragraph_ratio': short_ratio
            }
        }
    
    def get_repetitive_patterns(self, text: str) -> Dict[str, Any]:
        """
        Enhanced repetitive patterns identification with frequency scoring
        Args:
            text: Text to analyze
        Returns:
            Dictionary with repetitive patterns found with scores
        """
        # Get enhanced n-gram analysis
        analysis = self.analyze_text(text)
        ngram_analysis = analysis.get('ngram_analysis', {})
        
        # Extract patterns with scores
        patterns = {
            'bigrams': ngram_analysis.get('bigrams', {}).get('details', []),
            'trigrams': ngram_analysis.get('trigrams', {}).get('details', []),
            'fourgrams': ngram_analysis.get('fourgrams', {}).get('details', [])
        }
        
        # Legacy phrase analysis for compatibility
        sentences = sentence_splitter.split_into_sentences(text)
        phrases = []
        
        for sentence in sentences:
            words = sentence_splitter.tokenize_words(sentence)
            for i in range(len(words) - 2):
                phrase = ' '.join(words[i:i + 3])
                phrases.append(phrase)
        
        phrase_counts = Counter(phrases)
        
        return {
            'ngram_patterns': patterns,
            'repeated_phrases': [
                {'pattern': phrase, 'count': count}
                for phrase, count in phrase_counts.most_common(10) if count > 1
            ]
        }
    
    def analyze_text_with_patterns(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive analysis including new suspicious patterns
        Args:
            text: Text to analyze
        Returns:
            Enhanced analysis results with pattern detection
        """
        # Get base n-gram analysis
        base_analysis = self.analyze_text(text)
        
        # Add new pattern detection
        formatting_analysis = self.detect_formatting_abuse(text)
        paragraph_analysis = self.detect_paragraph_patterns(text)
        
        # Combine scores with appropriate weights
        pattern_score = (
            formatting_analysis['overall_score'] * 0.3 +
            paragraph_analysis['overall_score'] * 0.2
        )
        
        # Update overall score to include pattern analysis
        enhanced_overall_score = (
            base_analysis['overall_score'] * 0.7 +
            pattern_score * 0.3
        )
        
        # Merge results
        enhanced_analysis = base_analysis.copy()
        enhanced_analysis['overall_score'] = enhanced_overall_score
        enhanced_analysis['pattern_analysis'] = {
            'formatting': formatting_analysis,
            'paragraphs': paragraph_analysis
        }
        
        return enhanced_analysis

# Global n-gram analyzer instance
ngram_analyzer = NgramAnalyzer()