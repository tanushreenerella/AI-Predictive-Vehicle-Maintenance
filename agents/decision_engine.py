from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from agents.tools.failure_tool import analyze_vehicle_data

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

agent = create_react_agent(
    model=llm,
    tools=[analyze_vehicle_data]
)

sensor_input = {
    "engine_rpm": 6200,
    "lub_oil_pressure": 1.8,
    "fuel_pressure": 2.1,
    "coolant_pressure": 1.5,
    "lub_oil_temp": 125,
    "coolant_temp": 110
}

result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": f"""
Analyze engine health using sensor data:
{sensor_input}

Call the failure prediction tool.
Give maintenance advice.
"""
        }
    ]
})

print(result["messages"][-1].content)
