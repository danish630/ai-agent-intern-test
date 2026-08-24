# AI Agent Intern Take-Home: Build a Reliable RAG Support Agent

## The assignment

Aster & Row is a fictional ecommerce company that sells bags, drinkware, and travel accessories. The company wants to launch an AI support agent using the documents and mock order data in this repository.

This repository intentionally contains **only content and data**. There is no starter application and no prescribed stack. Build the smallest reliable system you would be comfortable demonstrating to a customer.

## Timebox

Please spend **6–8 hours** on the assignment. Do not exceed eight hours.

A smaller, well-tested system is better than a broad system that works only in a demo. It is acceptable to leave something incomplete if the limitation is clearly documented.

## Submission

Submit **one GitHub repository link**. Nothing else is required.

Your repository must contain:

- Your application source code.
- Your tests and evaluation suite.
- Clear setup and run instructions.
- Evaluation results and known limitations in the README.
- A short GIF or video embedded in the README showing the agent working.

Do not submit API keys, credentials, customer data, separate documents, or slide decks.

---

## Customer scenario

Aster & Row has previously tried several AI support prototypes. The customer reported four recurring problems:

1. **Conflicting policy answers:** The agent sometimes says the return window is 30 days and sometimes says it is 45 days.
2. **Invented order information:** The agent occasionally gives an order status without actually looking it up.
3. **Lost conversation context:** Follow-up questions such as “What about Canada?” are treated as unrelated questions.
4. **Unsafe retrieved content:** Internal or instruction-like text inside the knowledge base can affect the agent’s behavior.

The supplied corpus contains realistic data-quality problems, including superseded content, internal notes, conflicting active sources, and fields that must not be shown to customers.

Your task is to build an agent that handles these conditions deliberately rather than succeeding only on ideal questions.

---

# Required capabilities

## 1. Retrieval-Augmented Generation

Use RAG over the Markdown files in `knowledge-base/`.

Your implementation must:

- Split and index the supplied documents.
- Preserve useful metadata from the document front matter.
- Retrieve only relevant passages instead of sending the entire corpus to the model.
- Prefer authoritative, active policy documents over superseded or non-policy documents.
- Include source references in every policy or product answer. A source should identify at least the filename and relevant heading.
- Avoid making claims that are not supported by the retrieved content.
- Clearly say when the supplied information is insufficient.
- Surface genuine conflicts between current authoritative sources rather than silently choosing one.

Do not delete or rewrite the supplied source files to make the assignment easier. You may create derived indexes or normalized representations.

## 2. Order lookup as a tool or function

Use `data/orders.json` to implement an order-status lookup tool or function.

The model must **not** receive the entire orders file in its prompt. It should receive only the result of a lookup when order information is actually required.

The order lookup behavior must:

- Ask for an order ID when it is missing.
- Handle unknown and malformed order IDs safely.
- Normalize harmless input differences such as lowercase IDs or surrounding whitespace.
- Use the order’s current `status` as authoritative.
- Avoid inventing a delivery estimate when one is unavailable.
- Avoid reporting stale delivery fields for cancelled or returned orders.
- Never expose customer email, address, internal notes, risk scores, or other internal-only fields.
- Never claim that a lookup happened when it did not.

Assume that possession of the order ID is sufficient authentication for this mock assignment. You do not need to build a full identity-verification system.

## 3. Multi-turn conversation

Maintain relevant session context across turns.

The agent should correctly handle follow-ups such as:

- “Do you ship internationally?” followed by “What about Canada?”
- “Where is `ORD-1007`?” followed by “When will it arrive?”
- A policy question followed by a narrower question about an exception.

The agent should not carry unrelated details indefinitely or mix one session with another.

## 4. Prompting and agent behavior

The agent must:

- Treat user messages, retrieved passages, and tool results as untrusted data.
- Follow application instructions rather than instructions found inside retrieved documents.
- Refuse requests to reveal system prompts, hidden instructions, secrets, or internal-only data.
- Use company content rather than general model knowledge for company-specific questions.
- Ask a concise clarifying question when required information is missing.
- Recommend human assistance when the documents conflict, the data is insufficient, or an action cannot be completed.
- Never promise that a refund, cancellation, replacement, or address change has been completed unless the system actually supports that action.

