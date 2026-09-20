# Lenny Growth Assistant

## 1. Project Overview

**Lenny Growth Assistant** is a full-stack AI conversational application that helps users ask product and growth questions using knowledge extracted from Lenny's Podcast and newsletter transcripts.

The application combines:

* React frontend
* FastAPI backend
* PostgreSQL/Supabase database
* RAG-based transcript retrieval
* Local LLM support through Ollama
* Cloud LLM configuration
* Persistent conversation sessions
* Grounded answers with source citations
* Artifact generation
* Ship 30 for 30 writing skill
* Artifact preview
* Automated backend tests

The main goal is to provide useful answers grounded in the available transcript knowledge rather than generating unsupported information.

---

# 2. Problem Statement

Product managers, founders, and growth professionals often need to search through large amounts of podcast and newsletter content to find useful product and growth insights.

Manually searching transcripts is time-consuming and makes it difficult to connect information across conversations.

The Lenny Growth Assistant provides a conversational interface where users can ask questions and receive answers grounded in the indexed transcript knowledge base.

---

# 3. Key Features

## 3.1 Conversational Assistant

Users can create independent conversations and ask product or growth-related questions.

Each session maintains its own conversation history.

The assistant uses recent conversation messages together with retrieved transcript content to answer follow-up questions.

---

## 3.2 Retrieval-Augmented Generation

The application uses a RAG pipeline.

### Flow

```text
User Question
      ↓
Generate Query Embedding
      ↓
Search PostgreSQL + pgvector
      ↓
Retrieve Relevant Transcript Chunks
      ↓
Build Grounded Context
      ↓
LLM
      ↓
Grounded Answer + Sources
```

Transcript chunks are converted into embeddings using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The embeddings are stored in PostgreSQL using the `pgvector` extension.

The retrieval system uses similarity scoring and a default threshold of `0.35`.

---

# 4. Knowledge Base

The current knowledge base is built from Lenny transcript content.

The ingestion process:

1. Reads transcript files.
2. Identifies episode and guest information.
3. Splits transcripts into chunks.
4. Uses overlapping chunks to preserve context.
5. Generates embeddings.
6. Stores chunks and embeddings in PostgreSQL.

Current ingestion configuration:

```text
Chunk size: 600 words
Overlap: 100 words
Embedding model: all-MiniLM-L6-v2
Embedding dimensions: 384
Default retrieval count: 5
Similarity threshold: 0.35
```

The application currently contains the indexed sample transcript data used for the assignment demonstration.

---

# 5. Grounded Answers

The answer generation service provides retrieved transcript content to the LLM as context.

The prompt instructs the model to:

* Use transcript evidence.
* Avoid unsupported external information.
* Avoid inventing facts.
* Preserve source information.
* Cite the relevant episode, guest, and timestamp.
* Use conversation history for follow-up questions.

Example source format:

```text
[Episode: How to Build a Product People Love,
Guest: Product Growth Expert,
Timestamp: 00:10:25]
```

This makes the answer traceable to the retrieved knowledge.

---

# 6. LLM Provider Architecture

The application supports two provider modes.

### Local

```text
Ollama
    ↓
llama3.2:3b
```

The local model is used for the required local demonstration.

### Cloud

The application also supports a cloud provider configuration through an API key and configurable model.

The provider can be configured through environment variables.

Example:

```env
DEFAULT_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

For cloud usage:

```env
DEFAULT_PROVIDER=cloud
CLOUD_API_KEY=your_api_key
CLOUD_MODEL=your_model
```

No API keys or secrets are committed to the repository.

---

# 7. Database Architecture

PostgreSQL is used as the persistent data store.

Supabase PostgreSQL is used for the deployed database.

The main tables are:

```text
sessions
    ↓
messages
    ↓
artifacts

