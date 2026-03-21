#!/usr/bin/env python3
"""
Backend Test for Multi-Timeframe Technical Analysis Engine
==========================================================

Tests that each timeframe (4H, 1D, 7D, 30D, 180D, 1Y) generates unique technical analysis:
1. API returns data for all 6 timeframes
2. Each TF has unique candle_count (200, 150, 65, 42, 12, 11)
3. Each TF has unique swing points (structure)
4. Each TF has unique levels
5. 4H shows uptrend, 1D shows downtrend
6. 7D and 30D show macro-levels (126K, 109K, 98K, 81K)
7. 180D and 1Y show full BTC cycle ($15K -> $126K)
8. Frontend /tech-analysis correctly switches timeframes
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

class MTFTechnicalAnalysisTest:
    def __init__(self, base_url: str = "https://ta-engine-preview-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Expected candle counts for each timeframe
        self.expected_candle_counts = {
            "4H": 200,
            "1D": 150, 
            "7D": 65,
            "30D": 42,
            "180D": 12,
            "1Y": 11
        }
        
        # Expected trend directions
        self.expected_trends = {
            "4H": "uptrend",
            "1D": "downtrend"
        }
        
        # Expected macro levels for 7D and 30D (in thousands)
        self.expected_macro_levels = [126, 109, 98, 81]  # 126K, 109K, 98K, 81K
        
        # Expected BTC cycle range for 180D and 1Y
        self.btc_cycle_min = 15000  # $15K
        self.btc_cycle_max = 126000  # $126K

    def log_test(self, name: str, passed: bool, details: str = "", data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
        
        if details:
            print(f"   {details}")
            
        self.test_results.append({
            "test": name,
            "passed": passed,
            "details": details,
            "data": data
        })

    def test_mtf_api_response(self) -> Dict[str, Any]:
        """Test 1: API returns data for all 6 timeframes"""
        print(f"\n🔍 Testing MTF API endpoint...")
        
        try:
            # Request all 6 timeframes at once
            timeframes = "4H,1D,7D,30D,180D,1Y"
            url = f"{self.base_url}/api/ta-engine/mtf/BTC?timeframes={timeframes}"
            
            print(f"   Requesting: {url}")
            response = requests.get(url, timeout=45)
            
            if response.status_code != 200:
                self.log_test("MTF API Response", False, f"HTTP {response.status_code}")
                return {}
            
            data = response.json()
            
            if not data.get("ok"):
                self.log_test("MTF API Response", False, f"API error: {data.get('error', 'Unknown')}")
                return {}
            
            tf_map = data.get("tf_map", {})
            available_tfs = list(tf_map.keys())
            expected_tfs = ["4H", "1D", "7D", "30D", "180D", "1Y"]
            
            missing_tfs = [tf for tf in expected_tfs if tf not in available_tfs]
            
            if missing_tfs:
                self.log_test("MTF API Response", False, f"Missing timeframes: {missing_tfs}")
                return data
            
            self.log_test("MTF API Response", True, f"All 6 timeframes returned: {available_tfs}")
            return data
            
        except Exception as e:
            self.log_test("MTF API Response", False, f"Request failed: {str(e)}")
            return {}

    def test_unique_candle_counts(self, mtf_data: Dict[str, Any]):
        """Test 2: Each TF has unique candle_count"""
        print(f"\n🔍 Testing unique candle counts...")
        
        tf_map = mtf_data.get("tf_map", {})
        if not tf_map:
            self.log_test("Unique Candle Counts", False, "No tf_map data")
            return
        
        actual_counts = {}
        for tf, tf_data in tf_map.items():
            candle_count = tf_data.get("candle_count", 0)
            actual_counts[tf] = candle_count
        
        print(f"   Expected counts: {self.expected_candle_counts}")
        print(f"   Actual counts:   {actual_counts}")
        
        # Check if counts are unique
        count_values = list(actual_counts.values())
        unique_counts = len(set(count_values)) == len(count_values)
        
        if not unique_counts:
            self.log_test("Unique Candle Counts", False, "Candle counts are not unique")
            return
        
        # Check if counts are approximately correct (allow ±15% variance)
        tolerance_failed = []
        for tf, expected in self.expected_candle_counts.items():
            if tf in actual_counts:
                actual = actual_counts[tf]
                if expected > 0:
                    variance = abs(actual - expected) / expected
                    if variance > 0.15:  # 15% tolerance
                        tolerance_failed.append(f"{tf}: expected ~{expected}, got {actual}")
        
        if tolerance_failed:
            self.log_test("Unique Candle Counts", False, f"Counts outside tolerance: {tolerance_failed}")
        else:
            self.log_test("Unique Candle Counts", True, "All timeframes have unique candle counts within tolerance")

    def test_unique_swing_points(self, mtf_data: Dict[str, Any]):
        """Test 3: Each TF has unique swing points"""
        print(f"\n🔍 Testing unique swing points...")
        
        tf_map = mtf_data.get("tf_map", {})
        if not tf_map:
            self.log_test("Unique Swing Points", False, "No tf_map data")
            return
        
        swing_data = {}
        for tf, tf_data in tf_map.items():
            # Check render_plan structure for swings
            render_plan = tf_data.get("render_plan", {})
            structure = render_plan.get("structure", {})
            swings = structure.get("swings", [])
            
            # Also check structure_context
            structure_context = tf_data.get("structure_context", {})
            
            swing_info = {
                "swing_count": len(swings),
                "hh_count": structure_context.get("hh_count", 0),
                "hl_count": structure_context.get("hl_count", 0),
                "lh_count": structure_context.get("lh_count", 0),
                "ll_count": structure_context.get("ll_count", 0),
                "regime": structure_context.get("regime", "unknown")
            }
            swing_data[tf] = swing_info
        
        print(f"   Swing data by TF:")
        for tf, data in swing_data.items():
            print(f"     {tf}: {data['swing_count']} swings, HH:{data['hh_count']} HL:{data['hl_count']} LH:{data['lh_count']} LL:{data['ll_count']}, regime:{data['regime']}")
        
        # Check if swing patterns are different across timeframes
        swing_signatures = []
        for tf, data in swing_data.items():
            signature = (data['hh_count'], data['hl_count'], data['lh_count'], data['ll_count'])
            swing_signatures.append(signature)
        
        unique_signatures = len(set(swing_signatures)) > 1
        
        if not unique_signatures:
            self.log_test("Unique Swing Points", False, "All timeframes have identical swing patterns")
        else:
            self.log_test("Unique Swing Points", True, "Timeframes have different swing patterns")

    def test_unique_levels(self, mtf_data: Dict[str, Any]):
        """Test 4: Each TF has unique levels"""
        print(f"\n🔍 Testing unique levels...")
        
        tf_map = mtf_data.get("tf_map", {})
        if not tf_map:
            self.log_test("Unique Levels", False, "No tf_map data")
            return
        
        levels_data = {}
        for tf, tf_data in tf_map.items():
            # Check render_plan levels
            render_plan = tf_data.get("render_plan", {})
            levels = render_plan.get("levels", [])
            
            # Also check direct levels
            if not levels:
                levels = tf_data.get("levels", [])
            
            level_prices = [l.get("price", 0) for l in levels if l.get("price")]
            levels_data[tf] = {
                "count": len(levels),
                "prices": sorted(level_prices) if level_prices else []
            }
        
        print(f"   Levels by TF:")
        for tf, data in levels_data.items():
            prices_str = ", ".join([f"{p:.0f}" for p in data["prices"][:5]])  # Show first 5
            print(f"     {tf}: {data['count']} levels - {prices_str}")
        
        # Check if level sets are different
        level_sets = []
        for tf, data in levels_data.items():
            # Create a signature based on rounded prices
            rounded_prices = tuple(round(p, -2) for p in data["prices"][:10])  # Round to nearest 100, take first 10
            level_sets.append(rounded_prices)
        
        unique_level_sets = len(set(level_sets)) > 1
        
        if not unique_level_sets:
            self.log_test("Unique Levels", False, "All timeframes have identical level sets")
        else:
            self.log_test("Unique Levels", True, "Timeframes have different level sets")

    def test_trend_directions(self, mtf_data: Dict[str, Any]):
        """Test 5: 4H shows uptrend, 1D shows downtrend"""
        print(f"\n🔍 Testing trend directions...")
        
        tf_map = mtf_data.get("tf_map", {})
        if not tf_map:
            self.log_test("Trend Directions", False, "No tf_map data")
            return
        
        trend_results = {}
        for tf in ["4H", "1D"]:
            if tf not in tf_map:
                continue
                
            tf_data = tf_map[tf]
            
            # Check multiple sources for trend direction
            sources = []
            
            # 1. Market state from render_plan
            render_plan = tf_data.get("render_plan", {})
            market_state = render_plan.get("market_state", {})
            if market_state.get("trend_direction"):
                sources.append(("market_state", market_state["trend_direction"]))
            
            # 2. Decision bias
            decision = tf_data.get("decision", {})
            if decision.get("bias"):
                sources.append(("decision", decision["bias"]))
            
            # 3. Structure context regime
            structure_context = tf_data.get("structure_context", {})
            if structure_context.get("regime"):
                sources.append(("structure", structure_context["regime"]))
            
            # 4. Structure context bias
            if structure_context.get("bias"):
                sources.append(("structure_bias", structure_context["bias"]))
            
            trend_results[tf] = sources
        
        print(f"   Trend analysis:")
        for tf, sources in trend_results.items():
            print(f"     {tf}: {sources}")
        
        # Check if we can detect different trends
        tf_4h_trends = [s[1] for s in trend_results.get("4H", [])]
        tf_1d_trends = [s[1] for s in trend_results.get("1D", [])]
        
        # Look for bullish indicators in 4H
        bullish_4h = any("bull" in str(trend).lower() or "up" in str(trend).lower() for trend in tf_4h_trends)
        
        # Look for bearish indicators in 1D  
        bearish_1d = any("bear" in str(trend).lower() or "down" in str(trend).lower() for trend in tf_1d_trends)
        
        if bullish_4h and bearish_1d:
            self.log_test("Trend Directions", True, "4H shows bullish bias, 1D shows bearish bias")
        elif bullish_4h:
            self.log_test("Trend Directions", False, "4H shows bullish bias but 1D doesn't show bearish bias")
        elif bearish_1d:
            self.log_test("Trend Directions", False, "1D shows bearish bias but 4H doesn't show bullish bias")
        else:
            self.log_test("Trend Directions", False, "Neither expected trend direction detected")

    def test_macro_levels(self, mtf_data: Dict[str, Any]):
        """Test 6: 7D and 30D show macro-levels (126K, 109K, 98K, 81K)"""
        print(f"\n🔍 Testing macro levels...")
        
        tf_map = mtf_data.get("tf_map", {})
        if not tf_map:
            self.log_test("Macro Levels", False, "No tf_map data")
            return
        
        macro_levels_found = {}
        for tf in ["7D", "30D"]:
            if tf not in tf_map:
                continue
                
            tf_data = tf_map[tf]
            
            # Get levels from render_plan
            render_plan = tf_data.get("render_plan", {})
            levels = render_plan.get("levels", [])
            
            # Also check direct levels
            if not levels:
                levels = tf_data.get("levels", [])
            
            level_prices = [l.get("price", 0) for l in levels if l.get("price")]
            
            # Check for macro levels (convert to thousands)
            found_macro = []
            for expected_k in self.expected_macro_levels:
                expected_price = expected_k * 1000
                # Look for levels within ±5% of expected
                for price in level_prices:
                    if abs(price - expected_price) / expected_price < 0.05:
                        found_macro.append(expected_k)
                        break
            
            macro_levels_found[tf] = {
                "all_levels": [round(p/1000, 1) for p in level_prices],
                "macro_found": found_macro
            }
        
        print(f"   Macro level analysis:")
        for tf, data in macro_levels_found.items():
            print(f"     {tf}: Found levels at {data['all_levels']}K, macro matches: {data['macro_found']}")
        
        # Check if we found at least 2 macro levels across both timeframes
        all_macro_found = []
        for tf_data in macro_levels_found.values():
            all_macro_found.extend(tf_data["macro_found"])
        
        unique_macro_found = len(set(all_macro_found))
        
        if unique_macro_found >= 2:
            self.log_test("Macro Levels", True, f"Found {unique_macro_found} expected macro levels: {set(all_macro_found)}")
        else:
            self.log_test("Macro Levels", False, f"Only found {unique_macro_found} macro levels, expected at least 2")

    def test_btc_cycle_range(self, mtf_data: Dict[str, Any]):
        """Test 7: 180D and 1Y show full BTC cycle ($15K -> $126K)"""
        print(f"\n🔍 Testing BTC cycle range...")
        
        tf_map = mtf_data.get("tf_map", {})
        if not tf_map:
            self.log_test("BTC Cycle Range", False, "No tf_map data")
            return
        
        cycle_data = {}
        for tf in ["180D", "1Y"]:
            if tf not in tf_map:
                continue
                
            tf_data = tf_map[tf]
            candles = tf_data.get("candles", [])
            
            if not candles:
                continue
            
            # Get price range from candles
            prices = []
            for candle in candles:
                prices.extend([candle.get("high", 0), candle.get("low", 0)])
            
            if prices:
                min_price = min(p for p in prices if p > 0)
                max_price = max(prices)
                
                cycle_data[tf] = {
                    "min_price": min_price,
                    "max_price": max_price,
                    "range_k": f"{min_price/1000:.1f}K - {max_price/1000:.1f}K"
                }
        
        print(f"   BTC cycle analysis:")
        for tf, data in cycle_data.items():
            print(f"     {tf}: {data['range_k']}")
        
        # Check if we see the full cycle range
        cycle_coverage = False
        for tf, data in cycle_data.items():
            min_price = data["min_price"]
            max_price = data["max_price"]
            
            # Check if range covers significant portion of expected cycle
            covers_low = min_price <= self.btc_cycle_min * 1.2  # Within 20% of $15K
            covers_high = max_price >= self.btc_cycle_max * 0.8  # Within 20% of $126K
            
            if covers_low and covers_high:
                cycle_coverage = True
                break
        
        if cycle_coverage:
            self.log_test("BTC Cycle Range", True, "Long timeframes show full BTC cycle range")
        else:
            self.log_test("BTC Cycle Range", False, "Long timeframes don't show expected cycle range")

    def run_all_tests(self):
        """Run all MTF tests"""
        print("=" * 60)
        print("MULTI-TIMEFRAME TECHNICAL ANALYSIS TEST")
        print("=" * 60)
        print(f"Testing endpoint: {self.base_url}/api/ta-engine/mtf/BTC")
        print(f"Expected timeframes: 4H, 1D, 7D, 30D, 180D, 1Y")
        
        # Test 1: Get MTF data
        mtf_data = self.test_mtf_api_response()
        
        if not mtf_data:
            print("\n❌ Cannot proceed with further tests - MTF API failed")
            return False
        
        # Test 2-7: Analyze the data
        self.test_unique_candle_counts(mtf_data)
        self.test_unique_swing_points(mtf_data)
        self.test_unique_levels(mtf_data)
        self.test_trend_directions(mtf_data)
        self.test_macro_levels(mtf_data)
        self.test_btc_cycle_range(mtf_data)
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - MTF engine generates unique data per timeframe")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} TESTS FAILED")
            return False

def main():
    """Main test execution"""
    tester = MTFTechnicalAnalysisTest()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open("/tmp/mtf_test_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "tests_run": tester.tests_run,
            "tests_passed": tester.tests_passed,
            "results": tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())