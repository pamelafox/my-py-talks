import json

from rag import MODEL, client, search


def get_weather(city):
    return json.dumps({"city": city, "forecast": "rain", "high_f": 58})


def search_syllabus(query):
    return "\n\n".join(search(query))


tool_functions = {"get_weather": get_weather, "search_syllabus": search_syllabus}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get today's weather forecast for a city",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"]}}},
    {
        "type": "function",
        "function": {
            "name": "search_syllabus",
            "description": "Search the class syllabus for policies, dates, and locations",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]}}},
]

messages = [
    {"role": "system", "content": "You help students in a class. Use the tools to look up anything you don't know."},
    {"role": "user", "content": "Where are office hours, and do I need an umbrella to get there today?"}]

while True:
    response = client.chat.completions.create(
        model=MODEL, messages=messages, tools=tools)
    message = response.choices[0].message
    messages.append(message)
    if not message.tool_calls:
        break
    for tool_call in message.tool_calls:
        print(f"Calling {tool_call.function.name}({tool_call.function.arguments})")
        result = tool_functions[tool_call.function.name](**json.loads(tool_call.function.arguments))
        messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})
print(message.content)
