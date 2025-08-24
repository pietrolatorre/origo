"""
Sentence Splitter Utility for Origo
Handles text preprocessing, tokenization, and sentence segmentation
"""

import re
import logging
from typing import List, Dict, Any
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentenceSplitter:
    """
    Utility class for text preprocessing and sentence segmentation
    """
    
    def __init__(self):
        # Download required NLTK data
        self._download_nltk_data()
        self.stop_words = set(stopwords.words('english'))
    
    def _download_nltk_data(self):
        """Download necessary NLTK data if not already present"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            logger.info("Downloading NLTK punkt tokenizer...")
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            logger.info("Downloading NLTK stopwords...")
            nltk.download('stopwords')
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize input text
        Args:
            text: Raw input text
        Returns:
            Cleaned text string
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remove excessive whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove or normalize special characters while preserving punctuation
        text = re.sub(r'[^\w\s\.\!\?\;\:\,\-\'\"]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into individual sentences
        Args:
            text: Input text to split
        Returns:
            List of sentence strings
        """
        if not text:
            return []
        
        # Clean text first
        clean_text = self.clean_text(text)
        
        # Use NLTK sentence tokenizer
        sentences = sent_tokenize(clean_text)
        
        # Filter out very short sentences (likely artifacts)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
        
        return sentences
    
    def split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs based on double newlines
        Args:
            text: Input text to split
        Returns:
            List of paragraph strings
        """
        if not text:
            return []
        
        # Split on double newlines or more
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Clean and filter paragraphs
        paragraphs = [self.clean_text(p) for p in paragraphs if p.strip()]
        paragraphs = [p for p in paragraphs if len(p) > 10]  # Filter very short paragraphs
        
        return paragraphs
    
    def tokenize_words(self, text: str, remove_stopwords: bool = False) -> List[str]:
        """
        Tokenize text into individual words
        Args:
            text: Input text to tokenize
            remove_stopwords: Whether to remove common English stopwords
        Returns:
            List of word tokens
        """
        if not text:
            return []
        
        # Tokenize into words
        words = word_tokenize(text.lower())
        
        # Remove punctuation-only tokens
        words = [w for w in words if re.match(r'.*[a-zA-Z].*', w)]
        
        # Remove stopwords if requested
        if remove_stopwords:
            words = [w for w in words if w not in self.stop_words]
        
        return words
    
    def extract_word_positions(self, text: str, target_words: List[str]) -> Dict[str, List[int]]:
        """
        Find positions of specific words in text for highlighting
        Args:
            text: Source text
            target_words: List of words to find positions for
        Returns:
            Dictionary mapping words to their character positions
        """
        positions = {}
        
        for word in target_words:
            word_positions = []
            # Find all occurrences of the word (case-insensitive)
            pattern = r'\b' + re.escape(word) + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                word_positions.append({
                    'start': match.start(),
                    'end': match.end(),
                    'word': match.group()
                })
            
            if word_positions:
                positions[word] = word_positions
        
        return positions
    
    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """
        Calculate basic text statistics
        Args:
            text: Input text to analyze
        Returns:
            Dictionary with text statistics
        """
        if not text:
            return {}
        
        sentences = self.split_into_sentences(text)
        words = self.tokenize_words(text)
        
        stats = {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_words_per_sentence': len(words) / len(sentences) if sentences else 0,
            'avg_chars_per_word': sum(len(w) for w in words) / len(words) if words else 0,
            'unique_word_count': len(set(words)),
            'lexical_diversity': len(set(words)) / len(words) if words else 0
        }
        
        return stats

# Global sentence splitter instance
sentence_splitter = SentenceSplitter()