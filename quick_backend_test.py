#!/usr/bin/env python3
"""
Quick MTF Backend Test
=====================
Test the MTF endpoint with shorter timeouts to verify functionality
"""

import requests
import json
import time

def quick_mtf_test():
    """Quick test of MTF endpoint"""
    base_url = "https://ta-module.preview.emergentagent.com"
    
    tests = [
        {
            "name": "TA Engine Status",
            "url": f"{base_url}/api/ta-engine/status",
            "timeout": 10
        },
        {
            "name": "MTF Single TF (4H)",
            "url": f"{base_url}/api/ta-engine/mtf/BTC?timeframes=4H",
            "timeout": 30
        },
        {
            "name": "MTF Multi TF (1D,4H)",
            "url": f"{base_url}/api/ta-engine/mtf/BTC?timeframes=1D,4H",
            "timeout": 45
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"\n🔍 Testing: {test['name']}")
        print(f"   URL: {test['url']}")
        
        start_time = time.time()
        try:
            response = requests.get(test['url'], timeout=test['timeout'])
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('ok', False)
                
                if success:
                    print(f"   ✅ SUCCESS ({duration:.1f}s)")
                    
                    # Extract key info
                    if 'tf_map' in data:
                        tf_keys = list(data['tf_map'].keys())
                        print(f"   📊 Timeframes: {tf_keys}")
                        
                        # Check for candles in each TF
                        for tf in tf_keys:
                            candles = data['tf_map'][tf].get('candles', [])
                            print(f"      {tf}: {len(candles)} candles")
                    
                    if 'mtf_context' in data:
                        print(f"   🎯 MTF Context: present")
                        
                else:
                    print(f"   ❌ FAILED - not ok")
                    
                results.append({
                    'test': test['name'],
                    'success': success,
                    'duration': duration,
                    'status': response.status_code
                })
            else:
                print(f"   ❌ FAILED - Status {response.status_code}")
                results.append({
                    'test': test['name'], 
                    'success': False,
                    'duration': duration,
                    'status': response.status_code
                })
                
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            print(f"   ⏰ TIMEOUT after {duration:.1f}s")
            results.append({
                'test': test['name'],
                'success': False, 
                'duration': duration,
                'error': 'timeout'
            })
        except Exception as e:
            duration = time.time() - start_time
            print(f"   ❌ ERROR: {str(e)}")
            results.append({
                'test': test['name'],
                'success': False,
                'duration': duration, 
                'error': str(e)
            })
    
    # Summary
    successful = len([r for r in results if r.get('success', False)])
    total = len(results)
    
    print(f"\n{'='*50}")
    print(f"📊 QUICK TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Passed: {successful}/{total}")
    
    for result in results:
        status = "✅" if result.get('success') else "❌"
        duration = result.get('duration', 0)
        print(f"{status} {result['test']} ({duration:.1f}s)")
    
    return results

if __name__ == "__main__":
    quick_mtf_test()