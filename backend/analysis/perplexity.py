"""
Perplexity Analysis Module for Origo
Calculates perplexity using GPT-2 model to detect AI-generated text patterns
Higher perplexity typically indicates human-written text
"""

import logging
import numpy as np
import torch
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
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = model_loader.get_device()
    
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
                if word_score > 0.1:  # Only include significant words
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

# Global perplexity analyzer instance
perplexity_analyzer = PerplexityAnalyzer()