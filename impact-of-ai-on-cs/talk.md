
# The Impact of AI on Computer Science

Berkeley CS Teachers Association (CSTA)

## Talk details

- **Audience:** CS teachers
- **Date:**
- **Length:**
- **Format:**

## Abstract

## Outline

1. Introduction
2. Software is now built on top of probabilistic AI models
3. Software is now being built largely BY those AI models
4. From software engineering to product engineering
5. Software can now be built by anyone who can describe the end result
6. What this means for teaching CS
7. Q&A

## Key points

### 1. Software is now built on top of probabilistic AI models

Framing: traditional code is deterministic (same input, same output). AI-powered code calls models whose output is *sampled*, so AI engineering is mostly about constraining, grounding, and checking that output.

Proposed sequence (each step builds on the previous one):

1. **LLMs**: same prompt, different output
2. **Context engineering (RAG)**: give the LLM the right context to ground its answers
3. **Evaluations**: how you "test" probabilistic software
4. **Structured outputs**: constrain output to a schema
5. **Tool calling**: the LLM requests a function call, your code runs it
6. **Agents**: tool calling in a loop
7. **Other kinds of models**: image generation, embeddings, voice and transcription

Code examples use the OpenAI Python SDK, as in [python-openai-demos](https://github.com/Azure-Samples/python-openai-demos). Runnable demos are in this folder and use local Ollama models (`gpt-oss:20b` for chat, `nomic-embed-text` and `nomic-embed-text-v2-moe` for embeddings): `llm.py`, `rag.py`, `structured_outputs.py`, `evals.py`, `tool_calling.py`, `agent.py`, `embeddings.py`. Image generation and voice won't be demoed live. Example outputs below are placeholders: capture real ones before the talk.

#### LLMs

```python
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": "Write a haiku about recursion"}])
print(response.choices[0].message.content)
```

Show: run it twice, get two different haikus.

#### Context engineering (RAG)

Context engineering is deciding what goes into the LLM's context window: instructions, retrieved documents, conversation history, tool results. RAG (retrieval-augmented generation) is the most common technique.

```python
results = search(question)  # keyword and/or vector search over your documents
sources = "\n".join(result.text for result in results)
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[
        {"role": "system", "content": f"Answer ONLY using these sources, and cite them:\n{sources}"},
        {"role": "user", "content": question}])
```

Show: a course syllabus Q&A bot: "When is the final project due?" answered with a citation. Vector search relies on embedding models, covered later.

#### Evaluations

Start from what teachers already know: unit tests.

```python
def test_add():
    assert add(2, 3) == 5
```

That doesn't work when the output is different every time. Instead, you run an *eval*: many inputs, each checked against criteria with a pass/fail and a reason, summarized as pass rates.

```python
for question in dataset:
    answer, sources = rag_answer(question)
    has_citation = "[" in answer
    verdict = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content":
            f"Is every claim in this answer supported by the sources? Explain why, then end with PASS or FAIL.\n"
            f"Question: {question}\nSources: {sources}\nAnswer: {answer}"}]).choices[0].message.content
    grounded = "PASS" in verdict.strip().splitlines()[-1]
```

Show: pass rates before and after a prompt change, e.g. "cited: 82% to 96%, grounded: 78% to 94%".

| Unit tests | Evaluations |
|---|---|
| Deterministic output | Probabilistic output |
| A few hand-picked inputs | A dataset of many realistic inputs |
| Exact assertions (`==`) | Criteria checked by code, an LLM judge, or a human |
| Pass/fail per test | Pass/fail per input, with a reason |
| All tests must pass | Pass rate tracked over time, with a threshold |

Analogy for teachers: unit tests are an autograder, evals are grading with a rubric. LLM-as-judge is like a TA applying your rubric, so you still spot-check its grades.

Segue to structured outputs: the judge's verdict is free text, formatted differently each time ("**PASS**" on its own line, or "...supported by the source. PASS"), so parsing it is fragile.

#### Structured outputs

```python
class CodeFeedback(BaseModel):
    concepts_used: list[str]
    bugs: list[str]
    hints: list[str]

completion = client.chat.completions.parse(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": f"Review this student code:\n{code}"}],
    response_format=CodeFeedback)
feedback = completion.choices[0].message.parsed
```

Show: the parsed Python object, e.g. `CodeFeedback(concepts_used=['for loop', 'list'], bugs=['off-by-one in range()'], hints=[...])`. Callback to evals: the judge could return `Grade(reason: str, passed: bool)` instead of free text.

#### Tool calling

```python
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
    model="gpt-5-mini", messages=messages, tools=tools)
tool_call = response.choices[0].message.tool_calls[0]
```

Show: `tool_call.function.name == "get_weather"`, `tool_call.function.arguments == '{"city": "Berkeley"}'`. Key point: the model never runs code, it only *asks* your code to run it.

#### Agents

```python
while True:
    response = client.chat.completions.create(
        model="gpt-5-mini", messages=messages, tools=tools)
    message = response.choices[0].message
    messages.append(message)
    if not message.tool_calls:
        break
    for tool_call in message.tool_calls:
        result = run_tool(tool_call.function.name, json.loads(tool_call.function.arguments))
        messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})
print(message.content)
```

Show: an agent is just a while loop around tool calling.

#### Other kinds of models

##### Image generation

```python
result = client.images.generate(
    model="gpt-image-1",
    prompt="A cat teaching a high school CS class, chalkboard full of Python")
```

Show: two different images from the same prompt, side by side.

##### Embedding models

```python
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="dog")
vector = response.data[0].embedding  # [0.0123, -0.0456, ...] 1536 floats
```

Show: cosine similarity table, e.g. "dog" vs. "puppy" (high), "dog" vs. "spreadsheet" (low). This is what powers vector search in RAG.

Embedding models aren't probabilistic (same input gives the same vector), but they're very dependent on their training data, so they can still behave in surprising ways. Visuals from [A visual introduction to vector embeddings](http://blog.pamelafox.org/2025/05/a-visual-exploration-of-vector.html):

- Most similar words to "dog", compared to 1000 common words:
  - `text-embedding-ada-002`: animal, **god**, cat. Possibly it learned to pay attention to spelling.
  - `text-embedding-3-small`: animal, horse, cat. These are only similar in meaning.
- Multilingual support varies a lot by model, depending on what languages were in the training data. `embeddings.py` compares Nomic's English-only `nomic-embed-text` (v1.5) with its multilingual `nomic-embed-text-v2-moe`:

  | "dog" vs. | `nomic-embed-text` | `nomic-embed-text-v2-moe` |
  |---|---|---|
  | puppy | 0.789 | 0.734 |
  | cat | 0.602 | 0.386 |
  | perro | 0.419 | 0.665 |
  | chien | 0.462 | 0.731 |
  | Hund | 0.429 | 0.849 |
  | spreadsheet | 0.418 | 0.222 |

  With the English-only model, "perro" is about as similar to "dog" as "spreadsheet" is.

Live demo: [vectors-comparison](https://pamelafox.github.io/vectors-comparison/). Type "dog" and switch between the two embedding models to see different nearest neighbors.

##### Voice and transcription

```python
transcript = client.audio.transcriptions.create(
    model="gpt-4o-transcribe",
    file=open("lecture.mp3", "rb"))
print(transcript.text)

speech = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input="Welcome to CS 101!")
speech.write_to_file("welcome.mp3")
```

Show: transcribe a short clip, then play back generated speech. Mention realtime speech-to-speech models, which power voice assistants. Probabilistic angle: transcription models can hallucinate text that was never said, e.g. reports of Whisper inventing sentences during pauses (find a source before the talk).

Segue to point #2: coding agents put all of this together. A coding agent is that same while loop, with tools for reading files, editing files, and running tests, and it often uses other models too, like embeddings for codebase search and transcription for voice input.

References:

- Python + AI series: https://aka.ms/pythonai/rewatch
- https://github.com/Azure-Samples/python-openai-demos
- https://github.com/Azure-Samples/vector-embeddings-demos
- https://github.com/Azure-Samples/ai-quality-safety-demos
- https://github.com/Azure-Samples/python-ai-agent-frameworks-demos

### 2. Software is now being built largely BY those AI models

#### What is a coding agent?

Callback to the agent while loop from point #1: a coding agent is an LLM in that loop, with tools for software development:

- Read files and search the codebase (grep, embeddings)
- Edit and create files
- Run terminal commands: tests, linters, the app itself
- Fetch web pages and docs
- Plus context: instruction files (`AGENTS.md`, `.github/copilot-instructions.md`), skills, MCP servers

Show: a diagram of the loop: task, then LLM, then tool call, then result, repeated until "done, tests pass".

Show: a real agent session. The demos for point #1 were written by a coding agent, which also ran them against Ollama and fixed what it saw. It noticed `qwen3.5:9b` leaking its reasoning into the haiku and switched models. It saw the agent demo skip a tool call 1 in 3 times, so it rewrote the question and re-ran it until it was reliable. That's the loop in action, including verification.

#### Benchmarks: how capable are they?

- [SWE-bench Verified](https://www.swebench.com/): real GitHub issues from popular Python repos. The agent must produce a patch that passes the project's hidden tests. Callback to evals: it's graded by unit tests!
- [METR time horizons](https://metr.org/): the length of tasks (measured in human time) that agents can complete with 50% success. Their 2025 paper found it doubling roughly every 7 months.

Show: score-over-time charts for both. Pull the latest charts before the talk.

#### GitHub activity

From [The state of the tech industry in 2026](https://newsletter.pragmaticengineer.com/p/the-state-of-the-tech-industry-in):

- Agent-authored PRs on GitHub increased ninefold in eight months.
- In August 2026, there were more agent-authored PRs on GitHub than human-authored ones.
- Lines of code and commits on GitHub are growing exponentially, not linearly.
- At Linear, agents have created more issues than humans since July.

Show: the GitHub agent-authored PR chart and the commits/lines of code chart from that post.

Note: the post also estimates 75M+ fully AI-generated PRs per month, vs. 25M human PRs in December 2023, but labels it "as of today (October 2025)", which looks like a typo for 2026. Verify before quoting.

#### Huge jobs in weeks, not years

- Bun: rewritten from Zig to Rust in 11 days, vs. an estimated 1.5 engineering years
- Airbnb: 3,500 test files migrated to a new testing library in 6 weeks
- Uber: 600,000 JUnit 4 tests across 15 million lines of code migrated in 4 months

#### How engineers work now

- "Nobody writes code by hand anymore" is the #1 trend in the Pragmatic Engineer post.
- Engineers run several agents in parallel. Boris Cherny, creator of Claude Code: "I have 5 terminal tabs... I also run 5-10 Claudes on Claude Web, in parallel with my local Claudes."
- From the parallelize deck: before AI coding, one active feature was our limit. After AI coding, "we are engineering managers for agents": start, observe, unblock, review.

Show: the before/after feature lanes diagram from the parallelize deck.

#### The IDE is fading

The code editor used to be the center of a developer's work. Now the interface is increasingly for managing agents, not editing code. From the Pragmatic Engineer post:

- Antigravity 1.0 (Nov 2025) was the last major IDE launched as a VS Code fork. Antigravity 2.0 (May 2026) moved away from the IDE concept.
- Codex launched as a non-IDE app in Feb 2026.
- Cursor 3.0 (April 2026) dropped its IDE interface and now looks like the Codex and Claude desktop apps.
- JetBrains is pivoting to JetBrains Air, an agentic development environment.

Same trend at GitHub, from [Parallelize your development with GitHub Copilot](https://pamelafox.github.io/parallelize-development-github-copilot/): VS Code agent mode, then Copilot CLI, then the VS Code Agents window and Copilot app (which manage many agent sessions), then Copilot cloud agent (assign an issue, get a pull request).

Show: an IDE screenshot next to an agent app screenshot (e.g. Cursor 3.0 or the Copilot app), side by side.

Optional audience interaction: Steve Yegge's 8 levels of AI usage. Level 5 is "CLI-first: abandoned the IDE", and level 8 is "built a custom orchestrator to run 30+ agents". Ask the audience which level they're at.

Where it's heading: the IDE becomes a conversation, monitoring, and *verification* interface. How do we know the agent's output works? Kent Beck: "It's not that we don't need more perspective and context for our human-based decisions; it's that the context has changed."

#### Where agents are weakest: verification and system design

Framing: agents improve fastest on what can be checked automatically (do the tests pass?), and are weakest on what takes judgment: test coverage, security, maintainability, changes across many files. Callback to evals: agents are great at the autograder, worse at the rubric.

Verification:

- [METR](https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/) (Aug 2025): a Claude 3.7 Sonnet agent passed the maintainers' tests on 38% of real open-source tasks, but none of the 15 PRs reviewed were mergeable as-is. *Every* PR that passed the tests still lacked adequate test coverage, and even those took ~26 minutes each to fix (about a third of the human's original time).
- [Veracode](https://www.veracode.com/blog/genai-code-security-report/) (July 2025): 45% of AI-generated code samples failed security tests. Newer models wrote more working code, but not more secure code.
- Stack Overflow 2025 Developer Survey: only 3.1% of developers "highly trust" AI accuracy, and 46% distrust it.
- Jarred Sumner (Bun): "The AI writes pretty much all the code, but we have the AI write pretty much all the tests as well... You need to have a way to trust your code."

System design:

- [SWE-Bench Pro](https://arxiv.org/abs/2509.16941) (Scale AI, Sept 2025): realistic tasks averaging 107 lines across 4.1 files. At launch, top models scored ~23%, vs. 70%+ on SWE-bench Verified, and under 20% on private startup codebases. Resolve rates drop sharply as the number of files grows. Voss reports the best models are now around 59%, so update this before the talk.
- GitClear, "The Maintainability Gap" (June 2026, 623M code changes): refactoring is down 70% vs. 2022, and duplicated code blocks are up 81%. GitClear sells code quality tools.
- Demirer, Musolff & Yang (May 2026, 100,000+ GitHub developers): autonomous agents raised commits by 180%, but releases by only 30%. More code isn't more shipped software.
- [DORA](https://dora.dev/research/2024/dora-report/) 2024: AI adoption raised individual productivity but hurt software delivery stability and throughput. DORA 2025 calls AI an "amplifier" of an organization's existing strengths and weaknesses.

Counterpoint, to be fair: Popescu et al. (April 2026) found Codex PRs qualified for merge 87.5% of the time vs. 75.1% for human PRs. A [study of 567 Claude Code PRs](https://arxiv.org/pdf/2509.14745) across 157 open source projects found 84% eventually merged, vs. 91% for humans. Models are improving fast, and the METR data is from early-2025 models.

Also broken: human code review has become "theater" (nobody can keep up with 5-10x more code), and quality and reliability are down. A [study of 33,000 agent PRs](https://arxiv.org/abs/2605.02273) found most PRs on GitHub get no recorded review, and when agent PRs are reviewed, 58% of the time the only reviewer is another agent. curl shut down its bug bounty after the share of real bugs in AI-flooded reports fell from over 15% to under 5%. And non-engineers still aren't shipping production code (but see point #4).

References:

- https://newsletter.pragmaticengineer.com/p/the-state-of-the-tech-industry-in
- https://pamelafox.github.io/parallelize-development-github-copilot/

### 3. From software engineering to product engineering

Reference: [We are all Product Engineers now](https://seldo.com/posts/we-are-all-product-engineers-now/) (Laurie Voss, Sept 2026).

#### The software engineering lifecycle

Start with the full lifecycle, using terms teachers already know:

1. Understand the problem: talk to users, write user stories
2. Write the spec: requirements, design docs, what "done" looks like
3. Design the system: architecture, data model
4. Write the code
5. Write the tests
6. Review the code
7. Debug and maintain
8. Ship it
9. Scale and operate it
10. User testing: does it do what users actually meant? Is it pleasant to use?

Show: the lifecycle as a loop of boxes. Point out that most CS classes focus on box 4.

#### Where humans are most needed now

Show: the same diagram again, with boxes fading out as agents take them over. Based on Voss's breakdown and the evidence from point #2:

| Status | Boxes |
|---|---|
| Agents do it now | Write the code |
| Agents are getting there | Write the tests (though coverage is weak, per point #2), review the code, debug and maintain |
| Agents are next | Ship it, scale and operate it |
| Agents are weakest (point #2) | Design the system |
| Humans most needed | Understand the problem, write the spec (define "good"), user testing |

What's left is the beginning and the end of the loop: figuring out what to build, and checking that what got built is what people meant. Callback: defining "good" is evals from point #1.

#### Why the human part stays: software is a formalization of a human desire

- "I need to keep track of my orders" fits ten thousand pieces of software. Only one is right for a bakery, and only the baker knows she runs a bakery.
- That knowledge isn't in the training data: it's in the head of one specific baker who's never written it down.
- "Good" doesn't transfer: what's right for one bakery isn't right for the next. That's why software with a zillion config options still doesn't do what you need.
- When everyone can build the correct thing, the delightful thing is what's left to compete on.

#### There's no upper bound on demand for software

Look at the website for your dentist, your insurance company, or your school. It's bad because nobody could afford better, not because nobody knows how to build better. "Every small business runs on a spreadsheet and a group chat and a person who remembers stuff." Cheap code means more software, not fewer people building it.

#### The future of CS careers: product engineering

The jobs growing fastest are the ones built around the human parts of the lifecycle:

- "Forward deployed engineer" postings grew ~800% in nine months in 2025. There are now ~1,000 open roles across 462 companies, including OpenAI, Anthropic, Stripe, and Google Cloud, with ~$240K average pay.
- The same job is posted as solutions engineer, applied AI engineer, deployment engineer, or implementation engineer. The description: sit with the customer, understand their problem, build it with them, iterate until it works. The code is the smallest part.
- IBM is redesigning its entry-level role around customer contact and specification instead of typing.
- It's converging from the other side too: product managers are increasingly expected to build working prototypes with agents, not just write specs and mockups. The Pragmatic Engineer post found PMs and designers doing "a massive amount of prototyping", while engineers still decide what ships to production. So product management is becoming a CS career too. (Find a source for "expected", e.g. PM job postings that ask for prototyping.)
- This isn't a brand new job. In the 1960s, the *systems analyst* sat between the business and the programmers. That role split off into *product manager*, and now it's merging back with engineering into the *product engineer*.

For students: a CS career looks less like "write code from a ticket" and more like "figure out what someone needs, then build it."

### 4. Software can now be built by anyone who can describe the end result

Theme: the era of personal software. When code is cheap, people build software just for themselves, their families, their classrooms, and their communities.

#### Faster to build it than to find it

[Pamela's tweet](https://x.com/pamelafox/status/2095682199593046201) (Sept 3, 2026): "I was trying to find this one website that lets my kids record audio and plays it back with funny effects. Then I realized, screw it, its faster to vibe it than to find it! Two minutes later, boom, my kids can squirrel themselves to their hearts desires."

Show: the tweet and a quick demo of the app.

#### Not a new idea, just newly possible

- 2004: Clay Shirky described [situated software](https://web.archive.org/web/20050120085129/http://www.shirky.com/writings/situated_software.html), built for a particular group of people instead of millions. It was too expensive to build back then.
- 2020: Robin Sloan built a messaging app just for his family of four, and wrote [An app can be a home-cooked meal](https://www.robinsloan.com/notes/home-cooked-app/). They still use it daily. It took him a week.
- 2024: Maggie Appleton [predicted](https://maggieappleton.com/home-cooked-software) language models would bring a golden age of personal software, built by people in between end users and programmers, like "teachers who make elaborate Notion spreadsheets for managing classes".

#### Personal software vs. mass-market software

| Mass-market software | Personal software |
|---|---|
| Millions of users | A few people you know |
| One size fits all | Fits your exact needs |
| The company decides when it changes or shuts down | You decide |
| Needs a team of professionals | One person who knows the problem |

Callback to point #3: only the baker knows what her bakery needs. Now the baker can build it herself.

This also resolves the tension from point #2 (non-engineers still aren't shipping *production* code): personal software doesn't need to be production software.

It's already happening at work, too: at AI-native companies, "the salespeople are shipping (at least internal tools and automations for themselves)." ([Yoni Rechtman](https://99d.substack.com/p/there-will-only-be-four-jobs))

Show: live demo of building a small classroom tool from a plain-English description, e.g. a seating chart generator, or take a suggestion from the audience. Ask: who has already built a personal tool with AI?

#### What still takes CS knowledge

Anyone can describe what they want, but building something that works well still takes CS thinking:

- Describing it precisely enough: decomposition, edge cases, examples of what "good" looks like
- Checking that it actually works: testing, not just trying it once (point #1's evals, point #3's user testing)
- Knowing what the agent struggles with: storing data, logins, deployment, security (point #2)
- Protecting people: a teacher's homemade tool with student data still has to follow student privacy rules like FERPA

#### Transition: CS for all students

Not every student will become a software engineer, but every student will be able to build software. Sloan: "People don't only learn to cook so they can become chefs." That's the strongest argument yet for CS for *all* students: so they can build the software they need, and know enough to build it well.

### 5. What this means for teaching CS

Agents changed which parts of building software need humans (points #2 to #4). Four skills matter more than ever, whether students become software engineers or build software for themselves:

#### 1. Problem design

Figuring out what to build, and describing it precisely enough that someone (or an agent) can build it.

- Why: it's the part of the lifecycle where humans are most needed (point #3). Only the baker knows what her bakery needs.
- Voss: "Universities teach data structures. Bootcamps teach React. Nobody teaches 'go sit with a baker for a week and come back with a spec.'"
- In class:
  - Build for a real "client": a teacher, a school club, a family member. Interview them first.
  - Write the spec and examples before any code, like the *How to Design Programs* design recipe.
  - Hand the spec to an agent and see what it builds. Did you get what you meant? Spec quality becomes instantly visible.
- Standards: 1B-AP-13 (plan by considering user preferences), 2-AP-15 (incorporate feedback from users to meet user needs), 1A-AP-12 (describe goals and expected outcomes). The AP CSP Create task already asks for the program's purpose.

#### 2. Computational thinking

Decomposition, abstraction, pattern recognition, and algorithms: still the foundation, because they're how you steer agents.

- Why: agents work best on bounded tasks (point #2's parallel agents). Someone has to break a big problem into agent-sized pieces, recognize when the agent's approach is wrong, and know what's possible.
- Reading code matters more than ever: you need to understand what the agent wrote well enough to judge it.
- In class:
  - Decompose a project into tasks small enough for an agent, then run them.
  - Predict what agent-written code will do before running it, and explain it line by line.
- Open question for discussion: how much should students still write by hand to build a mental model? Calculator analogy: we still teach arithmetic.

#### 3. Systems design

How the pieces fit together: architecture, data models, interfaces, tradeoffs.

- Why: agents are weakest here (point #2). Success on SWE-Bench Pro drops sharply as tasks span more files, and GitClear found refactoring down 70% and duplicated code up 81%.
- Old best practices work great with agents: the Pragmatic Engineer post describes how designing up front, building a "tracer bullet" (one thin working path through the whole system) first, and using design patterns all lead to better agent output.
- In class:
  - Draw the architecture and data model before prompting.
  - Review agent output for duplication and missed abstractions, then refactor.
- Standards: 3A-AP-23 (document design decisions).

#### 4. Verification

Checking that it actually works: tests, evals, security, accessibility, and whether it's what users meant.

- Why: agents pass tests but miss what makes code mergeable (point #2's METR study), 45% of AI-generated code fails security tests, and human code review can't keep up. Evals are how you check probabilistic software (point #1).
- In class:
  - Students write the tests (and rubrics) for agent-written code.
  - Bug hunts: find the bugs in agent-written code.
  - Accessibility and bias audits of what they built.
  - User testing with their real "client" from problem design.
- Standards: 2-AP-17 (test using a range of test cases), 3A-AP-19 (incorporate feedback from users), 3A-AP-21 (make artifacts more usable and accessible), 3A-IC-25 (test and refine to reduce bias).

#### Also: judgment and communication

Two more skills from [There will only be four jobs](https://99d.substack.com/p/there-will-only-be-four-jobs) (Yoni Rechtman, April 2026), which matter even more when anyone can build anything quickly:

- Judgment: knowing when to say "hey, come on." When everyone can build fast, someone needs to ask whether it *should* be built, and whether it's safe, fair, and honest. In class: the Impacts of Computing strand of the CSTA standards, and discussing when *not* to build something.
- Communication and collaboration: making the work understandable to others, and making a team work well together. Rechtman calls these people "the interface layer." In class: presentations, demos, explaining your design decisions, teamwork (CSTA practices P2, Collaborating Around Computing, and P7, Communicating About Computing).

#### You already teach this

All of these are already in the [CSTA K-12 standards](https://csteachers.org/k12standards/interactive/), even if class time mostly goes to writing code. The shift is in emphasis, not a new subject: from writing the code to the steps around it.

#### For students who love coding

Many people who think they loved the typing actually loved "the moment before the typing, when a vague mess of a problem resolved into a precise shape in their head. That moment is the job now." (Voss) And the craft survives the way woodworking survived the furniture factory: "Developers write software the way singers sing."

## Appendix

### The entry-level job changed

For Q&A or for audience members focused on career preparation:

- The junior ladder is broken. Juniors were hired to turn well-specified tickets into code, which is exactly what agents got good at first. Seniors learned judgment by osmosis over a decade of that. (Voss)
- Stanford (Aug 2026 update): employment for 22-25 year olds in AI-exposed jobs is 19% below their less-exposed peers, through reduced hiring rather than layoffs. Young workers lost ground where the knowledge is *codified* (in the training data). Experienced workers gained where it's *tacit* (learned by doing).
- SignalFire 2026: entry-level hiring is down 65% at big tech since 2019, and 75% at early-stage startups. But engineering's share of hiring went *up*, from 46% to 55%.

So students need to arrive with the skills that used to take a decade of osmosis: the four skills from point #5.

## Notes

## Resources

https://99d.substack.com/p/there-will-only-be-four-jobs
https://techcommunity.microsoft.com/blog/educatordeveloperblog/level-up-your-python--ai-skills-with-our-complete-series/4464546

To add-
triangle/stack of assembly language to NLP
rag chat as example of personal software (between friends)
stats from marlenes presentation
