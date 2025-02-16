import React, { useState } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

function ChatBox({ apiEndpoint, title = "Chat with OpenAI", message = "No messages yet. Say hello!" }) {
  const [inputMessage, setInputMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Send a chat message to the provided API endpoint.
  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

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

      setConversation([userMessage, { role: 'assistant', content: data.reply }]);
      setInputMessage('');
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Handle input changes and send on Enter (unless Shift is pressed)
  const handleInputChange = (e) => {
    if (e.key === 'Enter' && e.shiftKey) {
      return; // allow newline
    } else if (e.key === 'Enter') {
      handleSend(e);
    } else {
      setInputMessage(e.target.value);
    }
  };

  return (
    <div className="chat-box">
      <h2>{title}</h2>
      <div className="chat-window">
        {conversation.length === 0 ? (
          <p>{message}</p>
        ) : (
          conversation.map((msg, index) => (
            <div key={index} className="chat-message">
              <strong>{msg.role === 'user' ? 'You' : 'Assistant'}:</strong> {msg.content}
            </div>
          ))
        )}
      </div>

      {error && <p className="error-message">{error}</p>}

      <form onSubmit={handleSend} className="chat-form">
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={handleInputChange}
          placeholder="Type your message..."
          className="chat-input"
        />
        <button type="submit" disabled={loading} className="chat-send-button">
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
}

export default ChatBox;
