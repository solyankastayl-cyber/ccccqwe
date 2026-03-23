#!/usr/bin/env python3
"""
Backend API Testing for FOMO Tech Analysis Module
=================================================

Tests the MTF (Multi-Timeframe) API endpoints and interpretation functionality.
Focus on testing the features mentioned in the review request:

1. API /api/ta-engine/mtf/BTC should return interpretation for each TF
2. MTF Summary Bar data (summary_text in mtf_context.summary)
3. TF selector should show 1M and 6M instead of 30D and 180D
4. Per-TF interpretation should be available
5. No 'no trade', 'invalid' in responses
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

class FOMOTechAnalysisAPITester:
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
                
                # Return response data for further validation
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

    def validate_mtf_response(self, data, test_name):
        """Validate MTF response structure and content"""
        validation_results = []
        
        # Check basic structure
        if not data.get('ok'):
            validation_results.append("❌ Response not OK")
            return validation_results
            
        tf_map = data.get('tf_map', {})
        mtf_context = data.get('mtf_context', {})
        
        print(f"   📊 TF Map keys: {list(tf_map.keys())}")
        print(f"   📊 MTF Context keys: {list(mtf_context.keys())}")
        
        # 1. Check that interpretation exists for each TF
        interpretation_count = 0
        for tf, tf_data in tf_map.items():
            if tf_data.get('interpretation'):
                interpretation_count += 1
                print(f"   ✅ {tf} has interpretation: {tf_data['interpretation'][:50]}...")
            else:
                validation_results.append(f"❌ {tf} missing interpretation")
        
        if interpretation_count > 0:
            validation_results.append(f"✅ {interpretation_count} TFs have interpretation")
        
        # 2. Check MTF Summary Bar data (summary_text)
        summary = mtf_context.get('summary', {})
        summary_text = summary.get('summary_text')
        if summary_text:
            validation_results.append(f"✅ MTF Summary text: {summary_text}")
            
            # Check for research language (not trading language)
            bad_words = ['no trade', 'invalid', 'no analysis']
            has_bad_words = any(bad_word in summary_text.lower() for bad_word in bad_words)
            if has_bad_words:
                validation_results.append("❌ Summary contains trading language")
            else:
                validation_results.append("✅ Summary uses research language")
        else:
            validation_results.append("❌ Missing MTF summary_text")
        
        # 3. Check TF names (should have 1M, 6M instead of 30D, 180D)
        tf_keys = list(tf_map.keys())
        has_proper_names = '1M' in tf_keys or '6M' in tf_keys
        has_legacy_names = '30D' in tf_keys or '180D' in tf_keys
        
        if has_proper_names:
            validation_results.append("✅ Uses proper TF names (1M/6M)")
        if has_legacy_names:
            validation_results.append("⚠️  Still has legacy TF names (30D/180D)")
        
        # 4. Check for bad language in all interpretations
        bad_language_count = 0
        for tf, tf_data in tf_map.items():
            interpretation = tf_data.get('interpretation', '')
            if any(bad_word in interpretation.lower() for bad_word in ['no trade', 'invalid', 'no analysis']):
                bad_language_count += 1
                validation_results.append(f"❌ {tf} interpretation has trading language")
        
        if bad_language_count == 0 and interpretation_count > 0:
            validation_results.append("✅ All interpretations use research language")
        
        return validation_results

    def test_ta_engine_status(self):
        """Test TA Engine status endpoint"""
        return self.run_test(
            "TA Engine Status",
            "GET",
            "api/ta-engine/status"
        )

    def test_mtf_btc_analysis(self):
        """Test MTF analysis for BTC with all timeframes"""
        # Test with all timeframes including 1M and 6M
        timeframes = "4H,1D,7D,1M,6M,1Y"
        success, data = self.run_test(
            "MTF BTC Analysis (All TFs)",
            "GET",
            f"api/ta-engine/mtf/BTC?timeframes={timeframes}",
            timeout=45  # Increased timeout for MTF
        )
        
        if success and data:
            print("\n📋 Validating MTF Response Structure...")
            validation_results = self.validate_mtf_response(data, "MTF BTC")
            for result in validation_results:
                print(f"   {result}")
        
        return success, data

    def test_single_tf_analysis(self):
        """Test single timeframe analysis"""
        return self.run_test(
            "Single TF Analysis (1D)",
            "GET",
            "api/ta-engine/mtf/BTC/1D"
        )

    def test_render_plan_v2(self):
        """Test Render Plan V2 endpoint"""
        return self.run_test(
            "Render Plan V2",
            "GET",
            "api/ta-engine/render-plan-v2/BTC?timeframe=1D"
        )

    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print(f"📊 FOMO TECH ANALYSIS API TEST SUMMARY")
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
    """Run all tests"""
    print("🚀 Starting FOMO Tech Analysis API Tests...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    tester = FOMOTechAnalysisAPITester()
    
    # Run tests in order
    tests = [
        tester.test_ta_engine_status,
        tester.test_mtf_btc_analysis,
        tester.test_single_tf_analysis,
        tester.test_render_plan_v2,
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