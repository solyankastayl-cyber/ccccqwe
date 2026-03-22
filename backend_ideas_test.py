#!/usr/bin/env python3
"""
Ideas API Backend Test
======================

Tests the Save Idea functionality for the technical analysis module:
1. POST /api/ta/ideas - Create new idea
2. GET /api/ta/ideas - List ideas
3. GET /api/ta/ideas/{id} - Get idea details
4. POST /api/ta/ideas/{id}/update - Update idea (create new version)
5. POST /api/ta/ideas/{id}/validate - Validate idea
6. GET /api/ta/ideas/{id}/timeline - Get idea timeline
7. DELETE /api/ta/ideas/{id} - Delete idea
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class IdeasAPITester:
    def __init__(self, base_url: str = "https://tech-analysis-15.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.created_idea_id = None
        
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

    def test_create_idea(self) -> Optional[str]:
        """Test 1: Create new idea via POST /api/ta/ideas"""
        print(f"\n🔍 Testing Create Idea...")
        
        try:
            url = f"{self.base_url}/api/ta/ideas"
            payload = {
                "asset": "BTCUSDT",
                "timeframe": "4H",
                "tags": ["test", "automation"],
                "notes": "Test idea created by automation"
            }
            
            print(f"   POST {url}")
            print(f"   Payload: {payload}")
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log_test("Create Idea", False, f"HTTP {response.status_code}: {response.text}")
                return None
            
            data = response.json()
            
            if not data.get("ok"):
                self.log_test("Create Idea", False, f"API error: {data.get('message', 'Unknown error')}")
                return None
            
            idea = data.get("idea", {})
            idea_id = idea.get("idea_id")
            
            if not idea_id:
                self.log_test("Create Idea", False, "No idea_id in response")
                return None
            
            # Validate idea structure
            required_fields = ["idea_id", "asset", "timeframe", "technical_bias", "confidence", "created_at"]
            missing_fields = [field for field in required_fields if field not in idea]
            
            if missing_fields:
                self.log_test("Create Idea", False, f"Missing fields in idea: {missing_fields}")
                return None
            
            self.created_idea_id = idea_id
            self.log_test("Create Idea", True, f"Created idea {idea_id} for {idea['asset']} {idea['timeframe']}")
            return idea_id
            
        except Exception as e:
            self.log_test("Create Idea", False, f"Request failed: {str(e)}")
            return None

    def test_list_ideas(self) -> bool:
        """Test 2: List ideas via GET /api/ta/ideas"""
        print(f"\n🔍 Testing List Ideas...")
        
        try:
            url = f"{self.base_url}/api/ta/ideas"
            
            print(f"   GET {url}")
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                self.log_test("List Ideas", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("ok"):
                self.log_test("List Ideas", False, f"API error: {data.get('message', 'Unknown error')}")
                return False
            
            ideas = data.get("ideas", [])
            count = data.get("count", 0)
            
            if count != len(ideas):
                self.log_test("List Ideas", False, f"Count mismatch: count={count}, actual={len(ideas)}")
                return False
            
            # Check if our created idea is in the list
            if self.created_idea_id:
                found_idea = any(idea.get("idea_id") == self.created_idea_id for idea in ideas)
                if not found_idea:
                    self.log_test("List Ideas", False, f"Created idea {self.created_idea_id} not found in list")
                    return False
            
            self.log_test("List Ideas", True, f"Listed {count} ideas successfully")
            return True
            
        except Exception as e:
            self.log_test("List Ideas", False, f"Request failed: {str(e)}")
            return False

    def test_get_idea(self, idea_id: str) -> bool:
        """Test 3: Get idea details via GET /api/ta/ideas/{id}"""
        print(f"\n🔍 Testing Get Idea Details...")
        
        try:
            url = f"{self.base_url}/api/ta/ideas/{idea_id}"
            
            print(f"   GET {url}")
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                self.log_test("Get Idea Details", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("ok"):
                self.log_test("Get Idea Details", False, f"API error: {data.get('message', 'Unknown error')}")
                return False
            
            idea = data.get("idea", {})
            
            if idea.get("idea_id") != idea_id:
                self.log_test("Get Idea Details", False, f"ID mismatch: expected {idea_id}, got {idea.get('idea_id')}")
                return False
            
            # Validate detailed structure
            required_fields = ["versions", "validations", "current_version", "status"]
            missing_fields = [field for field in required_fields if field not in idea]
            
            if missing_fields:
                self.log_test("Get Idea Details", False, f"Missing fields: {missing_fields}")
                return False
            
            versions = idea.get("versions", [])
            if not versions:
                self.log_test("Get Idea Details", False, "No versions found")
                return False
            
            self.log_test("Get Idea Details", True, f"Retrieved idea {idea_id} with {len(versions)} version(s)")
            return True
            
        except Exception as e:
            self.log_test("Get Idea Details", False, f"Request failed: {str(e)}")
            return False

    def test_update_idea(self, idea_id: str) -> bool:
        """Test 4: Update idea via POST /api/ta/ideas/{id}/update"""
        print(f"\n🔍 Testing Update Idea...")
        
        try:
            url = f"{self.base_url}/api/ta/ideas/{idea_id}/update"
            
            print(f"   POST {url}")
            response = requests.post(url, timeout=30)
            
            if response.status_code != 200:
                self.log_test("Update Idea", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("ok"):
                self.log_test("Update Idea", False, f"API error: {data.get('message', 'Unknown error')}")
                return False
            
            idea = data.get("idea", {})
            current_version = idea.get("current_version", 1)
            
            if current_version < 2:
                self.log_test("Update Idea", False, f"Version not incremented: {current_version}")
                return False
            
            self.log_test("Update Idea", True, f"Updated idea to version {current_version}")
            return True
            
        except Exception as e:
            self.log_test("Update Idea", False, f"Request failed: {str(e)}")
            return False

    def test_validate_idea(self, idea_id: str) -> bool:
        """Test 5: Validate idea via POST /api/ta/ideas/{id}/validate"""
        print(f"\n🔍 Testing Validate Idea...")
        
        try:
            url = f"{self.base_url}/api/ta/ideas/{idea_id}/validate"
            payload = {
                "current_price": 95000.0  # Mock current BTC price
            }
            
            print(f"   POST {url}")
            print(f"   Payload: {payload}")
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log_test("Validate Idea", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("ok"):
                self.log_test("Validate Idea", False, f"API error: {data.get('message', 'Unknown error')}")
                return False
            
            validation_result = data.get("validation_result")
            idea = data.get("idea", {})
            validations = idea.get("validations", [])
            
            if not validations:
                self.log_test("Validate Idea", False, "No validations found after validation")
                return False
            
            if not validation_result:
                self.log_test("Validate Idea", False, "No validation_result in response")
                return False
            
            self.log_test("Validate Idea", True, f"Validated idea with result: {validation_result}")
            return True
            
        except Exception as e:
            self.log_test("Validate Idea", False, f"Request failed: {str(e)}")
            return False

    def test_get_timeline(self, idea_id: str) -> bool:
        """Test 6: Get idea timeline via GET /api/ta/ideas/{id}/timeline"""
        print(f"\n🔍 Testing Get Timeline...")
        
        try:
            url = f"{self.base_url}/api/ta/ideas/{idea_id}/timeline"
            
            print(f"   GET {url}")
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                self.log_test("Get Timeline", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("ok"):
                self.log_test("Get Timeline", False, f"API error: {data.get('message', 'Unknown error')}")
                return False
            
            timeline = data.get("timeline", [])
            
            if not timeline:
                self.log_test("Get Timeline", False, "No timeline data found")
                return False
            
            # Check timeline structure
            for item in timeline:
                if "type" not in item or "timestamp" not in item:
                    self.log_test("Get Timeline", False, "Invalid timeline item structure")
                    return False
            
            self.log_test("Get Timeline", True, f"Retrieved timeline with {len(timeline)} events")
            return True
            
        except Exception as e:
            self.log_test("Get Timeline", False, f"Request failed: {str(e)}")
            return False

    def test_delete_idea(self, idea_id: str) -> bool:
        """Test 7: Delete idea via DELETE /api/ta/ideas/{id}"""
        print(f"\n🔍 Testing Delete Idea...")
        
        try:
            url = f"{self.base_url}/api/ta/ideas/{idea_id}"
            
            print(f"   DELETE {url}")
            response = requests.delete(url, timeout=30)
            
            if response.status_code != 200:
                self.log_test("Delete Idea", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("ok"):
                self.log_test("Delete Idea", False, f"API error: {data.get('message', 'Unknown error')}")
                return False
            
            # Verify idea is actually deleted by trying to get it
            time.sleep(1)  # Brief delay
            get_url = f"{self.base_url}/api/ta/ideas/{idea_id}"
            get_response = requests.get(get_url, timeout=30)
            
            if get_response.status_code == 200:
                get_data = get_response.json()
                if get_data.get("ok"):
                    self.log_test("Delete Idea", False, "Idea still exists after deletion")
                    return False
            
            self.log_test("Delete Idea", True, f"Successfully deleted idea {idea_id}")
            return True
            
        except Exception as e:
            self.log_test("Delete Idea", False, f"Request failed: {str(e)}")
            return False

    def test_list_with_filters(self) -> bool:
        """Test 8: List ideas with filters"""
        print(f"\n🔍 Testing List Ideas with Filters...")
        
        try:
            # Test with asset filter
            url = f"{self.base_url}/api/ta/ideas?asset=BTCUSDT&limit=10"
            
            print(f"   GET {url}")
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                self.log_test("List Ideas with Filters", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            if not data.get("ok"):
                self.log_test("List Ideas with Filters", False, f"API error: {data.get('message', 'Unknown error')}")
                return False
            
            ideas = data.get("ideas", [])
            
            # Verify all ideas are for BTCUSDT
            for idea in ideas:
                if idea.get("asset") != "BTCUSDT":
                    self.log_test("List Ideas with Filters", False, f"Filter failed: found {idea.get('asset')} instead of BTCUSDT")
                    return False
            
            self.log_test("List Ideas with Filters", True, f"Filter working: found {len(ideas)} BTCUSDT ideas")
            return True
            
        except Exception as e:
            self.log_test("List Ideas with Filters", False, f"Request failed: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all Ideas API tests"""
        print("=" * 60)
        print("IDEAS API BACKEND TEST")
        print("=" * 60)
        print(f"Testing endpoint: {self.base_url}/api/ta/ideas")
        print(f"Testing Save Idea functionality")
        
        # Test 1: Create idea
        idea_id = self.test_create_idea()
        
        if not idea_id:
            print("\n❌ Cannot proceed with further tests - Create Idea failed")
            return False
        
        # Test 2: List ideas
        self.test_list_ideas()
        
        # Test 3: Get idea details
        self.test_get_idea(idea_id)
        
        # Test 4: Update idea
        self.test_update_idea(idea_id)
        
        # Test 5: Validate idea
        self.test_validate_idea(idea_id)
        
        # Test 6: Get timeline
        self.test_get_timeline(idea_id)
        
        # Test 8: List with filters (before deleting)
        self.test_list_with_filters()
        
        # Test 7: Delete idea (last, as it removes the test data)
        self.test_delete_idea(idea_id)
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - Ideas API is working correctly")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} TESTS FAILED")
            return False

def main():
    """Main test execution"""
    tester = IdeasAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open("/tmp/ideas_api_test_results.json", "w") as f:
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