import os

import requests
from langchain.agents import Tool, initialize_agent
from langchain_groq import ChatGroq


def call_failure_agent(sensor_data: dict):
    url = os.getenv("FAILURE_AGENT_URL", "http://127.0.0.1:8000/predict")
    response = requests.post(url, json=sensor_data, timeout=20)
    response.raise_for_status()
    return response.json()


failure_tool = Tool(
    name="FailurePredictionAgent",
    func=call_failure_agent,
    description="Predicts vehicle component failures from sensor data.",
)

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

agent = initialize_agent(
    tools=[failure_tool],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True,
)


if __name__ == "__main__":
    sensor_input = {
        "engine_rpm": 6200.0,
        "lub_oil_pressure": 1.8,
        "fuel_pressure": 2.1,
        "coolant_pressure": 1.5,
        "lub_oil_temp": 125.0,
        "coolant_temp": 110.0,
    }

    result = agent.run(f"Check vehicle health for these sensor readings: {sensor_input}")
    print(result)
