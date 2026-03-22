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
- deepagents
- little focus on frontend
- no automated tests
- no voice interaction?

# Description of potential improvements
- better frontend
- an agent that runs SQL queries autonomously, thus replacing all the `get` / `list` methods on repositories

# Limitations
- no login screen / support to multi tenants
- absence of unit tests
- lack of human supervision in the generation of frontend and SSE-related code
- use pydantic models for agentic tools