/**
 * AnalysisDimensions component for controlling which analysis dimensions to include
 * Now supports 7 dimensions with new grid layout
 */

import { DimensionCard } from './DimensionCard';
import type { AnalysisDimension, DimensionToggleSettings, DimensionResults } from '../types/analysis';

interface AnalysisDimensionsProps {
  dimensions: DimensionToggleSettings;
  results?: DimensionResults;
  onDimensionToggle: (dimensionId: keyof DimensionToggleSettings, enabled: boolean) => void;
  onDimensionClick?: (dimensionId: string) => void;
  showResults?: boolean;
}

// Default weights from backend configuration - all dimensions equal
const DEFAULT_WEIGHTS = {
  perplexity: 0.143,  // 1/7 ≈ 0.143
  burstiness: 0.143,
  semantic_coherence: 0.143,
  ngram_repetition: 0.143,
  lexical_richness: 0.143,
  stylistic_markers: 0.143,
  readability: 0.142   // slightly less to sum to 1.0
};

const ANALYSIS_DIMENSIONS: AnalysisDimension[] = [
  {
    id: 'perplexity',
    name: 'Perplexity',
    description: 'Analyzes text predictability using language model patterns to detect statistical likelihood',
    icon: 'Brain',
    enabled: true,
    weight: DEFAULT_WEIGHTS.perplexity,
    atomicLevel: 'sentence',
    scoreInterpretation: 'Low = more natural, High = more likely artificial'
  },
  {
    id: 'burstiness',
    name: 'Burstiness',
    description: 'Measures variability in sentence lengths within paragraphs using coefficient of variation',
    icon: 'Shuffle',
    enabled: true,
    weight: DEFAULT_WEIGHTS.burstiness,
    atomicLevel: 'paragraph',
    scoreInterpretation: 'Very low = monotonous, Very high = unnatural oscillation'
  },
  {
    id: 'semantic_coherence',
    name: 'Semantic Coherence',
    description: 'Evaluates logical flow between text segments using sentence embeddings and cosine similarity',
    icon: 'Network',
    enabled: true,
    weight: DEFAULT_WEIGHTS.semantic_coherence,
    atomicLevel: 'paragraph',
    scoreInterpretation: 'High = coherent flow, Low = abrupt topic shifts'
  },
  {
    id: 'ngram_repetition',
    name: 'N-gram Repetition',
    description: 'Detects unusual repetition of word sequences and analyzes diversity patterns',
    icon: 'RotateCcw',
    enabled: true,
    weight: DEFAULT_WEIGHTS.ngram_repetition,
    atomicLevel: 'global',
    scoreInterpretation: 'High repetition = suspicious of artificiality'
  },
  {
    id: 'lexical_richness',
    name: 'Lexical Richness',
    description: 'Measures vocabulary variety using Type-Token Ratio analysis',
    icon: 'BookOpen',
    enabled: true,
    weight: DEFAULT_WEIGHTS.lexical_richness,
    atomicLevel: 'sentence',
    scoreInterpretation: 'Low = repetitive/poor vocabulary, High = rich'
  },
  {
    id: 'stylistic_markers',
    name: 'Stylistic Markers',
    description: 'Identifies unusual stylistic patterns in punctuation, POS tags, and word usage',
    icon: 'PenTool',
    enabled: true,
    weight: DEFAULT_WEIGHTS.stylistic_markers,
    atomicLevel: 'sentence',
    scoreInterpretation: 'Deviations from balanced style = possible artificial generation'
  },
  {
    id: 'readability',
    name: 'Readability',
    description: 'Measures natural readability using Flesch Reading Ease and complexity metrics',
    icon: 'FileText',
    enabled: true,
    weight: DEFAULT_WEIGHTS.readability,
    atomicLevel: 'sentence',
    scoreInterpretation: 'Very high = too simplistic, Very low = too complex'
  }
];

export const AnalysisDimensions: React.FC<AnalysisDimensionsProps> = ({
  dimensions,
  results,
  onDimensionToggle,
  onDimensionClick,
  showResults = false
}) => {
  // Update dimensions with current enabled state
  const updatedDimensions = ANALYSIS_DIMENSIONS.map(dimension => ({
    ...dimension,
    enabled: dimensions[dimension.id]
  }));

  return (
    <div className="analysis-dimensions">
      <div className="dimensions-grid">
        {updatedDimensions.map((dimension) => {
          const dimensionResult = results?.[dimension.id];
          
          return (
            <DimensionCard
              key={dimension.id}
              dimension={dimension}
              result={dimensionResult}
              onToggle={onDimensionToggle}
              onCardClick={onDimensionClick}
              isClickable={showResults}
            />
          );
        })}
      </div>
      
      {showResults && (
        <div className="dimensions-summary">
          <div className="active-dimensions">
            <strong>Active Dimensions:</strong> {Object.values(dimensions).filter(Boolean).length}/7
          </div>
          <div className="total-evidences">
            <strong>Total Evidences:</strong> {
              results ? Object.values(results)
                .filter(result => result.active)
                .reduce((sum, result) => sum + result.totalEvidences, 0) : 0
            }
          </div>
        </div>
      )}
    </div>
  );
};

