# intelligent-conversational-agent
> Conversational AI system that simulates a Customer Support Agent for a fictional business

# Video demos

- app: https://vimeo.com/1176148799?share=copy&fl=sv&fe=ci (03:18)
- code walkthru: https://vimeo.com/1176152007?share=copy&fl=sv&fe=ci (04:21)

# This repo

This repository implements:
- Frontend: a simple chat interface implemented using [Streamlit](https://streamlit.io/)
- Backend: a HTTP API implemented using: 
  - [FastAPI](https://fastapi.tiangolo.com/) for HTTP routing
  - [SQLModel](https://sqlmodel.tiangolo.com/) as ORM
  - [LangChain Deep Agents](https://github.com/langchain-ai/deepagents) for agents orchestration

As IDE, I used Cursor with Claude Sonnet 4.6

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

## Audio models

I've picked `tts-1` and `whisper-1` for a few simple reasons:
- **cost**: they're much cheaper than other more optimized models (e.g.: `tts-1`, `tts-1-hd`, `gpt-4o-audio-preview-2025-06-03`, `gpt-audio-2025-08-28`)
- **scope**: in my tests, I considered `tts-1` and `whisper-1` accurate enough for the scope of this exercise
- **speed**: both models demonstrated good speed when translating text <-> audio

## Voice interactions

When sending a voice prompt, the app does 2 things:
- invokes an endpoint for transcribing audio to text
- writes the transcription on the prompt textbox as opposed to firing a request to backend

This UX might not be considered optimal, but I decided for this approach to minimize user frustration. My angle was that it'd be frustrating for the user to speak their prompt and then have to wait a few seconds to then realize the transcription didn't go well and get a response that didn't help them. I opted for a "Human In The Loop" approach where they'd need to review the transcription before invoking the agent.
 
## Frontend implementation: Streamlit vs React

With a baby at home, my time was pretty limited during this weekend. Also, I'm far from being a frontend specialist. So, if I tried to create a fancy SPA in React, it'd:
- make me spend more time, especially in situations where I couldn't debate the best approach with Cursor
- add little value, as the focus of the exercise is not on UX

Therefore, I decided to go with a no-brainer option for the frontend: Streamlit, which I find to be a bit of a standard when it comes to Pythonic data apps.

## Using LangChain Deep Agents

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

# Description of potential improvements

## Add automated tests

As mentioned before, my time was very limited during this weekend. Therefore, I made the conscious choice of not adding automated tests.

My reasoning is:
- the logic in all classes / methos is pretty straightforward, hence unit tests would basically verify if Python works correctly, which wouldn't add value
- all the complexity lies in the agents / tools orchestration, which is already handled by LangChain

As future improvement, I'd add unit tests for:
- repositories (using [testcontainers](https://github.com/testcontainers/testcontainers-python))
- tools (to verify they're invoking the appropriate repository methods)
- routers (to verify they're invoking the proper dependencies)

And I'd add UI tests (using [Playwright](https://playwright.dev/)) to verify the chat interactions are working as expected

On top of that, I'd also introduce Automated Evals on [Langsmith](https://smith.langchain.com/), to verify the agents are responding within reasonable boundaries when:
- creating tickets
- informing valid options for master data
- verify that rewards were offered when sentiment analysis indicated frustrated customers

## Add agent responsible for running SQL queries

As you might see looking into the repositories, there are a lot of CRUD methods in there, which exist to serve the agentic tools. 

This approach improves accuracy when performing database operations, but are not scalable. E.g.: every time a new table is added to the data model, a new repository and new tools need to be added.

Therefore, it'd make sense to introduce an agent that can autonomously create simple queries on the fly, especially for reading data from the tables.

Although this approach is definitely more scalable, it also introduces challenges, such as opening the door attacks like prompt injection, escalation of privileges, data leakage, among others. 

This approach would require a comprehensive study to put safeguards in place to prevent these kinds of attachs. 

Examples of countermeasures include, but are not limited to: 
- Limiting said SQL Agent to use readonly connections
- Have their queries running on a read replica instead of the main database, to prevent DOS-like attacks
- Using a custom schema with access to a limited subset of tables
- Automatically reviewing the output of said Agent to make sure it wouldn't leak data or details about the DB storage to users

## Better frontend

In this repo I chose to use Streamlit due to limitations of time and knowledge. But I reckon the UX is very limited. 

One possible improvement could be to create a React / Angular / Svelte app that offers a better UX.

Another possible improvement would have been closer attention to the codebase itself. For the aforementioned reasons, I vibecoded all my way through the frontend codebase with Cursor and, looking at the codebase, it could probably benefit from some refactoring and a better split of responsibilities. But for the scope of this exercise I considered the current state of the frontend as good enough. 

## Support to multiple users / multiple tenants

The code in this repo does not worry about authentication / authorization or any others means of segregating data among different users. 

This is obviously suboptimal but I considered it to be enough for the scope of this exercise.

In a real world scenario, I'd introduce a login screen and use a `tenant_id` column in all tables to guarantee proper data segregation among different users, and therefore adding the logged user's `tenant_id` to all DB queries.

One might ask if I'd constantly pass this `tenant_id` back and forth between controller, agents, repositories, etc, and my answer would be yes, at least in a first version of the product. My reasoning is:
- the code is easier to read and clearer, especially when compared to techniques like Aspect Oriented Programming and other techniques to inject logged user's data in different parts of the codebase
- agentic code is non-deterministic by nature, so the less opportunity we give agents to choose the wrong piece of data, the better.

## Use pydantic models as parameters to agentic tools

This point is highly debatable. 

Right now the tools accept a list of parameters and this is working quite well. 

One might argue that replacing a list of parameters with a Pydantic class would be a better approach. I don't oppose to that, I just don't think it's super necessary for the current state of the codebase.

If this was to become a real product, I'd definitely go for this approach, as refactoring gets easier, ie, instead of changing different method signatures in a chain of calls, all I'd need to do is change a single class.

# Requirements coverage

1. Conversational Flow
- Implement a bot that can engage in natural conversation with users ✅
- Bot should collect specific information. For example, for a customer support agent, the agent would collect information about customer issues  including: order number, problem category, problem description, and urgency level ✅ 
- Extract and validate this information into a structured format ✅
- Handle basic error cases and invalid inputs gracefully ✅
- Maintain conversation context throughout the interaction ✅

2. Data Extraction & Storage
- Store conversations and extracted data in a structured format (JSON) ✅
- Implement basic data validation for collected information ✅
- Generate a summary of the conversation with extracted key points ✅

3. Technical Requirements
- Use Python for implementation ✅
- Implement proper error handling ✅
- Use the LLM of your choice, considering the use case ✅
- Use the conversational AI platform/model of your choice for text transcription and TTS ✅

4. Bonus Features (Optional)
- Implement RAG using a provided knowledge base. For example, for a customer support agent, knowledge of common customer issues
- Add sentiment analysis to detect customer frustration ✅
- Implement multi-turn conversation memory ✅
- Add support for multiple languages