
import React, { useState } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

function ChatBox({ apiEndpoint, title = "Chat with OpenAI" , message="No messages yet. Say hello!"}) {
  const [inputMessage, setInputMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Send a chat message to the provided API endpoint.
  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    // Start fresh with the new user message.
    const userMessage = { role: 'user', content: inputMessage };
    setConversation([userMessage]);
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}${apiEndpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat: inputMessage, context: "" }),
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

  // Handle input change and add newline when Shift + Enter is pressed
  const handleInputChange = (e) => {
    if (e.key === 'Enter' && e.shiftKey) {
      // Allow a newline to be added without submitting the form
      return
    } else if (e.key === 'Enter') {
      // If just Enter is pressed, send the message
      handleSend(e);
    } else {
      // Update input message on other key presses
      setInputMessage(e.target.value);
    }
  };

  return (
    <div
      className="chat-box"
      style={{
        flex: 1,
        border: '1px solid #ccc',
        padding: '1rem',
        borderRadius: '4px',
        backgroundColor: '#fff'
      }}
    >
      <h2 style={{ textAlign: 'center' }}>{title}</h2>
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
          <p>{message}</p>
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
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={handleInputChange}
          placeholder="Type your message..."
          style={{
            flex: 1,
            padding: '0.5rem',
            fontSize: '1rem',
            resize: 'none',
            height:'18px'
          }}
        />
        <button type="submit" disabled={loading} style={{ padding: '0.5rem 1rem', marginLeft: '0.5rem' }}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
}

function TwoChats() {
  return (
    <div
      className="two-chats-container"
      style={{
        display: 'flex',
        gap: '1rem',
        maxWidth: '1200px',
        margin: '2rem auto',
        padding: '0 1rem'
      }}
    >
      <ChatBox apiEndpoint="/auto_coder/ui_mod" title="Front End Auto Coder" message="Type what you would like the agent to do on the frontend." />
      <ChatBox apiEndpoint="/auto_coder/api_mod" title="Back End Auto Coder" message="Type what you would like the agent to do on the backend."/>
    </div>
  );
}

export default TwoChats;

