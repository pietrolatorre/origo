"""
Scoring Fusion Module for Origo
Combines multiple analysis heuristics into a single comprehensive score
Weighs different analysis components based on their reliability and importance
"""

import logging
from typing import Dict, List, Any
from .perplexity import perplexity_analyzer
from .burstiness import burstiness_analyzer
from .ngram import ngram_analyzer
from .semantic import semantic_analyzer
from utils.sentence_splitter import sentence_splitter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScoreFusion:
    """
    Combines multiple analysis scores into a comprehensive AI detection result
    """
    
    def __init__(self):
        # Weights for different analysis components
        self.weights = {
            'perplexity': 0.4,       # High weight - most reliable indicator
            'burstiness': 0.2,       # Medium weight - structural patterns
            'ngram_similarity': 0.2,  # Medium weight - repetition patterns
            'semantic_coherence': 0.2 # Medium weight - semantic patterns
        }
    
    def validate_weights(self):
        """Ensure weights sum to 1.0"""
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.001:
            logger.warning(f"Weights sum to {total_weight}, normalizing...")
            for key in self.weights:
                self.weights[key] /= total_weight
    
    def analyze_text_comprehensive(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis using all available methods
        Args:
            text: Input text to analyze
        Returns:
            Complete analysis results with combined scores
        """
        if not text or len(text.strip()) < 10:
            return self._create_empty_result()
        
        logger.info("Starting comprehensive text analysis...")
        
        try:
            # Perform individual analyses
            logger.info("Calculating perplexity...")
            perplexity_result = self._safe_analysis(
                lambda: perplexity_analyzer.calculate_perplexity(text),
                "perplexity"
            )
            
            logger.info("Analyzing burstiness...")
            burstiness_result = self._safe_analysis(
                lambda: burstiness_analyzer.analyze_text(text),
                "burstiness"
            )
            
            logger.info("Analyzing n-gram patterns...")
            ngram_result = self._safe_analysis(
                lambda: ngram_analyzer.analyze_text(text),
                "ngram"
            )
            
            logger.info("Analyzing semantic patterns...")
            semantic_result = self._safe_analysis(
                lambda: semantic_analyzer.analyze_text(text),
                "semantic"
            )
            
            # Extract scores from results
            scores = {
                'perplexity': perplexity_result if isinstance(perplexity_result, (int, float)) else perplexity_result.get('overall_score', 0.5),
                'burstiness': burstiness_result.get('overall_score', 0.5) if isinstance(burstiness_result, dict) else 0.5,
                'ngram_similarity': ngram_result.get('overall_score', 0.5) if isinstance(ngram_result, dict) else 0.5,
                'semantic_coherence': semantic_result.get('overall_score', 0.5) if isinstance(semantic_result, dict) else 0.5
            }
            
            # Calculate weighted overall score
            self.validate_weights()
            overall_score = sum(scores[key] * self.weights[key] for key in scores)
            overall_score = max(0.0, min(1.0, overall_score))  # Clamp to [0,1]
            
            # Analyze paragraph and sentence structure
            paragraphs_analysis = self._analyze_paragraphs(text)
            word_analysis = self._analyze_words(text)
            
            result = {
                'overall_score': round(overall_score, 3),
                'global_scores': {
                    'perplexity': round(scores['perplexity'], 3),
                    'burstiness': round(scores['burstiness'], 3),
                    'semantic_coherence': round(scores['semantic_coherence'], 3),
                    'ngram_similarity': round(scores['ngram_similarity'], 3)
                },
                'paragraphs': paragraphs_analysis,
                'word_analysis': word_analysis,
                'analysis_metadata': {
                    'text_length': len(text),
                    'word_count': len(sentence_splitter.tokenize_words(text)),
                    'sentence_count': len(sentence_splitter.split_into_sentences(text)),
                    'paragraph_count': len(sentence_splitter.split_into_paragraphs(text)),
                    'weights_used': self.weights.copy()
                }
            }
            
            logger.info(f"Analysis complete. Overall score: {overall_score:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return self._create_error_result(str(e))
    
    def _safe_analysis(self, analysis_func, analysis_name: str):
        """
        Safely execute analysis function with error handling
        Args:
            analysis_func: Function to execute
            analysis_name: Name of analysis for logging
        Returns:
            Analysis result or default value on error
        """
        try:
            return analysis_func()
        except Exception as e:
            logger.error(f"Error in {analysis_name} analysis: {e}")
            return 0.5 if analysis_name == 'perplexity' else {'overall_score': 0.5}
    
    def _analyze_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """
        Analyze individual paragraphs with sentence breakdown
        Args:
            text: Input text
        Returns:
            List of paragraph analyses
        """
        paragraphs = sentence_splitter.split_into_paragraphs(text)
        paragraph_analyses = []
        
        for paragraph in paragraphs:
            try:
                # Get paragraph-level score from each analyzer
                para_perplexity = perplexity_analyzer.calculate_perplexity(paragraph)
                para_burstiness = burstiness_analyzer.analyze_text(paragraph).get('overall_score', 0.5)
                para_ngram = ngram_analyzer.analyze_text(paragraph).get('overall_score', 0.5)
                para_semantic = semantic_analyzer.analyze_text(paragraph).get('overall_score', 0.5)
                
                # Calculate paragraph score
                paragraph_score = (
                    para_perplexity * self.weights['perplexity'] +
                    para_burstiness * self.weights['burstiness'] +
                    para_ngram * self.weights['ngram_similarity'] +
                    para_semantic * self.weights['semantic_coherence']
                )
                
                # Analyze sentences within paragraph
                sentences = sentence_splitter.split_into_sentences(paragraph)
                sentence_analyses = self._analyze_sentences(sentences)
                
                paragraph_analyses.append({
                    'text': paragraph,
                    'score': round(paragraph_score, 3),
                    'sentences': sentence_analyses
                })
                
            except Exception as e:
                logger.error(f"Error analyzing paragraph: {e}")
                paragraph_analyses.append({
                    'text': paragraph,
                    'score': 0.5,
                    'sentences': []
                })
        
        return paragraph_analyses
    
    def _analyze_sentences(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze individual sentences with word breakdown
        Args:
            sentences: List of sentences
        Returns:
            List of sentence analyses
        """
        sentence_analyses = []
        
        for sentence in sentences:
            try:
                # Get sentence-level scores
                sent_perplexity = perplexity_analyzer.calculate_perplexity(sentence)
                
                # Calculate sentence score (simplified for performance)
                sentence_score = sent_perplexity  # Use perplexity as primary indicator for sentences
                
                # Analyze significant words in sentence
                words = sentence_splitter.tokenize_words(sentence)
                word_analyses = []
                
                # Only analyze words that might be significant
                significant_words = [w for w in words if len(w) > 3 and w not in ['this', 'that', 'with', 'from', 'they', 'were', 'been']]
                
                for word in significant_words[:10]:  # Limit to 10 words per sentence for performance
                    try:
                        word_score = perplexity_analyzer.calculate_perplexity(word)
                        if word_score > 0.6:  # Only include high-scoring words
                            word_analyses.append({
                                'word': word,
                                'score': round(word_score, 3)
                            })
                    except:
                        continue
                
                sentence_analyses.append({
                    'text': sentence,
                    'score': round(sentence_score, 3),
                    'words': word_analyses
                })
                
            except Exception as e:
                logger.error(f"Error analyzing sentence: {e}")
                sentence_analyses.append({
                    'text': sentence,
                    'score': 0.5,
                    'words': []
                })
        
        return sentence_analyses
    
    def _analyze_words(self, text: str) -> Dict[str, Any]:
        """
        Perform word-level impact analysis
        Args:
            text: Input text
        Returns:
            Word analysis results
        """
        try:
            # Use perplexity analyzer for word impact
            word_impact = perplexity_analyzer.get_word_impact_analysis(text)
            return word_impact
            
        except Exception as e:
            logger.error(f"Error in word analysis: {e}")
            return {'unique_words': []}
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """Create result structure for empty/invalid input"""
        return {
            'overall_score': 0.0,
            'global_scores': {
                'perplexity': 0.0,
                'burstiness': 0.0,
                'semantic_coherence': 0.0,
                'ngram_similarity': 0.0
            },
            'paragraphs': [],
            'word_analysis': {'unique_words': []},
            'analysis_metadata': {
                'text_length': 0,
                'word_count': 0,
                'sentence_count': 0,
                'paragraph_count': 0,
                'error': 'Text too short or empty'
            }
        }
    
    def _create_error_result(self, error_msg: str) -> Dict[str, Any]:
        """Create result structure for error cases"""
        return {
            'overall_score': 0.5,
            'global_scores': {
                'perplexity': 0.5,
                'burstiness': 0.5,
                'semantic_coherence': 0.5,
                'ngram_similarity': 0.5
            },
            'paragraphs': [],
            'word_analysis': {'unique_words': []},
            'analysis_metadata': {
                'text_length': 0,
                'word_count': 0,
                'sentence_count': 0,
                'paragraph_count': 0,
                'error': error_msg
            }
        }
    
    def update_weights(self, new_weights: Dict[str, float]):
        """
        Update analysis weights
        Args:
            new_weights: Dictionary with new weight values
        """
        for key, value in new_weights.items():
            if key in self.weights:
                self.weights[key] = value
        
        self.validate_weights()
        logger.info(f"Updated weights: {self.weights}")

# Global score fusion instance
score_fusion = ScoreFusion()