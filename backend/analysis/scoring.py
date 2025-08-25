"""
Scoring Fusion Module for Origo
Combines multiple analysis heuristics into a single comprehensive score
Weighs different analysis components based on their reliability and importance
"""

import logging
import json
import os
import hashlib
import time
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        
        # Performance settings
        self.performance_settings = self.weights_config.get('performance_settings', {})
        self.parallel_enabled = self.performance_settings.get('parallel_analysis', True)
        self.cache_enabled = self.performance_settings.get('enable_caching', True)
        self.cache_ttl = self.performance_settings.get('cache_ttl_seconds', 300)
        self.max_workers = self.performance_settings.get('max_workers', 4)
        self.timeout_seconds = self.performance_settings.get('timeout_seconds', 60)
        
        # Simple in-memory cache
        self.cache = {} if self.cache_enabled else None
        self.cache_timestamps = {} if self.cache_enabled else None
    
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
    
    def _get_cache_key(self, text: str, analysis_type: str = 'full') -> str:
        """Generate cache key for text analysis"""
        if not self.cache_enabled:
            return None
        
        # Create hash of text content and analysis type
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"{analysis_type}_{text_hash}"
    
    def _get_from_cache(self, cache_key: str) -> Any:
        """Get result from cache if available and not expired"""
        if not self.cache_enabled or not cache_key or cache_key not in self.cache:
            return None
        
        # Check if cache entry is expired
        timestamp = self.cache_timestamps.get(cache_key, 0)
        if time.time() - timestamp > self.cache_ttl:
            # Remove expired entry
            del self.cache[cache_key]
            del self.cache_timestamps[cache_key]
            return None
        
        return self.cache[cache_key]
    
    def _store_in_cache(self, cache_key: str, result: Any) -> None:
        """Store result in cache"""
        if not self.cache_enabled or not cache_key:
            return
        
        self.cache[cache_key] = result
        self.cache_timestamps[cache_key] = time.time()
        
        # Simple cache cleanup - remove oldest entries if cache gets too large
        if len(self.cache) > 100:  # Max 100 cached entries
            oldest_key = min(self.cache_timestamps.keys(), key=lambda k: self.cache_timestamps[k])
            del self.cache[oldest_key]
            del self.cache_timestamps[oldest_key]
    
    def analyze_text_comprehensive(self, text: str, enabled_dimensions: Dict[str, bool] = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis using all available methods with caching and parallel processing
        Args:
            text: Input text to analyze
            enabled_dimensions: Dictionary specifying which dimensions to include (default: all enabled)
        Returns:
            Complete analysis results with combined scores
        """
        if not text or len(text.strip()) < 10:
            return self._create_empty_result()
        
        # Default to all dimensions enabled if not specified
        if enabled_dimensions is None:
            enabled_dimensions = {
                'perplexity': True,
                'burstiness': True,
                'semantic_coherence': True,
                'ngram_similarity': True
            }
        
        # Check cache first
        cache_key = self._get_cache_key(text, 'comprehensive')
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            logger.info("Retrieved comprehensive analysis from cache")
            return cached_result
        
        start_time = time.time()
        logger.info("Starting comprehensive text analysis with optimized parallel processing...")
        
        try:
            if self.parallel_enabled:
                # Run analysis modules in parallel for better performance
                analysis_results = self._run_optimized_parallel_analysis(text, enabled_dimensions)
            else:
                # Fallback to sequential analysis
                analysis_results = self._run_sequential_analysis(text, enabled_dimensions)
            
            # Extract scores from results using new aggregation method
            scores = {
                'perplexity': self._extract_score_with_aggregation(analysis_results.get('perplexity', {}), 'perplexity') if enabled_dimensions.get('perplexity', True) else 0.0,
                'burstiness': self._extract_score_with_aggregation(analysis_results.get('burstiness', {}), 'burstiness') if enabled_dimensions.get('burstiness', True) else 0.0,
                'ngram_similarity': self._extract_score_with_aggregation(analysis_results.get('ngram', {}), 'ngram') if enabled_dimensions.get('ngram_similarity', True) else 0.0,
                'semantic_coherence': self._extract_score_with_aggregation(analysis_results.get('semantic', {}), 'semantic') if enabled_dimensions.get('semantic_coherence', True) else 0.0
            }
            
            # Calculate weighted overall score only for enabled dimensions
            self.validate_weights()
            enabled_weights = {k: v for k, v in self.weights.items() if enabled_dimensions.get(k.replace('_similarity', '').replace('_coherence', ''), True)}
            
            # Normalize weights for enabled dimensions
            total_enabled_weight = sum(enabled_weights.values())
            if total_enabled_weight > 0:
                normalized_weights = {k: v / total_enabled_weight for k, v in enabled_weights.items()}
                overall_score = sum(scores[key] * normalized_weights.get(key, 0) for key in scores if scores[key] > 0)
            else:
                overall_score = 0.5  # Default when no dimensions enabled
            
            overall_score = max(0.0, min(1.0, overall_score))  # Clamp to [0,1]
            
            # Optimize paragraph and sentence analysis with selective processing
            paragraphs_analysis = self._analyze_paragraphs_optimized(text)
            word_analysis = self._analyze_words_optimized(text)
            
            processing_time = time.time() - start_time
            
            result = {
                'overall_score': round(overall_score, 3),
                'global_scores': {
                    'perplexity': round(scores['perplexity'], 3),
                    'burstiness': round(scores['burstiness'], 3),
                    'semantic_coherence': round(scores['semantic_coherence'], 3),
                    'ngram_similarity': round(scores['ngram_similarity'], 3)
                },
                'enhanced_analysis': {
                    'perplexity_details': analysis_results.get('perplexity', {'overall_score': scores['perplexity']}),
                    'burstiness_details': analysis_results.get('burstiness', {'overall_score': scores['burstiness']}),
                    'ngram_details': analysis_results.get('ngram', {'overall_score': scores['ngram_similarity']}),
                    'semantic_details': analysis_results.get('semantic', {'overall_score': scores['semantic_coherence']})
                },
                'paragraphs': paragraphs_analysis,
                'word_analysis': word_analysis,
                'analysis_metadata': {
                    'text_length': len(text),
                    'word_count': len(sentence_splitter.tokenize_words(text)),
                    'sentence_count': len(sentence_splitter.split_into_sentences(text)),
                    'paragraph_count': len(sentence_splitter.split_into_paragraphs(text)),
                    'weights_used': self.weights.copy(),
                    'parallel_processing_enabled': self.parallel_enabled,
                    'caching_enabled': self.cache_enabled,
                    'processing_time_seconds': round(processing_time, 3),
                    'enhanced_features_enabled': {
                        'stylistic_analysis': self.weights_config.get('feature_flags', {}).get('enable_stylistic_analysis', True),
                        'register_analysis': self.weights_config.get('feature_flags', {}).get('enable_register_analysis', True),
                        'structural_analysis': self.weights_config.get('feature_flags', {}).get('enable_structural_analysis', True)
                    }
                }
            }
            
            # Store result in cache
            self._store_in_cache(cache_key, result)
            
            logger.info(f"Analysis complete in {processing_time:.2f}s. Overall score: {overall_score:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return self._create_error_result(str(e))
    
    def _run_optimized_parallel_analysis(self, text: str, enabled_dimensions: Dict[str, bool] = None) -> Dict[str, Any]:
        """
        Run all analysis modules in parallel with optimized performance settings
        Args:
            text: Text to analyze
            enabled_dimensions: Dictionary specifying which dimensions to include
        Returns:
            Dictionary with results from enabled analyzers
        """
        results = {}
        
        if enabled_dimensions is None:
            enabled_dimensions = {'perplexity': True, 'burstiness': True, 'semantic_coherence': True, 'ngram_similarity': True}
        
        # Check cache for individual components first
        cached_components = {}
        for component in ['perplexity', 'burstiness', 'ngram', 'semantic']:
            if self._should_include_dimension(component, enabled_dimensions):
                cache_key = self._get_cache_key(text, component)
                cached_result = self._get_from_cache(cache_key)
                if cached_result is not None:
                    cached_components[component] = cached_result
                    logger.info(f"Retrieved {component} analysis from cache")
        
        # Define analysis tasks only for non-cached enabled components
        analysis_tasks = {}
        if 'perplexity' not in cached_components and enabled_dimensions.get('perplexity', True):
            analysis_tasks['perplexity'] = lambda: perplexity_analyzer.analyze_text(text)
        if 'burstiness' not in cached_components and enabled_dimensions.get('burstiness', True):
            analysis_tasks['burstiness'] = lambda: burstiness_analyzer.analyze_text(text)
        if 'ngram' not in cached_components and enabled_dimensions.get('ngram_similarity', True):
            analysis_tasks['ngram'] = lambda: ngram_analyzer.analyze_text_with_patterns(text)
        if 'semantic' not in cached_components and enabled_dimensions.get('semantic_coherence', True):
            analysis_tasks['semantic'] = lambda: semantic_analyzer.analyze_text(text)
        
        # Use cached results
        results.update(cached_components)
        
        # Execute only non-cached tasks in parallel
        if analysis_tasks:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_name = {executor.submit(task): name for name, task in analysis_tasks.items()}
                
                # Collect results as they complete
                for future in as_completed(future_to_name, timeout=self.timeout_seconds):
                    analysis_name = future_to_name[future]
                    try:
                        result = future.result(timeout=30)  # 30 second timeout per analyzer
                        results[analysis_name] = result
                        
                        # Cache individual component result
                        cache_key = self._get_cache_key(text, analysis_name)
                        self._store_in_cache(cache_key, result)
                        
                        logger.info(f"Completed {analysis_name} analysis")
                    except Exception as e:
                        logger.error(f"Error in {analysis_name} analysis: {e}")
                        results[analysis_name] = {'overall_score': 0.5}  # Default fallback
        
        return results
    
    def _should_include_dimension(self, component: str, enabled_dimensions: Dict[str, bool]) -> bool:
        """
        Check if a component should be included based on enabled dimensions
        Args:
            component: Component name ('perplexity', 'burstiness', 'ngram', 'semantic')
            enabled_dimensions: Dictionary of enabled dimensions
        Returns:
            True if component should be included
        """
        dimension_mapping = {
            'perplexity': 'perplexity',
            'burstiness': 'burstiness', 
            'ngram': 'ngram_similarity',
            'semantic': 'semantic_coherence'
        }
        return enabled_dimensions.get(dimension_mapping.get(component, component), True)
    
    def _extract_score_with_aggregation(self, result: Any, analysis_type: str) -> float:
        """
        Extract overall score from analysis result using new aggregation method:
        For dimensions with multiple components, use average of values above threshold
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
                # Check if we have paragraph/sentence level data for aggregation
                if 'paragraphs' in result or 'sentences' in result:
                    score = self._aggregate_scores_above_threshold(result)
                else:
                    score = float(result.get('overall_score', 0.5))
            else:
                logger.warning(f"Unexpected result format for {analysis_type}: {type(result)}")
                score = 0.5
            
            # Ensure score is within valid range [0.0, 1.0]
            score = max(0.0, min(1.0, score))
            return score
            
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Error extracting score for {analysis_type}: {e}, using default")
            return 0.5
    
    def _aggregate_scores_above_threshold(self, result: Dict[str, Any]) -> float:
        """
        Aggregate scores using average of values above threshold (0.6 for yellow threshold)
        This highlights the worst parts rather than averaging everything
        Args:
            result: Analysis result with paragraph/sentence data
        Returns:
            Aggregated score focusing on high-scoring (problematic) parts
        """
        threshold = 0.6  # Yellow threshold
        high_scores = []
        
        # Collect scores from paragraphs
        if 'paragraphs' in result:
            for paragraph in result['paragraphs']:
                if isinstance(paragraph, dict) and 'score' in paragraph:
                    score = float(paragraph['score'])
                    if score >= threshold:
                        high_scores.append(score)
                        
                # Also check sentences within paragraphs
                if 'sentences' in paragraph:
                    for sentence in paragraph['sentences']:
                        if isinstance(sentence, dict) and 'score' in sentence:
                            score = float(sentence['score'])
                            if score >= threshold:
                                high_scores.append(score)
        
        # Collect scores from direct sentences list
        if 'sentences' in result:
            for sentence in result['sentences']:
                if isinstance(sentence, dict) and 'score' in sentence:
                    score = float(sentence['score'])
                    if score >= threshold:
                        high_scores.append(score)
        
        # If we have high scores, use their average
        if high_scores:
            return sum(high_scores) / len(high_scores)
        
        # If no high scores, fall back to overall score or default
        return float(result.get('overall_score', 0.5))
    
    def _run_sequential_analysis(self, text: str, enabled_dimensions: Dict[str, bool] = None) -> Dict[str, Any]:
        """
        Run analysis modules sequentially as fallback
        Args:
            text: Text to analyze
            enabled_dimensions: Dictionary specifying which dimensions to include
        Returns:
            Dictionary with results from enabled analyzers
        """
        results = {}
        
        if enabled_dimensions is None:
            enabled_dimensions = {'perplexity': True, 'burstiness': True, 'semantic_coherence': True, 'ngram_similarity': True}
        
        analysis_methods = []
        if enabled_dimensions.get('perplexity', True):
            analysis_methods.append(('perplexity', lambda: perplexity_analyzer.analyze_text(text)))
        if enabled_dimensions.get('burstiness', True):
            analysis_methods.append(('burstiness', lambda: burstiness_analyzer.analyze_text(text)))
        if enabled_dimensions.get('ngram_similarity', True):
            analysis_methods.append(('ngram', lambda: ngram_analyzer.analyze_text_with_patterns(text)))
        if enabled_dimensions.get('semantic_coherence', True):
            analysis_methods.append(('semantic', lambda: semantic_analyzer.analyze_text(text)))
        
        for name, method in analysis_methods:
            try:
                # Check cache first
                cache_key = self._get_cache_key(text, name)
                cached_result = self._get_from_cache(cache_key)
                if cached_result is not None:
                    results[name] = cached_result
                    logger.info(f"Retrieved {name} analysis from cache")
                    continue
                
                # Run analysis and cache result
                result = method()
                results[name] = result
                self._store_in_cache(cache_key, result)
                logger.info(f"Completed {name} analysis")
                
            except Exception as e:
                logger.error(f"Error in {name} analysis: {e}")
                results[name] = {'overall_score': 0.5}
        
        return results
    
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
    
    def _analyze_paragraphs_optimized(self, text: str) -> List[Dict[str, Any]]:
        """
        Analyze individual paragraphs with optimized sentence breakdown
        Args:
            text: Input text
        Returns:
            List of paragraph analyses
        """
        paragraphs = sentence_splitter.split_into_paragraphs(text)
        paragraph_analyses = []
        
        # Limit paragraph analysis for very long texts
        max_paragraphs = 10 if len(paragraphs) > 10 else len(paragraphs)
        
        for i, paragraph in enumerate(paragraphs[:max_paragraphs]):
            try:
                # For performance, use simplified analysis for paragraphs
                # Only run perplexity and one other analyzer per paragraph
                para_perplexity_result = perplexity_analyzer.analyze_text(paragraph)
                para_burstiness_result = burstiness_analyzer.analyze_text(paragraph)
                
                # Extract scores with validation
                para_perplexity = self._extract_score(para_perplexity_result, 'perplexity')
                para_burstiness = self._extract_score(para_burstiness_result, 'burstiness')
                
                # Simplified scoring for performance (only use top 2 most reliable analyzers)
                paragraph_score = (para_perplexity * 0.6 + para_burstiness * 0.4)
                paragraph_score = max(0.0, min(1.0, paragraph_score))
                
                # Analyze sentences within paragraph (limited for performance)
                sentences = sentence_splitter.split_into_sentences(paragraph)
                sentence_analyses = self._analyze_sentences_optimized(sentences[:5])  # Limit to first 5 sentences
                
                paragraph_analyses.append({
                    'text': paragraph,
                    'score': round(paragraph_score, 3),
                    'sentences': sentence_analyses
                })
                
            except Exception as e:
                logger.error(f"Error analyzing paragraph {i}: {e}")
                safe_paragraph = str(paragraph) if paragraph else "Error: Unable to process paragraph"
                paragraph_analyses.append({
                    'text': safe_paragraph,
                    'score': 0.5,
                    'sentences': []
                })
        
        # Add summary for remaining paragraphs if truncated
        if len(paragraphs) > max_paragraphs:
            remaining_count = len(paragraphs) - max_paragraphs
            paragraph_analyses.append({
                'text': f"... and {remaining_count} more paragraphs (analysis truncated for performance)",
                'score': 0.5,
                'sentences': []
            })
        
        return paragraph_analyses
    
    def _analyze_sentences_optimized(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze individual sentences with optimized word breakdown
        Args:
            sentences: List of sentences
        Returns:
            List of sentence analyses
        """
        sentence_analyses = []
        
        # Limit sentence analysis for performance
        max_sentences = 8 if len(sentences) > 8 else len(sentences)
        
        for i, sentence in enumerate(sentences[:max_sentences]):
            try:
                # Use only perplexity for sentence-level analysis (fastest)
                sent_perplexity_result = perplexity_analyzer.analyze_text(sentence)
                sent_perplexity = self._extract_score(sent_perplexity_result, 'perplexity')
                
                # Ensure perplexity score is valid
                if not isinstance(sent_perplexity, (int, float)) or not (0 <= sent_perplexity <= 1):
                    sent_perplexity = 0.5
                
                sentence_score = float(sent_perplexity)
                
                # Minimal word analysis for performance
                words = sentence_splitter.tokenize_words(sentence)
                word_analyses = []
                
                # Only analyze high-impact words (length > 5, skip common words)
                significant_words = [w for w in words 
                                   if len(w) > 5 and w.lower() not in 
                                   ['this', 'that', 'with', 'from', 'they', 'were', 'been', 'have', 'will', 'would', 'could', 'should']]
                
                # Limit to 5 words per sentence for performance
                for word in significant_words[:5]:
                    try:
                        word_score = perplexity_analyzer.calculate_perplexity(word)
                        if word_score > 0.4:  # Higher threshold for better performance
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
                logger.error(f"Error analyzing sentence {i}: {e}")
                sentence_analyses.append({
                    'text': sentence,
                    'score': 0.5,
                    'words': []
                })
        
        # Add summary if sentences were truncated
        if len(sentences) > max_sentences:
            remaining_count = len(sentences) - max_sentences
            sentence_analyses.append({
                'text': f"... and {remaining_count} more sentences (analysis truncated for performance)",
                'score': 0.5,
                'words': []
            })
        
        return sentence_analyses
    
    def _analyze_words_optimized(self, text: str) -> Dict[str, Any]:
        """
        Perform optimized word-level impact analysis
        Args:
            text: Input text
        Returns:
            Enhanced word analysis results with performance optimizations
        """
        try:
            # Get word analysis but limit processing for performance
            word_impact = perplexity_analyzer.get_word_impact_analysis(text)
            suspicious_words = perplexity_analyzer.get_suspicious_words_in_text(text)
            
            # Ensure consistent data structures
            all_words = word_impact.get('unique_words', [])
            if not isinstance(all_words, list):
                all_words = []
            
            if not isinstance(suspicious_words, list):
                suspicious_words = []
            
            # Limit processing for performance - only top 15 words
            all_words = all_words[:15]
            suspicious_words = suspicious_words[:10]
            
            # Create efficient lookup for suspicious words
            suspicious_dict = {}
            for w in suspicious_words:
                if isinstance(w, dict) and 'word' in w:
                    word_key = str(w['word']).lower()
                    suspicious_dict[word_key] = {
                        'word': str(w['word']),
                        'average_score': float(w.get('average_score', 0.5)),
                        'count': int(w.get('count', 1)),
                        'category': str(w.get('category', 'suspicious'))
                    }
            
            # Process regular words efficiently
            updated_words = []
            for w in all_words:
                if isinstance(w, dict) and 'word' in w:
                    word = str(w['word'])
                    word_lower = word.lower()
                    
                    if word_lower in suspicious_dict:
                        # Merge with suspicious word data
                        susp_data = suspicious_dict[word_lower]
                        updated_words.append({
                            'word': word,
                            'average_score': max(float(w.get('average_score', 0.0)), susp_data['average_score']),
                            'count': int(w.get('count', 1)),
                            'category': susp_data['category']
                        })
                    else:
                        updated_words.append({
                            'word': word,
                            'average_score': float(w.get('average_score', 0.0)),
                            'count': int(w.get('count', 1)),
                            'category': 'normal'
                        })
            
            # Add remaining suspicious words
            for word_lower, susp_data in suspicious_dict.items():
                if not any(w['word'].lower() == word_lower for w in updated_words):
                    updated_words.append(susp_data)
            
            # Efficient sorting
            updated_words.sort(key=lambda x: float(x.get('average_score', 0)) * int(x.get('count', 1)), reverse=True)
            
            return {
                'unique_words': updated_words[:20],  # Limit to top 20 for performance
                'suspicious_words_found': len(suspicious_words),
                'total_unique_words': len(updated_words)
            }
            
        except Exception as e:
            logger.error(f"Error in optimized word analysis: {e}")
            return {'unique_words': [], 'suspicious_words_found': 0, 'total_unique_words': 0}
    
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