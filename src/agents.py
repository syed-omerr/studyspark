import os
from typing import Callable


def _fallback_agent() -> Callable[[str], str]:
    def run(prompt: str) -> str:
        lines = [
            "No LLM key detected. Using fallback heuristic.",
            "Here is a concise study suggestion based on your context:",
        ]
        # extract a few bullet points from the provided context lines
        suggestions = []
        for line in prompt.splitlines():
            line = line.strip()
            if line.startswith("-") and len(suggestions) < 3:
                suggestions.append(line[1:].strip())
        if not suggestions:
            suggestions = ["Review fundamentals and identify key terms in your question."]

        plan = [
            "Study plan:",
            "1) Read the topic overview and note definitions.",
            "2) Work through two example problems.",
            "3) Do a short quiz and reflect on mistakes.",
        ]
        return "\n".join(lines + ["Suggested topics:"] + [f"- {s}" for s in suggestions] + [""] + plan)

    return run


def get_simple_agent() -> Callable[[str], str]:
    """Return a callable agent(prompt)->str. Uses OpenAI if configured, else a fallback."""
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_BETA")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        return _fallback_agent()

    try:
        # Lazy import so the project runs without these deps if no key is present
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=api_key)

        def run(prompt: str) -> str:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful curriculum assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=400,
            )
            return resp.choices[0].message.content or ""

        return run
    except Exception:
        # If OpenAI is not installed or any error occurs, use fallback
        return _fallback_agent()


__all__ = ["get_simple_agent"]


