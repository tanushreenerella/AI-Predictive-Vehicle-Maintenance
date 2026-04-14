from agents.llm import call_llm
from agents.fallback_logic import fallback_schedule_decision

def agentic_scheduling_agent(vehicle_state: dict):
    try:
        prompt = f"""
        Vehicle health data:
        Risk level: {vehicle_state['risk_level']}
        Failure probability: {vehicle_state['failure_probability']}
        Last analyzed: {vehicle_state['last_analyzed']}

        Decide urgency and recommended action.
        Respond in JSON.
        """

        response = call_llm(prompt)
        return response

    except Exception as e:
        print("⚠️ LLM failed, using fallback:", e)
        return fallback_schedule_decision(vehicle_state)
