from rag import MODEL, answer, client

dataset = [
    "When is the final project due?",
    "What happens if I turn in homework late?",
    "Can I use ChatGPT to write my homework?",
    "When are office hours?",
    "How much is the midterm worth?",
    "Can I use Copilot to debug my homework?",
]

grounded_count = 0
for question in dataset:
    answer_text, sources = answer(question)
    verdict = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content":
            f"Is every claim in this answer supported by the sources? Start with PASS or FAIL, then give a one-sentence reason.\n"
            f"Question: {question}\nSources: {sources}\nAnswer: {answer_text}"}]).choices[0].message.content
    grounded = verdict.strip().strip("*").startswith("PASS")
    grounded_count += grounded
    print(f"{question}\n  grounded: {grounded}\n  judge: {verdict}\n")

print(f"Grounded: {grounded_count / len(dataset):.0%}")
