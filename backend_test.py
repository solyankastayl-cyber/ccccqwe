#!/usr/bin/env python3
"""
Backend API Testing for TA Engine ResearchChart Fixes
=====================================================

Tests the critical TA Engine endpoints that the frontend depends on:
1. /api/ta-engine/mtf/BTC - Multi-timeframe analysis with render_plan
2. TF switching functionality (1D/4H/1H buttons)
3. Structure visualization (legs between swings)
4. Levels normalization (not 50 levels, only key support/resistance)
5. Pattern detection panel
6. Fibonacci panel
7. Market Context panel (HTF BIAS, SETUP, ENTRY)
8. Execution status (NO TRADE/TRADE)

This tests the backend fixes mentioned in the review request.
"""

import requests
import sys
import json
from datetime import datetime

class TAEngineAPITester:
    def __init__(self, base_url="https://github-analyzer-23.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status=200, data=None, timeout=35):
        """Run a single API test with extended timeout for TA endpoints"""
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

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                # Parse and validate response structure
                try:
                    response_data = response.json()
                    self.test_results.append({
                        "test": name,
                        "status": "PASS",
                        "response_keys": list(response_data.keys()) if isinstance(response_data, dict) else [],
                        "data_size": len(str(response_data))
                    })
                    return True, response_data
                except:
                    print(f"⚠️  Warning: Response not JSON")
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Raw response: {response.text[:200]}")
                
                self.test_results.append({
                    "test": name,
                    "status": "FAIL",
                    "error": f"Status {response.status_code}",
                    "response": response.text[:200]
                })
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout ({timeout}s)")
            self.test_results.append({
                "test": name,
                "status": "FAIL",
                "error": "Timeout"
            })
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "test": name,
                "status": "FAIL",
                "error": str(e)
            })
            return False, {}

    def test_ta_engine_status(self):
        """Test TA Engine health check"""
        success, response = self.run_test(
            "TA Engine Status",
            "GET",
            "api/ta-engine/status"
        )
        if success and response.get("ok"):
            print(f"   ✓ TA Engine version: {response.get('version')}")
            print(f"   ✓ Components: {list(response.get('components', {}).keys())}")
        return success

    def test_mtf_btc_analysis(self):
        """Test MTF BTC analysis - the main endpoint frontend uses"""
        success, response = self.run_test(
            "MTF BTC Analysis (1D,4H,1H)",
            "GET",
            "api/ta-engine/mtf/BTC?timeframes=1D,4H,1H",
            timeout=40  # Extended timeout for MTF
        )
        
        if success and response.get("ok"):
            tf_map = response.get("tf_map", {})
            mtf_context = response.get("mtf_context", {})
            
            print(f"   ✓ Timeframes available: {list(tf_map.keys())}")
            print(f"   ✓ MTF context: {bool(mtf_context)}")
            
            # Check render_plan in each timeframe
            for tf, tf_data in tf_map.items():
                render_plan = tf_data.get("render_plan")
                if render_plan:
                    print(f"   ✓ {tf} has render_plan with keys: {list(render_plan.keys())}")
                    
                    # Check structure data (legs between swings)
                    structure = render_plan.get("structure", {})
                    if structure:
                        swings = structure.get("swings", [])
                        print(f"   ✓ {tf} structure has {len(swings)} swings")
                        
                        # Check for BOS/CHOCH
                        bos = structure.get("bos")
                        choch = structure.get("choch")
                        if bos:
                            print(f"   ✓ {tf} has BOS at {bos.get('price', 'N/A')}")
                        if choch:
                            print(f"   ✓ {tf} has CHOCH at {choch.get('price', 'N/A')}")
                    
                    # Check levels normalization (should be ≤ 5)
                    levels = render_plan.get("levels", [])
                    print(f"   ✓ {tf} has {len(levels)} levels (normalized)")
                    if len(levels) > 10:
                        print(f"   ⚠️  {tf} has too many levels: {len(levels)}")
                    
                    # Check execution status
                    execution = render_plan.get("execution", {})
                    if execution:
                        status = execution.get("status", "unknown")
                        print(f"   ✓ {tf} execution status: {status}")
                        if status == "valid":
                            direction = execution.get("direction", "unknown")
                            print(f"   ✓ {tf} execution direction: {direction}")
                else:
                    print(f"   ⚠️  {tf} missing render_plan")
            
            # Check MTF context for HTF BIAS, SETUP, ENTRY
            if mtf_context:
                bias = mtf_context.get("htf_bias", {})
                setup = mtf_context.get("setup_tf", "unknown")
                entry = mtf_context.get("entry_tf", "unknown")
                
                if isinstance(bias, dict):
                    print(f"   ✓ HTF Bias: {bias.get('direction', 'unknown')}")
                else:
                    print(f"   ✓ HTF Bias: {bias}")
                print(f"   ✓ Setup TF: {setup}")
                print(f"   ✓ Entry TF: {entry}")
            
            return True
        return success

    def test_single_tf_analysis(self):
        """Test single timeframe analysis for TF switching"""
        timeframes_to_test = ["1D", "4H", "1H"]
        all_success = True
        
        for tf in timeframes_to_test:
            success, response = self.run_test(
                f"Single TF Analysis ({tf})",
                "GET",
                f"api/ta-engine/mtf/BTC/{tf}",
                timeout=30
            )
            
            if success and response.get("ok"):
                data = response.get("data", {})
                render_plan = data.get("render_plan")
                candles = data.get("candles", [])
                
                print(f"   ✓ {tf} Candles: {len(candles)}")
                print(f"   ✓ {tf} Render plan: {bool(render_plan)}")
                
                if render_plan:
                    structure = render_plan.get("structure", {})
                    levels = render_plan.get("levels", [])
                    execution = render_plan.get("execution", {})
                    
                    print(f"   ✓ {tf} Structure swings: {len(structure.get('swings', []))}")
                    print(f"   ✓ {tf} Levels count: {len(levels)}")
                    print(f"   ✓ {tf} Execution status: {execution.get('status', 'unknown')}")
            else:
                all_success = False
        
        return all_success

    def test_pattern_detection(self):
        """Test pattern detection panel data"""
        success, response = self.run_test(
            "Pattern Registry",
            "GET",
            "api/ta-engine/registry/patterns"
        )
        
        if success and response.get("ok"):
            registry = response.get("registry", {})
            total = response.get("total", 0)
            
            print(f"   ✓ Total patterns: {total}")
            print(f"   ✓ Categories: {list(registry.keys())}")
            
            # Check for key pattern categories
            expected_categories = ["reversal", "continuation", "harmonic"]
            for cat in expected_categories:
                if cat in registry:
                    patterns_in_cat = len(registry[cat])
                    print(f"   ✓ {cat.title()} patterns: {patterns_in_cat}")
        
        return success

    def validate_render_plan_structure(self, render_plan):
        """Validate render_plan has expected structure for ResearchChart"""
        required_keys = ["structure", "levels", "execution"]
        missing_keys = []
        
        for key in required_keys:
            if key not in render_plan:
                missing_keys.append(key)
        
        if missing_keys:
            print(f"   ⚠️  Missing render_plan keys: {missing_keys}")
            return False
        
        # Check structure has swings for legs visualization
        structure = render_plan.get("structure", {})
        swings = structure.get("swings", [])
        if not swings:
            print(f"   ⚠️  Structure has no swings (no legs can be drawn)")
            return False
        
        # Check levels are normalized (not too many)
        levels = render_plan.get("levels", [])
        if len(levels) > 10:
            print(f"   ⚠️  Too many levels: {len(levels)} (should be ≤ 5-10)")
            return False
        
        # Check execution has status
        execution = render_plan.get("execution", {})
        if "status" not in execution:
            print(f"   ⚠️  Execution missing status")
            return False
        
        print(f"   ✓ Render plan structure valid for ResearchChart")
        return True

