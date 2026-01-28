# 🧠 Conversational AI with Agent Handoff (FastAPI + LLMs)

A production-oriented example of implementing **agent handoff** in a conversational AI system using Large Language Models (LLMs).

The project focuses on **clarity, control, and real-world applicability**, showing how different conversational agents can take ownership of a conversation depending on **user intent and context**.

---

## 🚀 What is this project?

This repository demonstrates a **multi-agent conversational assistant** where:

- Different agents handle different responsibilities (UX, technical, etc.)
- Control of the conversation can be **handed off** between agents
- A central orchestrator maintains state and routing logic

Instead of a single “do-everything” chatbot, the system is designed to resemble how real organizations work:  
general intake first, specialists when needed.

---

## 🏗️ High-Level Architecture

```text
User
│
▼
FastAPI API (Director / Orchestrator)
│
├─ Router (intent detection)
│
├─ UX Agent (formal, structured, non-technical)
│
└─ Technical Agent (specialist, implementation-focused)
````

* Only **one agent is active at a time**
* The orchestrator maintains **session state**
* Agents can trigger a **handoff** when intent changes

---

## 🧩 How it works

### FastAPI as the Director

FastAPI acts as the central coordinator:

* Receives user messages
* Loads session state
* Determines the active agent
* Applies routing and handoff rules

### Routing & Handoff

A lightweight router decides whether:

* The current agent should continue
* Or the conversation should be handed off to another agent

In this demo, routing is keyword-based.
In production, this could be an LLM classifier or a hybrid approach.

### Agent Configuration

Each agent defines:

* Its role and tone (system prompt)
* Model parameters (`temperature`, `max_tokens`)
* Allowed tools and permissions

This allows the system to adapt responses without changing models.

---

## 🧪 Example Flow

1. User asks a general question
2. UX Agent responds
3. Technical intent is detected
4. Conversation is handed off to the Technical Agent

The transition is seamless — the user does not repeat themselves.

---

## 🛠️ Tech Stack

* **Python**
* **FastAPI**
* **Large Language Models** (Claude, GPT, Gemini – configurable)
* Session-based state management
* Agent-oriented architecture

---

## 👤 About the author

Created by **Diego Isla** — Senior Backend Engineer · AI Enthusiast.

If you’re a recruiter or hiring manager, this repository is meant to be **read, not just run**.
Feel free to explore the codebase and reach out — feedback is always welcome.
