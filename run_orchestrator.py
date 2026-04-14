"""
run_orchestrator.py
Main entry point for ProactiveAI Orchestrator System
"""
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print("🚗 PROACTIVEAI - AGENTIC VEHICLE MAINTENANCE ECOSYSTEM")
    print("="*70)
    print("🤖 Multi-Agent Predictive Maintenance System")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

def main():
    """Main entry point"""
    print_banner()
    
    while True:
        print("\n📋 **MAIN MENU**")
        print("="*70)
        print("1. 🤖 Master Orchestrator (Full Agentic System)")
        print("2. 🧪 Run Test Suite")
        print("3. 🔧 Simple Orchestrator (Debug Mode)")
        print("4. 📊 Test API Endpoints")
        print("5. 📁 Generate Test Data")
        print("6. 🚪 Exit")
        print("="*70)
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting Master Orchestrator...")
            try:
                from orchestrators.master_orchestrator import MasterOrchestrator
                orchestrator = MasterOrchestrator()
                orchestrator.run_interactive()
            except Exception as e:
                print(f"❌ Error: {e}")
                print("Please check:")
                print("1. .env file with GROQ_API_KEY")
                print("2. FastAPI is running: uvicorn ai_microservices.failure_agent_api:app --reload")
        
        elif choice == "2":
            print("\n🧪 Running Test Suite...")
            try:
                from tests.test_tools import run_all_tests
                run_all_tests()
            except Exception as e:
                print(f"❌ Test error: {e}")
        
        elif choice == "3":
            print("\n🔧 Starting Simple Orchestrator...")
            try:
                from orchestrators.simple_orchestrator import analyze_simple
                test_data = {
                    "engine_rpm": 3200,
                    "lub_oil_pressure": 1.9,
                    "fuel_pressure": 2.3,
                    "coolant_pressure": 1.4,
                    "lub_oil_temp": 95,
                    "coolant_temp": 88
                }
                result = analyze_simple(test_data)
                print("\n" + "="*50)
                print("📄 ANALYSIS RESULT:")
                print("="*50)
                print(result)
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == "4":
            print("\n📊 Testing API Endpoints...")
            try:
                from tests.test_api import run_api_tests
                run_api_tests()
            except Exception as e:
                print(f"❌ API test error: {e}")
        
        elif choice == "5":
            print("\n📁 Generating Test Data...")
            try:
                from tests.test_data_generator import generate_engine_data
                generate_engine_data(500)
                print("✅ Test data generated successfully!")
            except Exception as e:
                print(f"❌ Data generation error: {e}")
        
        elif choice == "6":
            print("\n👋 Exiting ProactiveAI...")
            print("Thank you for using Agentic Vehicle Maintenance System!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")
        
        # Ask if user wants to continue
        if choice != "6":
            cont = input("\nReturn to main menu? (y/n): ").strip().lower()
            if cont != 'y':
                print("👋 Goodbye!")
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()