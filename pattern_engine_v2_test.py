#!/usr/bin/env python3
"""
Pattern Engine V2 Backend Test Suite
====================================

Tests the new Pattern Engine V2 API endpoint /api/ta/setup/v2 
for production-level pattern detection with lifecycle management.

Tests:
1. /api/ta/setup/v2 - Should contain pattern_v2 field
2. Pattern V2 structure validation (primary_pattern, alternative_patterns)
3. Pattern lifecycle states (active/broken/invalidated/expired) 
4. Pattern types (triangles, wedges, channels, double top/bottom, H&S)
5. Pattern geometry (lines, breakout_level, invalidation_level)
6. Pattern scoring system
"""

import requests
import sys
import json
from datetime import datetime

class PatternEngineV2Tester:
    def __init__(self):
        # Use the public endpoint from frontend env
        self.base_url = "https://ta-context-engine.preview.emergentagent.com"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_result(self, test_name, passed, details="", expected=None, actual=None):
        """Log test result"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
        
        result = {
            "test": test_name,
            "status": "PASS" if passed else "FAIL",
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        if expected is not None and actual is not None:
            result["expected"] = expected
            result["actual"] = actual
            
        self.test_results.append(result)
        
        status_symbol = "✅" if passed else "❌"
        print(f"{status_symbol} {test_name}")
        if details:
            print(f"   {details}")
        if not passed and expected is not None:
            print(f"   Expected: {expected}, Got: {actual}")
        print()

    def test_setup_v2_pattern_field(self):
        """Test that /api/ta/setup/v2 contains pattern_v2 field"""
        print("🔍 Testing Setup V2 API for Pattern V2 field...")
        
        try:
            url = f"{self.base_url}/api/ta/setup/v2?symbol=BTCUSDT&tf=1D"
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                self.log_result(
                    "Setup V2 API Status", 
                    False, 
                    f"Expected 200, got {response.status_code}"
                )
                return False, None
            
            data = response.json()
            
            # Check for pattern_v2 field
            if "pattern_v2" not in data:
                self.log_result(
                    "Setup V2 Pattern V2 Field", 
                    False, 
                    "Response missing 'pattern_v2' field"
                )
                return False, None
            
            pattern_v2 = data["pattern_v2"]
            
            self.log_result(
                "Setup V2 Pattern V2 Field", 
                True, 
                "Pattern V2 field present in API response"
            )
            
            return True, pattern_v2
            
        except requests.RequestException as e:
            self.log_result("Setup V2 API Connection", False, f"Request failed: {str(e)}")
            return False, None
        except json.JSONDecodeError as e:
            self.log_result("Setup V2 API JSON", False, f"Invalid JSON response: {str(e)}")
            return False, None
        except Exception as e:
            self.log_result("Setup V2 API", False, f"Unexpected error: {str(e)}")
            return False, None

    def test_pattern_v2_structure(self, pattern_v2):
        """Test pattern_v2 data structure"""
        print("🔍 Testing Pattern V2 Structure...")
        
        if not pattern_v2:
            self.log_result(
                "Pattern V2 Structure", 
                False, 
                "Pattern V2 data is None or empty"
            )
            return False
        
        # Check for required top-level fields
        required_fields = ["primary_pattern", "alternative_patterns"]
        for field in required_fields:
            if field not in pattern_v2:
                self.log_result(
                    f"Pattern V2 Field: {field}", 
                    False, 
                    f"Missing required field: {field}"
                )
                return False
            else:
                self.log_result(
                    f"Pattern V2 Field: {field}", 
                    True, 
                    f"Field present"
                )
        
        # Check data types
        if not isinstance(pattern_v2.get("alternative_patterns"), list):
            self.log_result(
                "Alternative Patterns Type", 
                False, 
                "alternative_patterns should be a list"
            )
            return False
        else:
            alt_count = len(pattern_v2["alternative_patterns"])
            self.log_result(
                "Alternative Patterns Type", 
                True, 
                f"alternative_patterns is list with {alt_count} patterns"
            )
        
        # Rule: Maximum 1 primary + 1 alternative pattern
        primary = pattern_v2.get("primary_pattern")
        alternatives = pattern_v2.get("alternative_patterns", [])
        
        if len(alternatives) > 1:
            self.log_result(
                "Pattern Count Limit", 
                False, 
                f"Should have max 1 alternative pattern, got {len(alternatives)}"
            )
        else:
            self.log_result(
                "Pattern Count Limit", 
                True, 
                f"Pattern count within limits: 1 primary + {len(alternatives)} alternative"
            )
        
        return True

    def test_pattern_structure_details(self, pattern_v2):
        """Test individual pattern structure"""
        print("🔍 Testing Pattern Structure Details...")
        
        primary = pattern_v2.get("primary_pattern")
        alternatives = pattern_v2.get("alternative_patterns", [])
        
        # Test primary pattern structure (if exists)
        if primary:
            success = self._test_single_pattern_structure(primary, "Primary Pattern")
            if not success:
                return False
        else:
            self.log_result(
                "Primary Pattern Present", 
                True, 
                "No primary pattern detected (acceptable)"
            )
        
        # Test alternative pattern structure (if exists)
        for i, alt in enumerate(alternatives):
            success = self._test_single_pattern_structure(alt, f"Alternative Pattern {i+1}")
            if not success:
                return False
        
        return True

    def _test_single_pattern_structure(self, pattern, pattern_name):
        """Test structure of a single pattern"""
        
        # Required fields for any pattern
        required_fields = [
            "type", "direction_bias", "state", "scores",
            "breakout_level", "invalidation_level", "lines"
        ]
        
        for field in required_fields:
            if field not in pattern:
                self.log_result(
                    f"{pattern_name} Field: {field}", 
                    False, 
                    f"Missing required field: {field}"
                )
                return False
        
        # Test pattern type
        pattern_type = pattern.get("type", "")
        valid_types = [
            "descending_triangle", "ascending_triangle", "symmetrical_triangle",
            "falling_wedge", "rising_wedge",
            "ascending_channel", "descending_channel", "horizontal_channel",
            "double_top", "double_bottom",
            "head_shoulders", "inverse_head_shoulders"
        ]
        
        if pattern_type not in valid_types:
            self.log_result(
                f"{pattern_name} Type", 
                False, 
                f"Invalid pattern type: {pattern_type}. Valid types: {valid_types}"
            )
        else:
            self.log_result(
                f"{pattern_name} Type", 
                True, 
                f"Valid pattern type: {pattern_type}"
            )
        
        # Test direction bias
        direction_bias = pattern.get("direction_bias", "")
        valid_biases = ["bullish", "bearish", "neutral"]
        
        if direction_bias not in valid_biases:
            self.log_result(
                f"{pattern_name} Direction Bias", 
                False, 
                f"Invalid direction bias: {direction_bias}. Valid: {valid_biases}"
            )
        else:
            self.log_result(
                f"{pattern_name} Direction Bias", 
                True, 
                f"Valid direction bias: {direction_bias}"
            )
        
        # Test lifecycle state
        state = pattern.get("state", "")
        valid_states = ["forming", "active", "broken", "invalidated", "expired"]
        
        if state not in valid_states:
            self.log_result(
                f"{pattern_name} State", 
                False, 
                f"Invalid state: {state}. Valid: {valid_states}"
            )
        else:
            self.log_result(
                f"{pattern_name} State", 
                True, 
                f"Valid lifecycle state: {state}"
            )
        
        # Test scores structure
        scores = pattern.get("scores", {})
        if not isinstance(scores, dict):
            self.log_result(
                f"{pattern_name} Scores Type", 
                False, 
                "Scores should be a dictionary"
            )
            return False
        
        required_score_fields = [
            "geometry", "touch_quality", "containment", 
            "context_fit", "recency", "cleanliness", "total"
        ]
        
        for score_field in required_score_fields:
            if score_field not in scores:
                self.log_result(
                    f"{pattern_name} Score Field: {score_field}", 
                    False, 
                    f"Missing score field: {score_field}"
                )
                return False
        
        # Test total score is in valid range
        total_score = scores.get("total", 0)
        if not isinstance(total_score, (int, float)) or total_score < 0 or total_score > 1:
            self.log_result(
                f"{pattern_name} Total Score Range", 
                False, 
                f"Total score should be between 0 and 1, got: {total_score}"
            )
        else:
            self.log_result(
                f"{pattern_name} Total Score Range", 
                True, 
                f"Total score in valid range: {total_score:.3f}"
            )
        
        # Test levels are numeric
        breakout_level = pattern.get("breakout_level")
        invalidation_level = pattern.get("invalidation_level")
        
        if breakout_level is not None and not isinstance(breakout_level, (int, float)):
            self.log_result(
                f"{pattern_name} Breakout Level Type", 
                False, 
                f"Breakout level should be numeric, got: {type(breakout_level)}"
            )
        else:
            self.log_result(
                f"{pattern_name} Breakout Level", 
                True, 
                f"Breakout level: ${breakout_level}" if breakout_level else "No breakout level"
            )
        
        if invalidation_level is not None and not isinstance(invalidation_level, (int, float)):
            self.log_result(
                f"{pattern_name} Invalidation Level Type", 
                False, 
                f"Invalidation level should be numeric, got: {type(invalidation_level)}"
            )
        else:
            self.log_result(
                f"{pattern_name} Invalidation Level", 
                True, 
                f"Invalidation level: ${invalidation_level}" if invalidation_level else "No invalidation level"
            )
        
        # Test lines structure
        lines = pattern.get("lines", [])
        if not isinstance(lines, list):
            self.log_result(
                f"{pattern_name} Lines Type", 
                False, 
                "Lines should be a list"
            )
            return False
        
        if len(lines) == 0:
            self.log_result(
                f"{pattern_name} Lines Count", 
                False, 
                "Pattern should have at least one line"
            )
        else:
            self.log_result(
                f"{pattern_name} Lines Count", 
                True, 
                f"Pattern has {len(lines)} lines"
            )
        
        # Test individual line structure
        for i, line in enumerate(lines[:2]):  # Test first 2 lines
            if not isinstance(line, dict):
                self.log_result(
                    f"{pattern_name} Line {i+1} Type", 
                    False, 
                    "Each line should be a dictionary"
                )
                continue
            
            # Required line fields
            line_fields = ["name", "points", "touches"]
            for field in line_fields:
                if field not in line:
                    self.log_result(
                        f"{pattern_name} Line {i+1} Field: {field}", 
                        False, 
                        f"Missing line field: {field}"
                    )
                    continue
            
            # Test points structure
            points = line.get("points", [])
            if not isinstance(points, list):
                self.log_result(
                    f"{pattern_name} Line {i+1} Points Type", 
                    False, 
                    "Line points should be a list"
                )
                continue
            
            if len(points) < 2:
                self.log_result(
                    f"{pattern_name} Line {i+1} Points Count", 
                    False, 
                    "Line should have at least 2 points"
                )
            else:
                self.log_result(
                    f"{pattern_name} Line {i+1} Structure", 
                    True, 
                    f"Line '{line.get('name')}' with {len(points)} points and {line.get('touches', 0)} touches"
                )
        
        return True

    def test_pattern_lifecycle_validation(self, pattern_v2):
        """Test pattern lifecycle management"""
        print("🔍 Testing Pattern Lifecycle Validation...")
        
        primary = pattern_v2.get("primary_pattern")
        alternatives = pattern_v2.get("alternative_patterns", [])
        
        all_patterns = []
        if primary:
            all_patterns.append(("Primary", primary))
        for i, alt in enumerate(alternatives):
            all_patterns.append((f"Alternative {i+1}", alt))
        
        if not all_patterns:
            self.log_result(
                "Pattern Lifecycle Test", 
                True, 
                "No patterns to test lifecycle (acceptable)"
            )
            return True
        
        # Test that active patterns have reasonable scores
        for name, pattern in all_patterns:
            state = pattern.get("state", "")
            scores = pattern.get("scores", {})
            total_score = scores.get("total", 0)
            
            if state == "active" and total_score < 0.3:
                self.log_result(
                    f"{name} Lifecycle Consistency", 
                    False, 
                    f"Active pattern has low score: {total_score:.3f} (should be >= 0.3)"
                )
            elif state in ["broken", "invalidated", "expired"] and total_score > 0.8:
                self.log_result(
                    f"{name} Lifecycle Consistency", 
                    False, 
                    f"Inactive pattern has high score: {total_score:.3f} (inconsistent with state '{state}')"
                )
            else:
                self.log_result(
                    f"{name} Lifecycle Consistency", 
                    True, 
                    f"State '{state}' consistent with score {total_score:.3f}"
                )
        
        return True

    def test_pattern_geometry_validation(self, pattern_v2):
        """Test pattern geometry makes sense"""
        print("🔍 Testing Pattern Geometry Validation...")
        
        primary = pattern_v2.get("primary_pattern")
        if not primary:
            self.log_result(
                "Pattern Geometry Test", 
                True, 
                "No primary pattern to test geometry (acceptable)"
            )
            return True
        
        pattern_type = primary.get("type", "")
        lines = primary.get("lines", [])
        
        # Test triangles have upper and lower lines
        if "triangle" in pattern_type or "wedge" in pattern_type:
            line_names = [line.get("name", "") for line in lines]
            
            has_upper = any("upper" in name.lower() for name in line_names)
            has_lower = any("lower" in name.lower() for name in line_names)
            
            if not (has_upper and has_lower):
                self.log_result(
                    "Triangle/Wedge Geometry", 
                    False, 
                    f"Triangle/wedge should have upper and lower lines. Found: {line_names}"
                )
            else:
                self.log_result(
                    "Triangle/Wedge Geometry", 
                    True, 
                    f"Triangle/wedge has proper upper/lower lines: {line_names}"
                )
        
        # Test double patterns have peaks/valleys and neckline
        elif "double_" in pattern_type:
            line_names = [line.get("name", "") for line in lines]
            
            has_peaks_or_valleys = any(name in ["peaks", "valleys"] for name in line_names)
            has_neckline = any("neckline" in name.lower() for name in line_names)
            
            if not (has_peaks_or_valleys and has_neckline):
                self.log_result(
                    "Double Pattern Geometry", 
                    False, 
                    f"Double pattern should have peaks/valleys and neckline. Found: {line_names}"
                )
            else:
                self.log_result(
                    "Double Pattern Geometry", 
                    True, 
                    f"Double pattern has proper structure: {line_names}"
                )
        
        # Test H&S patterns have shoulders, head, neckline
        elif "head" in pattern_type or "shoulders" in pattern_type:
            line_names = [line.get("name", "") for line in lines]
            
            has_shoulders = any("shoulder" in name.lower() for name in line_names)
            has_head = any("head" in name.lower() for name in line_names)
            has_neckline = any("neckline" in name.lower() for name in line_names)
            
            if not (has_shoulders and has_head and has_neckline):
                self.log_result(
                    "H&S Pattern Geometry", 
                    False, 
                    f"H&S pattern should have shoulders, head, and neckline. Found: {line_names}"
                )
            else:
                self.log_result(
                    "H&S Pattern Geometry", 
                    True, 
                    f"H&S pattern has proper structure: {line_names}"
                )
        
        else:
            self.log_result(
                "Pattern Geometry", 
                True, 
                f"Pattern type '{pattern_type}' geometry not specifically validated"
            )
        
        return True

    def run_all_tests(self):
        """Run all Pattern Engine V2 tests"""
        print("=" * 70)
        print("🚀 STARTING PATTERN ENGINE V2 BACKEND TESTS")
        print("=" * 70)
        print()
        
        # Test 1: Basic API and Pattern V2 field presence
        api_success, pattern_v2 = self.test_setup_v2_pattern_field()
        if not api_success:
            print("\n❌ API test failed - cannot continue with pattern tests")
            return False
        
        # Test 2: Pattern V2 structure validation
        structure_success = self.test_pattern_v2_structure(pattern_v2)
        
        # Test 3: Individual pattern structure details
        details_success = self.test_pattern_structure_details(pattern_v2)
        
        # Test 4: Pattern lifecycle validation
        lifecycle_success = self.test_pattern_lifecycle_validation(pattern_v2)
        
        # Test 5: Pattern geometry validation
        geometry_success = self.test_pattern_geometry_validation(pattern_v2)
        
        # Summary
        print("=" * 70)
        print("📊 PATTERN ENGINE V2 TEST SUMMARY")
        print("=" * 70)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        
        # Pattern summary
        if pattern_v2:
            primary = pattern_v2.get("primary_pattern")
            alternatives = pattern_v2.get("alternative_patterns", [])
            
            print("\n🔍 DETECTED PATTERNS:")
            if primary:
                print(f"Primary: {primary.get('type', 'unknown')} ({primary.get('direction_bias', 'unknown')} bias, state: {primary.get('state', 'unknown')})")
                scores = primary.get("scores", {})
                print(f"  Score: {scores.get('total', 0):.3f} (geometry: {scores.get('geometry', 0):.2f}, touches: {scores.get('touch_quality', 0):.2f})")
            else:
                print("Primary: None detected")
            
            if alternatives:
                for i, alt in enumerate(alternatives):
                    print(f"Alternative {i+1}: {alt.get('type', 'unknown')} ({alt.get('direction_bias', 'unknown')} bias, state: {alt.get('state', 'unknown')})")
                    scores = alt.get("scores", {})
                    print(f"  Score: {scores.get('total', 0):.3f}")
            else:
                print("Alternatives: None detected")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL PATTERN ENGINE V2 TESTS PASSED!")
            return True
        else:
            print(f"\n❌ {self.tests_run - self.tests_passed} PATTERN ENGINE V2 TESTS FAILED")
            return False

def main():
    tester = PatternEngineV2Tester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())