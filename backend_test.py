#!/usr/bin/env python3
"""
Backend API Tests for Gusto Restaurant
Tests all backend endpoints with comprehensive validation
"""

import requests
import json
from datetime import datetime, timedelta

# Base URL from environment
BASE_URL = "https://gusto-restaurant-hub.preview.emergentagent.com/api"

def print_test_header(test_name):
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")

def print_result(passed, message):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {message}")

def check_no_mongodb_id(data, path="root"):
    """Recursively check for MongoDB _id fields"""
    if isinstance(data, dict):
        if "_id" in data:
            return False, f"Found _id at {path}"
        for key, value in data.items():
            result, msg = check_no_mongodb_id(value, f"{path}.{key}")
            if not result:
                return False, msg
    elif isinstance(data, list):
        for i, item in enumerate(data):
            result, msg = check_no_mongodb_id(item, f"{path}[{i}]")
            if not result:
                return False, msg
    return True, "No _id found"

def test_health():
    """Test 1: GET /api/health"""
    print_test_header("GET /api/health")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") == True:
                print_result(True, "Health check returned 200 with ok:true")
                return True
            else:
                print_result(False, f"Expected ok:true, got {data}")
                return False
        else:
            print_result(False, f"Expected 200, got {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False

def test_bootstrap():
    """Test 2: GET /api/bootstrap - comprehensive validation"""
    print_test_header("GET /api/bootstrap")
    
    try:
        response = requests.get(f"{BASE_URL}/bootstrap", timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print_result(False, f"Expected 200, got {response.status_code}")
            return False
        
        data = response.json()
        all_passed = True
        
        # Check for required keys
        required_keys = ["brand", "branches", "categories", "menuItems"]
        for key in required_keys:
            if key not in data:
                print_result(False, f"Missing key: {key}")
                all_passed = False
        
        if not all_passed:
            return False
        
        # Check branches count and structure
        branches = data.get("branches", [])
        print(f"\nBranches count: {len(branches)}")
        if len(branches) != 3:
            print_result(False, f"Expected 3 branches, got {len(branches)}")
            all_passed = False
        else:
            print_result(True, "Branches count is 3")
        
        # Check branch slugs
        expected_slugs = ["seoul-street", "white-gate", "tenger"]
        actual_slugs = [b.get("slug") for b in branches]
        print(f"Branch slugs: {actual_slugs}")
        if set(actual_slugs) != set(expected_slugs):
            print_result(False, f"Expected slugs {expected_slugs}, got {actual_slugs}")
            all_passed = False
        else:
            print_result(True, "All expected branch slugs present")
        
        # Check each branch has required nested arrays
        for branch in branches:
            slug = branch.get("slug", "unknown")
            if "openingHours" not in branch:
                print_result(False, f"Branch {slug} missing openingHours array")
                all_passed = False
            elif not isinstance(branch["openingHours"], list):
                print_result(False, f"Branch {slug} openingHours is not an array")
                all_passed = False
            
            if "testimonials" not in branch:
                print_result(False, f"Branch {slug} missing testimonials array")
                all_passed = False
            elif not isinstance(branch["testimonials"], list):
                print_result(False, f"Branch {slug} testimonials is not an array")
                all_passed = False
            
            if "gallery" not in branch:
                print_result(False, f"Branch {slug} missing gallery array")
                all_passed = False
            elif not isinstance(branch["gallery"], list):
                print_result(False, f"Branch {slug} gallery is not an array")
                all_passed = False
        
        if all([b.get("openingHours") is not None and b.get("testimonials") is not None and b.get("gallery") is not None for b in branches]):
            print_result(True, "All branches have openingHours, testimonials, and gallery arrays")
        
        # Check categories count
        categories = data.get("categories", [])
        print(f"\nCategories count: {len(categories)}")
        if len(categories) != 6:
            print_result(False, f"Expected 6 categories, got {len(categories)}")
            all_passed = False
        else:
            print_result(True, "Categories count is 6")
        
        # Check menuItems count
        menu_items = data.get("menuItems", [])
        print(f"MenuItems count: {len(menu_items)}")
        if len(menu_items) != 15:
            print_result(False, f"Expected 15 menuItems, got {len(menu_items)}")
            all_passed = False
        else:
            print_result(True, "MenuItems count is 15")
        
        # Check every menuItem has branchOverrides array
        items_without_overrides = []
        for item in menu_items:
            item_id = item.get("id", "unknown")
            if "branchOverrides" not in item:
                items_without_overrides.append(item_id)
            elif not isinstance(item["branchOverrides"], list):
                items_without_overrides.append(f"{item_id} (not array)")
        
        if items_without_overrides:
            print_result(False, f"MenuItems missing branchOverrides: {items_without_overrides}")
            all_passed = False
        else:
            print_result(True, "All menuItems have branchOverrides array")
        
        # CRITICAL: Check for MongoDB _id fields
        print("\nChecking for MongoDB _id fields...")
        no_id_check, msg = check_no_mongodb_id(data)
        if not no_id_check:
            print_result(False, f"CRITICAL: MongoDB _id found in response: {msg}")
            all_passed = False
        else:
            print_result(True, "No MongoDB _id fields found in response")
        
        # Check brand structure
        brand = data.get("brand", {})
        brand_keys = ["name", "tagline", "positioning", "phone", "social"]
        missing_brand_keys = [k for k in brand_keys if k not in brand]
        if missing_brand_keys:
            print_result(False, f"Brand missing keys: {missing_brand_keys}")
            all_passed = False
        else:
            print_result(True, "Brand has all required keys (name, tagline, positioning, phone, social)")
        
        return all_passed
        
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_reservations():
    """Test 3: POST /api/reservations - validation matrix"""
    print_test_header("POST /api/reservations - Validation Matrix")
    
    all_passed = True
    
    # Calculate a future date (1 year ahead to be safe)
    future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    print(f"Using future date: {future_date}")
    
    # Test 3a: Missing fields (no name)
    print("\n--- Test 3a: Missing name field ---")
    try:
        payload = {
            "branchId": "br-seoul-street",
            "phone": "99001122",
            "partySize": 2,
            "date": future_date,
            "time": "20:00"
        }
        response = requests.post(f"{BASE_URL}/reservations", json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            data = response.json()
            if data.get("error") == "MISSING_FIELDS":
                print_result(True, "Missing name correctly rejected with MISSING_FIELDS")
            else:
                print_result(False, f"Expected error:MISSING_FIELDS, got {data}")
                all_passed = False
        else:
            print_result(False, f"Expected 400, got {response.status_code}")
            all_passed = False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        all_passed = False
    
    # Test 3b: Past time
    print("\n--- Test 3b: Past time (2020-01-01) ---")
    try:
        payload = {
            "branchId": "br-seoul-street",
            "name": "Enkhjargal Batbayar",
            "phone": "99112233",
            "partySize": 2,
            "date": "2020-01-01",
            "time": "20:00"
        }
        response = requests.post(f"{BASE_URL}/reservations", json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            data = response.json()
            if data.get("error") == "PAST_TIME":
                print_result(True, "Past time correctly rejected with PAST_TIME")
            else:
                print_result(False, f"Expected error:PAST_TIME, got {data}")
                all_passed = False
        else:
            print_result(False, f"Expected 400, got {response.status_code}")
            all_passed = False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        all_passed = False
    
    # Test 3c: Before open (Seoul Street opens at 09:00)
    print("\n--- Test 3c: Before open (08:00, opens at 09:00) ---")
    try:
        payload = {
            "branchId": "br-seoul-street",
            "name": "Oyungerel Tsend",
            "phone": "88223344",
            "partySize": 4,
            "date": future_date,
            "time": "08:00"
        }
        response = requests.post(f"{BASE_URL}/reservations", json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            data = response.json()
            if data.get("error") == "BEFORE_OPEN":
                print_result(True, "Before open time correctly rejected with BEFORE_OPEN")
            else:
                print_result(False, f"Expected error:BEFORE_OPEN, got {data}")
                all_passed = False
        else:
            print_result(False, f"Expected 400, got {response.status_code}")
            all_passed = False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        all_passed = False
    
    # Test 3d: Success at Seoul Street (20:00, closesAt is null)
    print("\n--- Test 3d: Success at Seoul Street (20:00) ---")
    try:
        payload = {
            "branchId": "br-seoul-street",
            "name": "Boldbaatar Ganbold",
            "phone": "77665544",
            "partySize": 3,
            "date": future_date,
            "time": "20:00",
            "guestLocale": "en"
        }
        response = requests.post(f"{BASE_URL}/reservations", json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            # Check response structure
            if "id" in data and "status" in data and "phone" in data:
                if data.get("status") == "requested" and data.get("phone") == "+976 7733 6969":
                    print_result(True, "Reservation created successfully with correct response structure")
                    
                    # SECURITY: Check that response only contains id, status, phone
                    if set(data.keys()) == {"id", "status", "phone"}:
                        print_result(True, "SECURITY: Response contains only id, status, phone (no PII leak)")
                    else:
                        print_result(False, f"SECURITY: Response has unexpected keys: {list(data.keys())}")
                        all_passed = False
                else:
                    print_result(False, f"Expected status:requested and phone:+976 7733 6969, got {data}")
                    all_passed = False
            else:
                print_result(False, f"Missing required keys in response: {data}")
                all_passed = False
        else:
            print_result(False, f"Expected 200, got {response.status_code}")
            all_passed = False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        all_passed = False
    
    # Test 3e: Success at Tenger (no opening hours)
    print("\n--- Test 3e: Success at Tenger (no opening hours, 13:00) ---")
    try:
        payload = {
            "branchId": "br-tenger",
            "name": "Sarangerel Dorj",
            "phone": "99887766",
            "partySize": 2,
            "date": future_date,
            "time": "13:00",
            "guestLocale": "mn"
        }
        response = requests.post(f"{BASE_URL}/reservations", json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and data.get("status") == "requested":
                print_result(True, "Tenger reservation accepted (no opening hours constraint)")
            else:
                print_result(False, f"Unexpected response: {data}")
                all_passed = False
        else:
            print_result(False, f"Expected 200, got {response.status_code}")
            all_passed = False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        all_passed = False
    
    # Test 3f: SECURITY - Check GET /api/reservations does not exist
    print("\n--- Test 3f: SECURITY - GET /api/reservations should not exist ---")
    try:
        response = requests.get(f"{BASE_URL}/reservations", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 404:
            print_result(True, "SECURITY: GET /api/reservations returns 404 (no PII exposure)")
        else:
            # Check if it returns any reservation data
            try:
                data = response.json()
                if isinstance(data, list) or (isinstance(data, dict) and "reservations" in data):
                    print_result(False, "SECURITY ISSUE: GET endpoint returns reservation data!")
                    all_passed = False
                else:
                    print_result(True, "SECURITY: No reservation list exposed")
            except:
                print_result(True, "SECURITY: No JSON reservation data returned")
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        all_passed = False
    
    return all_passed

def test_seed():
    """Test 4: POST /api/seed - idempotency"""
    print_test_header("POST /api/seed - Idempotency Test")
    
    all_passed = True
    
    # First seed call
    print("\n--- First seed call ---")
    try:
        response = requests.post(f"{BASE_URL}/seed", timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") == True and data.get("seeded") == True:
                print_result(True, "First seed call successful")
            else:
                print_result(False, f"Expected ok:true, seeded:true, got {data}")
                all_passed = False
        else:
            print_result(False, f"Expected 200, got {response.status_code}")
            all_passed = False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        all_passed = False
    
    # Second seed call (idempotency check)
    print("\n--- Second seed call (idempotency) ---")
    try:
        response = requests.post(f"{BASE_URL}/seed", timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") == True and data.get("seeded") == True:
                print_result(True, "Second seed call successful (idempotent)")
            else:
                print_result(False, f"Expected ok:true, seeded:true, got {data}")
                all_passed = False
        else:
            print_result(False, f"Expected 200, got {response.status_code}")
            all_passed = False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        all_passed = False
    
    # Verify bootstrap still works with correct counts
    print("\n--- Verify bootstrap after seed ---")
    try:
        response = requests.get(f"{BASE_URL}/bootstrap", timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            branches_count = len(data.get("branches", []))
            categories_count = len(data.get("categories", []))
            items_count = len(data.get("menuItems", []))
            
            print(f"Branches: {branches_count}, Categories: {categories_count}, MenuItems: {items_count}")
            
            if branches_count == 3 and categories_count == 6 and items_count == 15:
                print_result(True, "Bootstrap counts correct after seed (3 branches, 6 categories, 15 items)")
            else:
                print_result(False, f"Incorrect counts: branches={branches_count}, categories={categories_count}, items={items_count}")
                all_passed = False
        else:
            print_result(False, f"Bootstrap failed with status {response.status_code}")
            all_passed = False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        all_passed = False
    
    return all_passed

def main():
    print("\n" + "="*80)
    print("GUSTO RESTAURANT BACKEND API TEST SUITE")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    results = {}
    
    # Run all tests
    results["health"] = test_health()
    results["bootstrap"] = test_bootstrap()
    results["reservations"] = test_reservations()
    results["seed"] = test_seed()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())
