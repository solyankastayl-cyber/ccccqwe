#!/usr/bin/env python3
"""
Anchor-Based Pattern Engine Testing
===================================

Tests the specific features mentioned in the review request:
1. Pattern card shows 'Descending Triangle' (not Ascending)
2. Bias shows 'BEARISH'
3. Upper line — descending (lower highs)
4. Lower line — horizontal (flat support)
5. API returns touch_score > 0.5
6. API returns render_quality > 0.6
7. Pattern View mode works (clean chart)
8. Window zoom'd to pattern area
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

class AnchorPatternTester:
    def __init__(self, base_url: str = "https://tech-analysis-16.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status=200, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                self.failed_tests.append(f"{name} - Status {response.status_code}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout ({timeout}s)")
            self.failed_tests.append(f"{name} - Timeout")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append(f"{name} - {str(e)}")
            return False, {}

    def validate_anchor_pattern_features(self, data, test_name):
        """Validate anchor-based pattern features"""
        validation_results = []
        
        if not data.get('ok'):
            validation_results.append("❌ Response not OK")
            return validation_results
        
        # Check for pattern_render_contract (anchor-based)
        pattern_contract = data.get('pattern_render_contract')
        if not pattern_contract:
            validation_results.append("❌ No pattern_render_contract found")
            return validation_results
        
        print(f"   📊 Pattern contract keys: {list(pattern_contract.keys())}")
        
        # 1. Check pattern type is 'descending_triangle'
        pattern_type = pattern_contract.get('type')
        if pattern_type == 'descending_triangle':
            validation_results.append("✅ Pattern type is 'descending_triangle'")
        else:
            validation_results.append(f"❌ Pattern type is '{pattern_type}', expected 'descending_triangle'")
        
        # 2. Check bias is 'bearish'
        direction = pattern_contract.get('direction')
        if direction == 'bearish':
            validation_results.append("✅ Bias is 'bearish'")
        else:
            validation_results.append(f"❌ Bias is '{direction}', expected 'bearish'")
        
        # 3. Check touch_score > 0.5
        touch_score = pattern_contract.get('touch_score', 0)
        if touch_score > 0.5:
            validation_results.append(f"✅ Touch score {touch_score:.3f} > 0.5")
        else:
            validation_results.append(f"❌ Touch score {touch_score:.3f} <= 0.5")
        
        # 4. Check render_quality > 0.6
        render_quality = pattern_contract.get('render_quality', 0)
        if render_quality > 0.6:
            validation_results.append(f"✅ Render quality {render_quality:.3f} > 0.6")
        else:
            validation_results.append(f"❌ Render quality {render_quality:.3f} <= 0.6")
        
        # 5. Check anchor points structure
        anchors = pattern_contract.get('anchors', {})
        upper_anchors = anchors.get('upper', [])
        lower_anchors = anchors.get('lower', [])
        
        if len(upper_anchors) >= 2:
            validation_results.append(f"✅ Upper anchors: {len(upper_anchors)} points (descending highs)")
            # Check if upper line is descending
            if len(upper_anchors) >= 2:
                first_price = upper_anchors[0].get('price', 0)
                last_price = upper_anchors[-1].get('price', 0)
                if last_price < first_price:
                    validation_results.append("✅ Upper line is descending (lower highs)")
                else:
                    validation_results.append("❌ Upper line is not descending")
        else:
            validation_results.append(f"❌ Upper anchors: {len(upper_anchors)} points (need >= 2)")
        
        if len(lower_anchors) >= 2:
            validation_results.append(f"✅ Lower anchors: {len(lower_anchors)} points (flat support)")
            # Check if lower line is horizontal (flat)
            if len(lower_anchors) >= 2:
                prices = [a.get('price', 0) for a in lower_anchors]
                price_range = max(prices) - min(prices)
                avg_price = sum(prices) / len(prices)
                tolerance_pct = price_range / avg_price if avg_price > 0 else 0
                if tolerance_pct < 0.02:  # 2% tolerance for "flat"
                    validation_results.append("✅ Lower line is horizontal (flat support)")
                else:
                    validation_results.append(f"❌ Lower line not flat (range: {tolerance_pct:.1%})")
        else:
            validation_results.append(f"❌ Lower anchors: {len(lower_anchors)} points (need >= 2)")
        
        # 6. Check pattern window for zoom functionality
        window = pattern_contract.get('window')
        if window and window.get('start') and window.get('end'):
            validation_results.append("✅ Pattern window defined for zoom")
        else:
            validation_results.append("❌ Pattern window missing for zoom")
        
        # 7. Check render boundaries for chart display
        render_data = pattern_contract.get('render', {})
        boundaries = render_data.get('boundaries', [])
        if len(boundaries) >= 2:
            validation_results.append(f"✅ Render boundaries: {len(boundaries)} lines")
        else:
            validation_results.append(f"❌ Render boundaries: {len(boundaries)} lines (need >= 2)")
        
        return validation_results

    def test_descending_triangle_detection(self):
        """Test descending triangle pattern detection"""
        # Test with BTC 1D which should show descending triangle
        success, data = self.run_test(
            "Descending Triangle Detection",
            "GET",
            "api/ta-engine/mtf/BTC/1D",
            timeout=30
        )
        
        if success and data:
            print("\n📋 Validating Anchor Pattern Features...")
            validation_results = self.validate_anchor_pattern_features(data, "Descending Triangle")
            for result in validation_results:
                print(f"   {result}")
        
        return success, data

    def test_pattern_alternatives(self):
        """Test pattern alternatives (should have multiple patterns)"""
        success, data = self.run_test(
            "Pattern Alternatives",
            "GET",
            "api/ta-engine/mtf/BTC/1D",
            timeout=30
        )
        
        if success and data:
            alternatives = data.get('alternative_render_contracts', [])
            print(f"   📊 Alternative patterns: {len(alternatives)}")
            for i, alt in enumerate(alternatives):
                pattern_type = alt.get('type', 'unknown')
                confidence = alt.get('confidence', 0)
                print(f"   📊 Alt {i+1}: {pattern_type} (confidence: {confidence:.2f})")
        
        return success, data

    def test_mtf_pattern_consistency(self):
        """Test MTF pattern consistency across timeframes"""
        timeframes = ["4H", "1D", "7D"]
        pattern_results = {}
        
        for tf in timeframes:
            success, data = self.run_test(
                f"Pattern Detection {tf}",
                "GET",
                f"api/ta-engine/mtf/BTC/{tf}",
                timeout=30
            )
            
            if success and data:
                pattern_contract = data.get('pattern_render_contract')
                if pattern_contract:
                    pattern_results[tf] = {
                        'type': pattern_contract.get('type'),
                        'direction': pattern_contract.get('direction'),
                        'touch_score': pattern_contract.get('touch_score', 0),
                        'render_quality': pattern_contract.get('render_quality', 0),
                    }
        
        print(f"\n📊 Pattern Results Across Timeframes:")
        for tf, result in pattern_results.items():
            print(f"   {tf}: {result['type']} | {result['direction']} | touch={result['touch_score']:.2f} | quality={result['render_quality']:.2f}")
        
        return len(pattern_results) > 0

    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print(f"📊 ANCHOR PATTERN ENGINE TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.failed_tests:
            print(f"\n❌ Failed tests:")
            for failed in self.failed_tests:
                print(f"   - {failed}")
        else:
            print(f"\n✅ All tests passed!")
        
        return self.tests_passed == self.tests_run

def main():
    """Run all anchor pattern tests"""
    print("🚀 Starting Anchor-Based Pattern Engine Tests...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    tester = AnchorPatternTester()
    
    # Run tests in order
    tests = [
        tester.test_descending_triangle_detection,
        tester.test_pattern_alternatives,
        tester.test_mtf_pattern_consistency,
    ]
    
    for test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            tester.tests_run += 1
            tester.failed_tests.append(f"{test_func.__name__} - Crashed: {e}")
    
    # Print final summary
    all_passed = tester.print_summary()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())