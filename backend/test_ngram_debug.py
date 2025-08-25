#!/usr/bin/env python3
"""
Debug script for N-gram analysis issues
"""

from analysis.ngram import NgramAnalyzer
import json

def test_ngram_analysis():
    analyzer = NgramAnalyzer()
    
    # Test text with high repetition
    test_text = """The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The same phrase repeats here. The same phrase repeats here. The same phrase repeats here. Another identical sentence structure follows. Another identical sentence structure follows. Another identical sentence structure follows. This pattern continues with high repetition. This pattern continues with high repetition. This pattern continues with high repetition."""
    
    print("=== Testing N-gram Analysis ===")
    print(f"Text length: {len(test_text)} characters")
    print(f"Text: {test_text[:100]}...")
    print()
    
    # Get full analysis
    result = analyzer.analyze_text(test_text)
    
    print("=== Results ===")
    print(f"Overall Score: {result['overall_score']:.3f}")
    print()
    
    # Check each n-gram type
    ngram_analysis = result.get('ngram_analysis', {})
    
    for ngram_type in ['bigrams', 'trigrams', 'fourgrams']:
        print(f"=== {ngram_type.upper()} ===")
        ngram_data = ngram_analysis.get(ngram_type, {})
        score = ngram_data.get('score', 0)
        details = ngram_data.get('details', [])
        
        print(f"Score: {score:.3f}")
        print(f"Number of details: {len(details)}")
        
        if details:
            print("Top 5 patterns:")
            for i, item in enumerate(details[:5]):
                print(f"  {i+1}. '{item['text']}' - Freq: {item['frequency']}, Score: {item['score']:.3f}, Ratio: {item['frequency_ratio']:.3f}")
        else:
            print("  No patterns found!")
        print()
    
    # Test individual n-gram frequency calculation
    print("=== Individual N-gram Tests ===")
    for n in [2, 3, 4]:
        score, details = analyzer.calculate_ngram_frequency_score(test_text, n)
        print(f"{n}-gram frequency score: {score:.3f}, details count: {len(details)}")
        if details:
            top3 = details[:3]
            for item in top3:
                print(f"  '{item['text']}' - Freq: {item['frequency']}, Score: {item['score']:.3f}")
        print()

if __name__ == "__main__":
    test_ngram_analysis()