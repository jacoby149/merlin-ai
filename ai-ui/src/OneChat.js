
import React, { useState } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

function OneChat() {
  const [inputMessage, setInputMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Send a chat message to the API.
  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    // Start fresh with the new user message.
    const userMessage = { role: 'user', content: inputMessage };
    setConversation([userMessage]);
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // No session ID is needed now; just send the message.
        body: JSON.stringify({ message: inputMessage }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      const data = await response.json();

      // Replace the conversation with the user message and the assistant's reply.
      setConversation([userMessage, { role: 'assistant', content: data.reply }]);
      setInputMessage('');
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="chat-app"
      style={{
        maxWidth: '600px',
        margin: '2rem auto',
        fontFamily: 'Arial, sans-serif'
      }}
    >
      <h1>FullStack Auto Coder</h1>

      <div
        className="chat-window"
        style={{
          border: '1px solid #ccc',
          padding: '1rem',
          height: '300px',
          overflowY: 'scroll',
          backgroundColor: '#f9f9f9'
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
    </div>
  );
}

export default OneChat;

