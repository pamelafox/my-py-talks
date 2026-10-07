import os

import openai

client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")

response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Write a haiku about recursion"}])
print(response.choices[0].message.content)
