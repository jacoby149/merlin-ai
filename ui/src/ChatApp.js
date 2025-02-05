
import React, { useState, useEffect } from 'react';

// Use an environment variable for the API base URL if needed.
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function ChatApp() {
  // Initialize sessionId from localStorage or use "default".
  const [sessionId, setSessionId] = useState(() => {
    return localStorage.getItem('sessionId') || 'default';
  });
  const [inputMessage, setInputMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Send a chat message to the API.
  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    // Append the user's message locally.
    setConversation((prev) => [...prev, { role: 'user', content: inputMessage }]);
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: inputMessage }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      const data = await response.json();

      // If the backend generated a new session ID (because we sent "default"), update it.
      if (sessionId === 'default' && data.session_id) {
        setSessionId(data.session_id);
        localStorage.setItem('sessionId', data.session_id);
      }

      // Append the assistant's reply.
      setConversation((prev) => [...prev, { role: 'assistant', content: data.reply }]);
      setInputMessage('');
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Reset conversation both locally and on the server.
  const handleReset = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/history/${sessionId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      // Clear the local conversation and session ID.
      setConversation([]);
      localStorage.removeItem('sessionId');
      setSessionId('default');
    } catch (err) {
      setError(`Error resetting conversation: ${err.message}`);
    }
  };

  // (Optional) Load existing conversation history from the server when sessionId changes.
  useEffect(() => {
    const fetchHistory = async () => {
      if (sessionId === 'default') return;
      try {
        const response = await fetch(`${API_BASE_URL}/chat/history/${sessionId}`);
        if (!response.ok) {
          throw new Error(`HTTP error: ${response.status}`);
        }
        const data = await response.json();
        setConversation(data.history);
      } catch (err) {
        console.error('Failed to fetch history:', err);
      }
    };
    fetchHistory();
  }, [sessionId]);

  return (
    <div className="chat-app" style={{ maxWidth: '600px', margin: '2rem auto', fontFamily: 'Arial, sans-serif' }}>
      <h1>Chat with OpenAI</h1>

      <div
        className="chat-window"
        style={{
          border: '1px solid #ccc',
          padding: '1rem',
          height: '300px',
          overflowY: 'scroll',
          backgroundColor: '#f9f9f9',
        }}
      >
        {conversation.length === 0 ? (
          <p>No messages yet. Say hello!</p>
        ) : (
          conversation.map((msg, index) => (
            <div key={index} style={{ margin: '0.5rem 0' }}>
              <strong>{msg.role === 'user' ? 'You' : 'Assistant'}:</strong> {msg.content}
            </div>
          ))
        )}
      </div>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <form onSubmit={handleSend} style={{ marginTop: '1rem', display: 'flex' }}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your message..."
          style={{ flex: 1, padding: '0.5rem', fontSize: '1rem' }}
        />
        <button type="submit" disabled={loading} style={{ padding: '0.5rem 1rem', marginLeft: '0.5rem' }}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>

      <button onClick={handleReset} style={{ marginTop: '1rem', backgroundColor: '#e74c3c', color: '#fff', border: 'none', padding: '0.5rem 1rem', cursor: 'pointer' }}>
        Reset Conversation
      </button>
    </div>
  );
}

export default ChatApp;
