"""
tests/test_tools.py
Test all tools and dependencies
"""
import sys
import os
import json
import requests

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_dependencies():
    """Test if all required packages are installed"""
    print("🔍 Testing Dependencies...")
    print("="*50)
    
    dependencies = [
        ("langchain", "langchain"),
        ("langgraph", "langgraph"),
        ("langchain-groq", "langchain_groq"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("requests", "requests"),
        ("python-dotenv", "dotenv"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("scikit-learn", "sklearn"),
        ("xgboost", "xgboost"),
    ]
    
    results = []
    for name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {name}")
            results.append((name, True))
        except ImportError:
            print(f"❌ {name}")
            results.append((name, False))
    
    print("="*50)
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("🎉 All dependencies installed!")
    else:
        print("⚠️ Missing dependencies:")
        for name, passed in results:
            if not passed:
                print(f"  - pip install {name}")
    
    return all_passed

def test_fastapi_connection():
    """Test connection to FastAPI service"""
    print("\n🔌 Testing FastAPI Connection...")
    print("="*50)
    
    urls_to_test = [
        "http://localhost:8000/",
        "http://127.0.0.1:8000/",
        "http://0.0.0.0:8000/"
    ]
    
    for url in urls_to_test:
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print(f"✅ Connected to {url}")
                print(f"   Response: {response.json()}")
                return True, url
            else:
                print(f"⚠️ {url} returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to {url}")
        except Exception as e:
            print(f"⚠️ Error with {url}: {e}")
    
    print("="*50)
    print("❌ Could not connect to FastAPI service")
    print("Start it with: uvicorn ai_microservices.failure_agent_api:app --reload")
    return False, None

def test_prediction_endpoint():
    """Test the prediction endpoint"""
    print("\n🧪 Testing Prediction Endpoint...")
    print("="*50)
    
    test_data = {
        "engine_rpm": 3200.0,
        "lub_oil_pressure": 1.9,
        "fuel_pressure": 2.3,
        "coolant_pressure": 1.4,
        "lub_oil_temp": 95.0,
        "coolant_temp": 88.0
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/predict",
            json=test_data,
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Prediction successful!")
            print(f"\nPrediction Results:")
            print(json.dumps(result, indent=2))
            
            # Validate response structure
            required_fields = ["component", "failureProbability", "riskLevel"]
            missing = [field for field in required_fields if field not in result]
            
            if not missing:
                print("\n✅ Response structure valid")
                return True
            else:
                print(f"\n⚠️ Missing fields: {missing}")
                return False
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_orchestrator_tools():
    """Test orchestrator tool imports"""
    print("\n🛠️ Testing Orchestrator Tools...")
    print("="*50)
    
    try:
        # Test importing orchestrator modules
        from orchestrators.master_orchestrator import MasterOrchestrator
        from orchestrators.simple_orchestrator import SimpleOrchestrator
        from orchestrators.langgraph_basic import analyze_without_tools
        
        print("✅ Orchestrator modules imported successfully")
        
        # Test creating orchestrator
        try:
            orchestrator = MasterOrchestrator()
            print("✅ MasterOrchestrator created successfully")
        except Exception as e:
            print(f"⚠️ MasterOrchestrator creation: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Comprehensive Tests for ProactiveAI")
    print("="*60)
    
    test_results = []
    
    # Run tests
    test_results.append(("Dependencies", test_dependencies()))
    fastapi_ok, url = test_fastapi_connection()
    test_results.append(("FastAPI Connection", fastapi_ok))
    
    if fastapi_ok:
        test_results.append(("Prediction Endpoint", test_prediction_endpoint()))
    
    test_results.append(("Orchestrator Tools", test_orchestrator_tools()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30} {status}")
        if result:
            passed += 1
    
    print("="*60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready.")
        return True
    else:
        print(f"⚠️ {total - passed} test(s) failed. Please fix issues.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)