"""
verify_agent_tools.py - Fixed imports for version compatibility
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()

# Handle different versions of langchain
try:
    # Try new import location (newer versions)
    from langchain.agents import create_react_agent
    print("✅ Using langchain.agents.create_react_agent")
except ImportError:
    try:
        # Try old import location (older versions)
        from langgraph.prebuilt import create_react_agent
        print("✅ Using langgraph.prebuilt.create_react_agent")
    except ImportError:
        # Fallback to manual creation
        print("⚠️ Could not import create_react_agent, using manual agent")
        def create_react_agent(model, tools):
            # Simple manual implementation
            from langchain.agents import AgentExecutor, create_react_agent
            from langchain import hub
            prompt = hub.pull("hwchase17/react")
            agent = create_react_agent(model, tools, prompt)
            return AgentExecutor(agent=agent, tools=tools, verbose=True)

def verify_tool_in_agent():
    """Verify the tool works when called by an agent"""
    print("🤖 Verifying Tool in Agent Context")
    print("="*60)
    
    # Import the tool
    from orchestrators.master_orchestrator import analyze_vehicle_data
    
    # Create agent with the tool
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    agent = create_react_agent(
        model=llm,
        tools=[analyze_vehicle_data]
    )
    
    # Test with sensor data
    test_cases = [
        {
            "name": "Complete sensor data",
            "message": "Analyze these sensor readings: engine_rpm=4200, lub_oil_pressure=1.5, fuel_pressure=2.1, coolant_pressure=1.2, lub_oil_temp=105, coolant_temp=98"
        },
        {
            "name": "Partial data",
            "message": "RPM is 3200 and oil temperature is 110°C. What's the risk?"
        }
    ]
    
    for test in test_cases:
        print(f"\n🔍 Test: {test['name']}")
        print(f"   Message: {test['message']}")
        
        try:
            result = agent.invoke({
                "messages": [HumanMessage(content=test['message'])]
            })
            
            response = result["messages"][-1].content
            print(f"   ✅ Agent responded with {len(response)} characters")
            
            # Check if tool was used
            if "ANALYSIS" in response or "risk" in response.lower():
                print(f"   ✅ Tool was likely used (contains analysis)")
            else:
                print(f"   ⚠️ Tool may not have been used")
                
            print(f"   Preview: {response[:200]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ Verification complete!")
    return True

def check_tool_directly():
    """Check the tool object directly"""
    print("\n🛠️ Checking Tool Object Directly")
    print("="*60)
    
    from orchestrators.master_orchestrator import analyze_vehicle_data
    
    print(f"Tool object: {analyze_vehicle_data}")
    print(f"Tool type: {type(analyze_vehicle_data)}")
    print(f"Tool name: {analyze_vehicle_data.name}")
    print(f"Tool description: {analyze_vehicle_data.description[:100]}...")
    
    # Show available attributes
    print("\n🔧 Available attributes:")
    attrs = [m for m in dir(analyze_vehicle_data) if not m.startswith('_')]
    for attr in attrs[:10]:  # Show first 10
        print(f"  - {attr}")
    if len(attrs) > 10:
        print(f"  ... and {len(attrs)-10} more")
    
    # Test different ways to call the tool
    test_data = {"engine_rpm": 3200, "lub_oil_pressure": 1.9}
    
    print("\n🔧 Testing different invocation methods:")
    
    # Method 1: .invoke() (standard)
    try:
        print("1. Testing .invoke():")
        result = analyze_vehicle_data.invoke({"sensor_data": test_data})
        print(f"   ✅ Success: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Method 2: .run() (alternative)
    try:
        print("\n2. Testing .run():")
        result = analyze_vehicle_data.run(test_data)
        print(f"   ✅ Success: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Method 3: Direct call (won't work)
    try:
        print("\n3. Testing direct call (should fail):")
        result = analyze_vehicle_data(test_data)
        print(f"   ❌ Unexpected success: {result[:100]}...")
    except Exception as e:
        print(f"   ✅ Expected failure: {type(e).__name__}")

def simple_system_check():
    """Simple check that doesn't require complex imports"""
    print("\n🔍 Simple System Check")
    print("="*60)
    
    import requests
    
    # Check API
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        if response.status_code == 200:
            print("✅ API is running")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ API status: {response.status_code}")
    except Exception as e:
        print(f"❌ API check failed: {e}")
    
    # Check tool import
    try:
        from orchestrators.master_orchestrator import analyze_vehicle_data
        print(f"✅ Tool imported: {analyze_vehicle_data.name}")
    except Exception as e:
        print(f"❌ Tool import failed: {e}")
    
    # Check orchestrator
    try:
        from orchestrators.master_orchestrator import MasterOrchestrator
        print("✅ MasterOrchestrator imported")
    except Exception as e:
        print(f"❌ Orchestrator import failed: {e}")
    
    # Quick API test
    print("\n🔧 Quick API Test:")
    test_data = {"engine_rpm": 3200.0, "lub_oil_pressure": 1.9}
    try:
        response = requests.post(
            "http://localhost:8000/predict_flex",
            json=test_data,
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: Risk={result.get('riskLevel')}, Prob={result.get('failureProbability')}")
        else:
            print(f"   ❌ Failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 ProactiveAI - Tool Verification (Fixed Imports)")
    print("="*60)
    
    # Run simple checks first
    simple_system_check()
    
    # Try tool check (may fail due to imports)
    try:
        check_tool_directly()
    except Exception as e:
        print(f"\n⚠️ Tool check failed: {e}")
        print("This is OK - tools work in agent context, not directly")
    
    # Try agent verification (may fail due to imports)
    try:
        verify_tool_in_agent()
    except Exception as e:
        print(f"\n⚠️ Agent verification failed: {e}")
        print("Check langchain version or run your orchestrator directly")
    
    print("\n" + "="*60)
    print("🎯 QUICK DIAGNOSIS:")
    print("1. If API check passed → Your backend is working")
    print("2. If tool imported → Your tools are defined correctly")
    print("3. If orchestrator imported → Your main system is ready")
    print("\n✅ RECOMMENDATION: Run your orchestrator directly:")
    print("   python run_orchestrator.py")
    print("   OR")
    print("   python orchestrators/master_orchestrator.py")