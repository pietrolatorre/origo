/**
 * Disclaimer component for ethical AI detection notice
 */

import React from 'react';
import { AlertTriangle } from 'lucide-react';

export const Disclaimer: React.FC = () => {
  return (
    <footer className=\"disclaimer\">
      <div className=\"container\">
        <div className=\"disclaimer-content\">
          <AlertTriangle className=\"disclaimer-icon\" size={20} />
          <p className=\"disclaimer-text\">
            <strong>Important:</strong> AI-generated text detection is imperfect. 
            This tool provides probabilistic signals — not conclusive proof. 
            It is meant to support human judgment, not replace it.
          </p>
        </div>
      </div>
    </footer>
  );
};