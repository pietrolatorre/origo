/**
 * Header component for Origo application
 */

import React from 'react';
import { Search } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className=\"header\">
      <div className=\"container\">
        <div className=\"header-content\">
          <div className=\"logo\">
            <Search className=\"logo-icon\" size={32} />
            <div className=\"logo-text\">
              <h1>Origo</h1>
              <p className=\"tagline\">Breaking down the signals of writing origin</p>
            </div>
          </div>
          
          <div className=\"header-info\">
            <span className=\"version\">v1.0.0</span>
          </div>
        </div>
      </div>
    </header>
  );
};