# Origo Backend API Documentation

## Overview

The Origo Backend API provides advanced AI text detection through a comprehensive **7-dimension analysis framework**. This RESTful API is built with FastAPI and designed for seamless integration with frontend applications while supporting future extensions and real AI model implementations.

## 🎯 Core Features

- **7-Dimension Analysis Framework**: Comprehensive AI detection through multiple specialized analyzers
- **Weighted Scoring System**: Configurable dimension weights with automatic rebalancing  
- **Evidence-Based Results**: Detailed explanations with top 10 evidences per dimension
- **Real-Time Processing**: Fast analysis with < 5 second response times
- **TypeScript Compatible**: JSON responses matching frontend interfaces exactly
- **Comprehensive Documentation**: Interactive API docs with OpenAPI/Swagger
- **Production Ready**: Comprehensive error handling and logging

## 📊 Analysis Dimensions

### 1. Perplexity Analysis (Sentence Level)
- **Purpose**: Detect statistical likelihood using language model patterns
- **Method**: Next-word probability analysis using GPT-2 models (simulated)
- **Interpretation**: Low = natural, High = artificial
- **Weight**: 0.143 (14.3%)

### 2. Burstiness Analysis (Paragraph Level)  
- **Purpose**: Measure variability in sentence lengths
- **Method**: Coefficient of Variation (σ/μ) calculation
- **Interpretation**: Very low = monotonous, Very high = unnatural
- **Weight**: 0.143 (14.3%)

### 3. Semantic Coherence (Paragraph Level)
- **Purpose**: Analyze logical flow between text segments
- **Method**: Sentence-BERT embeddings + cosine similarity (simulated)
- **Interpretation**: High = coherent flow, Low = abrupt shifts
- **Weight**: 0.143 (14.3%)

### 4. N-gram Repetition (Global Level)
- **Purpose**: Detect unusual word sequence repetition
- **Method**: Bigram/trigram frequency analysis + diversity index
- **Interpretation**: High repetition = suspicious artificiality  
- **Weight**: 0.143 (14.3%)

### 5. Lexical Richness (Sentence Level)
- **Purpose**: Measure vocabulary variety
- **Method**: Type-Token Ratio (unique words / total words)
- **Interpretation**: Low = repetitive, High = rich vocabulary
- **Weight**: 0.143 (14.3%)

### 6. Stylistic Markers (Sentence Level)
- **Purpose**: Identify unusual stylistic patterns
- **Method**: Punctuation frequency + POS tag analysis (simulated)
- **Interpretation**: Deviations = possible artificial generation
- **Weight**: 0.143 (14.3%)

### 7. Readability Analysis (Sentence Level)
- **Purpose**: Measure natural text complexity
- **Method**: Flesch Reading Ease + complexity metrics
- **Interpretation**: Very high = too simple, Very low = too complex
- **Weight**: 0.142 (14.2%)

## 🚀 API Endpoints

### Core Analysis

#### `POST /analyze`
**Primary text analysis endpoint**

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Your text to analyze here...",
       "enabled_dimensions": {
         "perplexity": true,
         "burstiness": true,
         "semantic_coherence": true,
         "ngram_repetition": true,
         "lexical_richness": true,
         "stylistic_markers": true,
         "readability": true
       }
     }'
```

**Request Format:**
```typescript
interface TextAnalysisRequest {
  text: string;                    // 10-50,000 characters
  enabled_dimensions?: {           // Optional dimension toggles
    perplexity: boolean;
    burstiness: boolean;
    semantic_coherence: boolean;
    ngram_repetition: boolean;
    lexical_richness: boolean;
    stylistic_markers: boolean;
    readability: boolean;
  };
}
```

**Response Format:**
```typescript
interface TextAnalysisResponse {
  overall_score: number;                    // 0.0-1.0 global AI score
  global_scores: GlobalScores;              // Individual dimension scores
  dimension_results: DimensionResults;      // Detailed analysis with evidences
  weights_applied: Record<string, number>;  // Actual weights used
  active_dimensions: string[];              // Enabled dimensions
  analysis_metadata: AnalysisMetadata;      // Processing statistics
  paragraphs: ParagraphAnalysis[];          // Future extension
  word_analysis: WordAnalysisResult;        // Future extension
}
```

### Health & Status

#### `GET /health`
**System health check**

```bash
curl "http://localhost:8000/health"
```

#### `GET /`
**API welcome and information**

```bash
curl "http://localhost:8000/"
```

#### `GET /api-info`
**Comprehensive framework documentation**

```bash
curl "http://localhost:8000/api-info"
```

### Export & Reporting

#### `POST /export-pdf`
**Generate comprehensive PDF reports**

```bash
curl -X POST "http://localhost:8000/export-pdf" \
     -H "Content-Type: application/json" \
     -d '{"overview": {...}, "dimensions": {...}}'
