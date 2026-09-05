# Lenny Growth Assistant — Product Requirements Document

## 1. Product Overview

### Product Name

Lenny Growth Assistant

### Product Goal

Build a reliable AI-powered internal assistant that transforms Lenny's Podcast transcripts into actionable product-management and growth knowledge.

The assistant enables product managers and growth leaders to:

1. Ask grounded questions about product and growth topics.
2. Receive answers backed by relevant podcast transcript sources.
3. Generate approximately 1,250-word Ship 30 for 30-style essays.
4. Generate Markdown or HTML/CSS artifacts.
5. Preview generated artifacts directly inside the application.
6. Switch between a local Ollama model and a cloud LLM without changing application code.

The product is designed as a forward-deployed AI system rather than simply a chatbot.

---

## 2. User and Problem

### Primary User

The primary user is a product manager, growth leader, founder, or product professional who wants to quickly extract practical insights from Lenny's Podcast.

### User Problem

Lenny's Podcast contains a large amount of valuable product and growth knowledge distributed across many episodes and transcripts.

Users currently need to:

- Search through individual episodes.
- Listen to long podcast episodes.
- Remember which guest discussed a particular topic.
- Manually extract useful frameworks.
- Rewrite insights into reusable content.
- Use separate tools to turn generated content into visual artifacts.

This creates unnecessary research and synthesis effort.

### Job To Be Done

"When I have a product or growth question, I want to quickly find relevant insights from Lenny's Podcast and turn those insights into actionable content or artifacts, without manually searching through hours of podcast material."

---

## 3. Product Scope

### In Scope

- Transcript ingestion.
- Transcript chunking and metadata extraction.
- Vector embeddings.
- PostgreSQL with pgvector.
- Semantic transcript retrieval.
- Grounded conversational question answering.
- Source attribution.
- Session-based conversations.
- PostgreSQL conversation persistence.
- Ollama local LLM support.
- Cloud LLM support.
- Runtime model/provider switching.
- Ship 30 for 30 writing skill.
- Markdown artifact generation.
- HTML/CSS artifact generation.
- In-app artifact preview.
- Sandboxed HTML rendering.
- Structured backend logging.
- Health checks.
- Docker Compose deployment.
- Automated tests.
- Documentation and operational handoff.

### Out of Scope

- User billing.
- Multi-tenant enterprise administration.
- Native mobile applications.
- Voice transcription.
- Podcast audio processing.
- Fine-tuning custom language models.
- Complex user permission management.
- Real-time collaboration.

---

## 4. Success Metrics

### Retrieval Citation Accuracy

Target: **>= 90%**

Generated answers should correctly identify relevant transcript sources.

### Local Inference Latency

Target: **< 4 seconds to first token**

when using the local Ollama model under suitable local hardware conditions.

### Artifact Render Safety

Target: **0 known XSS vulnerabilities in the artifact rendering flow.**

Generated HTML must be treated as untrusted content and isolated using a sandboxed iframe.

---

## 5. Key User Flows

### Grounded Question Answering

1. User starts a new session.
2. User enters a product or growth question.
3. Backend generates an embedding for the query.
4. Vector search retrieves relevant transcript chunks.
5. System evaluates retrieval relevance.
6. Relevant context is supplied to the LLM.
7. LLM generates a grounded response.
8. Sources are displayed.
9. Message is persisted.

### Unsupported Question

1. User asks a question.
2. Retrieval finds no sufficiently relevant transcript context.
3. System does not invent an answer.
4. Assistant states that the archive does not contain sufficient information.

### Ship 30 for 30

1. User requests an essay.
2. System retrieves relevant transcript context.
3. Ship 30 for 30 skill is applied.
4. LLM generates approximately 1,250 words.
5. Content contains a strong hook, structured sections, skimmable formatting, and actionable takeaways.
6. Transcript-grounded claims are preserved.

### Artifact Generation

1. User requests Markdown or HTML/CSS.
2. Assistant generates the artifact.
3. Frontend detects the artifact.
4. Markdown is rendered.
5. HTML is sanitized and rendered in a sandboxed iframe.
6. Artifact appears beside the conversation.

