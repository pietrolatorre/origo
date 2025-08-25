/**
 * ScoreDisplay component for visualizing scores with color coding
 */

import React from 'react';

interface ScoreDisplayProps {
  score: number;
  size?: 'small' | 'medium' | 'large';
  label?: string;
  showPercentage?: boolean;
}

export const ScoreDisplay: React.FC<ScoreDisplayProps> = ({
  score,
  size = 'medium',
  label,
  showPercentage = true
}) => {
  const getScoreColor = (score: number): string => {
    if (score >= 0.7) return '#ef4444'; // red
    if (score >= 0.6) return '#f59e0b'; // yellow - changed from 0.4 to 0.6
    return '#10b981'; // green
  };

  const getScoreClass = (score: number): string => {
    if (score >= 0.7) return 'high';
    if (score >= 0.6) return 'medium'; // changed from 0.4 to 0.6
    return 'low';
  };

  const percentage = Math.round(score * 100);
  const circumference = 2 * Math.PI * 40;
  const strokeDashoffset = circumference - (score * circumference);

  return (
    <div className={`score-display ${size}`}>
      <div className="score-circle">
        <svg className="score-svg" width="100" height="100">
          {/* Background circle */}
          <circle
            className="score-bg"
            cx="50"
            cy="50"
            r="40"
            strokeWidth="8"
            fill="transparent"
            stroke="#e5e7eb"
          />
          {/* Progress circle */}
          <circle
            className={`score-progress ${getScoreClass(score)}`}
            cx="50"
            cy="50"
            r="40"
            strokeWidth="8"
            fill="transparent"
            stroke={getScoreColor(score)}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            transform="rotate(-90 50 50)"
          />
        </svg>
        <div className="score-text">
          <span className={`score-value ${getScoreClass(score)}`}>
            {showPercentage ? `${percentage}%` : score.toFixed(2)}
          </span>
        </div>
      </div>
      {label && (
        <div className="score-label">
          {label}
        </div>
      )}
    </div>
  );
};

export default ScoreDisplay;