```

### Configuration

#### `GET /weights`
**Get current dimension weights**

```bash
curl "http://localhost:8000/weights"
```

#### `POST /weights`
**Update dimension weights (experimental)**

```bash
curl -X POST "http://localhost:8000/weights" \
     -H "Content-Type: application/json" \
     -d '{
       "perplexity": 0.2,
       "burstiness": 0.15,
       "semantic_coherence": 0.15,
       "ngram_repetition": 0.15,
       "lexical_richness": 0.15,
       "stylistic_markers": 0.1,
       "readability": 0.1
     }'
```

## 📋 Response Examples

### Successful Analysis Response
```json
{
  "overall_score": 0.68,
  "global_scores": {
    "perplexity": 0.72,
    "burstiness": 0.45,
    "semantic_coherence": 0.61,
    "ngram_repetition": 0.78,
    "lexical_richness": 0.52,
    "stylistic_markers": 0.69,
    "readability": 0.71
  },
  "dimension_results": {
    "perplexity": {
      "score": 0.72,
      "weight": 0.143,
      "active": true,
      "totalEvidences": 15,
      "topEvidences": [
        {
          "text": "This sentence shows high predictability patterns.",
          "score": 0.85,
          "startIndex": 0,
          "endIndex": 48,
          "type": "sentence",
          "reason": "High predictability suggesting potential AI generation"
        }
      ]
    }
  },
  "weights_applied": {
    "perplexity": 0.143,
    "burstiness": 0.143
  },
  "active_dimensions": ["perplexity", "burstiness"],
  "analysis_metadata": {
    "text_length": 500,
    "word_count": 87,
    "sentence_count": 5,
    "paragraph_count": 2,
    "processing_time_seconds": 1.234
  }
}
```

### Error Response
```json
{
  "detail": "Text must be at least 10 characters long for meaningful analysis",
  "status_code": 400
}
```

## 🔧 Implementation Architecture

### Directory Structure
```
backend/
├── main.py                     # FastAPI application and endpoints
├── analysis/                   # Analysis framework
│   ├── analysis_coordinator.py # Main orchestrator
│   ├── base_analyzer.py        # Abstract base class
│   ├── perplexity_analyzer.py  # Perplexity analysis
│   ├── burstiness_analyzer.py  # Burstiness analysis
│   ├── semantic_coherence_analyzer.py
│   ├── ngram_repetition_analyzer.py
│   ├── lexical_richness_analyzer.py
│   ├── stylistic_markers_analyzer.py
│   └── readability_analyzer.py
├── utils/                      # Utility modules
│   ├── model_loader.py         # AI model management
│   └── pdf_generator.py        # Report generation
└── requirements.txt            # Python dependencies
```

### Core Classes

#### `AnalysisCoordinator`
- **Purpose**: Orchestrates all 7 analysis dimensions
- **Key Methods**:
  - `analyze_text_comprehensive()`: Main analysis entry point
  - `calculate_overall_score()`: Weighted aggregation
  - `generate_analysis_metadata()`: Statistics generation

#### `BaseAnalyzer` (Abstract)
- **Purpose**: Foundation for all dimension analyzers
- **Key Methods**:
  - `analyze()`: Abstract analysis method
  - `get_dimension_name()`: Human-readable name
  - `get_description()`: Detailed description

#### Individual Analyzers
Each dimension has a dedicated analyzer inheriting from `BaseAnalyzer`:
- Implements dimension-specific analysis logic
- Returns `DimensionResult` with scores and evidences
- Supports both simulated and real AI model calculations

## 🛠️ Development & Extension

### Adding New Dimensions

1. **Create New Analyzer**
```python
from .base_analyzer import BaseAnalyzer, DimensionResult, AnalysisLevel

class NewDimensionAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__(
            analysis_level=AnalysisLevel.SENTENCE,
            default_weight=0.125  # Adjust weights accordingly
        )
    
    def analyze(self, text: str) -> DimensionResult:
        # Implement analysis logic
        pass
    
    def get_dimension_name(self) -> str:
        return "New Dimension"
    
    def get_description(self) -> str:
        return "Description of new analysis dimension"
