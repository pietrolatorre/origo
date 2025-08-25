# Modifiche da implementare

lista non esaustiva da prendere come base e da estendere in base all'efficacia dell'implementazione.
Tradurre tutto in inglese dove necessario. Mantenere stabile l'attuale implementazione.

## 1. Sistema Target

**Dimensioni** (tutte alla pari):
1. `perplexity`: Complessità linguistica + pattern stilistici + autenticità registro
2. `burstiness`: Variabilità frasi + consistenza strutturale  
3. `semantic_coherence`: Coerenza semantica (invariata)
4. `ngram_similarity`: Pattern n-gram (invariata)

**Score globale**: Media aritmetica semplice delle dimensioni

## 2. Regole Implementazione

### R1. Estensione Implementazioni Esistenti
- Identificare classi attuali che implementano le 4 dimensioni esistenti
- Estendere le classi esistenti (non sostituire) con nuovi sub-componenti:
  - perplexity: aggiungere analisi stylistic patterns + register authenticity
  - burstiness: aggiungere analisi structural consistency
- Ogni classe estesa calcola score finale come weighted average dei suoi componenti

### R3. Separazione Dati/Implementazione
```
data/
├─ perplexity/
│   ├─ llm_red_flags.json          # Red flag da conversazione iniziale
│   ├─ punctuation_patterns.json   # Pattern punteggiatura sospetta
│   └─ register_authenticity.json  # Marker naturalezza registro
├─ burstiness/
│   └─ structural_patterns.json    # Pattern consistenza strutturale
└─ weights_config.json
```

### R8. Implementazione Componenti Aggiuntivi

**Stylistic Patterns** :
- Red flag vocabulary da `llm_red_flags.json` (verbi: delve, hinge, lurk, etc.)
- Punctuation analysis da `punctuation_patterns.json` (Oxford comma, em dash abuse, etc.)
- Formulaic expressions (firstly...secondly, thought-provoking, etc.)

**Register Authenticity**:
- Formality consistency analysis
- Emotional variance detection da `register_authenticity.json`
- Naturalezza espressioni idiomatiche

**Structural Consistency** :
- Paragraph length uniformity detection
- Sentence structure symmetry da `structural_patterns.json`
- Pattern transizioni meccaniche

### R10. Deployment e Migration
- **Zero breaking changes**: API mantiene stesso endpoint
- **Gradual rollout**: Feature flag per abilitare nuove dimensioni
- **Performance monitoring**: Log latency per dimension_5 separatamente
- **Rollback strategy**: Disabilitazione rapida dimension_5 se problemi

## 6. Checklist Implementazione

### 5.1 llm_red_flags.json
```json
{
  "suspicious_verbs": [
    "delve", "hinge", "lurk", "underscore", "foster", "leverage", 
    "encompass", "epitomize", "bolster", "transcend", "unpack"
  ],
  "suspicious_modifiers": [
    "thought-provoking", "nuanced", "multifaceted", "pivotal", 
    "crucial", "critical", "seamless", "seamlessly", "robust", 
    "comprehensive", "intricate", "profound", "profoundly", 
    "compelling", "unprecedented"
  ],
  "suspicious_nouns": [
    "landscape", "realm", "tapestry", "paradigm", "facet", 
    "nuance", "intricacies", "ramifications", "implications"
  ],
  "formulaic_phrases": [
    "it's worth noting that",
    "it's important to (?:recognize|understand) that",
    "as we delve deeper",
    "in today's .+ (?:world|landscape)",
    "it's no secret that",
    "there's no denying that",
    "it goes without saying that",
    "needless to say",
    "as we (?:all )?know",
    "in essence",
    "at its core",
    "the bottom line is",
    "when all is said and done",
    "in the grand scheme of things",
    "that said",
    "with that in mind",
    "at the end of the day"
  ],
  "transition_constructs": [
    "firstly.+secondly.+(?:thirdly.+)?finally",
    "on one hand.+on the other hand",
    "moreover.+furthermore.+additionally",
    "in recent years.+(?:looking ahead|as we move forward)"
  ],
  "weights": {
    "verbs": 2.0,
    "modifiers": 1.5,
    "nouns": 1.5,
    "formulaic_phrases": 3.0,
    "transition_constructs": 4.0
  }
}
```

### 5.2 punctuation_patterns.json
```json
{
  "patterns": {
    "oxford_comma": {
      "regex": ", (?:and|or) ",
      "threshold_per_1000_words": 20,
      "weight": 2.0
    },
    "em_dash_abuse": {
      "regex": "—",
      "threshold_per_1000_words": 3,
      "weight": 2.5
    },
    "bullet_points_with_periods": {
      "regex": "^\\s*[\\•\\-\\*]\\s*.+\\.\\s*$",
      "multiline": true,
      "weight": 3.0
    },
    "excessive_colons": {
      "char": ":",
      "threshold_per_1000_words": 10,
      "weight": 1.5
    },
    "parenthetical_clarifications": {
      "regex": "\\([ie]\\.g\\.,",
      "weight": 2.0
    }
  }
}
```

### 5.3 register_authenticity.json
```json
{
  "formality_inconsistencies": {
    "excessive_contractions": ["it's", "that's", "we'll", "they'll"],
    "overly_formal_phrases": [
      "one must consider",
      "it is imperative that",
      "furthermore, it should be noted"
    ],
    "mixed_register_markers": {
      "casual": ["kinda", "sorta", "basically", "actually"],
      "academic": ["henceforth", "aforementioned", "subsequent"]
    }
  },
  "emotional_variance_markers": {
    "low_variance_indicators": [
      "consistently neutral tone",
      "lack of personal opinion markers",
      "absence of emotional adjectives"
    ],
    "high_variance_expected": [
      "personal anecdotes",
      "opinion markers",
      "emotional responses"
    ]
  },
  "naturalness_patterns": {
    "unnatural_constructions": [
      "as we navigate",
      "it behooves us to",
      "in the realm of"
    ],
    "natural_constructions": [
      "honestly",
      "frankly",
      "to be fair"
    ]
  }
}
```

### 5.4 structural_patterns.json
```json
{
  "uniformity_detectors": {
    "paragraph_length": {
      "variance_threshold": 0.1,
      "suspicious_consistency": 0.05,
      "weight": 2.0
    },
    "sentence_symmetry": {
      "patterns": [
        "parallel_structure_excess",
        "repeated_sentence_starters",
        "mechanical_transitions"
      ],
      "weight": 2.5
    },
    "section_balance": {
      "intro_body_conclusion_ratio": [0.15, 0.70, 0.15],
      "tolerance": 0.05,
      "weight": 1.5
    }
  },
  "mechanical_patterns": {
    "transition_phrases": [
      "Moreover,",
      "Furthermore,",
      "Additionally,",
      "In addition,",
      "Nevertheless,",
      "Consequently,"
    ],
    "list_structures": [
      "Three-point lists",
      "Balanced subdivisions",
      "Systematic enumeration"
    ]
  }
}
```

### Configuration & Data
- [ ] Creare `llm_red_flags.json` con tutti i red flag identificati (verbi, aggettivi, frasi, pattern)
- [ ] Creare `punctuation_patterns.json` con pattern punteggiatura sospetta
- [ ] Creare `register_authenticity.json` con marker naturalezza linguistica
- [ ] Creare `structural_patterns.json` con pattern uniformità strutturale

### 6.4 Documentation
- [ ] Aggiornare README.md