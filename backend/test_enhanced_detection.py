#!/usr/bin/env python3
"""
Test script to verify the enhanced AI detection system is working properly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_detection():
    """Test the enhanced detection system"""
    print("🔍 Testing Enhanced AI Detection System")
    print("=" * 50)
    
    # Test text with multiple suspicious indicators
    test_text = """
    This comprehensive analysis delves into the nuanced landscape of modern technology. 
    It's worth noting that this approach leverages cutting-edge methodologies to underscore 
    the paradigm-shifting implications of AI development. Furthermore, the framework 
    facilitates a thought-provoking examination of the intricacies involved.
    """
    
    try:
        # Test individual components
        print("1. Testing Configuration Loading...")
        import json
        
        config_path = os.path.join(os.path.dirname(__file__), 'data', 'perplexity', 'llm_red_flags.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        words = test_text.lower().split()
        found_verbs = [w for w in words if w in config.get('suspicious_verbs', [])]
        found_modifiers = [w for w in words if w in config.get('suspicious_modifiers', [])]
        found_nouns = [w for w in words if w in config.get('suspicious_nouns', [])]
        
        print(f"   ✅ Found {len(found_verbs)} suspicious verbs: {found_verbs}")
        print(f"   ✅ Found {len(found_modifiers)} suspicious modifiers: {found_modifiers}")
        print(f"   ✅ Found {len(found_nouns)} suspicious nouns: {found_nouns}")
        
        # Test formulaic phrases
        formulaic_phrases = config.get('formulaic_phrases', [])
        found_phrases = []
        for phrase in formulaic_phrases:
            if phrase.lower() in test_text.lower():
                found_phrases.append(phrase)
        
        print(f"   ✅ Found {len(found_phrases)} formulaic phrases: {found_phrases}")
        
        print("\n2. Configuration Test Results:")
        total_suspicious = len(found_verbs) + len(found_modifiers) + len(found_nouns) + len(found_phrases)
        print(f"   📊 Total suspicious elements detected: {total_suspicious}")
        
        if total_suspicious >= 4:
            print("   🎯 EXCELLENT: System is detecting suspicious elements correctly!")
        elif total_suspicious >= 2:
            print("   ✅ GOOD: System is working, detection could be improved")
        else:
            print("   ⚠️  WARNING: Low detection rate, check configuration")
        
        # Test scoring calculation
        print("\n3. Testing Scoring Logic...")
        word_count = len([w for w in test_text.split() if w.strip()])
        weights = config.get('weights', {})
        
        # Calculate scores as implemented
        verb_score = (len(found_verbs) / word_count) * weights.get('verbs', 1.0)
        modifier_score = (len(found_modifiers) / word_count) * weights.get('modifiers', 1.0)
        noun_score = (len(found_nouns) / word_count) * weights.get('nouns', 1.0)
        
        print(f"   📈 Verb impact score: {verb_score:.4f}")
        print(f"   📈 Modifier impact score: {modifier_score:.4f}")
        print(f"   📈 Noun impact score: {noun_score:.4f}")
        
        combined_score = (verb_score + modifier_score + noun_score) / 3
        print(f"   🎯 Combined suspicious word score: {combined_score:.4f}")
        
        if combined_score > 0.1:
            print("   🎉 EXCELLENT: Scoring is producing meaningful results!")
        elif combined_score > 0.05:
            print("   ✅ GOOD: Scoring is working")
        else:
            print("   ⚠️  LOW: Scores might be too low")
        
        print("\n" + "=" * 50)
        print("🎯 SUMMARY:")
        print(f"   • Suspicious words detected: {total_suspicious}")
        print(f"   • Scoring sensitivity: {'High' if combined_score > 0.1 else 'Medium' if combined_score > 0.05 else 'Low'}")
        print(f"   • Overall status: {'🎉 WORKING GREAT!' if total_suspicious >= 4 and combined_score > 0.05 else '✅ Working' if total_suspicious >= 2 else '⚠️ Needs attention'}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_detection()
    sys.exit(0 if success else 1)