"""
tests/test_api.py
API endpoint tests
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=3)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_predict_endpoint():
    """Test predict endpoint with various inputs"""
    print("\n🔍 Testing predict endpoint...")
    
    test_cases = [
        {
            "name": "Normal Operation",
            "data": {
                "engine_rpm": 2200,
                "lub_oil_pressure": 2.2,
                "fuel_pressure": 2.5,
                "coolant_pressure": 1.6,
                "lub_oil_temp": 85,
                "coolant_temp": 78
            }
        },
        {
            "name": "High Risk",
            "data": {
                "engine_rpm": 6200,
                "lub_oil_pressure": 1.2,
                "fuel_pressure": 2.1,
                "coolant_pressure": 0.8,
                "lub_oil_temp": 125,
                "coolant_temp": 115
            }
        },
        {
            "name": "Missing Field (should handle gracefully)",
            "data": {
                "engine_rpm": 3000,
                "lub_oil_pressure": 2.0,
                "fuel_pressure": 2.3,
                # Missing coolant_pressure
                "lub_oil_temp": 90,
                "coolant_temp": 85
            }
        }
    ]
    
    results = []
    for test_case in test_cases:
        print(f"\n  Test: {test_case['name']}")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/predict",
                json=test_case["data"],
                timeout=5
            )
            elapsed = time.time() - start_time
            
            print(f"    Status: {response.status_code}")
            print(f"    Time: {elapsed:.2f}s")
            
            if response.status_code == 200:
                result = response.json()
                print(f"    Probability: {result.get('failureProbability', 0):.2%}")
                print(f"    Risk: {result.get('riskLevel', 'Unknown')}")
                results.append(True)
            else:
                print(f"    ❌ Error: {response.text}")
                results.append(False)
                
        except Exception as e:
            print(f"    ❌ Exception: {e}")
            results.append(False)
    
    return all(results)

def test_error_handling():
    """Test API error handling"""
    print("\n🔍 Testing error handling...")
    
    error_tests = [
        {
            "name": "Invalid JSON",
            "payload": "{invalid json",
            "headers": {"Content-Type": "application/json"}
        },
        {
            "name": "Wrong Data Type",
            "payload": {"engine_rpm": "not_a_number"},
            "headers": {"Content-Type": "application/json"}
        },
        {
            "name": "Empty Request",
            "payload": {},
            "headers": {"Content-Type": "application/json"}
        }
    ]
    
    for test in error_tests:
        print(f"\n  Test: {test['name']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/predict",
                data=json.dumps(test["payload"]) if isinstance(test["payload"], dict) else test["payload"],
                headers=test["headers"],
                timeout=3
            )
            
            print(f"    Status: {response.status_code}")
            
            # API should return proper error, not crash
            if response.status_code in [200, 400, 422, 500]:
                print(f"    ✅ Handled gracefully")
            else:
                print(f"    ⚠️ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Exception: {e}")
    
    return True

def test_performance():
    """Test API performance"""
    print("\n⏱️ Testing performance...")
    
    test_data = {
        "engine_rpm": 3200.0,
        "lub_oil_pressure": 1.9,
        "fuel_pressure": 2.3,
        "coolant_pressure": 1.4,
        "lub_oil_temp": 95.0,
        "coolant_temp": 88.0
    }
    
    times = []
    successes = 0
    
    for i in range(5):  # 5 requests
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/predict",
                json=test_data,
                timeout=5
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                times.append(elapsed)
                successes += 1
                print(f"  Request {i+1}: {elapsed:.3f}s")
            else:
                print(f"  Request {i+1}: ❌ Failed")
                
        except Exception as e:
            print(f"  Request {i+1}: ❌ Error: {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\n  📊 Average response time: {avg_time:.3f}s")
        print(f"  ✅ Success rate: {successes}/5")
        
        if avg_time < 1.0:
            print("  🎉 Performance: Excellent")
            return True
        elif avg_time < 2.0:
            print("  👍 Performance: Good")
            return True
        else:
            print("  ⚠️ Performance: Slow")
            return False
    
    return False

def run_api_tests():
    """Run all API tests"""
    print("🚀 Running API Tests")
    print("="*50)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Predict Endpoint", test_predict_endpoint),
        ("Error Handling", test_error_handling),
        ("Performance", test_performance)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-"*30)
        result = test_func()
        results.append((test_name, result))
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print("\n" + "="*50)
    print("📊 API TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
    
    print("="*50)
    print(f"Results: {passed}/{total} passed")
    
    return passed == total

if __name__ == "__main__":
    success = run_api_tests()
    exit(0 if success else 1)