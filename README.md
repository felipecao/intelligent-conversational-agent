# intelligent-conversational-agent
> Conversational AI system that simulates a Customer Support Agent for a fictional business

# This repo

This repository implements:
- Frontend: a simple chat interface implemented using [Streamlit](https://streamlit.io/)
- Backend: a HTTP API implemented using: 
  - [FastAPI](https://fastapi.tiangolo.com/) for HTTP routing
  - [SQLModel](https://sqlmodel.tiangolo.com/) as ORM
  - [LangChain Deep Agents](https://github.com/langchain-ai/deepagents) for agents orchestration

# Setup instructions

## Install uv package manager
- Follow instructions on https://docs.astral.sh/uv/getting-started/installation/
- Then on the project root run `uv sync` to install dependencies

## Seed DB
- On project root run `docker compose up -d`
- Then run `yoyo apply` and accept all questions

## Configure environment variables
- Make a copy of `.env.example` and call it `.env`
- Fill in `OPENAI_API_KEY`

### Start backend
- Run `uv run fastapi dev`

## Start frontend
- Run `uv run python -m streamlit run frontend/streamlit_frontend.py`
- **Voice (optional):** use the microphone control in the app to record a message. The backend transcribes with OpenAI Whisper (`POST /voice/transcribe`) and reads replies aloud with OpenAI TTS (`POST /voice/speak`). The same `OPENAI_API_KEY` as chat is used. Allow microphone access in your browser (HTTPS or `localhost`).

# System architecture overview

```
.
├── app/
│   ├── agents/        | holds the customer support agent and its subagents
│   │   └── tools/     | tools used by the agents
│   ├── entities/      | ORM entities
│   ├── repositories/  | holds the repositories (data access layer)
│   └── routers/       | routing of HTTP requests coming from frontend
└── frontend/          | frontend layer
```

Information flows in the following way:
1. User browses to http://localhost:8501/ and inputs a prompt
2. The request gets routed to the `chat_stream` router on `chat.py`...
3. ... which relays the prompt to the `CustomerSupportAgent`
4. Said agent will analyze the tone and contents of the message to decide which tool(s) to invoke. It might also offer a reward to the user, if it realizes the customer is angry or frustrated
5. Each tool calls different repository methods to fulfill what the user requests
6. Input validations are done automatically by the agents, based on the types of the parameters

# Explanation of key design decisions

## audio models

I've picked `tts-1` and `whisper-1` for a few simple reasons:
- **cost**: they're much cheaper than other more optimized models (e.g.: `tts-1`, `tts-1-hd`, `gpt-4o-audio-preview-2025-06-03`, `gpt-audio-2025-08-28`)
- **scope**: in my tests, I considered `tts-1` and `whisper-1` accurate enough for the scope of this exercise
- **speed**: both models demonstrated good speed when translating text <-> audio

## voice interactions

When sending a voice prompt, the app does 2 things:
- invokes an endpoint for transcribing audio to text
- writes the transcription on the prompt textbox as opposed to firing a request to backend

This UX might not be considered optimal, but I decided for this approach to minimize user frustration. My angle was that it'd be frustrating for the user to speak their prompt and then have to wait a few seconds to then realize the transcription didn't go well and get a response that didn't help them. I opted for a "Human In The Loop" approach where they'd need to review the transcription before invoking the agent.
 
## Frontend implementation: Streamlit vs React

With a baby at home, my time was pretty limited during this weekend. Also, I'm far from being a frontend specialist. So, if I tried to create a fancy SPA in React, it'd:
- make me spend more time, especially in situations where I couldn't debate the best approach with Cursor
- add little value, as the focus of the exercise is not on UX

Therefore, I decided to go with a no-brainer option for the frontend: Streamlit, which I find to be a bit of a standard when it comes to Pythonic data apps.

## using LangChain Deep Agents

As per their README, "Deep Agents is an agent harness. An opinionated, ready-to-run agent out of the box. Instead of wiring up prompts, tools, and context management yourself, you get a working agent immediately and customize what you need". This is something I already use in my day-to-day work, so it was another no-brainer. 

It allows me to focus on writing good descriptions for the tools and on good system prompts for the agents, barely having to worry about orchestration among them, or any other feature. For instance, if some large file has to be written to the filesystem to save space on the context window, or if I ever need a bare bones agent to handle simple inquiries, Deep Agents takes care of that for me.

In the end, for the purpose of this exercise, I decided to go with a small and simple agentic architecture:

```
.
└── Customer Support Agent: in charge of support operational tasks: create tickets, escalate them, close tickets, etc
    ├── Master Data Sub Agent: acts as a kind of "agentic CRUD interface", providing access to "static" data like: statuses, urgencies, orders, etc
    └── Sentiment Analysis Sub Agent: responsible for delivering the bonues feature 'Add sentiment analysis to detect customer frustration'
```

Each of them with their respective tools, enabling the agents to perform their duties while reducing the amount of space taken in their respective context windows.

- no automated tests

# Description of potential improvements
- better frontend
- an agent that runs SQL queries autonomously, thus replacing all the `get` / `list` methods on repositories

# Limitations
- no login screen / support to multi tenants
- absence of unit tests
- lack of human supervision in the generation of frontend and SSE-related code
- use pydantic models for agentic tools