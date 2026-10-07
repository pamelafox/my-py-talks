import json
import os
import urllib.request

import openai

client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")


def get_weather_alerts(state):
    request = urllib.request.Request(
        f"https://api.weather.gov/alerts/active?area={state}",
        headers={"User-Agent": "impact-of-ai-talk"})
    with urllib.request.urlopen(request) as response:
        alerts = json.load(response)["features"]
    return [f"{a['properties']['event']}: {a['properties']['areaDesc']}" for a in alerts]


tools = [{
    "type": "function",
    "function": {
        "name": "get_weather_alerts",
        "description": "Get active weather alerts from NOAA for a US state",
        "parameters": {
            "type": "object",
            "properties": {"state": {"type": "string", "description": "Two-letter state code"}},
            "required": ["state"]}}}]

response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Any weather alerts in California?"}],
    tools=tools)
tool_call = response.choices[0].message.tool_calls[0]
print(tool_call.function.name, tool_call.function.arguments)

args = json.loads(tool_call.function.arguments)
alerts = get_weather_alerts(**args)
print(f"{len(alerts)} alerts:")
for alert in alerts[:5]:
    print(" ", alert)
