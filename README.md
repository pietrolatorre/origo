# Origo - Advanced AI Text Detection Platform

Origo is a sophisticated web application that analyzes English text to detect signals of **human-written vs AI-generated content** using a comprehensive **7-dimension analysis framework**. Each dimension produces normalized scores (0-1) with detailed evidence and explanations.

## 🎯 What It Does

Origo provides **explainable AI detection** through multi-dimensional analysis:
- **Global Score**: Weighted average of active dimensions
- **Dimension-Specific Analysis**: 7 specialized detection methods
- **Evidence-Based Results**: Top 10 evidences per dimension with detailed reasoning
- **Configurable Analysis**: Toggle dimensions and adjust weights as needed

## ✨ Key Features

### Advanced Analysis Framework
- **7-Dimension Detection**: Perplexity, Burstiness, Semantic Coherence, N-gram Repetition, Lexical Richness, Stylistic Markers, Readability
- **Multi-Level Processing**: Sentence → Paragraph → Global aggregation
- **Real Aggregation**: Weighted scoring with coefficient of variation and statistical measures
- **Evidence Generation**: Detailed explanations with text highlighting and reasoning

### User Experience
- **Interactive Dimension Grid**: 7×1 layout with toggles and weight visualization
- **Dimension-Based Tabs**: Dedicated tab for each analysis dimension
- **Color-Coded Results**: Green (natural) → Yellow (moderate) → Red (suspicious)
- **Real-Time Analysis**: Fast processing with immediate visual feedback

### Export & Documentation
- **PDF Export**: Complete analysis reports with all evidences
- **Evidence Limiting**: Top 10 shown in UI, full results in export
- **Detailed Tooltips**: Hover explanations for all metrics

## 📊 7-Dimension Analysis Framework

### 1. **Perplexity** (Sentence Level)
- **Goal**: Detect statistical likelihood using language model patterns
- **Method**: Next-word probability analysis
- **Interpretation**: Low = natural, High = artificial

### 2. **Burstiness** (Paragraph Level)
- **Goal**: Measure variability in sentence lengths
- **Method**: Coefficient of Variation (σ/μ) calculation
- **Interpretation**: Very low = monotonous, Very high = unnatural

### 3. **Semantic Coherence** (Paragraph Level)
- **Goal**: Analyze logical flow between text segments
- **Method**: Sentence-BERT embeddings + cosine similarity
- **Interpretation**: High = coherent flow, Low = abrupt shifts

### 4. **N-gram Repetition** (Global Level)
- **Goal**: Detect unusual word sequence repetition
- **Method**: Bigram/trigram frequency analysis + diversity index
- **Interpretation**: High repetition = suspicious artificiality

### 5. **Lexical Richness** (Sentence Level)
- **Goal**: Measure vocabulary variety
- **Method**: Type-Token Ratio (unique words / total words)
- **Interpretation**: Low = repetitive, High = rich vocabulary

### 6. **Stylistic Markers** (Sentence Level)
- **Goal**: Identify unusual stylistic patterns
- **Method**: Punctuation frequency + POS tag analysis
- **Interpretation**: Deviations = possible artificial generation

### 7. **Readability** (Sentence Level)
- **Goal**: Measure natural text complexity
- **Method**: Flesch Reading Ease + complexity metrics
- **Interpretation**: Very high = too simple, Very low = too complex

## 🚀 Quick Start with Docker

```bash
# Clone the repository
git clone <repository-url>
cd origo

# Start the application
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 💻 Development Setup

### Prerequisites
- Node.js 18+ (Frontend)
- Python 3.11+ (Backend)
- Docker & Docker Compose (recommended)

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📈 API Response Format

The new 7-dimension API returns comprehensive analysis results:

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
          "reason": "High predictability suggesting potential AI generation (12 words)"
        }
      ]
    }
  },
  "weights_applied": {
    "perplexity": 0.143,
    "burstiness": 0.143,
    "semantic_coherence": 0.143,
    "ngram_repetition": 0.143,
    "lexical_richness": 0.143,
    "stylistic_markers": 0.143,
    "readability": 0.142
  },
  "active_dimensions": ["perplexity", "burstiness", "semantic_coherence", "ngram_repetition", "lexical_richness", "stylistic_markers", "readability"],
  "analysis_metadata": {
    "text_length": 1247,
    "word_count": 198,
    "sentence_count": 12,
    "paragraph_count": 3,
    "processing_time_seconds": 1.23,
    "weights_used": {...},
    "enhanced_features_enabled": {
      "stylistic_analysis": true,
      "structural_analysis": true
    }
  }
}
```

## 🎨 User Interface

### Main Screen
- **7×1 Dimension Grid**: Each row shows dimension name, description, score, weight, and toggle
- **Global Score Display**: Large prominent percentage with color coding
- **Statistics Banner**: Horizontal layout with key metrics

### Analysis Results
- **Overview Tab**: Global score, statistics, and dimension summary
- **7 Dimension Tabs**: Individual tabs for each analysis dimension
- **Evidence Display**: Top 10 evidences per dimension with highlighting
- **Color Coding**: Green (0-30%), Yellow (30-60%), Red (60-100%)

### Interaction Features
- **Dimension Toggles**: Enable/disable analysis dimensions
- **Evidence Inspection**: Click to see detailed reasoning
- **PDF Export**: Generate comprehensive reports
- **Responsive Design**: Works on desktop and mobile

## 🔧 Technical Architecture

### Backend (Python + FastAPI)
- **Analysis Coordinator**: Orchestrates all 7 analyzers
- **Base Analyzer**: Abstract class for dimension-specific analysis
- **Real Aggregation**: Weighted scoring with proper normalization
- **Evidence Generation**: Detailed explanations for each detection
- **PDF Generation**: Complete report export with ReportLab

### Frontend (React + TypeScript + Vite)
- **Component Architecture**: Modular design with typed interfaces
- **State Management**: React hooks for dimension toggles and results
- **Real-time Updates**: Immediate feedback during analysis
- **Responsive UI**: CSS Grid for optimal layout

### Current Implementation Status
- ✅ **7-Dimension Framework**: Complete architecture implemented
- ✅ **Simulated Calculations**: All analyzers provide realistic simulated results
- ✅ **Real Aggregation**: Weighted scoring and evidence generation
- ✅ **UI Complete**: Full frontend with dimension tabs and toggles
- ⏳ **Real AI Models**: Currently simulated, ready for model integration

## ⚠️ Ethical Use & Limitations

**Important**: AI detection is probabilistic, not definitive. This tool provides signals to support human judgment, not replace it.

- Use results as **guidance**, not absolute truth
- Always apply **human review** for important decisions
- Consider **context** and **purpose** of the text
- Respect **privacy** and **consent** when analyzing others' work

## 📄 License

This project is licensed under the MIT License.

---

*For detailed technical specifications, see [text_analysis_spec_v2.md](./text_analysis_spec_v2.md)*
