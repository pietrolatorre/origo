"""
Model Loader Utility for Origo
Loads and manages AI models efficiently with singleton pattern to avoid repeated loading
"""

import logging
from typing import Dict, Any, Optional, Tuple, Union

# Try importing AI libraries - fall back to None if not available (simulation mode)
try:
    from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPT2Config, pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    GPT2LMHeadModel = None
    GPT2Tokenizer = None
    GPT2Config = None
    pipeline = None

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    SentenceTransformer = None

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None

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
    
    def get_gpt2_model(self) -> Optional[Tuple[Any, Any]]:
        """
        Load GPT-2 model and tokenizer for perplexity calculation
        Returns: (model, tokenizer) tuple or None if in simulation mode
        """
        if not HAS_TRANSFORMERS:
            logger.info("GPT-2 model not available - running in simulation mode")
            return None
            
        if 'gpt2' not in self._models:
            logger.info("Loading GPT-2 model for perplexity analysis...")
            try:
                # Load model with explicit configuration to suppress warnings
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
    
    def get_sentence_transformer(self) -> Optional[Any]:
        """
        Load Sentence-BERT model for semantic analysis
        Returns: SentenceTransformer model or None if in simulation mode
        """
        if not HAS_SENTENCE_TRANSFORMERS:
            logger.info("Sentence-BERT model not available - running in simulation mode")
            return None
            
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
            if HAS_TORCH and torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
            self._models['device'] = device
            logger.info(f"Using device: {device}")
        
        return self._models['device']
    
    def preload_all_models(self):
        """
        Preload all models for faster initial requests
        Should be called during application startup
        """
        logger.info("Preloading all available models...")
        
        if HAS_TRANSFORMERS or HAS_SENTENCE_TRANSFORMERS:
            self.get_gpt2_model()
            self.get_sentence_transformer()
            logger.info("AI models preloaded successfully")
        else:
            logger.info("Running in simulation mode - no AI models to preload")
            
        self.get_device()
        logger.info("Model loading completed")
    
    def is_simulation_mode(self) -> bool:
        """
        Check if running in simulation mode (no AI libraries available)
        Returns: True if in simulation mode, False if real models available
        """
        return not (HAS_TRANSFORMERS and HAS_SENTENCE_TRANSFORMERS and HAS_TORCH)
    
    def get_available_features(self) -> Dict[str, bool]:
        """
        Get information about which AI libraries are available
        Returns: Dictionary with availability status
        """
        return {
            "transformers": HAS_TRANSFORMERS,
            "sentence_transformers": HAS_SENTENCE_TRANSFORMERS,
            "torch": HAS_TORCH,
            "simulation_mode": self.is_simulation_mode()
        }

# Global model loader instance
model_loader = ModelLoader()