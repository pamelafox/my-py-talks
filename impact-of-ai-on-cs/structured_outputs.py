import os

import openai
from pydantic import BaseModel

client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")


class CodeFeedback(BaseModel):
    concepts_used: list[str]
    bugs: list[str]
    hints: list[str]


code = """
def average(scores):
    total = 0
    for i in range(1, len(scores)):
        total += scores[i]
    return total / len(scores)
"""

completion = client.chat.completions.parse(
    model=MODEL,
    messages=[{"role": "user", "content": f"Review this student code:\n{code}"}],
    response_format=CodeFeedback)
feedback = completion.choices[0].message.parsed
print(repr(feedback))
