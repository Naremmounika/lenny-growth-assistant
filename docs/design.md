 Lenny Growth Assistant — Product & UX Design Specification

## 1. Design Overview

Lenny Growth Assistant is designed as a focused AI research and writing workspace.

The primary interaction is a conversational chat interface supported by transcript retrieval and an artifact workspace.

The interface should make three things immediately clear:

1. What the user asked.
2. What the assistant found and concluded.
3. What artifact was generated, if any.

The application should feel like a practical research assistant rather than a generic chatbot.


## 2. Primary User Experience

The primary desktop layout uses two major areas:

```text
┌──────────────────────────────────────────────────────────────┐
│ Lenny Growth Assistant                     Model: Ollama ▼    │
├──────────────────────────────┬───────────────────────────────┤
│                              │                               │
│          CHAT                │          ARTIFACT             │
│                              │                               │
│ User message                 │  Generated document          │
│                              │                               │
│ Assistant response           │  Markdown / HTML             │
│                              │                               │
│ Citations                    │                               │
│                              │                               │
│                              │                               │
├──────────────────────────────┴───────────────────────────────┤
│ Ask Lenny something...                         Send →         │
└──────────────────────────────────────────────────────────────┘

The chat area remains the primary workspace.

The artifact panel becomes useful when the assistant generates a longer document or visual artifact.

3. Design Goals

The UI should optimize for:

Clarity.
Speed.
Readability.
Trust.
Low cognitive load.
Easy follow-up questions.
Clear source attribution.
Safe artifact rendering.
Responsive behavior.
Professional appearance.

The interface should avoid unnecessary dashboard-style complexity.

4. Visual Hierarchy

The visual hierarchy should follow:

1. User question
2. Assistant answer
3. Sources / citations
4. Generated artifact
5. Provider/model information
6. Secondary controls

The main conversation should receive the largest visual emphasis.

Secondary information should not compete with the response.

5. Application Header

The top navigation/header should contain:

┌──────────────────────────────────────────────────────────────┐
│ Lenny Growth Assistant        Ollama ▼       New Session      │
└──────────────────────────────────────────────────────────────┘

Header responsibilities:

Application name.
Current provider/model.
New session action.
Optional session controls.
Connection status when necessary.

The header should remain visible while using the application.

6. Chat Interface

The chat interface consists of:

ChatPane
   │
   ├── Message list
   │
   ├── Source citations
   │
   ├── Loading state
   │
   └── Message composer

Each message should visually distinguish:

User message
                         ┌──────────────────────┐
                         │ What did Brian say   │
                         │ about retention?     │
                         └──────────────────────┘
Assistant message
┌─────────────────────────────────────────────────┐
│ Assistant                                       │
│                                                 │
│ Brian emphasizes retention as a key growth     │
│ lever because...                                │
│                                                 │
│ Sources                                         │
│ [Episode: Brian Balfour, Retention]             │
└─────────────────────────────────────────────────┘

Assistant responses should support Markdown.

7. Message Formatting

Assistant messages should support:

Paragraphs.
Headings.
Bold text.
Italic text.
Ordered lists.
Unordered lists.
Code blocks.
Tables.
Links.
Blockquotes.

GitHub-flavored Markdown should be supported.

Recommended libraries:

react-markdown
remark-gfm
8. Citation Design

Citations should be visually separated from the main answer.

Example:

Sources

[Episode: Brian Balfour, Retention]
[Episode: Elena Verna, Growth]

Citations should be:

Easy to scan.
Visually secondary.
Associated with the response.
Based only on retrieved transcript evidence.

Where possible, citations can expose metadata such as:

Episode.
Guest.
Timestamp.
Topic.
9. Source Trust UX

The application should make grounding visible.

A response can display:

✓ Grounded in 5 transcript sources

or:

No relevant transcript evidence found.

This helps the user distinguish between:

Transcript-backed information.
General reasoning.
Unsupported questions.

The application should never imply strong source confidence when retrieval did not find supporting evidence.

10. Abstention UX

When evidence is insufficient, the assistant should respond clearly.

Example:

I couldn't find enough evidence in Lenny's podcast transcripts
to answer that confidently.

Try asking about a specific guest, episode, or topic.

The interface should not display a normal confident answer followed by a hidden warning.

The limitation should be visible in the response itself.

11. Model Selector

The provider selector should be simple.

Example:

Model
┌─────────────────────┐
│ Ollama ▼            │
├─────────────────────┤
│ Ollama               │
│ Cloud LLM            │
└─────────────────────┘

If model selection is available:

Provider
└── Ollama

Model
└── llama3.2:3b

The selected provider should be visible during the conversation.

12. Provider States
Ollama available
● Ollama ready
Ollama unavailable
○ Ollama unavailable

The user should receive a clear explanation and, where possible, an alternative provider.

Example:

Ollama is not available.

You can start Ollama or switch to the cloud provider.
13. Message Composer

The message composer should remain at the bottom of the chat pane.

Example:

┌──────────────────────────────────────────────────────────────┐
│ Ask about Lenny's podcast...                          Send → │
└──────────────────────────────────────────────────────────────┘

Requirements:

Multi-line input.
Enter sends message.
Shift+Enter creates a new line.
Disabled while a request is being submitted if appropriate.
Clear loading state.
Accessible keyboard focus.

The composer should remain easy to access after long conversations.

14. Streaming UX

When the assistant is generating a response:

Assistant

Brian's main point is...
▌

The UI should progressively display the response when streaming is enabled.

The user should see:

Request is being processed.
Text is arriving.
Completion state.
Error state if streaming fails.

Avoid displaying an indefinite spinner without information.

15. Loading States

The application should have clear loading states.

Example:

Searching Lenny's transcripts...

Then:

Generating answer...

If only a generic loading state is available:

Thinking...

The loading state should disappear immediately after completion.

16. Error States

Errors should be understandable.

Bad:

500 Internal Server Error

Better:

Something went wrong while generating the response.

Please try again.

For provider errors:

The selected model is currently unavailable.

Try switching providers or starting Ollama.

For database errors:

We couldn't save this conversation.
Please retry.

Internal stack traces must not be shown to the user.

17. Artifact Viewer

The artifact viewer appears beside the chat on larger screens.

Example:

┌─────────────────────────────────────┐
│ Artifact                             │
│                                      │
│  How to Improve Product Retention    │
│                                      │
│  ## Key Lessons                      │
│                                      │
│  ...                                 │
│                                      │
│  ## Practical Takeaway               │
│                                      │
└─────────────────────────────────────┘

The artifact panel should have:

Title.
Artifact type.
Content.
Copy action.
Optional download/export action.
Refresh/regenerate action where appropriate.
18. Markdown Artifacts

Markdown artifacts should be rendered as readable documents.

Example:

Artifact: Ship30 Essay

# The Retention Trap

Opening paragraph...

## The Core Lesson

...

## What to Do

1. ...
2. ...
3. ...

Markdown should use the same typography system as the rest of the application.

19. HTML Artifacts

HTML artifacts should be rendered separately from normal Markdown.

The rendering architecture:

Generated HTML
      │
      ▼
Sanitization
      │
      ▼
Sandboxed iframe
      │
      ▼
Artifact Viewer

Generated HTML is considered untrusted.

The iframe should use:

sandbox="allow-scripts"

Avoid:

sandbox="allow-scripts allow-same-origin"

unless specifically required.

The artifact must not be able to access the main application DOM.

20. Artifact Tabs

If both Markdown and HTML versions exist, the viewer can provide:

┌───────────────────────────────────────────────┐
│ Preview    Markdown    HTML                   │
├───────────────────────────────────────────────┤
│                                               │
│              Artifact preview                 │
│                                               │
└───────────────────────────────────────────────┘

The default tab should be the most useful representation for the generated artifact.

21. Artifact Empty State

When no artifact exists:

┌───────────────────────────────────────────────┐
│                                               │
│             No artifact generated             │
│                                               │
│ Ask the assistant to create an essay,         │
│ report, page, or HTML artifact.               │
│                                               │
└───────────────────────────────────────────────┘

The empty state should not look like an error.

22. Responsive Design

On smaller screens, the two-pane layout should collapse.

Desktop:

┌──────────────────────┬──────────────────────┐
│ Chat                 │ Artifact             │
│                      │                      │
└──────────────────────┴──────────────────────┘

Mobile:

┌──────────────────────────────┐
│ Header                       │
├──────────────────────────────┤
│ Chat                         │
│                              │
│                              │
├──────────────────────────────┤
│ Artifact                     │
│                              │
└──────────────────────────────┘

The chat should remain the primary section.

The artifact can appear below the conversation or through a dedicated tab.

23. Desktop Layout

Recommended desktop proportions:

Chat:      ~55–60%
Artifact:  ~40–45%

The exact ratio should remain flexible based on content.

Both panels should support independent scrolling when necessary.

The message composer should remain accessible.

24. Accessibility

The application should support:

Keyboard navigation.
Visible focus states.
Semantic HTML.
Accessible buttons.
Accessible form labels.
Sufficient text contrast.
Screen-reader-friendly status messages.
Keyboard submission.
Meaningful error messages.

Interactive elements must have clear labels.

Example:

<button aria-label="Send message">
  Send
</button>
25. Session UX

A session represents a conversation.

The user should be able to:

Start a new session.
Continue an existing session.
See previous messages.
Rename a session if supported.
Switch between sessions.

Example:

Sessions

Today
──────────────
Retention strategy
Growth loops
Brian Balfour notes

Yesterday
──────────────
Product-market fit

Session management should remain secondary to the main chat experience.

26. New Session

The new-session action should be obvious.

Example:

+ New Session

When selected:

New conversation started.

The old conversation should remain persisted.

27. Conversation Persistence

Messages should be saved automatically.

The UI can show:

Saved

or:

Saving...

if persistence is asynchronous.

A failed save should produce a clear notification.

28. Ship30 Experience

The user should be able to ask:

Write a Ship30-style essay about product retention.

The application should:

Retrieve relevant transcripts.
Gather supporting evidence.
Generate the essay.
Display the essay in chat.
Create a Markdown artifact.
Display the artifact beside the conversation.

Example:

Chat
────────────────────────────

I've created a Ship30-style essay
grounded in the relevant episodes.

Sources:
[Episode: Guest, Topic]


Artifact
────────────────────────────

# The Retention Trap

Strong hook...

Narrative...

Practical takeaway...
29. Artifact Generation Experience

A user can request:

Create a landing page based on this growth strategy.

The assistant can generate:

HTML
CSS

The artifact viewer renders the result in a sandboxed environment.

The user should be able to inspect the generated artifact without leaving the application.

30. Copy and Export

Artifacts should provide convenient actions:

[Copy] [Regenerate]

Optional:

[Export Markdown]
[Export HTML]

Copy should copy the underlying artifact content rather than the rendered visual representation.

31. Empty Application State

On first launch:

Lenny Growth Assistant

Ask questions about Lenny's podcast,
growth, product, and startup lessons.

Try:

"How does Lenny recommend improving retention?"

"Write a Ship30 essay about growth loops."

"Create a landing page based on this lesson."

The empty state should help users understand what the application can do.

32. Suggested Prompts

Suggested prompts can appear in the initial empty state.

Examples:

What does Lenny say about retention?

Summarize lessons from growth leaders.

Write a Ship30 essay about product-led growth.

Create an artifact from this discussion.

These prompts should disappear or become less prominent after the conversation starts.

33. Trust and Transparency

The UI should communicate where information comes from.

The user should be able to distinguish:

Transcript-backed information
          vs.
General model reasoning

The application should prioritize transparency over pretending to know everything.

If evidence is insufficient, the assistant should say so.

34. Visual Design Direction

The visual style should be:

Clean.
Modern.
Minimal.
Professional.
Content-focused.
Comfortable for long reading sessions.

Avoid:

Excessive gradients.
Excessive animations.
Crowded dashboards.
Large decorative graphics.
Unnecessary controls.

The design should prioritize the content.

35. Component Structure

Recommended frontend components:

src/
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
36. ChatPane

Responsibilities:

Display messages.
Handle message submission.
Display loading state.
Display streaming output.
Display citations.
Connect to session state.

Conceptual structure:

ChatPane
 │
 ├── MessageList
 │    └── MessageItem
 │
 └── MessageComposer
37. MessageItem

Responsibilities:

Render user messages.
Render assistant messages.
Render Markdown.
Display citations.
Display artifact availability.
Display errors where applicable.
38. ModelSelector

Responsibilities:

Display current provider.
Display current model.
Allow provider switching.
Show availability state.
Prevent invalid provider selection where possible.
39. ArtifactViewer

Responsibilities:

Display generated artifacts.
Switch between representations.
Copy artifact content.
Regenerate artifact.
Display artifact metadata.
Handle empty state.
40. SandboxedIframe

Responsibilities:

Render generated HTML.
Apply safe sandbox configuration.
Isolate generated content.
Resize the preview where appropriate.
Prevent direct DOM interaction with the parent application.
41. Interaction States

Every major component should account for:

Idle
Loading
Streaming
Success
Empty
Error
Unavailable

This prevents inconsistent UX across the application.

42. Performance

The frontend should:

Avoid unnecessary re-renders.
Stream long responses.
Lazy-load large artifacts where useful.
Avoid rendering excessively large conversation histories at once.
Keep artifact rendering isolated.

The backend should:

Limit retrieval results.
Avoid unnecessarily large prompts.
Apply LLM timeouts.
Cache reusable data where appropriate.