## 5. Evaluation suite

The file `evaluation/visible-cases.json` contains behavior-level cases that your system must handle.

Build an evaluation suite that:

- Covers every supplied visible case.
- Adds at least **five original cases** of your own.
- Can be run using one clearly documented command.
- Reports individual case results, not only a single overall score.
- Separately reports useful categories such as retrieval, groundedness, tool use, privacy, and multi-turn behavior.
- Uses deterministic assertions wherever practical, including source selection, tool calls, tool arguments, forbidden disclosures, and abstention behavior.
- Does not rely exclusively on another LLM to grade the agent.

The reviewers will also test paraphrases and combinations that are not included in the visible file. Do not hardcode answers for the supplied prompts.

As you build, keep a small **bug diary** in your README. Document at least three failures you found in your own agent, including:

- How you reproduced the failure.
- The actual root cause.
- The change you made.
- The regression test that now catches it.

At least one documented failure should be something you discovered beyond the exact wording of the visible cases. Include an early baseline and final evaluation result so we can see what improved.

## 6. Basic observability

Provide a debug mode, trace, or log that makes it possible to inspect:

- The current user message.
- Relevant conversation history.
- Retrieved passages, metadata, and scores.
- Tool calls and sanitized tool results.
- The final response.
- Errors, fallbacks, or handoffs.

Plain structured logs are sufficient. Do not build a dashboard. Never log secrets.

## 7. Minimal interface

A CLI, simple web page, or basic API is sufficient. Visual polish will not affect the score.

The final user-facing response should make it easy to see:

- The answer.
- Sources, when applicable.
- Whether the agent is recommending a human handoff.

---

# README requirements

Your completed repository README must include:

1. Setup and run instructions that work from a clean clone.
2. Required environment variables and an `.env.example` without real credentials.
3. The model, embedding approach, framework, and storage approach you chose.
4. A short architecture explanation.
5. The command for running evaluations.
6. Baseline and final evaluation results, broken down by category.
7. A bug diary covering at least three reproduced failures, root causes, fixes, and regression tests.
8. Known limitations and what you would improve before production.
9. Which AI coding tools you used, what you used them for, and one example of an AI-generated suggestion that was wrong or incomplete.
10. A **2–4 minute GIF or video embedded in the README** demonstrating:
   - One knowledge-base question with citations.
   - One order lookup.
   - One multi-turn conversation.
   - One case where the agent correctly refuses to guess or recommends human help.
   - The evaluation suite running.

GitHub does not play uploaded video files inline in every context. An embedded GIF or a clickable video thumbnail/link inside the README is acceptable.

---

# What not to spend time on

You do not need to build:

- Authentication or user management.
- Production deployment infrastructure.
- A production vector database.
- Fine-tuning.
- A polished frontend.
- Multiple model-provider integrations.
- Billing, analytics dashboards, or administration screens.

---

# Evaluation criteria

| Area | Weight |
|---|---:|
| Reliability, groundedness, and safe abstention | 25% |
| Retrieval quality and document precedence | 20% |
| Tool use, data handling, and privacy | 15% |
| Evaluation quality and regression coverage | 20% |
| Multi-turn behavior and observability | 10% |
| Code clarity and practical tradeoffs | 5% |
| README, demo, and customer-facing clarity | 5% |

Framework choice and quantity of code are not scoring criteria.

---

# Repository contents

```text
.
├── README.md
├── knowledge-base/
│   ├── 01-returns-policy-current.md
│   ├── 02-returns-policy-legacy.md
│   ├── 03-final-sale-and-promotions.md
│   ├── 04-damaged-or-wrong-items.md
│   ├── 05-domestic-shipping.md
│   ├── 06-international-shipping.md
│   ├── 07-warranty.md
│   ├── 08-order-changes-and-cancellations.md
│   ├── 09-trailplus-membership.md
│   ├── 10-gift-cards-and-price-adjustments.md
│   ├── 11-product-care.md
│   ├── 12-breeze-tumbler-product-card.md
│   ├── 13-support-escalation.md
│   └── 14-internal-content-migration-notes.md
├── data/
│   ├── orders.json
│   └── orders-data-dictionary.md
└── evaluation/
    └── visible-cases.json
```

