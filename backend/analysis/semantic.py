"""
Semantic Coherence Analysis Module for Origo
Uses Sentence-BERT to analyze semantic coherence and detect AI-generated patterns
AI text may show different semantic flow patterns compared to human writing
"""

import logging
import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from utils.model_loader import model_loader
from utils.sentence_splitter import sentence_splitter

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
        Comprehensive semantic analysis including detailed evidence for modal display
        Args:
            text: Text to analyze
        Returns:
            Dictionary with semantic analysis results including detailed evidence
        """
        sentences = sentence_splitter.split_into_sentences(text)
        
        # Calculate different semantic metrics
        coherence = self.calculate_semantic_coherence(sentences)
        flow = self.calculate_semantic_flow(sentences)
        consistency = self.calculate_topic_consistency(text)
        repetition = self.calculate_semantic_repetition(sentences)
        
        # Get detailed evidence for modal insights
        semantic_evidence = self.analyze_semantic_evidence(text)
        
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
            'sentence_count': len(sentences),
            'detailed_evidence': semantic_evidence
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
    
    def analyze_semantic_evidence(self, text: str) -> Dict[str, Any]:
        """
        Enhanced semantic analysis to provide structured evidence for modal display
        Returns detailed semantic coherence analysis with specific patterns
        Args:
            text: Text to analyze
        Returns:
            Dictionary with detailed semantic evidence
        """
        sentences = sentence_splitter.split_into_sentences(text)
        
        if len(sentences) < 2:
            return {
                'coherence_patterns': [],
                'flow_analysis': {},
                'topic_clusters': [],
                'repetition_evidence': [],
                'summary': {
                    'overall_coherence': 0.5,
                    'ai_likelihood': 0.5,
                    'analysis_confidence': 'low'
                }
            }
        
        # Get sentence embeddings
        embeddings = self.get_sentence_embeddings(sentences)
        
        if embeddings.size == 0:
            return self._get_empty_semantic_evidence()
        
        # Analyze coherence patterns
        coherence_patterns = self._analyze_coherence_patterns(sentences, embeddings)
        
        # Analyze semantic flow
        flow_analysis = self._analyze_semantic_flow_detailed(sentences, embeddings)
        
        # Identify topic clusters
        topic_clusters = self._identify_topic_clusters(sentences, embeddings)
        
        # Find semantic repetitions
        repetition_evidence = self._find_semantic_repetitions(sentences, embeddings)
        
        # Calculate summary metrics
        summary = self._calculate_semantic_summary(coherence_patterns, flow_analysis, topic_clusters, repetition_evidence)
        
        return {
            'coherence_patterns': coherence_patterns,
            'flow_analysis': flow_analysis,
            'topic_clusters': topic_clusters,
            'repetition_evidence': repetition_evidence,
            'summary': summary
        }
    
    def _get_empty_semantic_evidence(self) -> Dict[str, Any]:
        """
        Return empty semantic evidence structure
        """
        return {
            'coherence_patterns': [],
            'flow_analysis': {'flow_uniformity': 0.5, 'transitions': []},
            'topic_clusters': [],
            'repetition_evidence': [],
            'summary': {
                'overall_coherence': 0.5,
                'ai_likelihood': 0.5,
                'analysis_confidence': 'low'
            }
        }
    
    def _analyze_coherence_patterns(self, sentences: List[str], embeddings: np.ndarray) -> List[Dict[str, Any]]:
        """
        Analyze coherence patterns in the text
        """
        patterns = []
        
        if len(embeddings) < 3:
            return patterns
        
        # Calculate all pairwise similarities
        similarity_matrix = cosine_similarity(embeddings)
        
        # Identify high coherence segments
        for i in range(len(sentences) - 2):
            # Check for consecutive high-coherence segments
            segment_similarities = []
            for j in range(i, min(i + 3, len(sentences))):
                for k in range(j + 1, min(i + 3, len(sentences))):
                    if j < len(similarity_matrix) and k < len(similarity_matrix[0]):
                        segment_similarities.append(similarity_matrix[j][k])
            
            if segment_similarities:
                avg_similarity = np.mean(segment_similarities)
                
                if avg_similarity > 0.75:  # High coherence threshold
                    pattern = {
                        'type': 'high_coherence_segment',
                        'start_sentence': i,
                        'end_sentence': min(i + 2, len(sentences) - 1),
                        'coherence_score': float(avg_similarity),
                        'sentences': sentences[i:min(i + 3, len(sentences))],
                        'evidence': f'Sentences {i+1}-{min(i + 3, len(sentences))} show unusually high semantic coherence ({avg_similarity:.2f})',
                        'ai_likelihood': min(1.0, avg_similarity * 1.1)
                    }
                    patterns.append(pattern)
        
        # Sort by AI likelihood and return top 5
        patterns.sort(key=lambda x: x['ai_likelihood'], reverse=True)
        return patterns[:5]
    
    def _analyze_semantic_flow_detailed(self, sentences: List[str], embeddings: np.ndarray) -> Dict[str, Any]:
        """
        Analyze detailed semantic flow patterns
        """
        if len(embeddings) < 3:
            return {'flow_uniformity': 0.5, 'transitions': []}
        
        # Calculate consecutive similarities
        consecutive_similarities = []
        transitions = []
        
        for i in range(len(embeddings) - 1):
            similarity = cosine_similarity(
                embeddings[i].reshape(1, -1),
                embeddings[i + 1].reshape(1, -1)
            )[0, 0]
            consecutive_similarities.append(similarity)
            
            # Identify notable transitions
            if similarity > 0.8:  # Very similar consecutive sentences
                transitions.append({
                    'type': 'high_similarity_transition',
                    'from_sentence': i,
                    'to_sentence': i + 1,
                    'similarity': float(similarity),
                    'evidence': f'Transition between sentences {i+1} and {i+2} shows unusual semantic similarity ({similarity:.2f})',
                    'ai_likelihood': float(similarity)
                })
            elif similarity < 0.3:  # Very different consecutive sentences
                transitions.append({
                    'type': 'low_similarity_transition',
                    'from_sentence': i,
                    'to_sentence': i + 1,
                    'similarity': float(similarity),
                    'evidence': f'Abrupt semantic shift between sentences {i+1} and {i+2} ({similarity:.2f})',
                    'ai_likelihood': 0.6  # Abrupt changes can also indicate AI
                })
        
        # Calculate flow uniformity
        if consecutive_similarities:
            flow_std = np.std(consecutive_similarities)
            flow_uniformity = 1.0 - min(1.0, flow_std * 3)  # Lower std = higher uniformity
        else:
            flow_uniformity = 0.5
        
        # Sort transitions by AI likelihood
        transitions.sort(key=lambda x: x['ai_likelihood'], reverse=True)
        
        return {
            'flow_uniformity': float(flow_uniformity),
            'transitions': transitions[:5],  # Top 5 transitions
            'avg_consecutive_similarity': float(np.mean(consecutive_similarities)) if consecutive_similarities else 0.5
        }
    
    def _identify_topic_clusters(self, sentences: List[str], embeddings: np.ndarray) -> List[Dict[str, Any]]:
        """
        Identify topic clusters in the text
        """
        if len(embeddings) < 3:
            return []
        
        # Use simple clustering based on similarity threshold
        clusters = []
        used_sentences = set()
        
        for i in range(len(sentences)):
            if i in used_sentences:
                continue
                
            # Find similar sentences
            cluster_sentences = [i]
            cluster_similarities = []
            
            for j in range(i + 1, len(sentences)):
                if j in used_sentences:
                    continue
                    
                similarity = cosine_similarity(
                    embeddings[i].reshape(1, -1),
                    embeddings[j].reshape(1, -1)
                )[0, 0]
                
                if similarity > 0.7:  # Similarity threshold for clustering
                    cluster_sentences.append(j)
                    cluster_similarities.append(similarity)
                    used_sentences.add(j)
            
            if len(cluster_sentences) > 1:  # Only include multi-sentence clusters
                avg_similarity = np.mean(cluster_similarities) if cluster_similarities else 0.0
                
                cluster = {
                    'id': f'cluster_{len(clusters) + 1}',
                    'sentence_indices': cluster_sentences,
                    'sentences': [sentences[idx] for idx in cluster_sentences],
                    'avg_similarity': float(avg_similarity),
                    'size': len(cluster_sentences),
                    'evidence': f'Topic cluster of {len(cluster_sentences)} sentences with high semantic similarity ({avg_similarity:.2f})',
                    'ai_likelihood': float(min(1.0, avg_similarity * 1.1))
                }
                clusters.append(cluster)
                
                # Mark sentences as used
                for idx in cluster_sentences:
                    used_sentences.add(idx)
        
        # Sort by AI likelihood
        clusters.sort(key=lambda x: x['ai_likelihood'], reverse=True)
        return clusters[:3]  # Top 3 clusters
    
    def _find_semantic_repetitions(self, sentences: List[str], embeddings: np.ndarray) -> List[Dict[str, Any]]:
        """
        Find semantic repetitions (similar meaning expressed differently)
        """
        repetitions = []
        
        if len(embeddings) < 3:
            return repetitions
        
        # Find non-consecutive sentences with high similarity
        for i in range(len(sentences)):
            for j in range(i + 2, len(sentences)):  # Skip adjacent sentences
                similarity = cosine_similarity(
                    embeddings[i].reshape(1, -1),
                    embeddings[j].reshape(1, -1)
                )[0, 0]
                
                if similarity > 0.8:  # High similarity threshold
                    repetition = {
                        'sentence_1_index': i,
                        'sentence_2_index': j,
                        'sentence_1': sentences[i],
                        'sentence_2': sentences[j],
                        'similarity': float(similarity),
                        'evidence': f'Sentences {i+1} and {j+1} express very similar ideas ({similarity:.2f} similarity)',
                        'ai_likelihood': float(similarity)
                    }
                    repetitions.append(repetition)
        
        # Sort by similarity and return top 5
        repetitions.sort(key=lambda x: x['similarity'], reverse=True)
        return repetitions[:5]
    
    def _calculate_semantic_summary(self, coherence_patterns: List[Dict], flow_analysis: Dict, 
                                   topic_clusters: List[Dict], repetition_evidence: List[Dict]) -> Dict[str, Any]:
        """
        Calculate overall semantic analysis summary
        """
        # Calculate overall coherence score
        if coherence_patterns:
            avg_coherence = np.mean([p['coherence_score'] for p in coherence_patterns])
        else:
            avg_coherence = 0.5
        
        # Calculate AI likelihood based on all evidence
        ai_indicators = []
        
        # High coherence patterns
        if coherence_patterns:
            ai_indicators.append(np.mean([p['ai_likelihood'] for p in coherence_patterns]))
        
        # Flow uniformity (high uniformity = AI-like)
        ai_indicators.append(flow_analysis.get('flow_uniformity', 0.5))
        
        # Topic clustering (many clusters = AI-like organization)
        if topic_clusters:
            cluster_score = min(1.0, len(topic_clusters) * 0.3 + np.mean([c['ai_likelihood'] for c in topic_clusters]))
            ai_indicators.append(cluster_score)
        
        # Semantic repetitions
        if repetition_evidence:
            repetition_score = min(1.0, len(repetition_evidence) * 0.2 + np.mean([r['ai_likelihood'] for r in repetition_evidence]))
            ai_indicators.append(repetition_score)
        
        # Calculate overall AI likelihood
        if ai_indicators:
            overall_ai_likelihood = np.mean(ai_indicators)
        else:
            overall_ai_likelihood = 0.5
        
        # Determine confidence level
        evidence_count = len(coherence_patterns) + len(topic_clusters) + len(repetition_evidence)
        if evidence_count >= 5:
            confidence = 'high'
        elif evidence_count >= 2:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        return {
            'overall_coherence': float(avg_coherence),
            'ai_likelihood': float(overall_ai_likelihood),
            'analysis_confidence': confidence,
            'evidence_count': evidence_count,
            'primary_indicators': [
                'High semantic coherence' if any(p['coherence_score'] > 0.8 for p in coherence_patterns) else None,
                'Uniform flow patterns' if flow_analysis.get('flow_uniformity', 0) > 0.7 else None,
                'Topic clustering' if topic_clusters else None,
                'Semantic repetitions' if repetition_evidence else None
            ]
        }

# Global semantic analyzer instance
semantic_analyzer = SemanticAnalyzer()