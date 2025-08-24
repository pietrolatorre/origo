/**
 * WordTable component for displaying word-level analysis results
 */

import React, { useState, useMemo } from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown, Search } from 'lucide-react';
import { ScoreDisplay } from './ScoreDisplay';
import type { UniqueWord } from '../types/analysis';

interface WordTableProps {
  words: UniqueWord[];
}

type SortKey = 'word' | 'score' | 'count';
type SortDirection = 'asc' | 'desc';

export const WordTable: React.FC<WordTableProps> = ({ words }) => {
  const [sortKey, setSortKey] = useState<SortKey>('score');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [searchTerm, setSearchTerm] = useState('');
  const [displayCount, setDisplayCount] = useState(20);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('desc');
    }
  };

  const getSortIcon = (key: SortKey) => {
    if (sortKey !== key) return <ArrowUpDown size={14} />;
    return sortDirection === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />;
  };

  const filteredAndSortedWords = useMemo(() => {
    let filtered = words;
    
    // Filter by search term
    if (searchTerm.trim()) {
      filtered = words.filter(word => 
        word.word.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Sort
    const sorted = [...filtered].sort((a, b) => {
      let aVal: number | string;
      let bVal: number | string;
      
      switch (sortKey) {
        case 'word':
          aVal = a.word.toLowerCase();
          bVal = b.word.toLowerCase();
          break;
        case 'score':
          aVal = a.average_score;
          bVal = b.average_score;
          break;
        case 'count':
          aVal = a.count;
          bVal = b.count;
          break;
        default:
          aVal = a.average_score;
          bVal = b.average_score;
      }
      
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortDirection === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      } else {
        const numA = aVal as number;
        const numB = bVal as number;
        return sortDirection === 'asc' ? numA - numB : numB - numA;
      }
    });
    
    return sorted.slice(0, displayCount);
  }, [words, searchTerm, sortKey, sortDirection, displayCount]);

  const getScoreCategory = (score: number): string => {
    if (score >= 0.8) return 'Very High';
    if (score >= 0.6) return 'High';
    if (score >= 0.4) return 'Medium';
    if (score >= 0.2) return 'Low';
    return 'Very Low';
  };

  const getImpactColor = (score: number, count: number): string => {
    const impact = score * count;
    if (impact >= 3) return 'high-impact';
    if (impact >= 1.5) return 'medium-impact';
    return 'low-impact';
  };

  return (
    <div className=\"word-table\">
      <div className=\"table-header\">
        <div className=\"header-controls\">
          <div className=\"search-box\">
            <Search size={16} className=\"search-icon\" />
            <input
              type=\"text\"
              placeholder=\"Search words...\"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className=\"search-input\"
            />
          </div>
          
          <div className=\"display-controls\">
            <label htmlFor=\"display-count\">Show:</label>
            <select 
              id=\"display-count\"
              value={displayCount} 
              onChange={(e) => setDisplayCount(Number(e.target.value))}
              className=\"display-select\"
            >
              <option value={10}>10 words</option>
              <option value={20}>20 words</option>
              <option value={50}>50 words</option>
              <option value={100}>100 words</option>
            </select>
          </div>
        </div>
        
        <div className=\"table-info\">
          <span className=\"results-count\">
            Showing {filteredAndSortedWords.length} of {words.length} words
          </span>
        </div>
      </div>

      <div className=\"table-container\">
        <table className=\"words-table\">
          <thead>
            <tr>
              <th 
                className={`sortable ${sortKey === 'word' ? 'active' : ''}`}
                onClick={() => handleSort('word')}
              >
                <span>Word</span>
                {getSortIcon('word')}
              </th>
              <th 
                className={`sortable ${sortKey === 'score' ? 'active' : ''}`}
                onClick={() => handleSort('score')}
              >
                <span>AI Score</span>
                {getSortIcon('score')}
              </th>
              <th 
                className={`sortable ${sortKey === 'count' ? 'active' : ''}`}
                onClick={() => handleSort('count')}
              >
                <span>Frequency</span>
                {getSortIcon('count')}
              </th>
              <th>Category</th>
              <th>Impact</th>
            </tr>
          </thead>
          <tbody>
            {filteredAndSortedWords.length === 0 ? (
              <tr>
                <td colSpan={5} className=\"no-results\">
                  {searchTerm ? `No words found matching \"${searchTerm}\"` : 'No word data available'}
                </td>
              </tr>
            ) : (
              filteredAndSortedWords.map((word, index) => {
                const impact = word.average_score * word.count;
                return (
                  <tr key={`${word.word}-${index}`} className=\"word-row\">
                    <td className=\"word-cell\">
                      <span className=\"word-text\">{word.word}</span>
                    </td>
                    <td className=\"score-cell\">
                      <ScoreDisplay 
                        score={word.average_score} 
                        size=\"small\" 
                        showPercentage={false}
                      />
                    </td>
                    <td className=\"count-cell\">
                      <span className=\"count-badge\">{word.count}</span>
                    </td>
                    <td className=\"category-cell\">
                      <span className={`category-badge ${word.average_score >= 0.7 ? 'high' : word.average_score >= 0.4 ? 'medium' : 'low'}`}>
                        {getScoreCategory(word.average_score)}
                      </span>
                    </td>
                    <td className=\"impact-cell\">
                      <div className={`impact-indicator ${getImpactColor(word.average_score, word.count)}`}>
                        <div className=\"impact-bar\" style={{ width: `${Math.min(impact * 20, 100)}%` }} />
                        <span className=\"impact-value\">{impact.toFixed(1)}</span>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
      
      <div className=\"table-footer\">
        <div className=\"table-legend\">
          <h4>Legend:</h4>
          <div className=\"legend-items\">
            <div className=\"legend-item\">
              <strong>AI Score:</strong> Individual word's likelihood of being AI-generated
            </div>
            <div className=\"legend-item\">
              <strong>Frequency:</strong> Number of times the word appears in the text
            </div>
            <div className=\"legend-item\">
              <strong>Impact:</strong> Combined influence (Score × Frequency) on overall analysis
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};