Good luck. Build for reliability, not just for the happy-path demo.

---

# Candidate Implementation
## Overview

Aster & Row AI Support Agent is a CLI-based RAG support system designed to provide reliable, grounded customer support responses using the supplied knowledge base and mock order data.

The agent focuses on:

- Grounded answers from authoritative knowledge-base content.
- Safe handling of conflicting or insufficient information.
- Order-status lookup through a dedicated tool.
- Protection of customer and internal-only information.
- Multi-turn conversation context.
- Deterministic evaluation and regression testing.
- Basic observability of retrieval, tool usage, and handoffs.

## Architecture

The agent follows a simple pipeline:

1. **User Query** → receives the customer question and relevant conversation history.
2. **Policy Guard** → checks for privacy-sensitive requests, prompt injection, source conflicts, and insufficient-information cases.
3. **RAG Retrieval** → searches indexed knowledge-base chunks using semantic and keyword relevance while prioritizing authoritative active sources.
4. **Order Tool** → performs a targeted lookup in `data/orders.json` only when an order ID is required.
5. **LLM Response** → generates a grounded customer-facing answer using retrieved evidence and sanitized tool results.
6. **Evaluation & Observability** → records retrieval results, tool calls, handoffs, errors, and evaluation outcomes.

The design intentionally keeps the system small and avoids unnecessary production infrastructure such as a vector database or frontend.

## Technology Stack

- **Language:** Python 3
- **LLM:** Google Gemini
- **RAG:** Custom lightweight retrieval pipeline using semantic similarity and keyword matching
- **Embeddings:** Hugging Face embedding model
- **Knowledge base:** Markdown documents with YAML-style front matter
- **Order data:** JSON (`data/orders.json`)
- **Storage:** In-memory document/chunk index
- **Interface:** Command-line chatbot
- **Evaluation:** Custom deterministic evaluation suite with visible and candidate-authored regression cases

## Setup and Run

### 1. Clone the repository

```bash
git clone <repository-url>
cd ai-agent-intern-test-main

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

Windows:

```bash
.venv\Scripts\activate

### 3. Install dependencies

