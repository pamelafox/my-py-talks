# The Impact of AI on CS Curriculum

Follow-up to [The Impact of AI on Software Engineering](../impact-of-ai-on-cs/) (Berkeley CSTA, October 2026). That talk ran out of time before "What this means for teaching CS", so this talk covers that section in full.

## Talk details

- **Audience:** CS teachers, K-12 and college
- **Date:**
- **Length:**
- **Format:** small, discussion-oriented meeting around one table. Discussion happens naturally throughout, with an open-questions slide at the end

## Outline

1. Introduction
2. The state of software engineering (recap)
3. The skills that matter now for software engineering
4. What changes in the classroom
5. By grade band: K-4, 5-8, 9-12, college
6. Closing and discussion

## 1. Introduction

- Hook slide: "What will kindergartners need by 2043?" Built up with fragments:
  1. A 2026-2043 timeline of a kid growing through K-4, 5-8, 9-12, and college, fading into fog and question marks: "What will software engineering look like?"
  2. Click: a look-back timeline below it (2009: GitHub and Stack Overflow are about a year old; 2017: Transformers paper; 2021-22: Copilot, ChatGPT; 2026: AI writes much of the code).
  3. Click: "To guess where we're going, start with where we are." Leads into the recap section.
- Today: a quick recap of how software engineering is changing, then the skills that matter now, then what we'd teach at each grade level, then discussion. This talk is meant to be a conversation: you know your classrooms better than I do.
- Framing quote (Jamie Maguire): "Syntax recall was never the goal." Code was always the means. The goal is to solve problems for people.

## 2. The state of software engineering (recap)

Keep this to ~6 slides, one per big point from the first talk.

### Software is built on top of AI models

- Traditional code is deterministic. AI-powered code is probabilistic: same input, different outputs.
- So building with AI is mostly context engineering (what goes into the prompt) and evaluation (did it work?).

### Software is built BY AI models

- Coding agents: an LLM in a loop with tools to read, edit, and run code.
- Huge jobs in weeks: Bun rewritten from Zig to Rust in 11 days.

### AI-written software is already the norm

Three bar charts, no stat cards (avoid "PR" jargon for teachers; say "code changes"): Google share of new code written by AI, GitHub share of code changes started by agents, and engineers by share of work done with AI (Google: 25% Oct 2024, 50% fall 2025, 75% Apr 2026; GitHub: 17% Mar 2026, 40%+ Sept 2026): 10.0B (2024), 12.9B (2025), 34.3B (2026), each year ending Sept 30: 1× in Sept 2025 to ~6× in Sept 2026, with a June inflection shaded as "Agents take off"):

