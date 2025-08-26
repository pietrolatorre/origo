#!/usr/bin/env python3
"""
API Format Validation Test Script

This script tests the Origo backend API to ensure the response format
matches exactly what the frontend TypeScript interfaces expect.

Run this after starting the backend server to validate the API.
"""

import requests
import json
import sys
import time
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"
TEST_TEXT = """
This is a comprehensive test text for the Origo AI detection system. 
The text contains multiple sentences with varying complexity and structure.
It includes different paragraph lengths and styles to trigger all analysis dimensions.

The purpose is to validate that the API returns properly formatted responses
that match the frontend TypeScript interfaces exactly. This ensures seamless
integration between backend and frontend components.

We need sufficient text length to trigger meaningful analysis across all
seven dimensions: perplexity, burstiness, semantic coherence, n-gram repetition,
lexical richness, stylistic markers, and readability analysis.
"""

def test_api_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_api_info():
    """Test the API info endpoint"""
    print("🔍 Testing API info endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api-info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ API info endpoint working")
            print(f"   Framework: {data.get('framework', {}).get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ API info endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API info endpoint error: {e}")
        return False

def validate_response_structure(data: Dict[str, Any]) -> bool:
    """Validate the response structure matches frontend expectations"""
    print("🔍 Validating response structure...")
    
    required_fields = [
        'overall_score',
        'global_scores', 
        'dimension_results',
        'weights_applied',
        'active_dimensions',
        'analysis_metadata'
    ]
    
    # Check top-level fields
    for field in required_fields:
        if field not in data:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Validate overall_score
    overall_score = data.get('overall_score')
    if not isinstance(overall_score, (int, float)) or not (0 <= overall_score <= 1):
        print(f"❌ Invalid overall_score: {overall_score}")
        return False
    
    # Validate global_scores structure
    global_scores = data.get('global_scores', {})
    expected_dimensions = [
        'perplexity', 'burstiness', 'semantic_coherence', 
        'ngram_repetition', 'lexical_richness', 'stylistic_markers', 'readability'
    ]
    
    for dim in expected_dimensions:
        if dim not in global_scores:
            print(f"❌ Missing dimension in global_scores: {dim}")
            return False
    
    # Validate dimension_results structure
    dimension_results = data.get('dimension_results', {})
    for dim in expected_dimensions:
        if dim in dimension_results and dimension_results[dim] is not None:
            dim_result = dimension_results[dim]
            required_dim_fields = ['score', 'weight', 'active', 'totalEvidences', 'topEvidences']
            for field in required_dim_fields:
                if field not in dim_result:
                    print(f"❌ Missing field in {dim} result: {field}")
                    return False
            
            # Validate evidence structure
            for evidence in dim_result.get('topEvidences', []):
                evidence_fields = ['text', 'score', 'startIndex', 'endIndex', 'type', 'reason']
                for field in evidence_fields:
                    if field not in evidence:
                        print(f"❌ Missing field in evidence: {field}")
                        return False
    
    # Validate metadata
    metadata = data.get('analysis_metadata', {})
    required_metadata = ['text_length', 'word_count', 'sentence_count', 'paragraph_count', 'processing_time_seconds']
    for field in required_metadata:
        if field not in metadata:
            print(f"❌ Missing metadata field: {field}")
            return False
    
    print("✅ Response structure validation passed")
    return True

def test_analyze_endpoint():
    """Test the main analyze endpoint"""
    print("🔍 Testing analyze endpoint...")
    
    # Test request payload
    request_data = {
        "text": TEST_TEXT,
        "enabled_dimensions": {
            "perplexity": True,
            "burstiness": True,
            "semantic_coherence": True,
            "ngram_repetition": True,
            "lexical_richness": True,
            "stylistic_markers": True,
            "readability": True
        }
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        processing_time = time.time() - start_time
        
        if response.status_code != 200:
            print(f"❌ Analyze endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        data = response.json()
        print(f"✅ Analyze endpoint working (processed in {processing_time:.2f}s)")
        print(f"   Overall score: {data.get('overall_score', 'N/A')}")
        print(f"   Active dimensions: {len(data.get('active_dimensions', []))}")
        
        # Validate structure
        if validate_response_structure(data):
            print("✅ All validation checks passed")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Analyze endpoint error: {e}")
        return False

def test_partial_dimensions():
    """Test with only some dimensions enabled"""
    print("🔍 Testing partial dimensions...")
    
    request_data = {
        "text": TEST_TEXT,
        "enabled_dimensions": {
            "perplexity": True,
            "burstiness": False,
            "semantic_coherence": True,
            "ngram_repetition": False,
            "lexical_richness": True,
            "stylistic_markers": False,
            "readability": True
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Partial dimensions test failed: {response.status_code}")
            return False
        
        data = response.json()
        active_count = len([d for d in data.get('active_dimensions', []) if d])
        expected_active = 4  # perplexity, semantic_coherence, lexical_richness, readability
        
        if active_count == expected_active:
            print(f"✅ Partial dimensions test passed ({active_count} active)")
            return True
        else:
            print(f"❌ Expected {expected_active} active dimensions, got {active_count}")
            return False
            
    except Exception as e:
        print(f"❌ Partial dimensions test error: {e}")
        return False

def test_error_handling():
    """Test error handling with invalid input"""
    print("🔍 Testing error handling...")
    
    # Test with text too short
    request_data = {"text": "short"}
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Error handling working (short text rejected)")
            return True
        else:
            print(f"❌ Expected 400 error, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error handling test error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Starting Origo API Format Validation Tests\n")
    
    tests = [
        test_api_health,
        test_api_info,
        test_analyze_endpoint,
        test_partial_dimensions,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Empty line between tests
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}\n")
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API format is correct.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()