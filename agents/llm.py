import os

_groq_client = None
_openai_client = None


def _get_groq():
    global _groq_client
    if _groq_client is None:
        from groq import Groq
        _groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _groq_client


def _get_openai():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _openai_client


def call_llm(prompt: str) -> str:
    # Try Groq first — faster and free tier available
    if os.getenv("GROQ_API_KEY"):
        try:
            response = _get_groq().chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq failed: {e}, trying OpenAI...")

    # Fall back to OpenAI
    if os.getenv("OPENAI_API_KEY"):
        try:
            response = _get_openai().chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI failed: {e}")

    raise Exception("No LLM API key configured (set GROQ_API_KEY or OPENAI_API_KEY)")
