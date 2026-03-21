#!/usr/bin/env python3

import requests
import json
import time

def test_mtf_requirements():
    """Test the specific MTF requirements from the review request"""
    base_url = "http://localhost:8001"
    
    results = {
        "tests": [],
        "passed": 0,
        "total": 0
    }
    
    def log_test(name, success, details=""):
        results["tests"].append({
            "name": name,
            "success": success,
            "details": details
        })
        results["total"] += 1
        if success:
            results["passed"] += 1
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    {details}")
    
    # Test 1: MTF endpoint /api/ta-engine/mtf/BTC?timeframes=1D,4H,1H should return ok: true
    try:
        response = requests.get(f"{base_url}/api/ta-engine/mtf/BTC?timeframes=1D,4H,1H", timeout=20)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") == True:
                log_test("MTF endpoint returns ok: true", True, "Status 200, ok: true")
            else:
                log_test("MTF endpoint returns ok: true", False, f"ok: {data.get('ok')}")
        else:
            log_test("MTF endpoint returns ok: true", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("MTF endpoint returns ok: true", False, f"Error: {e}")
    
    # Test 2: tf_map should contain data for 1D, 4H, 1H
    try:
        response = requests.get(f"{base_url}/api/ta-engine/mtf/BTC?timeframes=1D,4H,1H", timeout=20)
        if response.status_code == 200:
            data = response.json()
            tf_map = data.get("tf_map", {})
            expected_tfs = ["1D", "4H", "1H"]
            missing = [tf for tf in expected_tfs if tf not in tf_map]
            if not missing:
                log_test("tf_map contains data for 1D, 4H, 1H", True, f"All timeframes present: {list(tf_map.keys())}")
            else:
                log_test("tf_map contains data for 1D, 4H, 1H", False, f"Missing: {missing}")
        else:
            log_test("tf_map contains data for 1D, 4H, 1H", False, f"API error: {response.status_code}")
    except Exception as e:
        log_test("tf_map contains data for 1D, 4H, 1H", False, f"Error: {e}")
    
    # Test 3: Each TF should have candle_count > 0
    try:
        response = requests.get(f"{base_url}/api/ta-engine/mtf/BTC?timeframes=1D,4H,1H", timeout=20)
        if response.status_code == 200:
            data = response.json()
            tf_map = data.get("tf_map", {})
            candle_counts = {}
            for tf, tf_data in tf_map.items():
                candle_count = tf_data.get("candle_count", 0)
                candle_counts[tf] = candle_count
            
            failed_tfs = [tf for tf, count in candle_counts.items() if count <= 0]
            if not failed_tfs:
                log_test("Each TF has candle_count > 0", True, f"Candle counts: {candle_counts}")
            else:
                log_test("Each TF has candle_count > 0", False, f"Zero candles: {failed_tfs}")
        else:
            log_test("Each TF has candle_count > 0", False, f"API error: {response.status_code}")
    except Exception as e:
        log_test("Each TF has candle_count > 0", False, f"Error: {e}")
    
    # Test 4: Each TF should have current_price > 0
    try:
        response = requests.get(f"{base_url}/api/ta-engine/mtf/BTC?timeframes=1D,4H,1H", timeout=20)
        if response.status_code == 200:
            data = response.json()
            tf_map = data.get("tf_map", {})
            prices = {}
            for tf, tf_data in tf_map.items():
                price = tf_data.get("current_price", 0)
                prices[tf] = price
            
            failed_tfs = [tf for tf, price in prices.items() if price <= 0]
            if not failed_tfs:
                log_test("Each TF has current_price > 0", True, f"Prices: {prices}")
            else:
                log_test("Each TF has current_price > 0", False, f"Zero prices: {failed_tfs}")
        else:
            log_test("Each TF has current_price > 0", False, f"API error: {response.status_code}")
    except Exception as e:
        log_test("Each TF has current_price > 0", False, f"Error: {e}")
    
    # Test 5: mtf_context should have alignment, tradeability, global_bias
    try:
        response = requests.get(f"{base_url}/api/ta-engine/mtf/BTC?timeframes=1D,4H,1H", timeout=20)
        if response.status_code == 200:
            data = response.json()
            mtf_context = data.get("mtf_context", {})
            required_fields = ["alignment", "tradeability", "global_bias"]
            missing = [field for field in required_fields if field not in mtf_context]
            
            if not missing:
                values = {field: mtf_context[field] for field in required_fields}
                log_test("mtf_context has alignment, tradeability, global_bias", True, f"Values: {values}")
            else:
                log_test("mtf_context has alignment, tradeability, global_bias", False, f"Missing: {missing}")
        else:
            log_test("mtf_context has alignment, tradeability, global_bias", False, f"API error: {response.status_code}")
    except Exception as e:
        log_test("mtf_context has alignment, tradeability, global_bias", False, f"Error: {e}")
    
    # Test 6: Coinbase provider health should be connected
    try:
        response = requests.get(f"{base_url}/api/provider/coinbase/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "")
            if status == "connected":
                log_test("Coinbase provider health is connected", True, f"Status: {status}")
            else:
                log_test("Coinbase provider health is connected", False, f"Status: {status}")
        else:
            log_test("Coinbase provider health is connected", False, f"API error: {response.status_code}")
    except Exception as e:
        log_test("Coinbase provider health is connected", False, f"Error: {e}")
    
    # Test 7: /api/ta/setup/v2 endpoint should work
    try:
        response = requests.get(f"{base_url}/api/ta/setup/v2?symbol=BTCUSDT&tf=1d", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and len(data) > 0:
                log_test("/api/ta/setup/v2 endpoint works", True, "Returns valid data")
            else:
                log_test("/api/ta/setup/v2 endpoint works", False, "Empty response")
        else:
            log_test("/api/ta/setup/v2 endpoint works", False, f"Status: {response.status_code}")
    except Exception as e:
        log_test("/api/ta/setup/v2 endpoint works", False, f"Error: {e}")
    
    print(f"\n📊 SUMMARY: {results['passed']}/{results['total']} tests passed ({results['passed']/results['total']*100:.1f}%)")
    return results

if __name__ == "__main__":
    results = test_mtf_requirements()
    print(f"\n🎯 All required MTF features: {'✅ WORKING' if results['passed'] == results['total'] else '⚠️ ISSUES FOUND'}")