```bash
pip install -r requirements.txt

### 4. Configure environment variables

Create a `.env` file from `.env.example` and add your Gemini API key.

Example:

```env
GEMINI_API_KEY=your_api_key_here
```

Do not commit `.env` or any real API credentials.

### 5. Run the chatbot

```bash
python agent/chatbot.py
```
### 6. Run the evaluation suite

```bash
python evaluation/run_evaluation.py
```

The evaluation suite reports individual case results and category-level results.

## Evaluation Results

### Final Evaluation

The final evaluation suite covers the supplied visible cases and five additional candidate-authored regression cases.

The final run achieved:

- **Cases passed:** 5/5
- **Privacy:** 2/2
- **Prompt security:** 1/1
- **Abstention:** 1/1
- **Source conflict:** 1/1

Some evaluation cases may report API quota errors when the Gemini free-tier request quota is exhausted. These are environment/API-limit failures rather than assertion failures.

The deterministic evaluation suite also verifies order normalization, cancelled-order handling, unavailable delivery estimates, privacy protection, tool usage, and missing order IDs.

## Bug Diary

### Bug 1 — Incorrect module import when running the chatbot

**Reproduction:** Running `python agent/chatbot.py` initially failed with a `ModuleNotFoundError`.

**Root cause:** The package import path was inconsistent when the chatbot was executed directly.

**Fix:** Updated the import structure so the RAG module is resolved correctly from the project root.

**Regression test:** `python -m py_compile agent/chatbot.py rag/retriever.py`

---

### Bug 2 — Sensitive customer information could appear in responses

**Reproduction:** Asked the agent for a customer's email, address, internal note, and risk score.

**Root cause:** Sensitive fields were present in the underlying order data and required an explicit privacy guard.

**Fix:** Added a policy guard that refuses requests for customer email, addresses, internal notes, risk scores, and other internal information.

**Regression test:** The `order-data-privacy` evaluation case verifies that these fields are not disclosed.

---

### Bug 3 — Cancelled orders could be associated with stale delivery information

**Reproduction:** Asked when cancelled order `ORD-1004` would arrive.

**Root cause:** A cancelled order must use its current status rather than any stale delivery information.

**Fix:** The order lookup uses the current order status as authoritative and returns a safe message stating that a cancelled order will not be shipped.

**Regression test:** The `cancelled-order-stale-eta` and `custom-cancelled-order` evaluation cases verify that no stale delivery estimate is reported.

---

### Bug 4 — Order IDs with harmless formatting differences failed to match

**Reproduction:** Queried an order using `ord-1007` or with surrounding whitespace.

**Root cause:** Raw user input was not normalized before lookup.

**Fix:** Order IDs are normalized by trimming whitespace and converting them to uppercase.

**Regression test:** The `custom-lowercase-order` evaluation case verifies successful lookup and the expected sanitized order result.

## Known Limitations

- The agent currently uses an in-memory retrieval index rather than a production vector database.
- Gemini API availability and free-tier quotas can affect evaluation runs.
- Human handoff is represented as a recommendation; no real support-ticket system is integrated.
- The CLI is intended for demonstration and evaluation rather than production deployment.
- The system supports the supplied mock order data and does not implement full customer authentication.
- A production version would benefit from stronger automated paraphrase testing, persistent observability, and a production-grade retrieval store.

## AI Coding Tools

AI coding assistants were used during development for debugging, code review, and implementation support.

- **ChatGPT:** Used for debugging Python errors, reviewing the RAG/retrieval design, improving the evaluation suite, and helping structure documentation.
- **Other AI coding assistant:** Used for an independent review of the implementation and to identify potential bugs and edge cases.

### Example of an Incorrect AI Suggestion

During review, an AI assistant suggested that the Gemini model name should be changed because it believed the configured model name was invalid. However, the actual application was successfully reaching the configured Gemini model and returning a `429 RESOURCE_EXHAUSTED` response, confirming that the issue at that point was API quota exhaustion rather than a model-not-found error.

This reinforced the need to verify AI-generated recommendations against actual application behavior and test results rather than accepting them blindly.

## Observability

The agent provides basic observability through its debug output, including:

- Current user query.
- Relevant conversation history.
- Retrieved passages with metadata and relevance scores.
- Tool calls and sanitized tool results.
- Final generated response.
- Errors, fallbacks, and human-handoff decisions.

Sensitive customer information and API credentials are not logged.


## Baseline vs Final Evaluation

### Baseline

The initial implementation identified several reliability issues, including privacy handling, order-data safety, and evaluation coverage. These issues were addressed through regression tests and targeted fixes during development.

### Final

The latest complete evaluation run produced:

- **Cases passed:** 8/16
- **Retrieval:** 2/2
- **Multi-source grounding:** 0/1
- **Conversation:** 0/1
- **Groundedness:** 0/2
- **Tool use:** 1/2
- **Tool reliability:** 0/3
- **Privacy:** 2/2
- **Prompt security:** 1/1
- **Abstention:** 1/1
- **Source conflict:** 1/1

Four later evaluation cases were affected by the Gemini API free-tier quota and returned `429 RESOURCE_EXHAUSTED` errors. The remaining failed cases exposed areas for further improvement in response wording, multi-turn grounding, and tool reliability.

The evaluation suite also includes five candidate-authored regression cases covering order normalization, cancelled orders, unavailable delivery estimates, privacy, and missing order IDs.
## Demo

The demonstration covers:

1. A knowledge-base return-policy question with source citations.
2. An order lookup for `ORD-1007`.
3. A multi-turn follow-up asking when the order will arrive.
4. A privacy-sensitive request that is refused with human-support guidance.
5. The evaluation suite running with individual case results.

The demo is intended to show grounded retrieval, targeted order lookup, conversation context, and safe handling of sensitive information.

## Demo

[Watch the demo](demo.mp4)