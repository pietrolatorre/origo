"""
Model Loader Utility for Origo
Loads and manages AI models efficiently with singleton pattern to avoid repeated loading
"""

import logging
from typing import Dict, Any
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPT2Config, pipeline
from sentence_transformers import SentenceTransformer
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelLoader:
    """
    Singleton class to load and manage AI models
    Ensures models are loaded only once for efficiency
    """
    
    _instance = None
    _models = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            logger.info("Initializing ModelLoader singleton")
    
    def get_gpt2_model(self) -> tuple:
        """
        Load GPT-2 model and tokenizer for perplexity calculation
        Returns: (model, tokenizer) tuple
        """
        if 'gpt2' not in self._models:
            logger.info("Loading GPT-2 model for perplexity analysis...")
            try:
                # Load model with explicit configuration to suppress warnings
                from transformers import GPT2Config
                config = GPT2Config.from_pretrained('gpt2')
                # Explicitly set loss_type to avoid warnings
                if hasattr(config, 'loss_type'):
                    config.loss_type = None
                
                model = GPT2LMHeadModel.from_pretrained('gpt2', config=config)
                tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
                
                # Add padding token if not present
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                
                # Set model to evaluation mode
                model.eval()
                
                self._models['gpt2'] = (model, tokenizer)
                logger.info("GPT-2 model loaded successfully")
                
            except Exception as e:
                logger.error(f"Error loading GPT-2 model: {e}")
                raise
        
        return self._models['gpt2']
    
    def get_sentence_transformer(self) -> SentenceTransformer:
        """
        Load Sentence-BERT model for semantic analysis
        Returns: SentenceTransformer model
        """
        if 'sentence_bert' not in self._models:
            logger.info("Loading Sentence-BERT model for semantic analysis...")
            try:
                model = SentenceTransformer('all-MiniLM-L6-v2')
                self._models['sentence_bert'] = model
                logger.info("Sentence-BERT model loaded successfully")
                
            except Exception as e:
                logger.error(f"Error loading Sentence-BERT model: {e}")
                raise
        
        return self._models['sentence_bert']
    
    def get_device(self) -> str:
        """
        Get the appropriate device (CPU/GPU) for model inference
        Returns: device string ('cuda' or 'cpu')
        """
        if 'device' not in self._models:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self._models['device'] = device
            logger.info(f"Using device: {device}")
        
        return self._models['device']
    
    def preload_all_models(self):
        """
        Preload all models for faster initial requests
        Should be called during application startup
        """
        logger.info("Preloading all models...")
        self.get_gpt2_model()
        self.get_sentence_transformer()
        self.get_device()
        logger.info("All models preloaded successfully")

# Global model loader instance
model_loader = ModelLoader()