import { useEffect, useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import DOMPurify from "dompurify";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);

  const [artifact, setArtifact] = useState("");
  const [artifactType, setArtifactType] = useState("markdown");
  const [artifactView, setArtifactView] = useState("markdown");
  const [artifactLoading, setArtifactLoading] = useState(false);

  useEffect(() => {
    loadSessions();
  }, []);

  async function loadSessions() {
    try {
      const response = await axios.get(`${API}/api/sessions`);
      setSessions(response.data);
    } catch (error) {
      console.error("Failed to load sessions:", error);
    }
  }

  async function newChat() {
    try {
      const response = await axios.post(`${API}/api/sessions`, {
        title: "New conversation",
      });

      const session = response.data;

      setSessionId(session.id);
      setMessages([]);
      setArtifact("");
      setArtifactType("markdown");
      setArtifactView("markdown");

      setSessions((previous) => [session, ...previous]);
    } catch (error) {
      console.error("Failed to create session:", error);

      const detail = error.response?.data?.detail;

      alert(
        detail
          ? `Could not create conversation: ${detail}`
          : "Could not create conversation."
      );
    }
  }

  async function sendMessage(event) {
    event?.preventDefault();

    const text = query.trim();

    if (!text || loading) {
      return;
    }

    setQuery("");
    setLoading(true);

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: text,
      },
    ]);

    try {
      let currentSessionId = sessionId;

      if (!currentSessionId) {
        const sessionResponse = await axios.post(
          `${API}/api/sessions`,
          {
            title: text.slice(0, 50),
          }
        );

        currentSessionId = sessionResponse.data.id;

        setSessionId(currentSessionId);

        setSessions((previous) => [
          sessionResponse.data,
          ...previous,
        ]);
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: "",
          sources: [],
        },
      ]);

      const response = await fetch(`${API}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: currentSessionId,
          message: text,
          top_k: 5,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();

        throw new Error(
          errorText || "Chat request failed."
        );
      }

      if (!response.body) {
        throw new Error(
          "Streaming response is not available."
        );
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = "";
      let assistantAnswer = "";
      let sources = [];

      while (true) {
        const { value, done } = await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(value, {
          stream: true,
        });

        const lines = buffer.split("\n");

        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) {
            continue;
          }

          const data = JSON.parse(line);

          if (data.type === "token") {
            assistantAnswer += data.content;

            setMessages((previous) => {
              const updated = [...previous];

              const lastIndex = updated.length - 1;

              updated[lastIndex] = {
                ...updated[lastIndex],
                content: assistantAnswer,
              };

              return updated;
            });
          }

          if (data.type === "done") {
            sources = data.sources || [];

            setMessages((previous) => {
              const updated = [...previous];

              const lastIndex = updated.length - 1;

              updated[lastIndex] = {
                ...updated[lastIndex],
                id: data.message_id,
                content: assistantAnswer,
                sources,
              };

              return updated;
            });
          }

          if (data.type === "error") {
            throw new Error(
              data.message ||
                "LLM generation failed."
            );
          }
        }
      }

      if (buffer.trim()) {
        const data = JSON.parse(buffer);

        if (data.type === "token") {
          assistantAnswer += data.content;

          setMessages((previous) => {
            const updated = [...previous];

            const lastIndex = updated.length - 1;

            updated[lastIndex] = {
              ...updated[lastIndex],
              content: assistantAnswer,
            };

            return updated;
          });
        }

        if (data.type === "done") {
          sources = data.sources || [];

          setMessages((previous) => {
            const updated = [...previous];

            const lastIndex = updated.length - 1;

            updated[lastIndex] = {
              ...updated[lastIndex],
              id: data.message_id,
              content: assistantAnswer,
              sources,
            };

            return updated;
          });
        }

        if (data.type === "error") {
          throw new Error(
            data.message ||
              "LLM generation failed."
          );
        }
      }
    } catch (error) {
      console.error("Chat error:", error);

      const errorMessage =
        error.message ||
        "Sorry, I couldn't generate an answer. Please check that the backend and Ollama are running.";

      setMessages((previous) => {
        const updated = [...previous];

        const lastIndex = updated.length - 1;

        if (
          updated[lastIndex] &&
          updated[lastIndex].role === "assistant" &&
          !updated[lastIndex].content
        ) {
          updated[lastIndex] = {
            ...updated[lastIndex],
            content: errorMessage,
          };

          return updated;
        }

        return [
          ...updated,
          {
            role: "assistant",
            content: errorMessage,
            sources: [],
          },
        ];
      });
    } finally {
      setLoading(false);
    }
  }

  async function selectSession(id) {
    try {
      const response = await axios.get(
        `${API}/api/sessions/${id}`
      );

      setSessionId(id);

      setArtifact("");
      setArtifactType("markdown");
      setArtifactView("markdown");

      const loadedMessages =
        (response.data.messages || []).map(
          (message) => ({
            id: message.id,
            role: message.role,
            content: message.content,
            sources: message.sources || [],
          })
        );

      setMessages(loadedMessages);
    } catch (error) {
      console.error(
        "Failed to load conversation:",
        error
      );

      alert("Could not load conversation.");
    }
  }

  async function generateArtifact(
    message,
    type = "markdown"
  ) {
    if (!message?.id) {
      alert("Please send a message first.");
      return;
    }

    setArtifactLoading(true);

    try {
      const response = await axios.post(
        `${API}/api/artifacts/generate`,
        {
          request:
            type === "markdown"
              ? "Create a practical growth playbook from this answer"
              : type === "html"
                ? "Create a visual HTML growth playbook from this answer"
                : type === "css"
                  ? "Create CSS styling for a professional growth playbook based on this answer"
                  : "Create a complete HTML and CSS growth playbook from this answer",

          answer: message.content,

          artifact_type: type,

          message_id: message.id,
        }
      );

      console.log(
        "ARTIFACT RESPONSE:",
        response.data
      );

      const generatedType = (
        response.data.artifact_type ||
        response.data.type ||
        type
      ).toLowerCase();

      setArtifact(
        response.data.content || ""
      );

      setArtifactType(generatedType);

      setArtifactView(
        generatedType === "markdown"
          ? "markdown"
          : "preview"
      );
    } catch (error) {
      console.error(
        "ARTIFACT ERROR:",
        error
      );

      const detail =
        error.response?.data?.detail;

      alert(
        detail ||
          "Artifact generation failed."
      );
    } finally {
      setArtifactLoading(false);
    }
  }

  async function generateShip30(message) {
    if (!message?.id) {
      alert("Please send a message first.");
      return;
    }

    setArtifactLoading(true);

    try {
      const response = await fetch(
        `${API}/api/skills/ship30`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message_id: message.id,
            question: message.content,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Failed to generate Ship 30 essay."
        );
      }

      setArtifact(
        data.content || ""
      );

      setArtifactType("ship30");

      setArtifactView("markdown");
    } catch (error) {
      console.error(
        "Ship 30 generation failed:",
        error
      );

      alert(
        error.message ||
          "Ship 30 essay generation failed."
      );
    } finally {
      setArtifactLoading(false);
    }
  }

  function useExample(text) {
    setQuery(text);
  }

  return (
    <div className="app">

      {/* TOP BAR */}
      <header className="header">

        <div className="brand">

          <div className="brand-mark">
            L
          </div>

          <div>
            <h1>
              Lenny Growth Assistant
            </h1>

            <div className="brand-subtitle">
              Transcript-grounded product growth
              intelligence
            </div>
          </div>

        </div>

        <div className="header-actions">

          <div className="status-pill">
            <span className="status-dot"></span>
            Ollama connected
          </div>

          <button
            className="new-chat"
            onClick={newChat}
          >
            <span>＋</span>
            New Chat
          </button>

        </div>

      </header>

      <div className="layout">

        {/* SIDEBAR */}
        <aside className="sidebar">

          <div className="sidebar-top">

            <div className="sidebar-label">

              <span className="sidebar-icon">
                ◫
              </span>

              Conversations

            </div>

            <span className="conversation-count">
              {sessions.length}
            </span>

          </div>

          <div className="session-list">

            {sessions.length === 0 && (
              <div className="sidebar-empty">

                <div className="empty-small-icon">
                  💬
                </div>

                <p>
                  No conversations yet
                </p>

                <span>
                  Start a new conversation to
                  explore growth insights.
                </span>

              </div>
            )}

            {sessions.map((session) => (

              <button
                key={session.id}
                className={`session ${
                  sessionId === session.id
                    ? "active"
                    : ""
                }`}
                onClick={() =>
                  selectSession(session.id)
                }
              >

                <span className="session-icon">
                  ◌
                </span>

                <span className="session-title">
                  {session.title ||
                    "New conversation"}
                </span>

              </button>

            ))}

          </div>

          <div className="sidebar-footer">

            <div className="powered">
              <span className="powered-dot"></span>
              Grounded in Lenny Podcast
              transcripts
            </div>

          </div>

        </aside>

        {/* CHAT */}
        <main className="chat">

          <div className="chat-topbar">

            <div>

              <span className="chat-label">
                {sessionId
                  ? "CONVERSATION"
                  : "NEW CONVERSATION"}
              </span>

              <h2>
                {sessionId
                  ? "Growth discussion"
                  : "Explore product growth"}
              </h2>

            </div>

            <div className="evidence-badge">
              <span>✦</span>
              Evidence grounded
            </div>

          </div>

          <div className="messages">

            {/* WELCOME */}
            {messages.length === 0 && (

              <div className="welcome">

                <div className="welcome-icon">
                  ✦
                </div>

                <div className="welcome-eyebrow">
                  LENNY GROWTH ASSISTANT
                </div>

                <h2>
                  Turn Lenny's insights into
                  <span>
                    {" "}
                    actionable growth.
                  </span>
                </h2>

                <p>
                  Ask questions about the
                  ingested Lenny Podcast
                  transcripts. Every answer is
                  grounded in transcript evidence.
                </p>

                <div className="examples">

                  <button
                    onClick={() =>
                      useExample(
                        "What is activation and why is it important for growth?"
                      )
                    }
                  >
                    <span>⚡</span>
                    What is activation?
                  </button>

                  <button
                    onClick={() =>
                      useExample(
                        "What does the transcript say about customer interviews?"
                      )
                    }
                  >
                    <span>◉</span>
                    Customer interviews
                  </button>

                  <button
                    onClick={() =>
                      useExample(
                        "What growth channels should teams focus on?"
                      )
                    }
                  >
                    <span>↗</span>
                    Growth channels
                  </button>

                </div>

              </div>

            )}

            {/* MESSAGES */}
            {messages.map(
              (message, index) => (

                <div
                  key={index}
                  className={`message ${
                    message.role === "user"
                      ? "user"
                      : "assistant"
                  }`}
                >

                  <div className="message-avatar">
                    {message.role === "user"
                      ? "Y"
                      : "L"}
                  </div>

                  <div className="message-main">

                    <div className="message-meta">

                      <span>
                        {message.role === "user"
                          ? "You"
                          : "Lenny AI"}
                      </span>

                      {message.role ===
                        "assistant" && (
                        <span className="ai-label">
                          GROUNDED
                        </span>
                      )}

                    </div>

                    <div className="bubble">

                      <div className="content">
                        {message.content}

                        {loading &&
                          index ===
                            messages.length - 1 &&
                          message.role ===
                            "assistant" && (
                            <span className="streaming-cursor">
                              ▌
                            </span>
                          )}
                      </div>

                      {/* SOURCES */}
                      {message.sources &&
                        message.sources.length >
                          0 && (

                        <div className="sources">

                          <div className="sources-header">

                            <div>

                              <span className="source-symbol">
                                ◈
                              </span>

                              <strong>
                                Transcript evidence
                              </strong>

                            </div>

                            <span className="source-count">
                              {
                                message.sources
                                  .length
                              }{" "}
                              sources
                            </span>

                          </div>

                          {message.sources.map(
                            (
                              source,
                              sourceIndex
                            ) => (

                              <div
                                className="source"
                                key={
                                  sourceIndex
                                }
                              >

                                <div className="source-number">
                                  {String(
                                    sourceIndex +
                                      1
                                  ).padStart(
                                    2,
                                    "0"
                                  )}
                                </div>

                                <div className="source-info">

                                  <b>
                                    {
                                      source.episode_title
                                    }
                                  </b>

                                  <div className="source-details">

                                    <span>
                                      {source.guest_name ||
                                        "Unknown guest"}
                                    </span>

                                    <span>
                                      {source.timestamp ||
                                        "Unknown time"}
                                    </span>

                                    {source.topic && (
                                      <span>
                                        {
                                          source.topic
                                        }
                                      </span>
                                    )}

                                  </div>

                                </div>

                              </div>

                            )
                          )}

                          {/* ARTIFACT BUTTONS */}
                          <div className="artifact-actions">

                            <button
                              className="artifact-btn"
                              onClick={() =>
                                generateArtifact(
                                  message,
                                  "markdown"
                                )
                              }
                              disabled={
                                artifactLoading
                              }
                            >
                              <span>
                                ✦
                              </span>

                              Markdown

                              <span className="arrow">
                                →
                              </span>

                            </button>

                            <button
                              className="artifact-btn artifact-btn-secondary"
                              onClick={() =>
                                generateArtifact(
                                  message,
                                  "html"
                                )
                              }
                              disabled={
                                artifactLoading
                              }
                            >
                              <span>
                                ◇
                              </span>

                              HTML

                              <span className="arrow">
                                →
                              </span>

                            </button>

                            <button
                              className="artifact-btn artifact-btn-secondary"
                              onClick={() =>
                                generateArtifact(
                                  message,
                                  "html_css"
                                )
                              }
                              disabled={
                                artifactLoading
                              }
                            >
                              <span>
                                ◈
                              </span>

                              HTML + CSS

                              <span className="arrow">
                                →
                              </span>

                            </button>

                            <button
                              className="artifact-btn"
                              onClick={() =>
                                generateShip30(message)
                              }
                              disabled={
                                artifactLoading ||
                                !message.id
                              }
                            >
                              <span>
                                ✍
                              </span>

                              Ship 30 Essay

                              <span className="arrow">
                                →
                              </span>

                            </button>

                          </div>

                        </div>

                      )}

                    </div>

                  </div>

                </div>

              )
            )}

            {/* LOADING */}
            {loading && (

              <div className="message assistant">

                <div className="message-avatar ai-avatar">
                  L
                </div>

                <div className="message-main">

                  <div className="message-meta">

                    <span>
                      Lenny AI
                    </span>

                    <span className="ai-label">
                      STREAMING
                    </span>

                  </div>

                  <div className="bubble loading-bubble">

                    <div className="thinking">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>

                    <span className="thinking-text">
                      Searching transcript
                      evidence and generating
                      answer...
                    </span>

                  </div>

                </div>

              </div>

            )}

          </div>

          {/* INPUT */}
          <form
            className="input-area"
            onSubmit={sendMessage}
          >

            <div className="input-wrapper">

              <input
                value={query}
                onChange={(event) =>
                  setQuery(
                    event.target.value
                  )
                }
                placeholder="Ask Lenny about product growth..."
                disabled={loading}
              />

              <button
                type="submit"
                disabled={
                  loading ||
                  !query.trim()
                }
                className="send-button"
              >

                <span>
                  {loading
                    ? "..."
                    : "Send"}
                </span>

                {!loading && (
                  <span>↑</span>
                )}

              </button>

            </div>

            <div className="input-hint">

              <span>
                Answers are grounded in
                ingested transcript evidence.
              </span>

              <span className="shortcut">
                ↵ Send
              </span>

            </div>

          </form>

        </main>

        {/* ARTIFACT PANEL */}
        <aside className="artifact-panel">

          <div className="panel-header">

            <div className="panel-title">

              <div className="panel-icon">
                ◫
              </div>

              <div>

                <span className="panel-eyebrow">
                  WORKSPACE
                </span>

                <h3>
                  Growth Playbook
                </h3>

              </div>

            </div>

            {artifact && (
              <button
                className="clear-button"
                onClick={() => {
                  setArtifact("");
                  setArtifactType("markdown");
                  setArtifactView("markdown");
                }}
              >
                Clear
              </button>
            )}

          </div>

          <div className="artifact-divider"></div>

          {/* EMPTY STATE */}
          {!artifact &&
            !artifactLoading && (

            <div className="artifact-empty">

              <div className="artifact-empty-icon">
                ✦
              </div>

              <h4>
                Your playbook
                <br />
                will appear here
              </h4>

              <p>
                Generate a practical growth
                playbook from any grounded
                answer.
              </p>

              <div className="artifact-features">

                <span>
                  ✓ Key insights
                </span>

                <span>
                  ✓ Actionable recommendations
                </span>

                <span>
                  ✓ Transcript citations
                </span>

              </div>

            </div>

          )}

          {/* ARTIFACT LOADING */}
          {artifactLoading && (

            <div className="artifact-empty">

              <div className="artifact-spinner">
                ✦
              </div>

              <h4>
                Building your playbook
              </h4>

              <p>
                Turning transcript insights
                into actionable
                recommendations...
              </p>

            </div>

          )}

          {/* RENDERED ARTIFACT */}
          {artifact && (

            <div className="artifact-document">

              <div className="document-top">

                <div className="document-label">

                  <span>
                    GENERATED ARTIFACT
                  </span>

                  <span className="artifact-type-badge">
                    {artifactType.toUpperCase()}
                  </span>

                </div>

                {(artifactType === "html" ||
                  artifactType === "html_css" ||
                  artifactType === "css") && (

                  <div className="artifact-tabs">

                    <button
                      type="button"
                      className={
                        artifactView === "source"
                          ? "artifact-tab active"
                          : "artifact-tab"
                      }
                      onClick={() =>
                        setArtifactView("source")
                      }
                    >
                      Source
                    </button>

                    <button
                      type="button"
                      className={
                        artifactView === "preview"
                          ? "artifact-tab active"
                          : "artifact-tab"
                      }
                      onClick={() =>
                        setArtifactView("preview")
                      }
                    >
                      Preview
                    </button>

                  </div>

                )}

              </div>

              {artifactView === "preview" &&
              (artifactType === "html" ||
                artifactType === "html_css" ||
                artifactType === "css") ? (

                <div className="artifact-preview">

                  <iframe
                    title="Generated artifact preview"
                    className="artifact-iframe"
                    sandbox=""
                    referrerPolicy="no-referrer"
                    srcDoc={DOMPurify.sanitize(
                      artifactType === "css"
                        ? `<!doctype html>
<html>
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<style>${artifact}</style>
</head>
<body>
<div class="preview-placeholder">
  <h2>CSS Preview</h2>
  <p>This sandbox renders the generated CSS.</p>
</div>
</body>
</html>`
                        : artifact
                    )}
                  />

                </div>

              ) : (

                <div className="artifact-content markdown-content">

                  {artifactType === "markdown" ||
                  artifactType === "ship30" ? (

                    <ReactMarkdown>
                      {artifact}
                    </ReactMarkdown>

                  ) : (

                    <pre className="artifact-source">
                      {artifact}
                    </pre>

                  )}

                </div>

              )}

            </div>

          )}

        </aside>

      </div>

    </div>
  );
}

export default App;