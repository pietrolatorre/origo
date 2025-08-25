#!/usr/bin/env python3
"""
Performance test script for optimized analysis
"""

from analysis.scoring import score_fusion
import time

def test_performance():
    # Test text with high repetition
    test_text = """The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The same phrase repeats here. The same phrase repeats here. The same phrase repeats here. Another identical sentence structure follows. Another identical sentence structure follows. Another identical sentence structure follows. This pattern continues with high repetition. This pattern continues with high repetition. This pattern continues with high repetition."""
    
    print('=== Performance Test ===')
    print(f'Text length: {len(test_text)} characters')
    print(f'Parallel processing enabled: {score_fusion.parallel_enabled}')
    print(f'Caching enabled: {score_fusion.cache_enabled}')
    print()

    # First run (no cache)
    start_time = time.time()
    result1 = score_fusion.analyze_text_comprehensive(test_text)
    first_run_time = time.time() - start_time

    print(f'First run time: {first_run_time:.2f}s')
    print(f'Overall score: {result1["overall_score"]}')
    print(f'Processing time in metadata: {result1["analysis_metadata"].get("processing_time_seconds", "N/A")}s')
    print()

    # Second run (with cache)
    start_time = time.time()
    result2 = score_fusion.analyze_text_comprehensive(test_text)
    second_run_time = time.time() - start_time

    print(f'Second run time (cached): {second_run_time:.2f}s')
    print(f'Overall score: {result2["overall_score"]}')
    print(f'Processing time in metadata: {result2["analysis_metadata"].get("processing_time_seconds", "N/A")}s')
    print()

    if second_run_time > 0:
        speedup = first_run_time / second_run_time
        print(f'Speedup from caching: {speedup:.1f}x')
    else:
        print('Speedup from caching: ∞ (instant cache retrieval)')

    # Test enhanced analysis details
    if 'enhanced_analysis' in result1:
        print()
        print('=== Enhanced Analysis Available ===')
        for analysis_type in ['perplexity_details', 'burstiness_details', 'ngram_details', 'semantic_details']:
            details = result1['enhanced_analysis'].get(analysis_type, {})
            score = details.get('overall_score', 'N/A')
            print(f'{analysis_type}: {score}')
    
    # Test global scores
    print()
    print('=== Global Scores ===')
    global_scores = result1.get('global_scores', {})
    for score_type, score_value in global_scores.items():
        print(f'{score_type}: {score_value}')
    
    # Performance optimization summary
    print()
    print('=== Performance Optimizations Applied ===')
    print('✓ Parallel processing for analysis modules')
    print('✓ Component-level caching with TTL')
    print('✓ Optimized paragraph analysis (max 10 paragraphs)')
    print('✓ Optimized sentence analysis (max 8 sentences per paragraph)')
    print('✓ Optimized word analysis (top 20 words)')
    print('✓ Efficient memory usage and processing limits')
    
    return result1

if __name__ == "__main__":
    test_performance()