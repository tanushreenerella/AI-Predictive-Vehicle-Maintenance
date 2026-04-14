def test_orchestrator_tool():
    """Test the orchestrator's tool directly"""
    print("\n🤖 Testing Orchestrator Tool")
    print("="*60)
    
    try:
        # Import the tool object
        from orchestrators.master_orchestrator import analyze_vehicle_data
        print("✅ Imported tool: analyze_vehicle_data")
        print(f"   Tool type: {type(analyze_vehicle_data)}")
        
        test_data = [
            {"engine_rpm": 6200, "lub_oil_pressure": 1.8},
            {"RPM": 3200, "oil_temp": 105, "coolant_temp": 98},
            {"engine_rpm": 2200, "fuel_pressure": 2.5, "coolant_pressure": 1.6}
        ]
        
        all_passed = True
        
        for i, data in enumerate(test_data, 1):
            print(f"\nTest {i}: Input data = {data}")
            try:
                # ✅ CORRECT: Use .invoke() method for tools
                result = analyze_vehicle_data.invoke({"sensor_data": data})
                print(f"✅ Tool returned: {len(result)} characters")
                
                if "Error" in result or "error" in result.lower():
                    print(f"❌ Contains error: {result[:100]}...")
                    all_passed = False
                else:
                    print(f"✅ Success! Preview: {result[:150]}...")
            except Exception as e:
                print(f"❌ Tool error: {e}")
                # Try alternative method
                try:
                    print("Trying alternative call...")
                    result = analyze_vehicle_data.run(data)
                    print(f"✅ Alternative worked! Result: {result[:100]}...")
                except Exception as e2:
                    print(f"❌ Alternative also failed: {e2}")
                    all_passed = False
        
        print("\n" + ("✅ Tool working correctly!" if all_passed else "❌ Some tests failed"))
        return all_passed
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False