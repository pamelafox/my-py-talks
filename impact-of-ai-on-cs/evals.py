from rag import MODEL, answer, client

dataset = [
    "When is the final project due?",
    "What happens if I turn in homework late?",
    "Can I use ChatGPT to write my homework?",
    "When are office hours?",
    "How much is the midterm worth?",
    "Is there a field trip this semester?",
]

cited_count = 0
grounded_count = 0
for question in dataset:
    answer_text, sources = answer(question)
    has_citation = "[" in answer_text
    verdict = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content":
            f"Is every claim in this answer supported by the sources? Explain why, then end with PASS or FAIL.\n"
            f"Question: {question}\nSources: {sources}\nAnswer: {answer_text}"}]).choices[0].message.content
    grounded = "PASS" in verdict.strip().splitlines()[-1]
    cited_count += has_citation
    grounded_count += grounded
    print(f"{question}\n  cited: {has_citation}, grounded: {grounded}\n  judge: {verdict}\n")

print(f"Cited: {cited_count / len(dataset):.0%}")
print(f"Grounded: {grounded_count / len(dataset):.0%}")