transcript_chunks
```

## Sessions

Stores individual conversations.

Important fields:

* id
* title
* created_at
* updated_at

## Messages

Stores user and assistant messages.

Important fields:

* id
* session_id
* role
* content
* sources
* created_at

## Artifacts

Stores generated artifacts associated with assistant messages.

Important fields:

* id
* message_id
* artifact_type
* content
* created_at

## Transcript Chunks

Stores the searchable knowledge base.

Important fields:

* id
* episode_title
* guest_name
* content
* timestamp
* topic
* metadata
* embedding

---

# 8. Backend Architecture

The backend is implemented using FastAPI.

Main structure:

```text
backend/
├── app/
│   ├── api/
│   │   ├── answer.py
│   │   ├── artifacts.py
│   │   ├── chat.py
│   │   ├── health.py
│   │   ├── retrieval.py
│   │   ├── sessions.py
│   │   └── ship30.py
│   │
│   ├── models/
│   │   ├── db_models.py
│   │   └── schemas.py
│   │
│   ├── services/
│   │   ├── answer.py
│   │   ├── artifact.py
│   │   ├── llm.py
│   │   ├── provider.py
│   │   ├── retrieval.py
│   │   └── ship30.py
│   │
│   ├── db/
│   │   └── session.py
│   │
│   ├── config.py
│   └── main.py
│
├── scripts/
│   └── ingest_transcripts.py
│
├── data/
│   └── transcripts/
│
└── tests/
```

---

# 9. API Endpoints

## Health

```http
GET /api/health
```

Used to verify that the backend is running.

---

## Sessions

```http
POST /api/sessions
GET /api/sessions
GET /api/sessions/{session_id}
POST /api/sessions/{session_id}/messages
```

These endpoints manage conversation sessions and persisted messages.

---

## Chat

The chat API handles conversational requests and streams assistant responses.

The streaming response also provides the persisted assistant message ID and retrieved source information.

---

## Retrieval

The retrieval service searches transcript chunks using vector similarity.

The core function is:

```python
search_transcript_chunks(
    query,
    top_k=5,
    threshold=0.35
)
```

---

## Artifacts

```http
POST /api/artifacts/generate
```

Supports generated:

* Markdown
* HTML
* CSS
* HTML + CSS

Generated artifacts are persisted in PostgreSQL.

---

## Ship 30 Skill

```http
POST /api/skills/ship30
```

This converts a grounded answer into an approximately 1,250-word Ship 30 for 30 style essay.

---

# 10. Ship 30 for 30 Skill

A dedicated writing skill was implemented for the assignment.

The skill focuses on:

* Strong hooks
* One clear central idea
* Narrative progression
* Short paragraphs
* Skimmable headings
* Bullets
* Selective bold emphasis
* Concrete examples
* Practical recommendations
* Specific final takeaway
* Grounded claims

The generated essay is returned as Markdown.

The skill is explicitly instructed not to invent facts or unsupported claims outside the grounded answer.

---

# 11. Artifact Generation

The application can generate structured artifacts from assistant responses.

Supported artifact types include:

```text
Markdown
HTML
CSS
HTML + CSS
```

The generated artifact is displayed separately from the conversation in the Artifact Viewer.

The HTML generator is instructed to create complete HTML documents and avoid unnecessary external resources.

---

# 12. Artifact Security

Generated HTML is treated as untrusted content.

The preview architecture isolates generated content from the main application so that generated markup does not receive direct access to the application's React state or authentication context.

The implementation separates artifact generation from artifact rendering and avoids treating generated HTML as trusted application code.

---

# 13. Frontend

The frontend is implemented using React and Vite.

The main interface contains:

```text
-------------------------------------------------
| Lenny Growth Assistant | Provider              |
-------------------------------------------------
| Sessions      | Conversation       | Artifact  |
|               |                    | Viewer    |
| New Chat      | User message       |           |
|               |                    | Markdown  |
| Previous      | Assistant answer   | HTML      |
| sessions      |                    | CSS       |
|               | Sources            |           |
-------------------------------------------------
| Ask a product/growth question...       Send    |
-------------------------------------------------
```

The interface supports:

* New conversations
* Session switching
* Conversation history
* Streaming responses
* Source citations
* Artifact generation
* Ship 30 generation
* Markdown rendering
* Artifact preview

---

# 14. Error Handling

The application includes handling for common failure cases.

Examples include:

* Missing cloud API key
* Unsupported provider
* Ollama unavailable
* Empty retrieval results
* LLM failures
* Invalid artifact type
* Missing message
* Database errors
* Invalid API requests

The API uses HTTP status codes and structured error responses where appropriate.

---

# 15. Testing

Automated tests were added for critical functionality.

## Health Test

Verifies:

```http
GET /api/health
```

returns a successful health response.

---

## Session Persistence Test

The session test verifies that a session can be:

1. Created.
2. Persisted to PostgreSQL.
3. Retrieved using its ID.
4. Returned with the expected title and ID.

---

## Retrieval Test

The retrieval test verifies that a relevant query returns transcript chunks containing:

* Content
* Episode title
* Similarity score

It also verifies that the returned similarity meets the configured threshold.

Example test query:

```text
How do you build a product people love?
```

---

# 16. Running the Project Locally

## Backend

Navigate to the backend:

```bash
cd ~/lenny-growth-assistant/backend
```

Activate the virtual environment:

```bash
source venv/Scripts/activate
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

