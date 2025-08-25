"""
Scoring Fusion Module for Origo
Combines multiple analysis heuristics into a single comprehensive score
Weighs different analysis components based on their reliability and importance
"""

import logging
import json
import os
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
    Uses simple arithmetic mean as specified in MODIFICHE.md
    """
    
    def __init__(self):
        # Load configuration from file
        self.config_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.weights_config = self._load_config('weights_config.json')
        
        # Weights for different analysis components (simple arithmetic mean)
        self.weights = self.weights_config.get('scoring_weights', {
            'perplexity': 0.25,       # Equal weight
            'burstiness': 0.25,       # Equal weight
            'ngram_similarity': 0.25,  # Equal weight
            'semantic_coherence': 0.25 # Equal weight
        })
    
    def _load_config(self, filename: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            config_path = os.path.join(self.config_dir, filename)
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config {filename}: {e}")
            return {}
    
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
            # Perform individual analyses using enhanced methods
            logger.info("Calculating enhanced perplexity analysis...")
            perplexity_result = self._safe_analysis(
                lambda: perplexity_analyzer.analyze_text(text),
                "perplexity"
            )
            
            logger.info("Analyzing enhanced burstiness...")
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
            
            # Extract scores from results (handle both new enhanced format and legacy format)
            scores = {
                'perplexity': self._extract_score(perplexity_result, 'perplexity'),
                'burstiness': self._extract_score(burstiness_result, 'burstiness'),
                'ngram_similarity': self._extract_score(ngram_result, 'ngram'),
                'semantic_coherence': self._extract_score(semantic_result, 'semantic')
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
                'enhanced_analysis': {
                    'perplexity_details': perplexity_result if isinstance(perplexity_result, dict) else {'overall_score': perplexity_result},
                    'burstiness_details': burstiness_result if isinstance(burstiness_result, dict) else {'overall_score': burstiness_result},
                    'ngram_details': ngram_result if isinstance(ngram_result, dict) else {'overall_score': ngram_result},
                    'semantic_details': semantic_result if isinstance(semantic_result, dict) else {'overall_score': semantic_result}
                },
                'paragraphs': paragraphs_analysis,
                'word_analysis': word_analysis,
                'analysis_metadata': {
                    'text_length': len(text),
                    'word_count': len(sentence_splitter.tokenize_words(text)),
                    'sentence_count': len(sentence_splitter.split_into_sentences(text)),
                    'paragraph_count': len(sentence_splitter.split_into_paragraphs(text)),
                    'weights_used': self.weights.copy(),
                    'enhanced_features_enabled': {
                        'stylistic_analysis': self.weights_config.get('feature_flags', {}).get('enable_stylistic_analysis', True),
                        'register_analysis': self.weights_config.get('feature_flags', {}).get('enable_register_analysis', True),
                        'structural_analysis': self.weights_config.get('feature_flags', {}).get('enable_structural_analysis', True)
                    }
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
            return {'overall_score': 0.5} if analysis_name != 'perplexity' else 0.5
    
    def _extract_score(self, result: Any, analysis_type: str) -> float:
        """
        Extract overall score from analysis result, handling both enhanced and legacy formats
        Args:
            result: Analysis result from analyzer
            analysis_type: Type of analysis ('perplexity', 'burstiness', 'ngram', 'semantic')
        Returns:
            Overall score as float between 0.0 and 1.0
        """
        try:
            if isinstance(result, (int, float)):
                score = float(result)
            elif isinstance(result, dict):
                score = float(result.get('overall_score', 0.5))
            elif isinstance(result, (list, tuple)) and len(result) > 0:
                # If it's a list/tuple, try to extract the first numeric value
                score = float(result[0]) if isinstance(result[0], (int, float)) else 0.5
            else:
                logger.warning(f"Unexpected result format for {analysis_type}: {type(result)}")
                score = 0.5
            
            # Ensure score is within valid range [0.0, 1.0]
            if not (0.0 <= score <= 1.0):
                logger.warning(f"Score {score} for {analysis_type} outside valid range [0,1], clamping")
                score = max(0.0, min(1.0, score))
            
            return score
            
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Error extracting score for {analysis_type}: {e}, using default")
            return 0.5
    
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
                para_perplexity_result = perplexity_analyzer.analyze_text(paragraph)
                para_burstiness_result = burstiness_analyzer.analyze_text(paragraph)
                para_ngram_result = ngram_analyzer.analyze_text(paragraph)
                para_semantic_result = semantic_analyzer.analyze_text(paragraph)
                
                # Extract scores with validation
                para_perplexity = self._extract_score(para_perplexity_result, 'perplexity')
                para_burstiness = self._extract_score(para_burstiness_result, 'burstiness')
                para_ngram = self._extract_score(para_ngram_result, 'ngram')
                para_semantic = self._extract_score(para_semantic_result, 'semantic')
                
                # Validate all scores are numeric before calculation
                scores_valid = all(isinstance(score, (int, float)) and 0 <= score <= 1 
                                 for score in [para_perplexity, para_burstiness, para_ngram, para_semantic])
                
                if not scores_valid:
                    logger.warning(f"Invalid scores detected in paragraph analysis, using defaults")
                    para_perplexity = para_burstiness = para_ngram = para_semantic = 0.5
                
                # Calculate paragraph score safely
                try:
                    paragraph_score = (
                        float(para_perplexity) * self.weights['perplexity'] +
                        float(para_burstiness) * self.weights['burstiness'] +
                        float(para_ngram) * self.weights['ngram_similarity'] +
                        float(para_semantic) * self.weights['semantic_coherence']
                    )
                    paragraph_score = max(0.0, min(1.0, paragraph_score))  # Clamp to valid range
                except (TypeError, ValueError) as e:
                    logger.warning(f"Error calculating paragraph score: {e}, using default")
                    paragraph_score = 0.5
                
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
                # Ensure paragraph text is properly handled even in error cases
                safe_paragraph = str(paragraph) if paragraph else "Error: Unable to process paragraph"
                paragraph_analyses.append({
                    'text': safe_paragraph,
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
                # Get sentence-level scores (simplified for performance)
                sent_perplexity_result = perplexity_analyzer.analyze_text(sentence)
                sent_perplexity = self._extract_score(sent_perplexity_result, 'perplexity')
                
                # Ensure perplexity score is a valid float
                if not isinstance(sent_perplexity, (int, float)) or not (0 <= sent_perplexity <= 1):
                    sent_perplexity = 0.5
                
                # Calculate sentence score (simplified using only perplexity for performance)
                sentence_score = float(sent_perplexity)  # Use perplexity as primary indicator for sentences
                
                # Analyze significant words in sentence
                words = sentence_splitter.tokenize_words(sentence)
                word_analyses = []
                
                # Only analyze words that might be significant
                significant_words = [w for w in words if len(w) > 3 and w not in ['this', 'that', 'with', 'from', 'they', 'were', 'been']]
                
                for word in significant_words[:10]:  # Limit to 10 words per sentence for performance
                    try:
                        word_score = perplexity_analyzer.calculate_perplexity(word)
                        if word_score > 0.3:  # More reasonable threshold for including words
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
        Perform word-level impact analysis including suspicious words detection
        Args:
            text: Input text
        Returns:
            Enhanced word analysis results
        """
        try:
            # Get traditional word impact analysis
            word_impact = perplexity_analyzer.get_word_impact_analysis(text)
            
            # Get suspicious words specifically identified
            suspicious_words = perplexity_analyzer.get_suspicious_words_in_text(text)
            
            # Ensure consistent data structures
            all_words = word_impact.get('unique_words', [])
            if not isinstance(all_words, list):
                all_words = []
            
            if not isinstance(suspicious_words, list):
                suspicious_words = []
            
            # Create dictionaries for efficient lookup and ensure proper data types
            suspicious_words_dict = {}
            for w in suspicious_words:
                if isinstance(w, dict) and 'word' in w:
                    # Ensure all required fields have safe default values
                    word_key = str(w['word']).lower()
                    suspicious_words_dict[word_key] = {
                        'word': str(w['word']),
                        'average_score': float(w.get('average_score', 0.5)),
                        'count': int(w.get('count', 1)),
                        'category': str(w.get('category', 'suspicious'))
                    }
            
            existing_words = {}
            for w in all_words:
                if isinstance(w, dict) and 'word' in w:
                    word_key = str(w['word'])
                    existing_words[word_key] = {
                        'word': word_key,
                        'average_score': float(w.get('average_score', 0.0)),
                        'count': int(w.get('count', 1)),
                        'category': str(w.get('category', 'normal'))
                    }
            
            # Combine words with consistent data structure
            updated_words = []
            
            # Include all traditional words, giving priority to suspicious words
            for word, word_data in existing_words.items():
                word_lower = word.lower()
                if word_lower in suspicious_words_dict:
                    # Use suspicious word data (higher scores)
                    susp_data = suspicious_words_dict[word_lower]
                    updated_words.append({
                        'word': word,
                        'average_score': max(word_data['average_score'], susp_data['average_score']),
                        'count': word_data['count'],
                        'category': susp_data['category']
                    })
                else:
                    updated_words.append(word_data)
            
            # Add suspicious words that weren't in the original list
            for word_lower, susp_data in suspicious_words_dict.items():
                if susp_data['word'] not in existing_words:
                    updated_words.append({
                        'word': susp_data['word'],
                        'average_score': susp_data['average_score'],
                        'count': susp_data['count'],
                        'category': susp_data['category']
                    })
            
            # Safe sorting with proper numeric values
            def safe_sort_key(x):
                try:
                    score = float(x.get('average_score', 0.0))
                    count = int(x.get('count', 1))
                    return score * count
                except (ValueError, TypeError):
                    return 0.0
            
            updated_words.sort(key=safe_sort_key, reverse=True)
            
            return {
                'unique_words': updated_words[:25],  # Increased to show more suspicious words
                'suspicious_words_found': len(suspicious_words),
                'total_unique_words': len(updated_words)
            }
            
        except Exception as e:
            logger.error(f"Error in word analysis: {e}")
            return {'unique_words': [], 'suspicious_words_found': 0, 'total_unique_words': 0}
    
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