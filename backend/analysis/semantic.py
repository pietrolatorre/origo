"""
Semantic Coherence Analysis Module for Origo
Uses Sentence-BERT to analyze semantic coherence and detect AI-generated patterns
AI text may show different semantic flow patterns compared to human writing
"""

import logging
import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from ..utils.model_loader import model_loader
from ..utils.sentence_splitter import sentence_splitter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticAnalyzer:
    """
    Analyzes semantic coherence and flow using sentence embeddings
    Unusual semantic patterns may indicate AI generation
    """
    
    def __init__(self):
        self.model = None
    
    def _load_model(self):
        """Load Sentence-BERT model if not already loaded"""
        if self.model is None:
            self.model = model_loader.get_sentence_transformer()
    
    def get_sentence_embeddings(self, sentences: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of sentences
        Args:
            sentences: List of sentence strings
        Returns:
            NumPy array of sentence embeddings
        """
        if not sentences:
            return np.array([])
        
        self._load_model()
        
        try:
            # Filter out empty sentences
            valid_sentences = [s for s in sentences if s.strip()]
            
            if not valid_sentences:
                return np.array([])
            
            # Generate embeddings
            embeddings = self.model.encode(valid_sentences)
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating sentence embeddings: {e}")
            return np.array([])
    
    def calculate_semantic_coherence(self, sentences: List[str]) -> float:
        """
        Calculate overall semantic coherence of text
        Args:
            sentences: List of sentences
        Returns:
            Coherence score (higher = more coherent, may indicate AI)
        """
        if len(sentences) < 2:
            return 0.5
        
        embeddings = self.get_sentence_embeddings(sentences)
        
        if embeddings.size == 0 or len(embeddings) < 2:
            return 0.5
        
        # Calculate pairwise cosine similarities
        similarities = []
        
        for i in range(len(embeddings) - 1):
            for j in range(i + 1, len(embeddings)):
                similarity = cosine_similarity(
                    embeddings[i].reshape(1, -1),
                    embeddings[j].reshape(1, -1)
                )[0, 0]
                similarities.append(similarity)
        
        if not similarities:
            return 0.5
        
        # Average similarity as coherence measure
        avg_coherence = np.mean(similarities)
        
        # Normalize and adjust for AI detection
        # Very high coherence might indicate AI (overly consistent)
        # Very low coherence might indicate poor AI or human rambling
        normalized_coherence = max(0.0, min(1.0, avg_coherence))
        
        # AI detection: moderate to high coherence is suspicious
        if normalized_coherence > 0.7:
            ai_score = normalized_coherence
        elif normalized_coherence < 0.3:
            ai_score = 0.6  # Low coherence also suspicious for AI
        else:
            ai_score = normalized_coherence * 0.8
        
        return ai_score
    
    def calculate_semantic_flow(self, sentences: List[str]) -> float:
        """
        Analyze semantic flow between consecutive sentences
        Args:
            sentences: List of sentences
        Returns:
            Flow score (unusual patterns may indicate AI)
        """
        if len(sentences) < 3:
            return 0.5
        
        embeddings = self.get_sentence_embeddings(sentences)
        
        if embeddings.size == 0 or len(embeddings) < 3:
            return 0.5
        
        # Calculate consecutive sentence similarities
        consecutive_similarities = []
        
        for i in range(len(embeddings) - 1):
            similarity = cosine_similarity(
                embeddings[i].reshape(1, -1),
                embeddings[i + 1].reshape(1, -1)
            )[0, 0]
            consecutive_similarities.append(similarity)
        
        if not consecutive_similarities:
            return 0.5
        
        # Analyze flow patterns
        mean_flow = np.mean(consecutive_similarities)
        std_flow = np.std(consecutive_similarities)
        
        # AI text often has more uniform flow (lower variation)
        if std_flow < 0.1:  # Very uniform flow
            ai_score = 0.8
        elif std_flow > 0.3:  # Very variable flow
            ai_score = 0.6
        else:
            # Moderate variation is more human-like
            ai_score = 1.0 - (std_flow / 0.3) * 0.5
        
        return min(1.0, max(0.0, ai_score))
    
    def calculate_topic_consistency(self, text: str) -> float:
        """
        Analyze topic consistency throughout the text
        Args:
            text: Full text to analyze
        Returns:
            Consistency score (extreme consistency may indicate AI)
        """
        paragraphs = sentence_splitter.split_into_paragraphs(text)
        
        if len(paragraphs) < 2:
            return 0.5
        
        # Get paragraph embeddings
        paragraph_embeddings = self.get_sentence_embeddings(paragraphs)
        
        if paragraph_embeddings.size == 0 or len(paragraph_embeddings) < 2:
            return 0.5
        
        # Calculate topic consistency
        similarities = []
        
        for i in range(len(paragraph_embeddings)):
            for j in range(i + 1, len(paragraph_embeddings)):
                similarity = cosine_similarity(
                    paragraph_embeddings[i].reshape(1, -1),
                    paragraph_embeddings[j].reshape(1, -1)
                )[0, 0]
                similarities.append(similarity)
        
        if not similarities:
            return 0.5
        
        consistency = np.mean(similarities)
        
        # Very high consistency across paragraphs might indicate AI
        if consistency > 0.8:
            ai_score = consistency
        else:
            ai_score = consistency * 0.7
        
        return min(1.0, max(0.0, ai_score))
    
    def calculate_semantic_repetition(self, sentences: List[str]) -> float:
        """
        Detect semantic repetition (saying the same thing differently)
        Args:
            sentences: List of sentences
        Returns:
            Repetition score (higher = more repetitive/AI-like)
        """
        if len(sentences) < 3:
            return 0.0
        
        embeddings = self.get_sentence_embeddings(sentences)
        
        if embeddings.size == 0 or len(embeddings) < 3:
            return 0.0
        
        # Find highly similar non-consecutive sentences
        high_similarity_count = 0
        total_comparisons = 0
        
        for i in range(len(embeddings)):
            for j in range(i + 2, len(embeddings)):  # Skip consecutive sentences
                similarity = cosine_similarity(
                    embeddings[i].reshape(1, -1),
                    embeddings[j].reshape(1, -1)
                )[0, 0]
                
                total_comparisons += 1
                
                if similarity > 0.8:  # Very high similarity threshold
                    high_similarity_count += 1
        
        if total_comparisons == 0:
            return 0.0
        
        repetition_rate = high_similarity_count / total_comparisons
        
        return min(1.0, repetition_rate * 3)  # Scale up for visibility
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive semantic analysis
        Args:
            text: Text to analyze
        Returns:
            Dictionary with semantic analysis results
        """
        sentences = sentence_splitter.split_into_sentences(text)
        
        # Calculate different semantic metrics
        coherence = self.calculate_semantic_coherence(sentences)
        flow = self.calculate_semantic_flow(sentences)
        consistency = self.calculate_topic_consistency(text)
        repetition = self.calculate_semantic_repetition(sentences)
        
        # Combined semantic score (weighted average)
        overall_score = (
            coherence * 0.3 +
            flow * 0.3 +
            consistency * 0.2 +
            repetition * 0.2
        )
        
        return {
            'overall_score': overall_score,
            'components': {
                'semantic_coherence': coherence,
                'semantic_flow': flow,
                'topic_consistency': consistency,
                'semantic_repetition': repetition
            },
            'sentence_count': len(sentences)
        }
    
    def analyze_sentences(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze semantic patterns for individual sentences in context
        Args:
            sentences: List of sentences
        Returns:
            List of sentence analyses
        """
        sentence_analysis = []
        embeddings = self.get_sentence_embeddings(sentences)
        
        for i, sentence in enumerate(sentences):
            # Calculate sentence's semantic score based on context
            if embeddings.size > 0 and i < len(embeddings):
                # Compare with surrounding sentences
                context_similarities = []
                
                for j in range(max(0, i - 2), min(len(embeddings), i + 3)):
                    if j != i:
                        similarity = cosine_similarity(
                            embeddings[i].reshape(1, -1),
                            embeddings[j].reshape(1, -1)
                        )[0, 0]
                        context_similarities.append(similarity)
                
                if context_similarities:
                    # High similarity with context might indicate AI
                    avg_similarity = np.mean(context_similarities)
                    sentence_score = min(1.0, avg_similarity * 1.2)
                else:
                    sentence_score = 0.5
            else:
                sentence_score = 0.5
            
            sentence_analysis.append({
                'text': sentence,
                'score': sentence_score,
                'words': []  # Individual word analysis not applicable for semantics
            })
        
        return sentence_analysis

# Global semantic analyzer instance
semantic_analyzer = SemanticAnalyzer()