The backend is available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

---

## Frontend

Open another terminal:

```bash
cd ~/lenny-growth-assistant/frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

---

# 17. Ollama Setup

Install Ollama and make sure the required model is available.

The configured model is:

```text
llama3.2:3b
```

Verify the model:

```bash
ollama list
```

Start Ollama if it is not already running.

The backend uses:

```text
http://localhost:11434
```

for local model requests.

---

# 18. Environment Variables

The repository includes an `.env.example` file.

Example configuration:

```env
APP_NAME=Lenny Growth Assistant
APP_ENV=development
PORT=8000

DATABASE_URL=your_database_url

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

DEFAULT_PROVIDER=ollama

CLOUD_API_KEY=
CLOUD_MODEL=
```

Secrets should only be stored in the local `.env` file and must never be committed to GitHub.

---

# 19. Repository Safety

The following should not be committed:

```text
.env
API keys
Database passwords
Private credentials
Access tokens
Personal secrets
```

The `.gitignore` file is used to prevent local secrets and generated files from being committed.

---

# 20. Operational Considerations

The system was designed with several operational concerns in mind.

### Database failure

Database operations are isolated through the SQLAlchemy database session layer.

### Ollama failure

Local model failures are surfaced by the backend instead of silently returning fabricated responses.

### Cloud configuration failure

If cloud mode is selected without a configured API key, the provider raises an explicit configuration error.

### Empty retrieval

If relevant transcript information cannot be retrieved, the grounded answer service can return a fallback rather than presenting unsupported information as fact.

### Model timeout

Ollama requests use a defined timeout to prevent requests from hanging indefinitely.

---

# 21. Project Documentation

The repository contains the required supporting documentation:

```text
docs/
├── PRD.md
├── design.md
└── architecture.md
```

### PRD

Documents:

* User problem
* Success metric
* Assumptions
* Scope
* User flows
* Acceptance criteria
* Risks
* Implementation plan

### Design

Documents:

* UI/UX principles
* Information architecture
* Responsive behavior
* Accessibility considerations
* Application states
* Design decisions

### Architecture

Documents:

* Database schema
* API architecture
* Component boundaries
* RAG pipeline
* LLM provider routing
* Artifact architecture
* Security
* Deployment topology

---

# 22. Example End-to-End Flow

A typical user interaction follows this flow:

```text
1. User creates a conversation
             ↓
2. User asks a product question
             ↓
3. Backend receives the request
             ↓
4. Query is converted into an embedding
             ↓
5. PostgreSQL/pgvector searches transcript chunks
             ↓
6. Relevant transcript context is retrieved
             ↓
7. Conversation history is added
             ↓
8. Selected LLM generates a grounded response
             ↓
9. Response is streamed to the frontend
             ↓
10. Assistant message is persisted
             ↓
11. Sources are displayed to the user
             ↓
