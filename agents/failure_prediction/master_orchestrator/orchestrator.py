from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
import requests

# Tool: Call Failure Prediction Agent
def call_failure_agent(sensor_data: dict):
    url = "http://127.0.0.1:8000/predict"
    response = requests.post(url, json=sensor_data)
    return response.json()

# Wrap as LangChain Tool
failure_tool = Tool(
    name="FailurePredictionAgent",
    func=call_failure_agent,
    description="Predicts vehicle component failures from sensor data."
)

# Initialize LLM (OpenAI GPT)
llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

# Initialize agent with the tool
agent = initialize_agent(
    tools=[failure_tool],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

# Example usage
sensor_input = {
    "engine_rpm": 6200.0,  # Use float
    "lub_oil_pressure": 1.8,
    "fuel_pressure": 2.1,
    "coolant_pressure": 1.5,
    "lub_oil_temp": 125.0,
    "coolant_temp": 110.0
}

result = agent.run(f"Check vehicle health for these sensor readings: {sensor_input}")
print(result)
