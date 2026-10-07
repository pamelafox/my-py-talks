import os
import re
import sys

import openai

client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")

STOPWORDS = {"a", "an", "and", "are", "can", "do", "how", "i", "in", "is", "it", "my", "of", "on", "the", "to", "what", "when", "where"}

with open(os.path.join(os.path.dirname(__file__), "syllabus.md")) as f:
    SECTIONS = f.read().split("\n## ")[1:]


def keywords(text):
    return set(re.findall(r"\w+", text.lower())) - STOPWORDS


def search(query, top=2):
    query_words = keywords(query)
    ranked = sorted(SECTIONS, key=lambda section: len(query_words & keywords(section)), reverse=True)
    return ranked[:top]


def answer(question):
    sources = "\n\n".join(search(question))
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": (
                "Answer ONLY using these syllabus sections. Cite the section title in square brackets, "
                f"like [Grading]. If the answer isn't in the sections, say you don't know.\n\n{sources}")},
            {"role": "user", "content": question}])
    return response.choices[0].message.content, sources


if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "When is the final project due?"
    answer_text, _ = answer(question)
    print(answer_text)
