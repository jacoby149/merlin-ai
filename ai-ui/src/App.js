import React, { useState, useEffect } from 'react';
import './App.css';
import { FaDiscord, FaGithub, FaEnvelope, FaComments } from 'react-icons/fa';

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


function TwoChats() {
  return (
    <div className="two-chats-container">
      <ChatBox 
        apiEndpoint="/auto_coder/ui_mod" 
        title="Front End Auto Coder" 
        message="Type what you would like the agent to do on the frontend." 
      />
      <ChatBox 
        apiEndpoint="/auto_coder/api_mod" 
        title="Back End Auto Coder" 
        message="Type what you would like the agent to do on the backend." 
      />
    </div>
  );
}


function App() {
  const [UIMode, setUIMode] = useState('Web');
  const [licenseKey, setLicenseKey] = useState('');
  const [licenseActivated, setLicenseActivated] = useState(false);
  const [chatgptToken, setChatgptToken] = useState('');
  const [tokenValid, setTokenValid] = useState(false);
  const [selectedModel, setSelectedModel] = useState('4o-mini');
  const [selectedEngine, setSelectedEngine] = useState('ChatGPT');
  const [isDarkMode, setIsDarkMode] = useState(true);

  useEffect(() => {
    // Check for saved theme preference in local storage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setIsDarkMode(savedTheme === 'dark');
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  const renderView = () => {
    switch (UIMode) {
    case "Web":
    return <TwoChats />;
    default:
      return <div>Invalid Type</div>;
  }
};

  const handleLicenseSubmit = () => {
    if (licenseKey.trim() !== '') {
      setLicenseActivated(true);
    } else {
      setLicenseActivated(false);
    }
    console.log('Submitted license key:', licenseKey);
  };

  const handleLicenseKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleLicenseSubmit();
    }
  };

  const handleTokenSubmit = () => {
    if (chatgptToken.trim().startsWith('sk-')) {
      setTokenValid(true);
    } else {
      setTokenValid(false);
    }
    console.log('Submitted ChatGPT token:', chatgptToken);
  };

  const handleTokenKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleTokenSubmit();
    }
  };

  return (
    <div className={`App ${isDarkMode ? 'dark' : 'light'}`}>
      <header className="topbar">
        <div className="leftSection">
          <div className="brand">
            <img src="/Merlin-no-back-small.png" alt="Merlin logo" className="brand-logo" /> Merlin AI
          </div>
          <nav className="nav">
            <button className="button" onClick={() => setUIMode('Web')}>Web</button>
            <button className="button" onClick={() => setUIMode('Mobile')} disabled>
              Mobile
            </button>
          </nav>
        </div>
        <div className="dropdownContainer">
          <select
            className="engineDropdown"
            value={selectedEngine}
            onChange={(e) => setSelectedEngine(e.target.value)}
          >
            <option value="ChatGPT">ChatGPT</option>
            <option value="Deepseek" disabled>
              Deepseek (TBD)
            </option>
          </select>

          <select
            className="modelDropdown"
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            <option value="4o">4o</option>
            <option value="4o-mini">4o-mini</option>
            <option value="o3-mini">o3-mini</option>
            <option value="o3-mini-high">o3-mini-high</option>
          </select>
        </div>
        <button className="toggleButton" onClick={() => setIsDarkMode(prev => !prev)}>
          {isDarkMode ? '🌙' : '☀️'}
        </button>
      </header>

      {/* Configuration Section: License (left) & ChatGPT Token (right) */}
      <div className="configContainer">


{/* License Section */}
<div className="licenseContainer">
  <div className="inputRow">
    <input
      type="password"
      placeholder="License key"
      value={licenseKey}
      onChange={(e) => setLicenseKey(e.target.value)}
      onKeyDown={handleLicenseKeyDown}
      className="smallInput"
    />
    <button className="smallButton" onClick={handleLicenseSubmit}>
      Submit
    </button>
    <div className={`statusText ${licenseActivated ? 'activated' : 'notActivated'}`}>
      {licenseActivated ? 'License Activated' : 'License Not Activated'}
    </div>
  </div>
  <div className="helpText">
    Need a license key?{' '}
    <a
      href="https://licenses.merlinai.cloud"
      target="_blank"
      rel="noopener noreferrer"
    >
      Click here
    </a>
  </div>
</div>


{/* ChatGPT Token Section */}
<div className="tokenContainer">
  <div className="inputRow">
    <input
      type="password"
      placeholder="OpenAI token"
      value={chatgptToken}
      onChange={(e) => setChatgptToken(e.target.value)}
      onKeyDown={handleTokenKeyDown}
      className="smallInput"
    />
    <button className="smallButton" onClick={handleTokenSubmit}>
      Submit
    </button>
    <div className={`statusText ${tokenValid ? 'activated' : 'notActivated'}`}>
      {tokenValid ? 'Valid OpenAI Token' : 'Invalid OpenAI Token'}
    </div>
  </div>
  <div className="helpText helpTextRight">
    Need an OpenAI token?{' '}
    <a
      href="https://platform.openai.com/api-keys"
      target="_blank"
      rel="noopener noreferrer"
    >
      Click here
    </a>
  </div>
</div>
      </div>
            <h1><center>Coming Out in Four Weeks. <a style={{color:"orange"}}href="https://www.loom.com/share/e0050bcf46f945bf9a571cdbf495886b?sid=79e17692-f3f5-4829-95a0-631fe611024a" target="_blank" rel="noopener noreferrer">
  Watch Video
</a></center></h1>
      <center>
   </center>
      <main className={`content ${isDarkMode ? 'dark' : 'light'}`}>{renderView()}</main>
      {/* Floating Purchase License Button */}
      <a  href="https://licenses.merlinai.cloud" target="_blank" rel="noopener noreferrer">
      <button className="purchaseLicenseButton">Purchase License</button>
      </a>
      {/* Bottom Icons Container */}
      <div className="bottomIconsContainer">
        <a href="https://discord.gg/upggguqpx7" target="_blank" rel="noopener noreferrer" title="Join us on Discord">
          <FaDiscord />
        </a>
        <a href="https://github.com/jacoby149/merlin-ai" target="_blank" rel="noopener noreferrer" title="Star us on GitHub">
          <FaGithub />
        </a>
        <a href="mailto:support@merlinai.cloud" title="Email Support">
          <FaEnvelope />
        </a>
        {/* <a href="https://merlinai.com/support" target="_blank" rel="noopener noreferrer" title="Get Started"> */}
        {/*   <FaComments /> */}
        {/* </a> */}
      </div>
    </div>
  );
}

export default App;

