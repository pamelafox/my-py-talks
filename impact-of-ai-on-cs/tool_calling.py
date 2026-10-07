import os

import openai

client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"]}}}]

response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Is it sunny in Berkeley right now?"}],
    tools=tools)
tool_call = response.choices[0].message.tool_calls[0]
print(tool_call.function.name)
print(tool_call.function.arguments)
