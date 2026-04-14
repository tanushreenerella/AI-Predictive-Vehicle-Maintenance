"""
orchestrators/simple_orchestrator.py
Simple orchestrator for basic testing
"""
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

load_dotenv()

class SimpleOrchestrator:
    """Simple orchestrator without complex tools"""
    
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        # Agent without tools
        self.agent = create_react_agent(
            model=self.llm,
            tools=[]
        )
    
    def analyze(self, sensor_data: dict) -> str:
        """Simple analysis without tool calls"""
        message = HumanMessage(
            content=f"""You are a vehicle maintenance assistant.

Sensor Data:
- Engine RPM: {sensor_data.get('engine_rpm', 'N/A')}
- Oil Pressure: {sensor_data.get('lub_oil_pressure', 'N/A')} bar
- Fuel Pressure: {sensor_data.get('fuel_pressure', 'N/A')} bar
- Coolant Pressure: {sensor_data.get('coolant_pressure', 'N/A')} bar
- Oil Temperature: {sensor_data.get('lub_oil_temp', 'N/A')}°C
- Coolant Temperature: {sensor_data.get('coolant_temp', 'N/A')}°C

Normal Ranges:
- Engine RPM: 600-3000 (idle-cruising)
- Oil Pressure: 1.5-3.0 bar
- Fuel Pressure: 2.0-3.0 bar  
- Coolant Pressure: 1.0-1.5 bar
- Oil Temp: 80-110°C
- Coolant Temp: 80-100°C

Analyze if readings are normal, and give simple advice.
"""
        )
        
        result = self.agent.invoke({"messages": [message]})
        return result["messages"][-1].content

def analyze_simple(sensor_data: dict) -> str:
    """Quick analysis function"""
    orchestrator = SimpleOrchestrator()
    return orchestrator.analyze(sensor_data)

if __name__ == "__main__":
    test_data = {
        "engine_rpm": 3200,
        "lub_oil_pressure": 1.9,
        "fuel_pressure": 2.3,
        "coolant_pressure": 1.4,
        "lub_oil_temp": 95,
        "coolant_temp": 88
    }
    
    print("🤖 Simple Analysis:")
    result = analyze_simple(test_data)
    print(result)