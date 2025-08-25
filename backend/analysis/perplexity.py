"""
Perplexity Analysis Module for Origo
Calculates perplexity using GPT-2 model to detect AI-generated text patterns
Higher perplexity typically indicates human-written text
"""

import logging
import numpy as np
import torch
import json
import re
import os
from typing import List, Dict, Any
from utils.model_loader import model_loader
from utils.sentence_splitter import sentence_splitter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerplexityAnalyzer:
    """
    Analyzes text perplexity using GPT-2 language model
    Low perplexity suggests text is similar to AI training data
    Enhanced with stylistic patterns and register authenticity analysis
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = model_loader.get_device()
        
        # Load configuration files
        self.config_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.llm_red_flags = self._load_config('perplexity/llm_red_flags.json')
        self.punctuation_patterns = self._load_config('perplexity/punctuation_patterns.json')
        self.register_authenticity = self._load_config('perplexity/register_authenticity.json')
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
    
    def _load_model(self):
        """Load GPT-2 model and tokenizer if not already loaded"""
        if self.model is None or self.tokenizer is None:
            self.model, self.tokenizer = model_loader.get_gpt2_model()
            self.model.to(self.device)
    
    def calculate_perplexity(self, text: str) -> float:
        """
        Calculate perplexity for a given text
        Args:
            text: Input text to analyze
        Returns:
            Perplexity score (lower = more AI-like)
        """
        if not text or len(text.strip()) < 5:
            return 0.0
        
        self._load_model()
        
        try:
            # Tokenize the text
            encodings = self.tokenizer(
                text, 
                return_tensors='pt', 
                padding=True, 
                truncation=True, 
                max_length=512
            )
            
            input_ids = encodings.input_ids.to(self.device)
            attention_mask = encodings.attention_mask.to(self.device)
            
            # Calculate loss using the model
            with torch.no_grad():
                outputs = self.model(
                    input_ids=input_ids, 
                    attention_mask=attention_mask, 
                    labels=input_ids
                )
                loss = outputs.loss
            
            # Convert loss to perplexity
            perplexity = torch.exp(loss).item()
            
            # Normalize perplexity to 0-1 scale (inverted for AI detection)
            # Lower perplexity = higher AI probability
            normalized_score = min(1.0, max(0.0, (100 - perplexity) / 100))
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"Error calculating perplexity: {e}")
            return 0.5  # Return neutral score on error
    
    def analyze_stylistic_patterns(self, text: str) -> Dict[str, Any]:
        """
        Analyze stylistic patterns that indicate AI generation
        Args:
            text: Input text to analyze
        Returns:
            Dictionary with stylistic pattern analysis
        """
        if not self.llm_red_flags:
            return {'overall_score': 0.5, 'details': {}}
        
        text_lower = text.lower()
        words = sentence_splitter.tokenize_words(text)
        word_count = len(words)
        
        if word_count == 0:
            return {'overall_score': 0.5, 'details': {}}
        
        scores = {}
        weights = self.llm_red_flags.get('weights', {})
        
        # Analyze suspicious verbs
        verb_count = sum(1 for word in words if word.lower() in self.llm_red_flags.get('suspicious_verbs', []))
        verb_score = min(1.0, (verb_count / word_count) * weights.get('verbs', 1.0))
        scores['suspicious_verbs'] = verb_score
        
        # Analyze suspicious modifiers
        modifier_count = sum(1 for word in words if word.lower() in self.llm_red_flags.get('suspicious_modifiers', []))
        modifier_score = min(1.0, (modifier_count / word_count) * weights.get('modifiers', 1.0))
        scores['suspicious_modifiers'] = modifier_score
        
        # Analyze suspicious nouns
        noun_count = sum(1 for word in words if word.lower() in self.llm_red_flags.get('suspicious_nouns', []))
        noun_score = min(1.0, (noun_count / word_count) * weights.get('nouns', 1.0))
        scores['suspicious_nouns'] = noun_score
        
        # Analyze formulaic phrases
        phrase_matches = 0
        matched_phrases = []
        for phrase_pattern in self.llm_red_flags.get('formulaic_phrases', []):
            matches = re.findall(phrase_pattern, text_lower, re.IGNORECASE)
            if matches:
                phrase_matches += len(matches)
                matched_phrases.extend(matches)
        
        # Score based on phrase density per 100 words (more reasonable than per sentence)
        phrase_score = min(1.0, (phrase_matches / max(1, word_count / 100)) * weights.get('formulaic_phrases', 1.0))
        scores['formulaic_phrases'] = phrase_score
        scores['matched_phrases'] = matched_phrases[:5]  # Store first 5 matches for debugging
        
        # Analyze transition constructs
        transition_matches = 0
        matched_transitions = []
        for transition_pattern in self.llm_red_flags.get('transition_constructs', []):
            matches = re.findall(transition_pattern, text_lower, re.IGNORECASE)
            if matches:
                transition_matches += len(matches)
                matched_transitions.extend(matches)
        
        # Score based on transition density - more generous scoring
        transition_score = min(1.0, (transition_matches / max(1, word_count / 50)) * weights.get('transition_constructs', 1.0))
        scores['transition_constructs'] = transition_score
        scores['matched_transitions'] = matched_transitions[:3]  # Store first 3 matches
        
        # Analyze punctuation patterns
        punct_score = self._analyze_punctuation_patterns(text, word_count)
        scores['punctuation_patterns'] = punct_score
        
        # Calculate overall stylistic score safely
        score_values = []
        for key, value in scores.items():
            try:
                # Skip non-numeric values (like matched_phrases, matched_transitions)
                if key in ['matched_phrases', 'matched_transitions']:
                    continue
                # Ensure all values are converted to float scalars
                if isinstance(value, (int, float)):
                    score_values.append(float(value))
                elif isinstance(value, (list, tuple)) and len(value) > 0:
                    # If it's a list/tuple, take the first numeric value
                    score_values.append(float(value[0]))
                else:
                    # Fallback to neutral score
                    score_values.append(0.0)
            except (ValueError, TypeError, IndexError):
                # If conversion fails, use neutral score
                score_values.append(0.0)
        
        # Calculate overall score safely
        if score_values:
            overall_score = sum(score_values) / len(score_values)  # Use standard mean instead of np.mean
        else:
            overall_score = 0.0
        
        return {
            'overall_score': min(1.0, max(0.0, overall_score)),
            'details': scores
        }
    
    def _analyze_punctuation_patterns(self, text: str, word_count: int) -> float:
        """
        Analyze punctuation patterns for AI indicators
        """
        if not self.punctuation_patterns or word_count == 0:
            return 0.0  # Default to no penalty
        
        patterns = self.punctuation_patterns.get('patterns', {})
        penalties = []
        
        words_per_1000 = max(1, word_count / 1000)
        
        for pattern_name, pattern_config in patterns.items():
            weight = pattern_config.get('weight', 1.0)
            
            if 'regex' in pattern_config:
                matches = len(re.findall(pattern_config['regex'], text, 
                                       re.MULTILINE if pattern_config.get('multiline') else 0))
                if 'threshold_per_1000_words' in pattern_config:
                    threshold = pattern_config['threshold_per_1000_words'] * words_per_1000
                    if matches > threshold:
                        penalty = min(0.3, (matches - threshold) / max(1, threshold) * weight * 0.1)  # Much more conservative
                        penalties.append(penalty)
                else:
                    penalty = min(0.2, matches * weight * 0.05)  # Reduced multiplier
                    penalties.append(penalty)
            
            elif 'char' in pattern_config:
                char_count = text.count(pattern_config['char'])
                threshold = pattern_config.get('threshold_per_1000_words', 5) * words_per_1000
                if char_count > threshold:
                    penalty = min(0.3, (char_count - threshold) / max(1, threshold) * weight * 0.1)  # More conservative
                    penalties.append(penalty)
        
        if penalties:
            # Ensure all penalties are float values before calculating mean
            valid_penalties = []
            for penalty in penalties:
                try:
                    valid_penalties.append(float(penalty))
                except (ValueError, TypeError):
                    continue
            
            if valid_penalties:
                return min(0.5, sum(valid_penalties) / len(valid_penalties))  # Use standard mean instead of np.mean
            else:
                return 0.0
        return 0.0
    
    def analyze_register_authenticity(self, text: str) -> Dict[str, Any]:
        """
        Analyze register authenticity and naturalness markers
        Args:
            text: Input text to analyze
        Returns:
            Dictionary with register authenticity analysis
        """
        if not self.register_authenticity:
            return {'overall_score': 0.5, 'details': {}}
        
        text_lower = text.lower()
        words = sentence_splitter.tokenize_words(text)
        word_count = len(words)
        
        if word_count == 0:
            return {'overall_score': 0.5, 'details': {}}
        
        scores = {}
        
        # Analyze formality inconsistencies
        formality_score = self._analyze_formality_inconsistencies(text_lower, words, word_count)
        scores['formality_consistency'] = formality_score
        
        # Analyze emotional variance
        emotional_score = self._analyze_emotional_variance(text_lower, words)
        scores['emotional_variance'] = emotional_score
        
        # Analyze naturalness patterns
        naturalness_score = self._analyze_naturalness_patterns(text_lower, words)
        scores['naturalness'] = naturalness_score
        
        # Analyze discourse markers
        discourse_score = self._analyze_discourse_markers(text_lower, word_count)
        scores['discourse_markers'] = discourse_score
        
        # Calculate overall register authenticity score safely
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
                    score_values.append(0.0)
            except (ValueError, TypeError, IndexError):
                # If conversion fails, use neutral score
                score_values.append(0.0)
        
        # Calculate overall score safely
        if score_values:
            overall_score = sum(score_values) / len(score_values)  # Use standard mean instead of np.mean
        else:
            overall_score = 0.0
        
        return {
            'overall_score': min(1.0, max(0.0, overall_score)),
            'details': scores
        }
    
    def _analyze_formality_inconsistencies(self, text_lower: str, words: List[str], word_count: int) -> float:
        """Analyze formality inconsistencies in text"""
        formality_config = self.register_authenticity.get('formality_inconsistencies', {})
        
        # Check excessive contractions
        contractions = formality_config.get('excessive_contractions', {}).get('patterns', [])
        contraction_count = sum(1 for word in words if word.lower() in contractions)
        contraction_threshold = formality_config.get('excessive_contractions', {}).get('threshold_per_100_words', 8)
        contraction_penalty = (contraction_count / max(1, word_count / 100)) / contraction_threshold
        
        # Check overly formal phrases
        formal_phrases = formality_config.get('overly_formal_phrases', {}).get('patterns', [])
        formal_count = sum(1 for phrase in formal_phrases if phrase in text_lower)
        formal_penalty = formal_count * 0.2
        
        # Check mixed register markers
        mixed_register = formality_config.get('mixed_register_markers', {})
        casual_words = mixed_register.get('casual', {}).get('patterns', [])
        academic_words = mixed_register.get('academic', {}).get('patterns', [])
        
        casual_count = sum(1 for word in words if word.lower() in casual_words)
        academic_count = sum(1 for word in words if word.lower() in academic_words)
        
        if casual_count > 0 and academic_count > 0:
            mixed_penalty = 0.5  # Penalty for mixing registers
        else:
            mixed_penalty = 0.0
        
        total_penalty = min(1.0, contraction_penalty + formal_penalty + mixed_penalty)
        return total_penalty
    
    def _analyze_emotional_variance(self, text_lower: str, words: List[str]) -> float:
        """Analyze emotional variance in text"""
        emotional_config = self.register_authenticity.get('emotional_variance_markers', {})
        
        # Check for low variance indicators
        low_variance_patterns = emotional_config.get('low_variance_indicators', {}).get('patterns', [])
        low_variance_count = sum(1 for pattern in low_variance_patterns if pattern in text_lower)
        
        # Check for high variance expected patterns
        high_variance_patterns = emotional_config.get('high_variance_expected', {}).get('patterns', [])
        high_variance_count = sum(1 for pattern in high_variance_patterns if pattern in text_lower)
        
        # Analyze emotional adjectives distribution
        emotional_adj = emotional_config.get('emotional_adjectives', {})
        positive_adj = emotional_adj.get('positive', [])
        negative_adj = emotional_adj.get('negative', [])
        neutral_adj = emotional_adj.get('neutral', [])
        
        pos_count = sum(1 for word in words if word.lower() in positive_adj)
        neg_count = sum(1 for word in words if word.lower() in negative_adj)
        neu_count = sum(1 for word in words if word.lower() in neutral_adj)
        
        total_emotional = pos_count + neg_count + neu_count
        if total_emotional > 0:
            # Check if distribution is too uniform (AI-like)
            expected_variance = 0.3
            actual_variance = np.std([pos_count, neg_count, neu_count]) / max(1, np.mean([pos_count, neg_count, neu_count]))
            if actual_variance < expected_variance:
                emotional_penalty = 0.4
            else:
                emotional_penalty = 0.0
        else:
            emotional_penalty = 0.2  # Penalty for lack of emotional content
        
        variance_penalty = low_variance_count * 0.3 - high_variance_count * 0.2
        total_penalty = min(1.0, max(0.0, variance_penalty + emotional_penalty))
        return total_penalty
    
    def _analyze_naturalness_patterns(self, text_lower: str, words: List[str]) -> float:
        """Analyze naturalness patterns in text"""
        naturalness_config = self.register_authenticity.get('naturalness_patterns', {})
        
        # Check unnatural constructions
        unnatural_patterns = naturalness_config.get('unnatural_constructions', {}).get('patterns', [])
        unnatural_count = sum(1 for pattern in unnatural_patterns if pattern in text_lower)
        
        # Check natural constructions
        natural_patterns = naturalness_config.get('natural_constructions', {}).get('patterns', [])
        natural_count = sum(1 for pattern in natural_patterns if pattern in text_lower)
        
        # Check hedge words
        hedge_config = naturalness_config.get('hedge_words', {})
        artificial_hedges = hedge_config.get('artificial', [])
        natural_hedges = hedge_config.get('natural', [])
        
        artificial_hedge_count = sum(1 for word in words if word.lower() in artificial_hedges)
        natural_hedge_count = sum(1 for word in words if word.lower() in natural_hedges)
        
        # Calculate naturalness penalty
        unnatural_penalty = unnatural_count * 0.3
        natural_bonus = natural_count * 0.1
        hedge_penalty = artificial_hedge_count * 0.2 - natural_hedge_count * 0.1
        
        total_penalty = min(1.0, max(0.0, unnatural_penalty + hedge_penalty - natural_bonus))
        return total_penalty
    
    def _analyze_discourse_markers(self, text_lower: str, word_count: int) -> float:
        """Analyze discourse markers for mechanical patterns"""
        discourse_config = self.register_authenticity.get('discourse_markers', {})
        
        # Check mechanical transitions
        mechanical_patterns = discourse_config.get('mechanical_transitions', {}).get('patterns', [])
        mechanical_count = sum(1 for pattern in mechanical_patterns if pattern in text_lower)
        
        # Check natural transitions
        natural_patterns = discourse_config.get('natural_transitions', {}).get('patterns', [])
        natural_count = sum(1 for pattern in natural_patterns if pattern in text_lower)
        
        # Calculate discourse marker density
        total_transitions = mechanical_count + natural_count
        if word_count > 0 and total_transitions > 0:
            transition_density = total_transitions / word_count
            threshold_density = discourse_config.get('mechanical_transitions', {}).get('threshold_density', 0.02)
            
            if transition_density > threshold_density:
                mechanical_ratio = mechanical_count / total_transitions if total_transitions > 0 else 0
                penalty = mechanical_ratio * 0.5
            else:
                penalty = 0.0
        else:
            penalty = 0.0
        
        return min(1.0, penalty)
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive text analysis combining perplexity, stylistic patterns, and register authenticity
        Args:
            text: Input text to analyze
        Returns:
            Dictionary with comprehensive analysis results including detailed sentence analysis
        """
        if not text or len(text.strip()) < 10:
            return {
                'overall_score': 0.5,
                'base_perplexity': 0.5,
                'stylistic_patterns': {'overall_score': 0.5, 'details': {}},
                'register_authenticity': {'overall_score': 0.5, 'details': {}},
                'detailed_sentences': []
            }
        
        # Get component weights from configuration
        perplexity_weights = self.weights_config.get('perplexity_components', {
            'base_perplexity': 0.4,
            'stylistic_patterns': 0.3,
            'register_authenticity': 0.3
        })
        
        # Calculate base perplexity
        base_perplexity = self.calculate_perplexity(text)
        
        # Analyze stylistic patterns
        stylistic_analysis = self.analyze_stylistic_patterns(text)
        
        # Analyze register authenticity
        register_analysis = self.analyze_register_authenticity(text)
        
        # Get detailed sentence analysis for modal insights
        sentences = sentence_splitter.split_into_sentences(text)
        detailed_sentences = self.analyze_sentences_detailed(sentences)
        
        # Calculate weighted overall score
        overall_score = (
            base_perplexity * perplexity_weights['base_perplexity'] +
            stylistic_analysis['overall_score'] * perplexity_weights['stylistic_patterns'] +
            register_analysis['overall_score'] * perplexity_weights['register_authenticity']
        )
        
        overall_score = min(1.0, max(0.0, overall_score))
        
        return {
            'overall_score': round(overall_score, 3),
            'base_perplexity': round(base_perplexity, 3),
            'stylistic_patterns': stylistic_analysis,
            'register_authenticity': register_analysis,
            'component_weights': perplexity_weights,
            'detailed_sentences': detailed_sentences
        }
    
    def analyze_sentences(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze perplexity for each sentence
        Args:
            sentences: List of sentence strings
        Returns:
            List of dictionaries with sentence analysis
        """
        sentence_analysis = []
        
        for sentence in sentences:
            score = self.calculate_perplexity(sentence)
            
            # Analyze individual words in the sentence
            words = sentence_splitter.tokenize_words(sentence)
            word_analysis = []
            
            for word in words:
                word_score = self.calculate_perplexity(word)
                if word_score > 0.01:  # Much more permissive threshold for suspicious words
                    word_analysis.append({
                        'word': word,
                        'score': word_score
                    })
            
            sentence_analysis.append({
                'text': sentence,
                'score': score,
                'words': word_analysis
            })
        
        return sentence_analysis
    
    def analyze_sentences_detailed(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """
        Enhanced sentence-level perplexity analysis with detailed insights
        Returns top sentences with highlighted impactful parts
        Args:
            sentences: List of sentences to analyze
        Returns:
            List of detailed sentence analyses sorted by AI likelihood
        """
        sentence_analyses = []
        
        for sentence in sentences:
            if len(sentence.strip()) < 5:
                continue
                
            # Calculate perplexity score for the sentence
            perplexity_score = self.calculate_perplexity(sentence)
            
            # Analyze stylistic patterns
            stylistic_analysis = self.analyze_stylistic_patterns(sentence)
            
            # Identify impactful parts within the sentence
            impactful_parts = self._identify_impactful_parts(sentence)
            
            # Get register authenticity analysis
            register_analysis = self.analyze_register_authenticity(sentence)
            
            # Calculate combined score
            combined_score = (
                perplexity_score * 0.4 +
                stylistic_analysis['overall_score'] * 0.3 +
                register_analysis['overall_score'] * 0.3
            )
            
            sentence_analyses.append({
                'text': sentence,
                'score': combined_score,
                'perplexity_score': perplexity_score,
                'stylistic_score': stylistic_analysis['overall_score'],
                'register_score': register_analysis['overall_score'],
                'impactful_parts': impactful_parts,
                'evidence': {
                    'suspicious_words': self._extract_suspicious_words(sentence),
                    'formulaic_phrases': stylistic_analysis['details'].get('matched_phrases', []),
                    'transitions': stylistic_analysis['details'].get('matched_transitions', []),
                    'register_issues': register_analysis['details']
                }
            })
        
        # Sort by AI likelihood score (descending) and return top 10
        sentence_analyses.sort(key=lambda x: x['score'], reverse=True)
        return sentence_analyses[:10]
    
    def _identify_impactful_parts(self, sentence: str) -> List[Dict[str, Any]]:
        """
        Identify parts of the sentence that contribute most to AI likelihood
        Args:
            sentence: Sentence to analyze
        Returns:
            List of impactful parts with their positions and reasons
        """
        impactful_parts = []
        words = sentence_splitter.tokenize_words(sentence)
        
        if not words:
            return impactful_parts
        
        # Check for suspicious patterns from loaded configurations
        if self.llm_red_flags:
            # Identify suspicious verbs
            suspicious_verbs = self.llm_red_flags.get('suspicious_verbs', [])
            suspicious_modifiers = self.llm_red_flags.get('suspicious_modifiers', [])
            suspicious_nouns = self.llm_red_flags.get('suspicious_nouns', [])
            
            for i, word in enumerate(words):
                word_lower = word.lower()
                impact_type = None
                impact_score = 0.0
                
                if word_lower in suspicious_verbs:
                    impact_type = 'suspicious_verb'
                    impact_score = 0.7
                elif word_lower in suspicious_modifiers:
                    impact_type = 'suspicious_modifier'
                    impact_score = 0.6
                elif word_lower in suspicious_nouns:
                    impact_type = 'suspicious_noun'
                    impact_score = 0.5
                
                if impact_type:
                    # Find word position in original sentence
                    start_pos = sentence.lower().find(word_lower)
                    if start_pos != -1:
                        impactful_parts.append({
                            'text': word,
                            'start_pos': start_pos,
                            'end_pos': start_pos + len(word),
                            'impact_type': impact_type,
                            'score': impact_score,
                            'explanation': self._get_impact_explanation(impact_type)
                        })
        
        # Check for formulaic phrases
        if self.llm_red_flags:
            for phrase_pattern in self.llm_red_flags.get('formulaic_phrases', []):
                try:
                    matches = re.finditer(phrase_pattern, sentence, re.IGNORECASE)
                    for match in matches:
                        impactful_parts.append({
                            'text': match.group(),
                            'start_pos': match.start(),
                            'end_pos': match.end(),
                            'impact_type': 'formulaic_phrase',
                            'score': 0.8,
                            'explanation': 'Formulaic phrases common in AI-generated text'
                        })
                except re.error:
                    # Skip invalid regex patterns
                    continue
        
        # Sort by impact score and return top 5
        impactful_parts.sort(key=lambda x: x['score'], reverse=True)
        return impactful_parts[:5]
    
    def _extract_suspicious_words(self, sentence: str) -> List[str]:
        """
        Extract suspicious words from sentence
        Args:
            sentence: Sentence to analyze
        Returns:
            List of suspicious words found
        """
        suspicious_words = []
        words = sentence_splitter.tokenize_words(sentence)
        
        if self.llm_red_flags:
            all_suspicious = (
                self.llm_red_flags.get('suspicious_verbs', []) +
                self.llm_red_flags.get('suspicious_modifiers', []) +
                self.llm_red_flags.get('suspicious_nouns', [])
            )
            
            for word in words:
                if word.lower() in all_suspicious:
                    suspicious_words.append(word)
        
        return suspicious_words[:5]  # Limit to top 5
    
    def _get_impact_explanation(self, impact_type: str) -> str:
        """
        Get explanation for impact type
        Args:
            impact_type: Type of impact identified
        Returns:
            Human-readable explanation
        """
        explanations = {
            'suspicious_verb': 'Verb commonly overused in AI-generated text',
            'suspicious_modifier': 'Modifier/adjective frequently used by AI models',
            'suspicious_noun': 'Noun that appears disproportionately in AI text',
            'formulaic_phrase': 'Phrase pattern typical of AI language models',
            'transition_construct': 'Transition phrase characteristic of AI writing'
        }
        return explanations.get(impact_type, 'Potentially AI-generated pattern')
    
    def analyze_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """
        Analyze perplexity for each paragraph
        Args:
            text: Full text to analyze
        Returns:
            List of paragraph analyses
        """
        paragraphs = sentence_splitter.split_into_paragraphs(text)
        paragraph_analysis = []
        
        for paragraph in paragraphs:
            # Calculate paragraph-level score
            paragraph_score = self.calculate_perplexity(paragraph)
            
            # Analyze sentences within the paragraph
            sentences = sentence_splitter.split_into_sentences(paragraph)
            sentence_analysis = self.analyze_sentences(sentences)
            
            paragraph_analysis.append({
                'text': paragraph,
                'score': paragraph_score,
                'sentences': sentence_analysis
            })
        
        return paragraph_analysis
    
    def get_word_impact_analysis(self, text: str) -> Dict[str, Any]:
        """
        Analyze impact of individual words on perplexity
        Args:
            text: Text to analyze
        Returns:
            Dictionary with word impact analysis
        """
        words = sentence_splitter.tokenize_words(text)
        word_scores = {}
        
        # Calculate score for each unique word
        unique_words = list(set(words))
        
        for word in unique_words:
            score = self.calculate_perplexity(word)
            count = words.count(word)
            
            word_scores[word] = {
                'average_score': score,
                'count': count,
                'total_impact': score * count
            }
        
        # Sort by impact (score * frequency)
        sorted_words = sorted(
            word_scores.items(), 
            key=lambda x: x[1]['total_impact'], 
            reverse=True
        )
        
        return {
            'unique_words': [
                {
                    'word': word,
                    'average_score': data['average_score'],
                    'count': data['count']
                }
                for word, data in sorted_words[:20]  # Top 20 impactful words
            ]
        }
    
    def get_suspicious_words_in_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Identify suspicious words from red flags that appear in the text
        Args:
            text: Text to analyze
        Returns:
            List of suspicious words found with their categories and scores
        """
        if not self.llm_red_flags:
            return []
        
        words = sentence_splitter.tokenize_words(text)
        word_set = set(word.lower() for word in words)
        
        suspicious_found = []
        
        # Check suspicious verbs
        for verb in self.llm_red_flags.get('suspicious_verbs', []):
            if verb in word_set:
                score = self.calculate_perplexity(verb)
                count = sum(1 for w in words if w.lower() == verb)
                suspicious_found.append({
                    'word': verb,
                    'category': 'suspicious_verb',
                    'average_score': max(0.6, score),  # Ensure minimum suspicion score
                    'count': count
                })
        
        # Check suspicious modifiers
        for modifier in self.llm_red_flags.get('suspicious_modifiers', []):
            if modifier in word_set:
                score = self.calculate_perplexity(modifier)
                count = sum(1 for w in words if w.lower() == modifier)
                suspicious_found.append({
                    'word': modifier,
                    'category': 'suspicious_modifier',
                    'average_score': max(0.55, score),  # Ensure minimum suspicion score
                    'count': count
                })
        
        # Check suspicious nouns
        for noun in self.llm_red_flags.get('suspicious_nouns', []):
            if noun in word_set:
                score = self.calculate_perplexity(noun)
                count = sum(1 for w in words if w.lower() == noun)
                suspicious_found.append({
                    'word': noun,
                    'category': 'suspicious_noun',
                    'average_score': max(0.55, score),  # Ensure minimum suspicion score
                    'count': count
                })
        
        # Sort by score * count (impact) and return top results
        suspicious_found.sort(key=lambda x: x['average_score'] * x['count'], reverse=True)
        return suspicious_found[:10]

# Global perplexity analyzer instance
perplexity_analyzer = PerplexityAnalyzer()