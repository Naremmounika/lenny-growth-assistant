# Lenny Growth Assistant — Architecture Specification

## 1. Architecture Overview

The Lenny Growth Assistant follows a layered architecture:

```text
                    ┌─────────────────────────┐
                    │       Frontend          │
                    │ React / Next.js         │
                    │ Chat + Artifact Viewer  │
                    └────────────┬────────────┘
                                 │ HTTP / SSE
                                 ▼
                    ┌─────────────────────────┐
                    │       FastAPI           │
                    │ API + Validation        │
                    │ Sessions + Chat         │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       ┌─────────────┐   ┌──────────────┐   ┌──────────────┐
       │ RAG Layer   │   │ Agent/Skill  │   │ LLM Provider │
       │ Retrieval   │   │ Layer        │   │ Abstraction  │
       └──────┬──────┘   └──────────────┘   └───────┬──────┘
              │                                      │
              ▼                            ┌─────────┴─────────┐
       ┌─────────────┐                      ▼                   ▼
       │ PostgreSQL  │                ┌──────────┐       ┌──────────┐
       │ + pgvector  │                │ Ollama   │       │ Cloud LLM│
       └─────────────┘                └──────────┘       └──────────┘
The architecture supports both local and cloud-based LLM execution without changing the application core.

2. Architecture Goals

The architecture is designed around the following goals:

Ground answers in Lenny's Podcast transcripts.
Support conversational follow-up questions.
Maintain persistent sessions and messages.
Support local Ollama models.
Support a cloud LLM provider.
Allow switching between providers through configuration.
Provide explicit abstention when transcript evidence is insufficient.
Generate Ship30-style writing when requested.
Generate Markdown and HTML artifacts.
Safely render generated HTML.
Keep the backend modular and testable.
Support local development through Docker Compose.
Provide clear observability and failure handling.
3. System Components
3.1 Frontend

The frontend provides the user-facing application.

Responsibilities:

Display chat interface.
Display conversation history.
Create and select sessions.
Send user messages.
Display assistant responses.
Display citations and transcript sources.
Display provider/model selection.
Display generated artifacts.
Render Markdown.
Safely render generated HTML.
Display loading and error states.

Recommended stack:

React / Next.js
TypeScript
Tailwind CSS
react-markdown
remark-gfm
DOMPurify

The frontend communicates with the backend using HTTP APIs and SSE where streaming is required.

3.2 FastAPI API Layer

FastAPI acts as the application entry point.

Responsibilities:

Request validation.
Session management.
Chat requests.
Streaming responses.
Authentication of internal application requests if required.
Calling the agent/orchestrator.
Persisting messages.
Returning sources and artifacts.
Health checks.
Error handling.

Primary API endpoints:

POST /api/sessions
GET  /api/sessions/{session_id}
POST /api/chat
GET  /api/health
4. Agent / Orchestrator

The agent/orchestrator coordinates the application workflow.

Instead of directly coupling the API to an LLM, the API sends requests to the agent layer.

The agent determines:

What the user is asking.
Whether transcript retrieval is required.
Which transcript chunks are relevant.
Whether additional conversation context is required.
Which skill should be used.
Which LLM provider should generate the response.
Whether enough evidence exists to answer.
Whether an artifact should be generated.

Conceptual flow:

User Question
     │
     ▼
Agent / Orchestrator
     │
     ├── Retrieve transcript context
     │
     ├── Retrieve conversation context
     │
     ├── Select required skill
     │
     ├── Select LLM provider
     │
     ├── Generate grounded response
     │
     └── Return response + citations + artifact

The agent layer should not invent transcript facts when retrieval does not provide sufficient evidence.

5. RAG Architecture

The RAG system provides transcript-grounded retrieval.

5.1 Transcript Pipeline
Podcast Transcripts
        │
        ▼
Document Cleaning
        │
        ▼
Chunking
        │
        ▼
Embedding Generation
        │
        ▼
PostgreSQL + pgvector

Target chunk configuration:

Chunk size: approximately 500–800 tokens.
Overlap: approximately 100 tokens.
Each chunk retains episode metadata.
Each chunk stores its embedding.
5.2 Retrieval Pipeline
User Question
      │
      ▼
Query Embedding
      │
      ▼
Vector Similarity Search
      │
      ▼
Top K Relevant Chunks
      │
      ▼
Similarity Threshold
      │
      ├── Sufficient evidence
      │        │
      │        ▼
      │   Agent / LLM
      │
      └── Insufficient evidence
               │
               ▼
          Abstain

Recommended retrieval configuration:

Top K: 4–6 chunks.
Similarity threshold: configurable, initially around 0.65.
Vector index: HNSW.
Embedding model: sentence-transformers/all-MiniLM-L6-v2 or Ollama embedding model.
6. Grounding and Citations

Every transcript-grounded answer should preserve the source context used to generate the response.

Citation format:

[Episode: Guest Name, Timestamp/Topic]

Example:

Lenny's key lesson is to focus on retention before optimizing acquisition.

[Episode: Brian Balfour, Retention]

The assistant should avoid unsupported claims.

If retrieval confidence is below the configured threshold, the assistant should explicitly state that the available transcripts do not provide enough evidence.

Example:

I couldn't find enough evidence in Lenny's podcast transcripts to answer that confidently.
7. PostgreSQL + pgvector

PostgreSQL is the primary persistence layer.

pgvector provides vector storage and similarity search.

The database stores:

Sessions.
Messages.
Podcast episodes.
Transcript chunks.
Embeddings.
Generated artifacts.

Conceptual database structure:

Session
  │
  └──< Message
          │
          └──< Artifact

Episode
  │
  └──< TranscriptChunk
              │
              └── Embedding
8. Database Schema
Session
sessions
--------------------------------
id          UUID PRIMARY KEY
title       TEXT
created_at  TIMESTAMP
updated_at  TIMESTAMP
Message
messages
--------------------------------
id          UUID PRIMARY KEY
session_id  UUID REFERENCES sessions
role        TEXT
content     TEXT
sources     JSONB
created_at  TIMESTAMP
Transcript Episode
episodes
--------------------------------
id          UUID PRIMARY KEY
title       TEXT
guest_name  TEXT
episode_url TEXT
published_at TIMESTAMP
Transcript Chunk
transcript_chunks
--------------------------------
id              UUID PRIMARY KEY
episode_id      UUID REFERENCES episodes
content         TEXT
start_time      TEXT
topic           TEXT
embedding       VECTOR
metadata        JSONB
Artifact
artifacts
--------------------------------
id            UUID PRIMARY KEY
message_id    UUID REFERENCES messages
artifact_type TEXT
content       TEXT
created_at    TIMESTAMP
9. LLM Provider Abstraction

The application should not directly depend on one LLM provider.

A common provider interface is used:

BaseLLMProvider
       │
       ├── OllamaProvider
       │
       └── CloudProvider

Example interface:

class BaseLLMProvider:
    async def generate(
        self,
        messages,
        system_prompt=None,
        temperature=0.2,
    ):
        raise NotImplementedError

The agent interacts with BaseLLMProvider rather than directly calling Ollama or Anthropic.

10. Ollama Provider

Ollama is mandatory for the local demonstration.

Example models:

llama3.2:3b
llama3.1:8b
mistral:7b

Configuration:

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

The application should gracefully handle:

Ollama not running.
Model not installed.
Request timeout.
Connection failure.
Invalid model name.
11. Cloud LLM Provider

The cloud provider can use Anthropic Claude or another supported cloud LLM.

Configuration should be environment based:

CLOUD_LLM_API_KEY=
CLOUD_LLM_MODEL=

The API key must never be committed to Git.

Provider selection should be configurable:

DEFAULT_PROVIDER=ollama

or:

DEFAULT_PROVIDER=cloud

The core application should not need to change when switching providers.

12. Conversation Context

Each chat message belongs to a session.

The session provides conversational continuity.

Example:

Session
 │
 ├── User: What did Brian say about retention?
 │
 ├── Assistant: ...
 │
 ├── User: How would I apply that to a startup?
 │
 └── Assistant: ...

For follow-up questions, the agent uses:

Current user message.
Relevant previous messages.
Retrieved transcript context.

The system should avoid sending unnecessarily large conversation histories to the model.

13. Ship30 Writer Skill

The Ship30 Writer is a specialized skill for producing concise, useful essays.

Target:

Approximately 1,250 words.
Strong opening hook.
Narrative structure.
Skimmable formatting.
Practical takeaway.
Transcript-grounded claims.

Conceptual flow:

User Request
     │
     ▼
Retrieve Evidence
     │
     ▼
Ship30 Writer Skill
     │
     ▼
LLM Provider
     │
     ▼
~1250 Word Essay

The skill must use retrieved transcript evidence rather than inventing quotes or claims.

14. Artifact Generator

The artifact generator creates content that can be displayed beside the chat.

Supported types:

markdown
html

Example:

User
 │
 ▼
Artifact Generator
 │
 ├── Markdown
 │
 └── HTML + CSS

Artifacts are persisted in the database and associated with the message that generated them.

15. Artifact Security

Generated HTML is treated as untrusted content.

The frontend must sanitize generated HTML before rendering.

Recommended architecture:

Generated HTML
      │
      ▼
DOMPurify
      │
      ▼
Sandboxed iframe
      │
      ▼
Artifact Viewer

The iframe should use sandboxing.

Recommended configuration:

<iframe sandbox="allow-scripts">

Do not use:

sandbox="allow-scripts allow-same-origin"

unless there is a specific security requirement and the implications have been reviewed.

The artifact viewer should prevent generated HTML from accessing the parent application.

16. API Request Flow
Chat Request
Frontend
   │
   │ POST /api/chat
   ▼
FastAPI
   │
   ▼
Session Validation
   │
   ▼
Agent / Orchestrator
   │
   ├── Conversation Context
   │
   ├── RAG Retrieval
   │
   ├── Skill Selection
   │
   └── Provider Selection
   │
   ▼
LLM
   │
   ▼
Grounded Response
   │
   ├── Citations
   │
   └── Artifact
   │
   ▼
PostgreSQL
   │
   ▼
FastAPI
   │
   ▼
Frontend
17. Streaming

SSE can be used for assistant response streaming.

Example:

Frontend
    │
    │ POST /api/chat
    ▼
FastAPI
    │
    ▼
Agent
    │
    ▼
LLM streaming response
    │
    │ SSE
    ▼
Frontend

Streaming improves perceived responsiveness for longer answers.

18. Health Checks

The backend exposes:

GET /api/health

The health response should verify application dependencies where appropriate.

Example:

{
  "status": "ok",
  "database": "ok",
  "ollama": "ok"
}

A degraded dependency should be represented clearly rather than causing the entire application to fail silently.

19. Resilience

The system should gracefully handle:

Missing cloud API key
Cloud provider unavailable.
Use Ollama or configure the required API key.
Ollama unavailable
Local model unavailable.
Switch to the cloud provider or start Ollama.
Empty retrieval
No relevant transcript evidence was found.
Database failure
Unable to persist the conversation.
Please retry.
LLM timeout

The backend should:

Apply a timeout.
Log the failure.
Return a user-friendly error.
Avoid exposing internal stack traces.
20. Observability

Structured logging should capture:

Request ID.
Session ID.
Provider.
Model.
Retrieval count.
Retrieval scores.
Response latency.
LLM latency.
Errors.
Artifact generation status.

Example:

{
  "event": "chat_completed",
  "session_id": "session-id",
  "provider": "ollama",
  "model": "llama3.2:3b",
  "retrieved_chunks": 5,
  "latency_ms": 3200
}

Sensitive information such as API keys must never be logged.

21. Security

Security requirements include:

Never commit secrets.
Use .env for local secrets.
Provide .env.example.
Validate API inputs.
Sanitize generated HTML.
Sandbox artifact rendering.
Avoid exposing internal errors.
Restrict database access.
Use parameterized database queries.
Validate session identifiers.
Keep generated artifacts isolated from the parent application.
22. Deployment Architecture

Recommended Docker Compose topology:

                    Docker Compose
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   Frontend          FastAPI          PostgreSQL
                                      + pgvector
        │                │
        │                │
        │                └───────┐
        │                        │
        ▼                        ▼
      Browser                 Ollama

Services:

frontend
backend
db
ollama (optional container)

For local development, Ollama may also run directly on the host machine.

23. Project Structure
lenny-growth-assistant/
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
│
├── docs/
│   ├── PRD.md
│   ├── architecture.md
│   └── design.md
│
├── agent_transcripts/
│   ├── 01_initial_scaffolding.md
│   └── 02_debugging_pgvector_indexing.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   │
│   ├── scripts/
│   │   ├── download_transcripts.py
│   │   └── ingest.py
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   │
│   │   ├── models/
│   │   │   ├── db_models.py
│   │   │   └── schemas.py
│   │   │
│   │   ├── providers/
│   │   │   ├── base.py
│   │   │   ├── ollama_provider.py
│   │   │   └── cloud_provider.py
│   │   │
│   │   ├── rag/
│   │   │   ├── retriever.py
│   │   │   └── embeddings.py
│   │   │
│   │   ├── skills/
│   │   │   ├── ship30_writer.py
│   │   │   └── artifact_generator.py
│   │   │
│   │   └── api/
│   │       ├── sessions.py
│   │       ├── chat.py
│   │       └── health.py
│   │
│   └── tests/
│       ├── test_api.py
│       ├── test_retrieval.py
│       └── test_providers.py
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── tailwind.config.js
    ├── tsconfig.json
    │
    └── src/
        ├── app/
        │   ├── layout.tsx
        │   └── page.tsx
        │
        ├── components/
        │   ├── Chat/
        │   │   ├── ChatPane.tsx
        │   │   ├── MessageItem.tsx
        │   │   └── ModelSelector.tsx
        │   │
        │   └── Artifact/
        │       ├── ArtifactViewer.tsx
        │       └── SandboxedIframe.tsx
        │
        ├── hooks/
        │   └── useChatStream.ts
        │
        └── lib/
            └── api.ts
24. Testing Strategy

Testing is divided into several layers.

Unit Tests

Test:

Chunking.
Embeddings.
Retrieval.
Provider abstraction.
Provider failures.
Skill logic.
Artifact generation.
API Tests

Test:

Session creation.
Session retrieval.
Chat requests.
Health endpoint.
Invalid requests.
Database failures.
Integration Tests

Test:

API
 ↓
Agent
 ↓
RAG
 ↓
PostgreSQL
 ↓
LLM Provider
Security Tests

Test:

HTML sanitization.
iframe sandboxing.
Invalid input.
Error leakage.
Secret handling.

## 25. Design Principles

The implementation follows these principles:

1. Separation of concerns.
2. Provider independence.
3. Retrieval-first grounding.
4. Explicit abstention.
5. Secure artifact rendering.
6. Persistent conversations.
7. Observable failures.
8. Testable components.
9. Simple local development.
10. Clear user experience.

The architecture should remain simple enough for a single engineer to understand and operate while still demonstrating production-oriented engineering decisions.
