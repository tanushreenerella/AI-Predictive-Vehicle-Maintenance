"""
orchestrators/master_orchestrator.py
MAIN Master Orchestrator Agent - Full implementation
"""
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.tools import tool
import requests

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# --------------------------------------------------
# Load environment
# --------------------------------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8001")

# --------------------------------------------------
# Tool 1: Failure Prediction Tool
# --------------------------------------------------
def normalize_sensor_keys(sensor_data: Dict[str, Any]) -> Dict[str, float]:
    key_map = {
        "Engine RPM": "engine_rpm",
        "Lubrication Oil Pressure": "lub_oil_pressure",
        "Fuel Pressure": "fuel_pressure",
        "Coolant Pressure": "coolant_pressure",
        "Lubrication Oil Temperature": "lub_oil_temp",
        "Coolant Temperature": "coolant_temp",
    }

    normalized = {}

    for human_key, api_key in key_map.items():
        if human_key in sensor_data:
            normalized[api_key] = float(sensor_data[human_key])

    return normalized
def analyze_vehicle_data(sensor_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predicts vehicle component failures from sensor data.
    Returns structured JSON with failureProbability, riskLevel, confidence, etc.
    """
    try:
        print(f"🔍 [DEBUG] Tool received: {sensor_data}")

        key_map = {
            "Engine RPM": "engine_rpm",
            "Lubrication Oil Pressure": "lub_oil_pressure",
            "Fuel Pressure": "fuel_pressure",
            "Coolant Pressure": "coolant_pressure",
            "Lubrication Oil Temperature": "lub_oil_temp",
            "Coolant Temperature": "coolant_temp",
        }

        defaults = {
            "engine_rpm": 3000.0,
            "lub_oil_pressure": 2.0,
            "fuel_pressure": 2.5,
            "coolant_pressure": 1.2,
            "lub_oil_temp": 90.0,
            "coolant_temp": 85.0
        }

        final_data = defaults.copy()
        for human_key, api_key in key_map.items():
            if human_key in sensor_data:
                try:
                    final_data[api_key] = float(sensor_data[human_key])
                except:
                    pass  # keep default

        print("🚀 FINAL DATA SENT TO MODEL:", final_data)

        # Call your prediction model
        response = requests.post(
            "http://localhost:8001/predict_flex",
            json=final_data,
            timeout=10
        )
        print(f"📥 [DEBUG] API Response: {response.status_code}")

        if response.status_code != 200:
            return {"error": f"API Error: {response.text}"}

        result = response.json()
        print("📦 MODEL OUTPUT:", result)

        # Return structured JSON
        return {
            "component": result.get("component", "Engine"),
            "failureProbability": float(result.get("failureProbability", 0)),
            "riskLevel": result.get("riskLevel", "LOW"),
            "confidence": float(result.get("confidence", 0)),
            "message": result.get("message", "Analysis complete"),
            "estimatedFailureWindow": result.get("estimatedFailureWindow", "")
        }

    except Exception as e:
        return {"error": str(e)}

# --------------------------------------------------
# Tool 2: Diagnostic Questions Tool
# --------------------------------------------------
@tool
def diagnostic_questions_tool(symptom: str = "") -> str:
    """
    Provides diagnostic questions based on symptoms.
    
    Args:
        symptom: Optional symptom description
    
    Returns:
        List of diagnostic questions
    """
    base_questions = [
        "1. Are there any unusual noises (knocking, rattling, squealing)?",
        "2. Have you seen any warning lights (check engine, oil, temperature)?",
        "3. Is there reduced power or acceleration?",
        "4. Have you noticed any fluid leaks under the vehicle?",
        "5. When was your last oil change and service?",
        "6. Are there starting issues (cranking but not starting)?",
        "7. Have you observed changes in fuel efficiency?",
        "8. Is there excessive smoke from the exhaust?",
        "9. Does the vehicle overheat during normal driving?",
        "10. Are there any vibrations at idle or while driving?"
    ]
    
    symptom_based = {
        "overheating": [
            "• Does the temperature gauge go above normal?",
            "• Is coolant level dropping frequently?",
            "• Does the radiator fan work properly?"
        ],
        "noise": [
            "• When does the noise occur (startup, acceleration, idle)?",
            "• Where is the noise coming from (front, back, engine, wheels)?",
            "• Does the noise change with speed or gear?"
        ],
        "electrical": [
            "• Are lights dimming or flickering?",
            "• Does the battery need frequent jumps?",
            "• Any issues with power windows/locks?"
        ]
    }
    
    response = "🩺 **DIAGNOSTIC QUESTIONS**\n\n"
    response += "General Questions:\n" + "\n".join(base_questions)
    
    if symptom:
        symptom = symptom.lower()
        for key, questions in symptom_based.items():
            if key in symptom:
                response += f"\n\nAdditional questions for {symptom}:\n"
                response += "\n".join(questions)
                break
    
    return response

# --------------------------------------------------
# Tool 3: Service Recommendation Tool
# --------------------------------------------------
@tool
def service_recommendation_tool(risk_level: str, component: str = "Engine") -> str:
    """
    Recommends service actions based on risk level.
    
    Args:
        risk_level: HIGH, MEDIUM, or LOW
        component: Affected component
    
    Returns:
        Service recommendations
    """
    risk_level = risk_level.upper()
    
    recommendations = {
        "HIGH": {
            "urgency": "🔴 IMMEDIATE ACTION REQUIRED",
            "actions": [
                "• Stop driving if safe to do so",
                "• Contact roadside assistance immediately",
                "• Schedule emergency service within 24 hours",
                "• Do not ignore - risk of catastrophic failure"
            ],
            "checklist": [
                f"Complete {component} diagnostic scan",
                "Fluid pressure and leak testing",
                "Component stress testing",
                "Emergency parts assessment",
                "Safety system verification"
            ],
            "estimated_cost": "$$$ (High - emergency service)",
            "timeframe": "Within 24 hours"
        },
        "MEDIUM": {
            "urgency": "🟡 SCHEDULE SERVICE SOON",
            "actions": [
                "• Schedule service within 3-7 days",
                "• Limit high-speed or long-distance driving",
                "• Monitor gauges and warning lights",
                "• Check fluid levels daily"
            ],
            "checklist": [
                f"Preventive {component} maintenance",
                "Component wear assessment",
                "Fluid analysis and replacement",
                "System calibration and tuning",
                "Performance optimization"
            ],
            "estimated_cost": "$$ (Medium - scheduled service)",
            "timeframe": "Within 1 week"
        },
        "LOW": {
            "urgency": "🟢 ROUTINE MAINTENANCE",
            "actions": [
                "• Schedule routine service within 2-4 weeks",
                "• Continue normal operation",
                "• Note any changes in performance",
                "• Regular maintenance check"
            ],
            "checklist": [
                f"Routine {component} inspection",
                "Performance benchmarking",
                "Software/firmware updates",
                "General system health check",
                "Preventive maintenance planning"
            ],
            "estimated_cost": "$ (Low - routine service)",
            "timeframe": "Within 1 month"
        }
    }
    
    if risk_level not in recommendations:
        return f"⚠️ Unknown risk level: {risk_level}"
    
    rec = recommendations[risk_level]
    
    return f"""
📋 **SERVICE RECOMMENDATIONS** - {component}

{rec['urgency']}

**Recommended Actions:**
{chr(10).join(rec['actions'])}

**Service Checklist:**
{chr(10).join(rec['checklist'])}

**Estimated Cost:** {rec['estimated_cost']}
**Timeframe:** {rec['timeframe']}
"""

# --------------------------------------------------
# Tool 4: RCA (Root Cause Analysis) Tool
# --------------------------------------------------
@tool
def rca_analysis_tool(component: str, symptoms: str) -> str:
    """
    Performs Root Cause Analysis for component failures.
    
    Args:
        component: Failed component
        symptoms: Observed symptoms
    
    Returns:
        RCA analysis
    """
    common_causes = {
        "engine": {
            "overheating": ["Coolant leak", "Thermostat failure", "Water pump issue", "Radiator blockage"],
            "knocking": ["Low oil pressure", "Worn bearings", "Fuel octane too low", "Timing issues"],
            "loss_of_power": ["Clogged fuel filter", "Turbo failure", "Catalytic converter blockage", "Sensor failure"]
        },
        "battery": {
            "not_charging": ["Alternator failure", "Belt issues", "Voltage regulator problem", "Wiring fault"],
            "draining_fast": ["Parasitic drain", "Old battery", "Short circuit", "Accessory left on"]
        },
        "brakes": {
            "squealing": ["Worn pads", "Rotor issues", "Dust contamination", "Missing shims"],
            "pulsating": ["Warped rotors", "Uneven wear", "Caliper issues", "ABS problems"]
        }
    }
    
    component = component.lower()
    symptoms = symptoms.lower()
    
    response = f"🔍 **ROOT CAUSE ANALYSIS** - {component.upper()}\n\n"
    response += f"Reported Symptoms: {symptoms}\n\n"
    
    if component in common_causes:
        response += "**Most Common Causes:**\n"
        for symptom_key, causes in common_causes[component].items():
            if symptom_key in symptoms or any(word in symptoms for word in symptom_key.split('_')):
                response += f"\nFor '{symptom_key.replace('_', ' ')}':\n"
                for cause in causes:
                    response += f"• {cause}\n"
    else:
        response += "**General Failure Causes:**\n"
        response += "• Wear and tear over time\n• Manufacturing defects\n• Improper maintenance\n• Environmental factors\n• Installation errors\n\n"
    
    response += "\n**Recommended Diagnostic Steps:**\n"
    response += "1. Visual inspection for obvious issues\n"
    response += "2. Diagnostic code scanning\n"
    response += "3. Component testing under load\n"
    response += "4. Compare with known failure patterns\n"
    response += "5. Check service history for patterns\n"
    
    return response

# --------------------------------------------------
# Master Orchestrator Class
# --------------------------------------------------
class MasterOrchestrator:
    """Main orchestrator agent for ProactiveAI"""
    
    def __init__(self, model: str = "llama-3.1-8b-instant"):
        """Initialize the orchestrator"""
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in .env file")
        
        self.llm = ChatGroq(
            model=model,
            temperature=0,
            api_key=GROQ_API_KEY,
            max_tokens=1500
        )
        
        # Create agent with all tools
        self.agent = create_react_agent(
            model=self.llm,
            tools=[
                analyze_vehicle_data,
                diagnostic_questions_tool,
                service_recommendation_tool,
                rca_analysis_tool
            ]
        )
        
        # System prompt
        self.system_prompt = SystemMessage(content="""You are the **Master Orchestrator Agent** for ProactiveAI - an intelligent vehicle maintenance system.

## ROLE & CAPABILITIES:
You coordinate between specialized tools to provide comprehensive vehicle health analysis.

## TOOLS AVAILABLE:
1. **analyze_vehicle_data** - Analyze sensor data for failure predictions
2. **diagnostic_questions_tool** - Get diagnostic questions for symptoms
3. **service_recommendation_tool** - Get service recommendations based on risk
4. **rca_analysis_tool** - Perform root cause analysis

## WORKFLOW:
1. ALWAYS start with analyze_vehicle_data when given sensor data
2. Interpret the results in plain language
3. Use service_recommendation_tool for action items
4. Use diagnostic_questions_tool if more info is needed
5. Use rca_analysis_tool for understanding underlying causes

## RESPONSE FORMAT:
🚨 **RISK ASSESSMENT**
[Summary]

🔍 **TECHNICAL ANALYSIS**  
[Detailed interpretation]

⚡ **IMMEDIATE ACTIONS**
[Urgent steps if needed]

🔧 **SERVICE RECOMMENDATIONS**
[Maintenance plan]

📋 **DIAGNOSTIC NEXT STEPS**
[What to check next]

Be professional, safety-focused, and provide actionable advice.
""")
        
        print(f"✅ Master Orchestrator initialized with model: {model}")
    
    def analyze(self, sensor_data: Dict[str, Any], user_context: str = "") -> Dict[str, Any]:
     try:
        print(f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - MASTER ORCHESTRATOR ANALYSIS")

        # 1️⃣ Call the predictive tool first
        tool_result = analyze_vehicle_data(sensor_data)

        # 2️⃣ Build your AI agent prompt
        user_content = f"""
**VEHICLE SENSOR DATA:** {sensor_data}
**ADDITIONAL CONTEXT:** {user_context or 'None'}
Analyze this data and include recommendations.
"""
        user_message = HumanMessage(content=user_content)
        ai_response = self.agent.invoke({"messages": [self.system_prompt, user_message]})
        ai_text = ai_response["messages"][-1].content

        # 3️⃣ Return combined results
        return {
            "timestamp": datetime.now().isoformat(),
            "sensor_data": sensor_data,
            "analysis": ai_text,
            "status": "success",
            "component": tool_result.get("component", "Master Orchestrator"),
            "failureProbability": tool_result.get("failureProbability", 0),
            "riskLevel": tool_result.get("riskLevel", "LOW"),
            "confidence": tool_result.get("confidence", 0),
            "estimatedFailureWindow": tool_result.get("estimatedFailureWindow", "")
        }

     except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "sensor_data": sensor_data,
            "analysis": f"❌ Orchestration failed: {str(e)}",
            "status": "error",
            "component": "Master Orchestrator",
            "failureProbability": 0,
            "riskLevel": "LOW",
            "confidence": 0,
            "estimatedFailureWindow": ""
        }
    def run_test_scenarios(self):
        """Run predefined test scenarios"""
        test_scenarios = [
            {
                "name": "🔴 HIGH RISK - Overheating Engine",
                "data": {
                    "engine_rpm": 6200,
                    "lub_oil_pressure": 1.2,
                    "fuel_pressure": 2.1,
                    "coolant_pressure": 0.8,
                    "lub_oil_temp": 135,
                    "coolant_temp": 115
                },
                "context": "Vehicle overheating, temperature warning light on"
            },
            {
                "name": "🟡 MEDIUM RISK - Oil Pressure Issues",
                "data": {
                    "engine_rpm": 3200,
                    "lub_oil_pressure": 1.5,
                    "fuel_pressure": 2.3,
                    "coolant_pressure": 1.4,
                    "lub_oil_temp": 105,
                    "coolant_temp": 95
                },
                "context": "Slight knocking noise, oil light flickering"
            },
            {
                "name": "🟢 LOW RISK - Normal Operation",
                "data": {
                    "engine_rpm": 2200,
                    "lub_oil_pressure": 2.2,
                    "fuel_pressure": 2.5,
                    "coolant_pressure": 1.6,
                    "lub_oil_temp": 85,
                    "coolant_temp": 78
                },
                "context": "Regular maintenance due soon"
            }
        ]
        
        print(f"\n{'#'*60}")
        print("🧪 RUNNING TEST SCENARIOS")
        print(f"{'#'*60}")
        
        results = []
        for scenario in test_scenarios:
            print(f"\n📋 Scenario: {scenario['name']}")
            print(f"📊 Data: {scenario['data']}")
            
            result = self.analyze(scenario['data'], scenario['context'])
            results.append(result)
            
            if scenario != test_scenarios[-1]:
                input("\n⏸️ Press Enter for next scenario...")
        
        return results
    
    def run_interactive(self):
        """Interactive command-line interface"""
        print(f"\n{'='*60}")
        print("🚗 PROACTIVEAI - MASTER ORCHESTRATOR")
        print(f"{'='*60}")
        
        while True:
            print("\n📋 **MAIN MENU**")
            print("1. 📊 Analyze custom sensor data")
            print("2. 🧪 Run test scenarios")
            print("3. 🔍 Diagnostic questions only")
            print("4. 📋 Service recommendations only")
            print("5. 🚪 Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                print("\n📝 Enter sensor data:")
                try:
                    sensor_data = {
                        "engine_rpm": float(input("Engine RPM: ") or "3000"),
                        "lub_oil_pressure": float(input("Lub Oil Pressure (bar): ") or "2.0"),
                        "fuel_pressure": float(input("Fuel Pressure (bar): ") or "2.5"),
                        "coolant_pressure": float(input("Coolant Pressure (bar): ") or "1.2"),
                        "lub_oil_temp": float(input("Lub Oil Temp (°C): ") or "90"),
                        "coolant_temp": float(input("Coolant Temp (°C): ") or "85")
                    }
                    
                    context = input("Additional context (press Enter to skip): ").strip()
                    
                    result = self.analyze(sensor_data, context)
                    
                    print(f"\n{'='*60}")
                    print("📄 **FINAL REPORT**")
                    print(f"{'='*60}")
                    print(result["analysis"])
                    
                    # Save to file
                    filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(filename, "w") as f:
                        f.write(f"ProactiveAI Analysis Report\n")
                        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Sensor Data: {json.dumps(sensor_data, indent=2)}\n")
                        f.write(f"\n{'='*60}\n")
                        f.write(result["analysis"])
                    
                    print(f"\n💾 Report saved to: {filename}")
                    
                except ValueError:
                    print("❌ Invalid input. Please enter numeric values.")
            
            elif choice == "2":
                self.run_test_scenarios()
            # In master_orchestrator.py, fix the menu options:

            elif choice == "3":  # Diagnostic questions
               symptom = input("Enter symptom description: ").strip()
             # Don't call tool directly, use the agent
               message = f"Provide diagnostic questions for: {symptom}"
               user_msg = HumanMessage(content=message)
               result = self.agent.invoke({"messages": [user_msg]})
               print(result["messages"][-1].content)

            elif choice == "4":  # Service recommendations
              risk = input("Risk level (HIGH/MEDIUM/LOW): ").strip().upper()
              component = input("Component (press Enter for Engine): ").strip() or "Engine"
            # Don't call tool directly, use the agent
              message = f"Provide service recommendations for {component} with {risk} risk level"
              user_msg = HumanMessage(content=message)
              result = self.agent.invoke({"messages": [user_msg]})
              print(result["messages"][-1].content)
            
            elif choice == "5":
                print("👋 Exiting Master Orchestrator...")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")

# --------------------------------------------------
# Main entry point
# --------------------------------------------------
if __name__ == "__main__":
    try:
        orchestrator = MasterOrchestrator()
        orchestrator.run_interactive()
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        print("Please check:")
        print("1. .env file exists with GROQ_API_KEY")
        print("2. FastAPI is running on localhost:8000")
        print("3. Required packages are installed")