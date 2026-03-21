#!/usr/bin/env python3

import requests
import json
import time

def test_endpoint(name, url, timeout=15):
    print(f"\n🔍 Testing {name}...")
    try:
        response = requests.get(url, timeout=timeout)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response OK: {data.get('ok', 'unknown')}")
            return True, data
        else:
            print(f"Error: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"Exception: {e}")
        return False, None

def main():
    base_url = "http://localhost:8001"
    
    # Test 1: MTF Endpoint
    success1, data1 = test_endpoint(
        "MTF Endpoint", 
        f"{base_url}/api/ta-engine/mtf/BTC?timeframes=1D,4H,1H"
    )
    
    # Test 2: Coinbase Health  
    success2, data2 = test_endpoint(
        "Coinbase Health",
        f"{base_url}/api/provider/coinbase/health"
    )
    
    # Test 3: TA Setup V2
    success3, data3 = test_endpoint(
        "TA Setup V2",
        f"{base_url}/api/ta/setup/v2?symbol=BTCUSDT&tf=1d"
    )
    
    # Test 4: TA Engine Status
    success4, data4 = test_endpoint(
        "TA Engine Status",
        f"{base_url}/api/ta-engine/status"
    )
    
    print(f"\n📊 Results:")
    print(f"MTF Endpoint: {'✅' if success1 else '❌'}")
    print(f"Coinbase Health: {'✅' if success2 else '❌'}")  
    print(f"TA Setup V2: {'✅' if success3 else '❌'}")
    print(f"TA Engine Status: {'✅' if success4 else '❌'}")
    
    if success1 and data1:
        tf_map = data1.get('tf_map', {})
        print(f"\nMTF tf_map contains: {list(tf_map.keys())}")
        for tf, tf_data in tf_map.items():
            candle_count = tf_data.get('candle_count', 0)
            current_price = tf_data.get('current_price', 0)
            print(f"  {tf}: {candle_count} candles, price: {current_price}")

if __name__ == "__main__":
    main()