
# Text Analysis Application – Specification (v2)

## Overview
The application analyzes English text to detect signals of **human-written vs AI-generated content**.  
It evaluates the text across **7 analysis dimensions**, each producing a normalized score (0–1).  
A **global score** is calculated as a weighted average of active dimensions.  

The system must be:
- **Configurable** (frontend toggle per dimension).  
- **Efficient** (backend parallelizes calculations at sentence level where possible).  
- **Explainable** (frontend shows global score, per-dimension scores, and top evidences).  
- **Exportable** (backend calculates full results for PDF export, frontend shows only top N).  

---

## Dimensions of Analysis

### 1. Perplexity
- **Goal:** Detect statistical likelihood of text under an LLM.  
- **Atomic level:** Sentence (predict next word probability).  
- **Aggregation:**  
  - Paragraph: `max(sentence perplexity)`  
  - Global: `mean(paragraph perplexity)`  
- **Score interpretation:**  
  - Low = more natural, High = more likely artificial.  
- **Evidences (Top 10):** Sentences with highest perplexity.  

---

### 2. Burstiness
- **Goal:** Measure variability in sentence lengths within paragraphs.  
- **Atomic level:** Sentence length (tokens).  
- **Formula per paragraph:**  
  - Compute array `L = [len(sentence1), len(sentence2), ...]`  
  - Mean `μ = mean(L)`  
  - Std Dev `σ = std(L)`  
  - Burstiness = `σ / μ` (Coefficient of Variation).  
- **Aggregation:**  
  - Global: mean of paragraph burstiness.  
- **Score interpretation:**  
  - Very low = monotonous, Very high = unnatural oscillation.  
- **Evidences (Top 10):** Paragraphs with extreme burstiness (too flat or too irregular).  

---

### 3. Semantic Coherence
- **Goal:** Measure logical flow between text segments.  
- **Atomic level:** Paragraph embeddings (Sentence-BERT).  
- **Formula:**  
  - For each adjacent pair `(pi, pi+1)` compute cosine similarity.  
  - Paragraph coherence = mean of similarities inside the paragraph.  
  - Global coherence = mean of similarities across all paragraphs.  
- **Score interpretation:**  
  - High = coherent flow, Low = abrupt topic shifts.  
- **Evidences (Top 10):** Pairs of paragraphs with lowest similarity.  

---

### 4. N-gram Repetition
- **Goal:** Detect unusual repetition of word sequences.  
- **Atomic level:** Entire text.  
- **Metrics:**  
  - Repetition rate = `#repeated n-grams / #total n-grams`  
  - Diversity index (Type/Token ratio).  
  - Entropy of n-gram frequency distribution.  
- **Aggregation:** Already global (no paragraph/sentence).  
- **Score interpretation:**  
  - High repetition = suspicious of artificiality.  
- **Evidences (Top 10):** Most frequent repeated n-grams.  

---

### 5. Lexical Richness (Alternative Dimension 1)
- **Goal:** Measure vocabulary variety.  
- **Atomic level:** Sentence → vocabulary set.  
- **Formula:**  
  - Type-Token Ratio = `unique_words / total_words`.  
- **Aggregation:**  
  - Paragraph = mean of sentence TTR.  
  - Global = mean of paragraph TTR.  
- **Score interpretation:**  
  - Low = repetitive / poor vocabulary, High = rich.  
- **Evidences (Top 10):** Sentences with lowest lexical richness.  

---

### 6. Stylistic Markers (Alternative Dimension 2)
- **Goal:** Identify unusual stylistic patterns.  
- **Atomic level:** Sentence.  
- **Metrics:**  
  - Punctuation frequency (commas, semicolons, exclamation marks).  
  - POS tag distribution consistency.  
  - Use of stopwords vs content words ratio.  
- **Aggregation:**  
  - Paragraph = mean stylistic variance of sentences.  
  - Global = mean across paragraphs.  
- **Score interpretation:**  
  - Deviations from balanced style = possible artificial generation.  
- **Evidences (Top 10):** Sentences with extreme stylistic anomalies.  

---

### 7. Readability (Alternative Dimension 3)
- **Goal:** Measure natural readability of the text.  
- **Atomic level:** Sentence length + syllables.  
- **Formula (example):** Flesch Reading Ease.  
- **Aggregation:**  
  - Paragraph = mean of sentence readability.  
  - Global = mean of paragraph readability.  
- **Score interpretation:**  
  - Very high = too simplistic, Very low = too complex.  
- **Evidences (Top 10):** Sentences with lowest readability.  

---

## Backend Processing

### Input
- Raw text.  
- List of active dimensions (toggles from UI).  

### Processing Strategy
- Preprocess text once: tokenize → sentences → paragraphs.  
- In parallel: run all dimension-specific computations on tokens/sentences.  
- Disabled dimensions are skipped.  
- Active weights are rebalanced:  
  - If 5/7 dimensions active, global score = weighted mean over 5.  

### Output
- Global score.  
- Per-dimension score (with applied weight).  
- Top evidences (limited for frontend).  
- Full detailed results (for PDF export).  

---

## Frontend Specification

### Main Screen
- Column layout (7×1 grid).  
- Each row = dimension with:  
  - Name  
  - Short description  
  - Score (0–1)  
  - Weight used  
  - Toggle (active/inactive)  

### Tabs
- One tab per dimension.  
- Inside each tab:  
  - Top 10 evidences (sentences/paragraphs/n-grams).  
  - Highlighted with color scale (green–yellow–red).  
  - Long elements truncated (`first 200 chars ...`).  

### Export
- PDF includes **all evidences**, not only top 10.  

---

## Color Coding
- **Green:** Score within natural range.  
- **Yellow:** Moderate suspicion.  
- **Red:** High suspicion of artificiality.  

---

## Implementation Plan
1. **Frontend refactor**:  
   - Replace old tabs with dimension-based tabs.  
   - Add toggles + weight visualization.  
2. **Backend refactor**:  
   - Efficient preprocessing (single pass over text).  
   - Modular dimension calculators.  
   - Parallel execution per sentence where possible.  
3. **Scoring & weights**:  
   - Normalize all scores 0–1.  
   - Apply active weights only.  
4. **UI evidence integration**:  
   - Limit to top 10 for view.  
   - Expand full results in PDF export.  