```

2. **Register in AnalysisCoordinator**
```python
self.analyzers['new_dimension'] = NewDimensionAnalyzer()
self.default_weights['new_dimension'] = 0.125
```

3. **Update Response Models**
```python
class GlobalScores(BaseModel):
    # ... existing dimensions
    new_dimension: Optional[float] = None

class DimensionResults(BaseModel):
    # ... existing dimensions  
    new_dimension: Optional[DimensionAnalysisResult] = None
```

### Implementing Real AI Models

**Current State**: All analyzers use simulated calculations for development

**Implementation Path**:
1. Uncomment AI libraries in `requirements.txt`
2. Update `model_loader.py` to load real models
3. Replace simulated calculations in individual analyzers
4. Update Docker configuration for GPU support if needed

**Example Real Implementation**:
```python
def analyze(self, text: str) -> DimensionResult:
    # Replace simulated calculation
    from utils.model_loader import model_loader
    
    model = model_loader.get_model('gpt2')
    real_perplexity = calculate_real_perplexity(text, model)
    
    # Convert to 0-1 score and generate evidences
    return self._format_result(real_perplexity, text)
```

### Error Handling Best Practices

```python
try:
    result = analyzer.analyze(text)
except Exception as e:
    logger.error(f"Analysis failed for {dimension}: {e}")
    # Return default/fallback result
    return self._create_fallback_result()
```

### Logging Standards

```python
import logging

logger = logging.getLogger(__name__)

# Info: Normal operations
logger.info(f"Starting analysis for {len(text)} characters")

# Warning: Recoverable issues  
logger.warning(f"Dimension {dim} returned suspicious score: {score}")

# Error: Failures requiring attention
logger.error(f"Model loading failed: {e}", exc_info=True)
```

## 🧪 Testing

### Running Tests
```bash
# Unit tests for individual analyzers
python -m pytest tests/test_analyzers.py

# Integration tests for API endpoints
python -m pytest tests/test_api.py

# Performance tests
python -m pytest tests/test_performance.py
```

### Test Coverage
- Unit tests for each analyzer
- Integration tests for API endpoints  
- Performance benchmarks
- Error handling validation

## 🚀 Deployment

### Docker Deployment
```bash
# Build image
docker build -t origo-backend .

# Run container
docker run -p 8000:8000 origo-backend

# With environment variables
docker run -p 8000:8000 -e LOG_LEVEL=DEBUG origo-backend
```

### Environment Variables
```bash
# Optional configuration
LOG_LEVEL=INFO              # Logging level
MODEL_CACHE_SIZE=100        # Model cache size
ENABLE_METRICS=true         # Performance metrics
MAX_CONCURRENT_REQUESTS=10  # Request limiting
```

### Production Considerations
- **Scaling**: Use multiple workers with `uvicorn`
- **Monitoring**: Integrate with APM tools
- **Caching**: Redis for model and result caching
- **Rate Limiting**: Implement request throttling
- **Security**: Add authentication and input validation

## 🔍 Monitoring & Metrics

### Health Endpoints
- `/health`: Basic health check
- `/metrics`: Performance metrics (optional)
- `/status`: Detailed system status

### Key Metrics
- Request latency and throughput
- Analysis processing time per dimension
- Error rates and types
- Memory and CPU usage
- Model loading times

### Logging Structure
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO", 
  "message": "Analysis completed",
  "context": {
    "text_length": 500,
    "dimensions_active": 7,
    "processing_time": 1.234,
    "overall_score": 0.68
  }
}
```

## 📚 Additional Resources

- **Interactive API Docs**: `GET /docs` (Swagger UI)
- **ReDoc Documentation**: `GET /redoc` 
- **Framework Info**: `GET /api-info`
- **Frontend Integration**: See `frontend/src/services/api.ts`
- **Model Documentation**: See individual analyzer files

## 🤝 Contributing

### Code Standards
- Follow PEP 8 Python style guide
- Use type hints for all functions
- Include comprehensive docstrings
- Add unit tests for new features
- Update documentation for API changes

### Pull Request Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation
4. Ensure all tests pass
5. Submit PR with detailed description

### Issues & Support
- Report bugs via GitHub issues
- Feature requests welcome
- Include logs and reproduction steps
- Check existing issues before creating new ones