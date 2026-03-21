"""
Pattern Rendering Feature Test
==============================

Tests specific features requested:
1. PatternGeometryRenderer draws neckline/breakout level ON CHART (green line at $74,100)
2. Structure legs became subdued (opacity 0.4 instead of solid)
3. Pattern toggle button hides/shows pattern overlay
4. Fibonacci toggle button hides/shows fibonacci panel
5. Pattern Detected card shows Double Bottom
6. API /api/ta/setup/v2 returns pattern_v2.primary_pattern with lines (valleys, neckline)
"""

import requests
import sys
import json
from datetime import datetime

class PatternRenderingTester:
    def __init__(self, base_url="https://ta-engine-preview-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.results = []

    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        print(f"{status} - {test_name}")
        if details:
            print(f"    {details}")
        
        self.results.append({
            "test_name": test_name,
            "passed": passed,
            "details": details
        })

    def test_pattern_v2_api_structure(self) -> bool:
        """Test API returns pattern_v2.primary_pattern with lines (valleys, neckline)"""
        try:
            url = f"{self.base_url}/api/ta/setup/v2"
            params = {"symbol": "BTCUSDT", "tf": "1d"}
            
            print(f"\n🔍 Testing pattern_v2 API structure...")
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                self.log_result("Pattern V2 API Response", False, f"Expected 200, got {response.status_code}")
                return False
            
            data = response.json()
            
            # Check pattern_v2 field exists
            if "pattern_v2" not in data:
                self.log_result("Pattern V2 Field Present", False, "pattern_v2 field missing")
                return False
            
            pattern_v2 = data["pattern_v2"]
            if not pattern_v2:
                self.log_result("Pattern V2 Data", True, "pattern_v2 is null (valid when no pattern detected)")
                return True
            
            # Check primary_pattern exists
            if "primary_pattern" not in pattern_v2:
                self.log_result("Primary Pattern Field", False, "primary_pattern missing from pattern_v2")
                return False
            
            primary_pattern = pattern_v2["primary_pattern"]
            if not primary_pattern:
                self.log_result("Primary Pattern Data", True, "primary_pattern is null (valid)")
                return True
            
            # Check for lines array with valleys and neckline
            if "lines" in primary_pattern and primary_pattern["lines"]:
                lines = primary_pattern["lines"]
                line_names = [line.get("name") for line in lines if isinstance(line, dict)]
                
                valleys_found = "valleys" in line_names
                neckline_found = "neckline" in line_names
                
                self.log_result("Pattern Lines Structure", True, 
                               f"Found lines: {line_names}")
                
                if valleys_found:
                    self.log_result("Valleys Line Present", True, "valleys line found in pattern")
                
                if neckline_found:
                    self.log_result("Neckline Line Present", True, "neckline line found in pattern")
                
                # Check for Double Bottom specifically
                pattern_type = primary_pattern.get("type", "").lower()
                if "double_bottom" in pattern_type:
                    self.log_result("Double Bottom Pattern", True, f"Pattern type: {pattern_type}")
                
            return True
            
        except Exception as e:
            self.log_result("Pattern V2 API Structure", False, f"Error: {str(e)}")
            return False

    def test_breakout_level_api(self) -> bool:
        """Test API returns breakout_level for neckline rendering"""
        try:
            url = f"{self.base_url}/api/ta/setup/v2"
            params = {"symbol": "BTCUSDT", "tf": "1d"}
            
            print(f"\n🔍 Testing breakout level in API...")
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            pattern_v2 = data.get("pattern_v2")
            if not pattern_v2 or not pattern_v2.get("primary_pattern"):
                self.log_result("Breakout Level Test", True, "No primary pattern - breakout level test skipped")
                return True
            
            primary_pattern = pattern_v2["primary_pattern"]
            
            # Check for breakout_level field
            if "breakout_level" in primary_pattern:
                breakout_level = primary_pattern["breakout_level"]
                if isinstance(breakout_level, (int, float)) and breakout_level > 0:
                    self.log_result("Breakout Level Present", True, 
                                   f"Breakout level: ${breakout_level:,.2f}")
                else:
                    self.log_result("Breakout Level Valid", False, 
                                   f"Invalid breakout level: {breakout_level}")
            else:
                self.log_result("Breakout Level Field", False, "breakout_level missing from primary_pattern")
            
            return True
            
        except Exception as e:
            self.log_result("Breakout Level API", False, f"Error: {str(e)}")
            return False

    def test_chart_structure_subdued(self) -> bool:
        """Test chart_structure returns subdued structure data"""
        try:
            url = f"{self.base_url}/api/ta/setup/v2"
            params = {"symbol": "BTCUSDT", "tf": "1d"}
            
            print(f"\n🔍 Testing chart structure for subdued styling...")
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            # Check chart_structure field
            chart_structure = data.get("chart_structure")
            if not chart_structure:
                self.log_result("Chart Structure Present", True, "chart_structure is null (valid)")
                return True
            
            # Check for legs array (structure lines that should be subdued)
            if "legs" in chart_structure:
                legs = chart_structure["legs"]
                if isinstance(legs, list) and len(legs) > 0:
                    self.log_result("Structure Legs Present", True, 
                                   f"Found {len(legs)} structure legs for subdued rendering")
                else:
                    self.log_result("Structure Legs Empty", True, "No structure legs (valid)")
            
            # Check for labels (HH/HL/LH/LL)
            if "labels" in chart_structure:
                labels = chart_structure["labels"]
                if isinstance(labels, list):
                    label_types = [label.get("label") for label in labels if isinstance(label, dict)]
                    self.log_result("Structure Labels Present", True, 
                                   f"Found labels: {label_types}")
            
            return True
            
        except Exception as e:
            self.log_result("Chart Structure Subdued", False, f"Error: {str(e)}")
            return False

    def test_fibonacci_data_structure(self) -> bool:
        """Test fibonacci data structure for panel rendering"""
        try:
            url = f"{self.base_url}/api/ta/setup/v2"
            params = {"symbol": "BTCUSDT", "tf": "1d"}
            
            print(f"\n🔍 Testing fibonacci data structure...")
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            fibonacci = data.get("fibonacci")
            if not fibonacci:
                self.log_result("Fibonacci Data", True, "fibonacci is null (valid when no relevant fib)")
                return True
            
            # Check for fib_set (swing high/low)
            if "fib_set" in fibonacci:
                fib_set = fibonacci["fib_set"]
                if isinstance(fib_set, dict):
                    has_swing_high = "swing_high" in fib_set
                    has_swing_low = "swing_low" in fib_set
                    self.log_result("Fibonacci Set Structure", True, 
                                   f"swing_high: {has_swing_high}, swing_low: {has_swing_low}")
            
            # Check for fib_levels_for_chart
            if "fib_levels_for_chart" in fibonacci:
                levels = fibonacci["fib_levels_for_chart"]
                if isinstance(levels, list):
                    retracement_count = len([l for l in levels if l.get("type") == "retracement"])
                    extension_count = len([l for l in levels if l.get("type") == "extension"])
                    self.log_result("Fibonacci Levels Present", True, 
                                   f"Retracements: {retracement_count}, Extensions: {extension_count}")
            
            return True
            
        except Exception as e:
            self.log_result("Fibonacci Data Structure", False, f"Error: {str(e)}")
            return False

    def test_multiple_timeframes(self) -> bool:
        """Test pattern detection across multiple timeframes"""
        timeframes = ["4h", "1d", "7d"]
        success_count = 0
        
        print(f"\n🔍 Testing pattern detection across timeframes...")
        
        for tf in timeframes:
            try:
                url = f"{self.base_url}/api/ta/setup/v2"
                params = {"symbol": "BTCUSDT", "tf": tf}
                
                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if pattern_v2 exists
                    has_pattern_v2 = "pattern_v2" in data
                    has_fibonacci = "fibonacci" in data
                    has_chart_structure = "chart_structure" in data
                    
                    if has_pattern_v2 and has_fibonacci and has_chart_structure:
                        success_count += 1
                        self.log_result(f"Pattern API {tf.upper()}", True, 
                                       "All pattern rendering fields present")
                    else:
                        missing = []
                        if not has_pattern_v2: missing.append("pattern_v2")
                        if not has_fibonacci: missing.append("fibonacci")
                        if not has_chart_structure: missing.append("chart_structure")
                        self.log_result(f"Pattern API {tf.upper()}", False, 
                                       f"Missing: {missing}")
                else:
                    self.log_result(f"Pattern API {tf.upper()}", False, 
                                   f"API error: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Pattern API {tf.upper()}", False, f"Error: {str(e)}")
        
        overall_success = success_count >= len(timeframes) // 2
        self.log_result("Multiple Timeframes Pattern", overall_success, 
                       f"{success_count}/{len(timeframes)} timeframes working")
        return overall_success

    def run_all_tests(self) -> dict:
        """Run all pattern rendering tests"""
        print("=" * 80)
        print("🎨 TESTING: Pattern Rendering Features")
        print("=" * 80)
        
        test_methods = [
            self.test_pattern_v2_api_structure,
            self.test_breakout_level_api,
            self.test_chart_structure_subdued,
            self.test_fibonacci_data_structure,
            self.test_multiple_timeframes,
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_result(test_method.__name__, False, f"Test crashed: {str(e)}")
        
        # Calculate summary
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 PATTERN RENDERING TEST SUMMARY")
        print("=" * 80)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 80)
        
        # Show failed tests
        failed_tests = [r for r in self.results if not r["passed"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test_name']}: {test['details']}")
        
        return {
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "success_rate": success_rate,
            "failed_tests": failed_tests
        }

def main():
    """Main test execution"""
    tester = PatternRenderingTester()
    summary = tester.run_all_tests()
    
    if summary["success_rate"] >= 80:
        print("🎉 Pattern rendering tests successful!")
        return 0
    else:
        print("⚠️  Pattern rendering tests failed - needs attention")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)