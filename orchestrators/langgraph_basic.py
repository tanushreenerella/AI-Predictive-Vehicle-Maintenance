"""
orchestrators/langgraph_basic.py
Basic LangGraph agent without any tools
"""
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

def analyze_without_tools(sensor_data: dict, use_system_prompt: bool = True) -> str:
    """
    Analyze sensor data without using any external tools
    
    Args:
        sensor_data: Dictionary of sensor readings
        use_system_prompt: Whether to use system prompt
    
    Returns:
        Analysis text
    """
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    agent = create_react_agent(model=llm, tools=[])
    
    messages = []
    
    if use_system_prompt:
        system_msg = SystemMessage(content="""You are an AI vehicle diagnostic assistant.
Analyze sensor readings and provide maintenance advice.
Be concise but thorough.""")
        messages.append(system_msg)
    
    user_msg = HumanMessage(content=f"""
Vehicle Sensor Readings:

Engine RPM: {sensor_data.get('engine_rpm', 'N/A')}
Oil Pressure: {sensor_data.get('lub_oil_pressure', 'N/A')} bar  
Fuel Pressure: {sensor_data.get('fuel_pressure', 'N/A')} bar
Coolant Pressure: {sensor_data.get('coolant_pressure', 'N/A')} bar
Oil Temperature: {sensor_data.get('lub_oil_temp', 'N/A')}°C
Coolant Temperature: {sensor_data.get('coolant_temp', 'N/A')}°C

Provide analysis in this format:
1. 📊 Status Summary (Normal/Concerning/Critical)
2. ⚠️ Issues Detected
3. 🔧 Recommendations
4. ⏰ Urgency Level
""")
    messages.append(user_msg)
    
    result = agent.invoke({"messages": messages})
    return result["messages"][-1].content

if __name__ == "__main__":
    # Test with sample data
    sample_data = {
        "engine_rpm": 2500,
        "lub_oil_pressure": 2.1,
        "fuel_pressure": 2.4,
        "coolant_pressure": 1.3,
        "lub_oil_temp": 92,
        "coolant_temp": 87
    }
    
    print("🔧 Basic LangGraph Analysis (No Tools)")
    print("="*50)
    analysis = analyze_without_tools(sample_data)
    print(analysis)