---

## 6. Product Requirements

### PR-01 — Sessions

Users must be able to create independent chat sessions.

### PR-02 — Conversation Persistence

Messages must be persisted in PostgreSQL.

### PR-03 — Grounded Retrieval

Questions must be answered using retrieved transcript context.

### PR-04 — Source Attribution

Answers must identify episode, guest, and timestamp/topic when available.

### PR-05 — Abstention

The system must refuse to fabricate information when retrieval confidence is below the configured threshold.

### PR-06 — Local Model

The application must support Ollama for the evaluation demo.

### PR-07 — Cloud Model

The application must support at least one cloud LLM provider.

### PR-08 — Model Switching

The model/provider must be configurable without changing application code.

### PR-09 — Ship 30 for 30

The system must generate approximately 1,250-word structured essays.

### PR-10 — Artifact Viewer

The frontend must preview generated Markdown and HTML/CSS artifacts.

### PR-11 — Artifact Security

Generated HTML must be treated as untrusted content.

### PR-12 — Deployment

The system should be runnable through a reproducible Docker Compose setup.

---

## 7. Assumptions

1. The initial user does not require authentication.
2. A single local deployment is sufficient for evaluation.
3. PostgreSQL is the source of truth for sessions, messages, and transcript chunks.
4. pgvector will be used for semantic retrieval.
5. Transcript timestamps may not be available for every chunk.
6. Ollama is the mandatory local demonstration provider.
7. A cloud provider is used as an alternative provider.
8. The application is optimized for desktop but remains responsive.
9. Generated HTML is untrusted and must never receive access to the parent application's origin.
10. Retrieval quality depends on transcript quality, chunking, embedding quality, and similarity thresholds.

---

## 8. Risks and Trade-offs

### Hallucination Risk

The LLM may generate information not present in transcripts.

Mitigation:

- Retrieval threshold.
- Grounded system prompt.
- Source attribution.
- Explicit abstention behavior.

### Local Model Quality

Smaller local models may provide weaker reasoning than cloud models.

Trade-off:

- Ollama satisfies local evaluation and privacy/cost requirements.
- Cloud providers provide stronger reasoning when available.

### Latency

Local inference may be slower depending on hardware.

Mitigation:

- Streaming responses.
- Reasonable model selection.
- Limited retrieval context.

### Cost

Cloud inference creates API costs.

Mitigation:

- Local Ollama provider.
- Runtime provider selection.

### Unsafe Artifact Rendering

Generated HTML may contain malicious JavaScript.

Mitigation:

- DOMPurify sanitization.
- Sandboxed iframe.
- No `allow-same-origin`.

---

## 9. Acceptance Criteria

- [ ] User can create a session.
- [ ] User can ask questions about Lenny's Podcast.
- [ ] Answers are grounded in transcript retrieval.
- [ ] Sources are displayed.
- [ ] Unsupported questions produce an abstention response.
- [ ] Conversation history is persisted.
- [ ] Ollama works as the local provider.
- [ ] Cloud provider can be selected.
- [ ] Provider switching works.
- [ ] Ship 30 for 30 content can be generated.
- [ ] Markdown artifacts render.
- [ ] HTML artifacts render inside a sandbox.
- [ ] PostgreSQL and pgvector are operational.
- [ ] Health endpoints report system status.
- [ ] Automated tests cover critical functionality.
- [ ] Docker Compose starts the application.
- [ ] README contains setup and troubleshooting instructions.
- [ ] Demo video demonstrates the local Ollama workflow.

---

## 10. Implementation Plan

1. Project scaffolding.
2. Discovery documentation.
3. PostgreSQL and pgvector setup.
4. FastAPI backend foundation.
5. Transcript acquisition.
6. Transcript parsing and chunking.
7. Embedding generation.
8. Vector retrieval.
9. LLM provider abstraction.
10. Ollama integration.
11. Cloud provider integration.
12. Grounded RAG chat.
13. Session and message persistence.
14. Ship 30 for 30 skill.
15. Frontend implementation.
16. Artifact viewer.
17. Security hardening.
18. Docker Compose.
19. Automated tests.
20. Documentation and final demo.