- GitHub: 17% → 40%+ of pull requests started by an agent, March to September 2026; 110M in September alone. [Octoverse 2026](https://github.blog/news-insights/octoverse/octoverse-commits-pushes-reach-new-highs-in-2026-as-developers-build-with-agents/)
- Google: 75% of new code is AI-generated and approved by engineers (April 2026), up from 25% in Oct 2024 and 50% in fall 2025. [Fast Company](https://www.fastcompany.com/91531519/google-ceo-says-75-of-the-companys-code-is-ai-generated)
- Pragmatic Engineer AI tooling survey (Mar 2026, 900+ respondents): 25% do under 40% of their work with AI, 19% do 40-69% (derived), 56% do 70%+; 55% regularly use agents.
- Note: Pragmatic Engineer's "more agent-authored PRs than human-authored ones in August 2026" conflicts with Octoverse's 40%+, so this deck uses GitHub's official number.

### Software engineers manage multiple agents

- Engineers run 5-10 agents at once: start, observe, unblock, review.
- The skills that matter most for this: context engineering, multitasking, and reviewing and verifying outputs.

### From software engineering to product engineering

No separate slide: the lifecycle diagram appears once, in "The skills you still need" (section 3). Mention this in the notes for "But is the software actually good?".

- Agents took over "write the code", and are moving into tests, review, and deploys.
- Humans are most needed at the start and end: figuring out what to build, and checking that it's what people meant.

### Building software keeps getting easier

Reuses the programming-language ladder from the first talk (machine code → assembly → C → Python → English), with who could program at each layer. No subhead. Notes: Grace Hopper and FLOW-MATIC; CACM's "flaky compiler" (deterministic layers below, ambiguous and non-deterministic on top), which sets up "But is the software actually good?"

### Anyone can build software now

Examples from people who aren't software engineers:

- Kevin Roose, NYT tech columnist: "I am not a coder." Built a podcast summarizer, "Will It Fit?" (will this fit in my trunk?), and "LunchBox Buddy" (what to pack for his son's lunch). [Not a Coder? With A.I., Just Having an Idea Can Be Enough](https://www.nytimes.com/2025/02/27/technology/personaltech/vibecoding-ai-software-programming.html), Feb 2025.
- Meng To's 8-year-old son, with no coding experience, built 2 platformer games, a drawing app, an animation app, and an AI chat app, about 2 hours each. [Post on X](https://x.com/MengTo/status/1830122851028123911), Sept 2024.
- Personal software: "faster to build it than to find it."
- But building something that works well, safely, still takes CS thinking.

### But is the software actually good?

Agents are weakest at verification and design. Placed at the end of the recap as the bridge into the skills section.

- Agents pass the tests but miss what makes code mergeable (METR: 0 of 15 PRs mergeable as-is).
- 45% of AI-generated code fails security tests (Veracode).
- Outages are up ~30% at companies with heavy AI use, while features shipped are flat (Titus Winters).
- Agents struggle more as changes span more files (SWE-Bench Pro).

## 3. The skills that matter now for software engineering

### The skills that got deprecated

("Deprecated": still around, but on its way out.) Each tool paired with the skill it deprecated:

| Tool | Deprecated skill |
|---|---|
| IntelliSense (2000s) | Memorizing APIs |
| Stack Overflow & open source packages (2008+) | Solving every problem from scratch |
| AI autocomplete (2021+) | Syntax recall |
| Coding agents (2025+) | Writing code |
| ? (next) | Reading code? |

Takeaway: each tool freed us up for harder problems.

- Reading code is the open question. Agents now write more code than anyone can read, so review is shifting from reading the code to checking what it *does*: its behavior, outputs, tests, and evals. CACM: "Tracing does not scale."
- Counterpoint for discussion: "You can't review what you don't understand." (Maguire) But understanding may come from how programs work, not from reading every line.

### The skills you still need (4 slides)

Each title starts with "Skills you still need:" (lighter color), then:

1. "building software": the lifecycle loop with 10 steps (no "debug & maintain"), including a new "4. Manage the agents" step. Human-led steps are all blue with a 🧑🏽 badge; steps mostly done by agents (write the code, write the tests) are gray with a 🤖 badge. "Review the work", "Ship it", and "Scale & operate" are shared: half blue, half gray, with both badges. Legend at the bottom: "🧑🏽 = humans lead", "🤖 = mostly done by agents".
1b. "verification": Kent C. Dodds' testing trophy (static base, unit stem, big integration bowl, end-to-end on top, which matters even more with agents since agent-written unit tests can pass while the app is broken), plus three clusters: edge cases (property + fuzz tests), safe and fast (security + load tests), and guaranteed correct (formal proofs in Lean). Each with a quiz-app example.
2. "understanding the machine": three cards (computational thinking, how computers work, how AI works), each with what it is and why it matters.
3. "product judgment": judgment, prioritization, agency, taste.
4. "working with people": collaboration, communication, feedback.

#### Details

Agents write the code, but these skills haven't gone away. Most matter *more* now, because they're the parts agents are weakest at. They're the foundation, and each one gets its own row in the grade-band progression (section 5).

Show: the lifecycle loop from the first talk, with the human-heavy boxes highlighted.

The lifecycle skills:

1. **Problem design:** understand who it's for and what they need, then describe it precisely (a spec with examples).
2. **System design:** high-level architecture: how the pieces fit together, data, interfaces, and tradeoffs. Agents are weakest here, and architecture depends on context only people have.
3. **Verification:** does it work? Check the output, not the code: tests, edge cases, evals, security, and trying it like a user would. Agents pass tests but miss what makes software good.
4. **User feedback and usability:** does it do what people *meant*, and is it pleasant and accessible to use? Only real users can answer this.

The foundations:

6. **How computers work:** from code down to memory, networks, and the CPU/GPU. You can't judge agent output, or know what's possible, if the machine is a black box.
7. **How AI works:** AI models are probabilistic: same question, different answers. They learn from training data, so they inherit its gaps and biases, and they can sound confident while being wrong. Everyone uses AI systems now, long before they build anything, so this is for every student, not just future engineers.

#### Product judgment and working with people: what sets the best engineers apart

Cards: judgment, prioritization, agency, taste, and collaboration (moved here from the lifecycle slide). Collaboration and communication: building with a team, giving and receiving feedback, and explaining and defending your decisions. Software is built with and for people, and agents don't change that. It still gets its own row in the grade-band progression.

Once the foundation is there, these are what distinguish great engineers working with agents. From my notes (find the source to cite):

- **Judgment:** is this approach the right one? Should this feature ship or be binned? Is it safe and fair?
- **Prioritization:** what's the most important thing to work on next, and what's not worth doing right now?
- **Agency:** relentlessly coming up with ideas and parallelizing work with agents, without being prompted.
- **Taste:** knowing what "great" looks like, in functionality, architecture, and design.


These build on the foundation: you can't have taste in architecture without knowing system design, or judge an approach without knowing how computers (and AI) work. They grow mostly through open-ended projects with real choices, so they show up more in 9-12 and college.

Open question: can we teach these directly, or do they come from doing lots of projects and getting feedback?

## 4. What changes in the classroom

The shifts are the main slides. The quiz-app example sets them up, and keep/change/add/drop sums them up.

### A quiz app project, before and after AI

One slide, two columns:

- **Before AI:** a classic unit project, a quiz app. Students spend weeks on syntax, loops, and getting it to run. Most of the learning is about getting code onto the page.
- **After AI:** an agent builds a working quiz app in five minutes. So what do students do with the rest of the unit?
- The answer is the rest of this section: the learning moves to before and after the code.

### Shift 1: From writing code to describing what you want

- What students write for an agent is a specification: who it's for, what it should do, examples, and constraints.
- Natural language is ambiguous, so vague descriptions get vague results. Precision is the skill.
- In class: write the spec and examples before anyone (human or agent) writes code.

### Shift 2: From "it runs" to "it's verified"

- Getting it to run used to be the finish line. Now it's the starting line.
- Does it work on the edge cases? Is it secure, usable, accessible? Is it what the user meant?
- In class: tests, bug hunts, and accessibility checks on agent-built apps.

### Shift 3: From the autograder to real users

- An assignment with no user has no way to tell if it's good, only if it runs.
- Build for a real person: a classmate, a teacher, a school club, a family member.
- In class: interview the user first, test with them at the end, iterate.

### Shift 4: From grading code to grading decisions

- If an agent can write the code, the code alone doesn't show what a student learned.
- Grade the specs, tests, design diagrams, and explanations of why.
- In class: demos and short oral explanations: "Walk me through why you built it this way."

### Shift 5: From AI-proof assignments to AI-assumed assignments

- Trying to keep AI out of assignments is a losing battle, and it doesn't prepare students for how software is built.
- Design assignments that assume students use AI, and are still hard: the challenge is in deciding, designing, and verifying.
- In class: be clear about when AI is expected, when it's not (building a mental model by hand), and how to disclose it.

### Summary: a curriculum diff (change, add, drop)

One slide, four quadrants:

| Keep | Change |
|---|---|
| Computational thinking, how computers work, collaboration | When and how much students write code by hand, what we grade |

| Add | Drop (or shrink) |
|---|---|
| How AI works, specs, verification, user testing | Syntax drills, memorizing APIs, assignments that end at "it runs" |

Leads into section 5: what this looks like at each age.

## 5. By grade band

Start with one slide showing how each skill builds across the grades, then go through one grade band at a time.

### Skill progression across grades

| Skill | K-4 | 5-8 | 9-12 | College |
|---|---|---|---|---|
| Problem design | Give precise instructions | Interview a user, write a spec with examples | Spec for a real client: requirements, examples, constraints | Spec as the main artifact, discovery with real stakeholders |
| System design | Break a task into steps | Plan with flowcharts, decide what data to store | Draw the architecture and data model before prompting, refactor agent output | Architecture tradeoffs, design across many files and services |
| Verification | Predict, run, compare | Write test cases and edge cases first, find bugs in AI-built apps by testing them | Write tests for agent code, evals for AI features, security basics | Test suites, CI, monitoring, security, performance, reviewing agent output at scale |
| User feedback and usability | "Did my partner get what they wanted?" | Peer review: does it work for the person it's for? | User testing with a real client, accessibility audits | Usability studies, iterating on real user data |
| Programming basics | Sequences, loops, patterns | Predict what a program will do, variables, conditions, loops | Data structures, algorithms, enough hand-coding for a mental model | Algorithms, complexity, theory |
| How computers work | Inputs, outputs, and stored information | Hardware, binary, how the internet sends data | Memory, networks, how an app talks to a server and a database | Systems from code down to the CPU/GPU/NPU: OS, networks, databases |
| How AI works | AI learns from examples, guesses, and can be wrong or unfair | Training data and bias, why answers vary, AI makes things up, privacy | Build on AI models: prompts, context, embeddings, evals, bias testing | Machine learning, neural networks, LLMs, building AI-powered systems |
| Collaboration and communication | Pair programming, taking turns | Team projects, giving kind and specific feedback | Peer review, team roles, presenting and defending decisions | Team-based projects, review norms, technical writing |

Optional: show it as a staircase, with each skill growing from a playful version to a professional one.

### K-4: Understand the AI you already use, and say exactly what you mean

Kids talk to voice assistants, get video recommendations, and see AI-generated images long before they build anything. So K-4 starts with how AI works.

- **How AI works (the emphasis for this band):**
  - AI learns from examples. Train a simple image classifier as a class (e.g. Teachable Machine), then see it fail on things it never saw.
  - AI guesses, so it can give different answers to the same question. Unplugged: build a story by drawing the next word from a bag, and compare stories.
  - AI can be wrong, even when it sounds sure. Ask a chatbot (teacher-led) a question the class knows the answer to.
  - AI can be unfair. If we only trained it on pictures of one kind of dog, what happens with other dogs? Who gets left out?
  - People decide what to trust, and when to ask a grown-up.
- **Problem design:** give precise instructions, and notice what happens when someone follows them literally (the PB&J sandwich activity).
- **Verification:** predict what a program will do, run it, compare. Debugging is a normal part of building.
- **User feedback:** build something for a partner, then ask: is this what you wanted?
- **Programming basics:** sequences, loops, and conditionals, only unplugged or with robots like LEGO SPIKE Essential.
- **How computers work:** inputs, outputs, and how computers store information.
- **In class:** students describe a drawing or a dance, and the teacher (or a teacher-run agent) builds exactly what they said. Did it match?
- **AI tools:** teacher-led, whole-class demos only.
- **Code.org AI activities:** [AI for Oceans](https://code.org/oceans) (grades 3+, train a model to sort fish from trash, then see where it goes wrong), How AI Makes Decisions (grades 3-5, one-week unit).
- **CS Unplugged:** [Kidbots](https://www.csunplugged.org/en/topics/kidbots/) (precise instructions), [Error detection](https://www.csunplugged.org/en/topics/error-detection-and-correction/) (verification), [Chocolate Factory](https://classic.csunplugged.org/activities/human-interface-design/) (user feedback), [Binary numbers](https://www.csunplugged.org/en/topics/binary-numbers/) (how computers work), [Orange Game](https://classic.csunplugged.org/activities/routing-and-deadlock/) (how the web works).
- **Standards:** AI4K12 Five Big Ideas (perception, representation and reasoning, learning, natural interaction, societal impact). CSTA: 1A-AP-12 (develop plans), 1B-AP-13 (plan by considering user preferences), plus 1A-AP-08 (model daily processes as algorithms), 1A-AP-11 (decompose steps), 1A-AP-14 (debug).

### 5-8: Build for someone else

- **Problem design:** interview a user (a classmate, a teacher, a family member) before building. Write a short spec with examples.
- **System design:** plan with flowcharts or pseudocode. What data does the program need to store?
- **Verification:** write test cases, including edge cases, before building. Find the bugs in AI-written code.
- **User feedback and usability:** peer review and quick user tests. Is it easy to use? Can everyone use it?
- **Programming basics:** block-based or Python. Mostly reading code: predict what a program will do, then run it.
- **How computers work:** hardware and software, binary, how the internet sends data.
- **Collaboration:** team projects, giving kind and specific feedback on each other's work.
- **How AI works:** training data and where bias comes from. Why the same prompt gives different answers. Why AI makes things up, and how to check. What happens to the data you give an AI tool, and what data your own program collects.
- **In class:** write a spec and examples for a small tool (a quiz, a classroom timer), then compare what an agent builds against the spec.
- **AI tools:** teacher-guided, using education platforms with age-appropriate terms. Hand-written code for core concepts.
- **Code.org AI activities:** AI Discoveries (6-8, full year), Thinking Critically About AI (6-8, one month), AI and Machine Learning (6-12, CS Discoveries unit 7), How AI Works (6-12, video series).
- **Standards:** 2-AP-15 (incorporate feedback from users to meet user needs), 2-AP-17 (test using a range of test cases), plus 2-AP-10 (flowcharts/pseudocode), 2-IC-23 (tradeoffs of public vs. private information).

### 9-12: Build real software, and stand behind it

- **Problem design:** specs for a real client: requirements, examples, constraints, what "done" looks like. Context engineering: what does the agent need to know?
- **System design:** draw the architecture and data model before prompting. Ask the agent to explain the structure it built, and compare it against your design. Document design decisions.
- **Verification:** write the tests for agent-written code. Security basics.
- **User feedback and usability:** user testing with the real client. Accessibility and bias audits. Iterate on what you learn.
- **Computational thinking:** text-based programming, data structures, algorithms. Write some code by hand to build a mental model of how programs work.
- **How computers work:** memory, networks, and how an app talks to a server and a database. What actually happens when the agent's code runs?
- **How AI works:** build a small app on top of an AI model: prompts, context, embeddings. Test it for bias and write evals, since its output is probabilistic.
- **Collaboration and communication:** team roles, reviewing each other's (and agents') work, presenting and defending design decisions.
- **Judgment and prioritization:** what should we build first, and what shouldn't we build at all?
- **In class:** semester project for a real client (a school club, a local business, a teacher), ending with a demo where students defend their design decisions.
- **AP courses (own slide, "9-12: Where the AP courses fit"):** a checkmark table of the skills vs. AP CSP and AP CSA. AP CSP is much more relevant: it covers the goals of both 9-12 slides (Create task asks for purpose and testing; big ideas include creative development, data, systems and networks, impact of computing). AP CSA is still useful for students who want to see how programs work under the hood.
- **AI tools:** students use coding agents directly, with a disclosure of how they used them.
- **Code.org AI activities:** AI Foundations (9-12, full year or semester), Foundations of Generative AI (9-12, with an unplugged version), Coding with AI (6-12, using LLMs to write code), Computer Vision (6-12), AI and the Systems that Power It (9-12).
- **Standards:** 3A-AP-19 (incorporate feedback from users), 3A-AP-21 (make artifacts more usable and accessible), 3A-AP-23 (document design decisions), 3A-IC-25 (test and refine to reduce bias), plus 3B-AP-21 (test cases against design specs), 3B-AP-08 and 3B-AP-09 (how AI drives systems, implement an AI algorithm). Practice P6: Testing and Refining Computational Artifacts.

### College: Software you can stand behind

- **Problem design:** specs and tests from day one of the intro course (CACM). Product engineering: talk to users, decide what to build.
- **System design:** architecture tradeoffs, design across many files and services. Old practices work great with agents: design up front, build a "tracer bullet" first.
- **Verification:** software engineering practices from the first year instead of an upper-level elective: test suites, CI, monitoring, security, performance. Reviewing agent output at scale, by its behavior rather than line by line.
- **User feedback and usability:** HCI and usability studies, accessibility, iterating on real user data.
- **Computational thinking:** algorithms, complexity, and theory.
- **How computers work, with more depth:** from code down to the CPU/GPU/NPU: operating systems, networks, databases. That's what lets you judge agent output and know what's possible.
- **Collaboration and communication:** team-based projects throughout, review norms, technical writing.
- **How AI works:** machine learning, neural networks, and how LLMs are trained. Building AI-powered systems: context engineering, RAG, tool calling, evals.
- **New topics:** working with many agents in parallel.
- **In class:** capstones with real clients, graded on impact and process. Oral defenses of design decisions.

## 6. Closing and discussion

### Closing: Every student will build software

- Callback to personal software from the first talk: "faster to build it than to find it." Your students will build tools for their families, their jobs, and their communities, whether or not they ever take another CS class.
- They'll build them with AI, with or without us.
- The question is whether they'll know how to build things that work, that are fair, and that do what people meant: the skills from this talk.
- End with: "That's our job now. So let's figure out how, together."

### Open questions for discussion

Leave this slide up for the rest of the session. Open table discussion: start with whichever question gets the most reaction.

- Should students still write code by hand? How much, and when?
- Will people still read code, or only review what it does? If only the output, what do students need to understand to review it well?
- What do we grade now?
- When should students start using agents themselves?
- How do we teach students to tell if something actually works?
- What happens to students who love to code?
- What do teachers need (training, tools, time) to teach this way?
- Who gets access to good AI tools at school and at home?

### Thank you

Thank-you slide with links to the slides and resources, as the backdrop once discussion wraps up.

## Resources

- [Teaching Novice Computing and Programming in the Agentic AI Era](https://cacm.acm.org/opinion/teaching-novice-computing-and-programming-in-the-agentic-ai-era/), CACM
- [Software engineering at Google and AI](https://newsletter.pragmaticengineer.com/p/software-engineering-at-google-and), The Pragmatic Engineer with Titus Winters
- [Syntax recall was never the goal](https://jamiemaguire.net/index.php/2026/10/17/syntax-recall-was-never-the-goal/), Jamie Maguire
- [We are all Product Engineers now](https://seldo.com/posts/we-are-all-product-engineers-now/), Laurie Voss
- [CSTA K-12 Computer Science Standards](https://csteachers.org/k12standards/interactive/)
- [Code.org AI curriculum catalog](https://studio.code.org/catalog?topic=artificial_intelligence) and [Code.org AI hub](https://code.org/artificial-intelligence)
- [AI4K12 Five Big Ideas in AI](https://ai4k12.org/)
- [CS Unplugged](https://www.csunplugged.org/)
- [The Impact of AI on Software Engineering](https://pamelafox.github.io/my-py-talks/impact-of-ai-on-cs/), the first talk

## To verify

- Source for the judgment / prioritization / agency / taste list.
- CSTA standards not in the first deck: 1A-AP-08, 1A-AP-11, 1A-AP-14, 2-AP-10, 2-IC-23, 3B-AP-21, 3B-AP-08, 3B-AP-09.
- Code.org course names and grade ranges (from their catalog, Nov 2026).
- Age requirements (13+) for the AI tools teachers are likely to use, including Teachable Machine.
- AI4K12 Five Big Ideas wording.
