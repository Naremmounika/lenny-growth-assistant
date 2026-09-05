import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [artifact, setArtifact] = useState("");
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
            title: "New conversation",
          }
        );

        currentSessionId = sessionResponse.data.id;

        setSessionId(currentSessionId);

        setSessions((previous) => [
          sessionResponse.data,
          ...previous,
        ]);
      }

      const response = await axios.post(`${API}/api/answer`, {
        query: text,
        top_k: 5,
        session_id: currentSessionId,
      });

      const assistantMessage = {
        role: "assistant",
        content: response.data.answer,
        sources: response.data.sources || [],
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);
    } catch (error) {
      console.error("Answer error:", error);

      const detail = error.response?.data?.detail;

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            detail ||
            "Sorry, I couldn't generate an answer. Please check that the backend and Ollama are running.",
        },
      ]);
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

      const loadedMessages = (response.data.messages || []).map(
        (message) => ({
          role: message.role,
          content: message.content,
          sources: message.sources || [],
        })
      );

      setMessages(loadedMessages);
    } catch (error) {
      console.error("Failed to load conversation:", error);
      alert("Could not load conversation.");
    }
  }

  async function generateArtifact(message) {
    setArtifactLoading(true);

    try {
      const response = await axios.post(
        `${API}/api/artifacts/generate`,
        {
          request:
            "Create a practical growth playbook from this answer",
          answer: message.content,
        }
      );

      setArtifact(response.data.content);
    } catch (error) {
      console.error("Artifact error:", error);

      const detail = error.response?.data?.detail;

      alert(detail || "Artifact generation failed.");
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
          <div className="brand-mark">L</div>

          <div>
            <h1>Lenny Growth Assistant</h1>
            <div className="brand-subtitle">
              Transcript-grounded product growth intelligence
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
              <span className="sidebar-icon">◫</span>
              Conversations
            </div>

            <span className="conversation-count">
              {sessions.length}
            </span>
          </div>

          <div className="session-list">

            {sessions.length === 0 && (
              <div className="sidebar-empty">
                <div className="empty-small-icon">💬</div>
                <p>No conversations yet</p>
                <span>
                  Start a new conversation to explore
                  growth insights.
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
                  {session.title || "New conversation"}
                </span>
              </button>
            ))}

          </div>

          <div className="sidebar-footer">
            <div className="powered">
              <span className="powered-dot"></span>
              Grounded in Lenny Podcast transcripts
            </div>
          </div>

        </aside>

        {/* CHAT AREA */}
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
                  <span> actionable growth.</span>
                </h2>

                <p>
                  Ask questions about the ingested
                  Lenny Podcast transcripts. Every
                  answer is grounded in transcript
                  evidence.
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
            {messages.map((message, index) => (

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

                    {message.role === "assistant" && (
                      <span className="ai-label">
                        GROUNDED
                      </span>
                    )}
                  </div>

                  <div className="bubble">
                    <div className="content">
                      {message.content}
                    </div>

                    {message.sources &&
                      message.sources.length > 0 && (

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
                            {message.sources.length} sources
                          </span>
                        </div>

                        {message.sources.map(
                          (source, sourceIndex) => (

                            <div
                              className="source"
                              key={sourceIndex}
                            >

                              <div className="source-number">
                                {String(
                                  sourceIndex + 1
                                ).padStart(2, "0")}
                              </div>

                              <div className="source-info">

                                <b>
                                  {source.episode_title}
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
                                      {source.topic}
                                    </span>
                                  )}
                                </div>

                              </div>

                            </div>

                          )
                        )}

                        <button
                          className="artifact-btn"
                          onClick={() =>
                            generateArtifact(message)
                          }
                        >
                          <span>✦</span>
                          Generate Growth Playbook
                          <span className="arrow">→</span>
                        </button>

                      </div>
                    )}

                  </div>

                </div>

              </div>

            ))}

            {/* LOADING */}
            {loading && (
              <div className="message assistant">

                <div className="message-avatar ai-avatar">
                  L
                </div>

                <div className="message-main">

                  <div className="message-meta">
                    <span>Lenny AI</span>
                    <span className="ai-label">
                      THINKING
                    </span>
                  </div>

                  <div className="bubble loading-bubble">
                    <div className="thinking">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>

                    <span className="thinking-text">
                      Searching transcript evidence...
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
                  setQuery(event.target.value)
                }
                placeholder="Ask Lenny about product growth..."
                disabled={loading}
              />

              <button
                type="submit"
                disabled={
                  loading || !query.trim()
                }
                className="send-button"
              >
                <span>
                  {loading ? "..." : "Send"}
                </span>

                {!loading && <span>↑</span>}
              </button>

            </div>

            <div className="input-hint">
              <span>
                Answers are grounded in ingested
                transcript evidence.
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
                onClick={() =>
                  setArtifact("")
                }
              >
                Clear
              </button>
            )}

          </div>

          <div className="artifact-divider"></div>

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
                <span>✓ Key insights</span>
                <span>✓ Actionable recommendations</span>
                <span>✓ Transcript citations</span>
              </div>

            </div>

          )}

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
                into actionable recommendations...
              </p>

            </div>
          )}

          {artifact && (
            <div className="artifact-document">

              <div className="document-top">
                <span>
                  GENERATED ARTIFACT
                </span>

                <span>
                  MARKDOWN
                </span>
              </div>

              <pre className="artifact-content">
                {artifact}
              </pre>

            </div>
          )}

        </aside>

      </div>
    </div>
  );
}

export default App;