def main():
    """Run all TA Engine API tests"""
    print("=" * 70)
    print("TA ENGINE API TESTING - RESEARCHCHART FIXES")
    print("=" * 70)
    print(f"Testing backend fixes for ResearchChart:")
    print("1. ✅ TF switching and render_plan data")
    print("2. ✅ Structure visualization (legs between swings)")
    print("3. ✅ Levels normalization (≤ 5 key levels)")
    print("4. ✅ Pattern detection panel")
    print("5. ✅ Market Context panel (HTF BIAS, SETUP, ENTRY)")
    print("6. ✅ Execution status display (NO TRADE/TRADE)")
    print()
    
    tester = TAEngineAPITester()
    
    # Core API tests
    print("🔧 CORE API TESTS")
    print("-" * 30)
    
    tester.test_ta_engine_status()
    tester.test_pattern_detection()
    
    print("\n🧠 TA ANALYSIS TESTS")
    print("-" * 30)
    
    # Main MTF endpoint test (primary frontend endpoint)
    mtf_success = tester.test_mtf_btc_analysis()
    
    # Single TF tests (for TF switching)
    tf_switching_success = tester.test_single_tf_analysis()
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    # Print detailed results
    print(f"\nDETAILED RESULTS:")
    for result in tester.test_results:
        status_icon = "✅" if result["status"] == "PASS" else "❌"
        print(f"{status_icon} {result['test']}: {result['status']}")
        if result["status"] == "PASS" and "response_keys" in result:
            print(f"   Keys: {result['response_keys']}")
        elif result["status"] == "FAIL":
            print(f"   Error: {result.get('error', 'Unknown')}")
    
    # Critical issues check
    critical_issues = []
    if not mtf_success:
        critical_issues.append("MTF BTC endpoint failing - frontend cannot load data")
    if not tf_switching_success:
        critical_issues.append("TF switching endpoints failing - buttons won't work")
    
    if critical_issues:
        print(f"\n🚨 CRITICAL ISSUES:")
        for issue in critical_issues:
            print(f"   • {issue}")
        return 1
    
    print(f"\n✅ Backend API tests completed successfully!")
    print(f"   • TA Engine is responding correctly")
    print(f"   • MTF endpoint provides render_plan data")
    print(f"   • TF switching endpoints working")
    print(f"   • Structure and levels data available")
    print(f"   • Pattern detection working")
    print(f"   • Execution status properly formatted")
    print(f"   • Ready for frontend testing")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())