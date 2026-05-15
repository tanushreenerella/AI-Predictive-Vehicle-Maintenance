import os

_groq_client = None

DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def _get_groq():
    global _groq_client
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")
    if _groq_client is None:
        from groq import Groq

        _groq_client = Groq(api_key=api_key)
    return _groq_client


def call_llm(prompt: str) -> str:
    """
    Groq-only LLM wrapper.

    Secondary-provider fallback is intentionally disabled so user-facing
    diagnosis, RCA, and scheduling flows use one configured provider only.
    """
    try:
        response = _get_groq().chat.completions.create(
            model=DEFAULT_GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        raise RuntimeError(f"Groq LLM call failed: {exc}") from exc