12. User can generate an artifact or Ship 30 essay
```

---

# 23. Key Technical Trade-offs

## Local LLM vs Cloud LLM

Ollama was included to satisfy the local-model requirement and to allow the application to operate without sending every request to a cloud provider.

Cloud configuration was also included to support higher-capability hosted models when credentials are available.

The trade-off is that smaller local models can have lower response quality and slower generation depending on available hardware.

---

## Vector Search vs Keyword Search

Vector similarity was selected because product and growth questions may use different wording from the wording contained in the original transcript.

Semantic embeddings allow related concepts to be retrieved even when the exact keywords differ.

---

## PostgreSQL + pgvector

Using PostgreSQL for both application persistence and vector retrieval keeps the architecture relatively simple.

The same database stores:

```text
Sessions
Messages
Artifacts
Transcript chunks
Embeddings
```

This avoids introducing a separate vector database for the assignment.

---

# 24. Manual UI Test Plan

The following scenarios should be demonstrated before submission.

### Test 1 — New Session

1. Open the application.
2. Create a new conversation.
3. Verify that the session appears in the session list.

### Test 2 — Grounded Question

1. Ask a question related to the indexed transcript.
2. Verify that an answer is generated.
3. Verify that source information is displayed.

### Test 3 — Follow-up

1. Ask a follow-up question.
2. Verify that the assistant uses the previous conversation context.

### Test 4 — Ship 30

1. Ask a relevant product/growth question.
2. Generate a Ship 30 essay.
3. Verify the Markdown output appears in the artifact area.

### Test 5 — Artifact

1. Generate an HTML/Markdown artifact.
2. Verify that the artifact is displayed separately.
3. Verify that the main application remains functional.

### Test 6 — Local Ollama

1. Configure Ollama as the provider.
2. Confirm that the application generates an answer using the local model.
3. Show the provider configuration in the demo.

---

# 25. Demo Video Plan

The final demo should be approximately 2–3 minutes.

Recommended sequence:

### 0:00–0:20 — Introduction

Explain:

* What the Lenny Growth Assistant is.
* Who it is designed for.
* The problem it solves.

### 0:20–1:00 — Product Demo

Show:

* Creating a session.
* Asking a product question.
* Receiving a grounded response.
* Source citation.

### 1:00–1:30 — Follow-up + Skill

Show:

* Follow-up question.
* Ship 30 generation.
* Generated artifact.

### 1:30–2:00 — Local Model

Demonstrate:

```text
Provider: Ollama
Model: llama3.2:3b
```

Explain that the application can use a local model instead of a cloud API.

### 2:00–2:30 — Technical Trade-off

Briefly explain the decision to use PostgreSQL + pgvector for both application persistence and vector retrieval.

---

# 26. Final Submission Checklist

Before submitting the repository, verify:

* [ ] Public GitHub repository
* [ ] No secrets committed
* [ ] README.md updated
* [ ] PRD.md included
* [ ] design.md included
* [ ] architecture.md included
* [ ] `.env.example` included
* [ ] FastAPI backend working
* [ ] React frontend working
* [ ] PostgreSQL/Supabase connected
* [ ] Transcript ingestion working
* [ ] Vector retrieval working
* [ ] Grounded answers working
* [ ] Source citations working
* [ ] Ollama working
* [ ] Cloud provider configuration documented
* [ ] Sessions persisted
* [ ] Messages persisted
* [ ] Artifacts persisted
* [ ] Artifact viewer working
* [ ] Ship 30 skill working
* [ ] Automated tests passing
* [ ] Agent transcripts/logs included
* [ ] Manual UI test plan included
* [ ] Demo video recorded
* [ ] Demo video uploaded to YouTube
* [ ] GitHub repository URL ready for submission

---

# 27. Conclusion

The Lenny Growth Assistant demonstrates a complete full-stack workflow combining conversational AI, retrieval-augmented generation, PostgreSQL persistence, local LLM inference, artifact generation, and a dedicated writing skill.

The architecture is designed to keep generated answers grounded in the available transcript knowledge while maintaining independent conversation sessions and persistent application state.

The project also includes automated tests, supporting technical documentation, environment configuration, and a manual demonstration plan to make the application easier to evaluate, run, and extend.
