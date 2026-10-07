import math

import openai

client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODELS = ["nomic-embed-text", "nomic-embed-text-v2-moe"]


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


words = ["dog", "puppy", "cat", "perro", "chien", "Hund", "犬", "spreadsheet"]

similarities = {}
for model in MODELS:
    response = client.embeddings.create(model=model, input=words)
    vectors = [item.embedding for item in response.data]
    print(f"{model}: {len(vectors[0])} floats, starting {vectors[0][:3]}")
    similarities[model] = [cosine_similarity(vectors[0], vector) for vector in vectors[1:]]

print(f"\n{'dog vs.':<14}" + "".join(f"{model:>26}" for model in MODELS))
for i, word in enumerate(words[1:]):
    print(f"{word:<14}" + "".join(f"{similarities[model][i]:>26.3f}" for model in MODELS))
