
// App.js
import React, { useState } from 'react';
import ChatAppDemo from './ChatAppDemo';
import TwoChats from './TwoChats';
import OneChat from './OneChat';

function App() {
  const [view, setView] = useState('TwoChats');

  // License state
  const [licenseKey, setLicenseKey] = useState('');
  const [licenseActivated, setLicenseActivated] = useState(false);

  // ChatGPT Token state
  const [chatgptToken, setChatgptToken] = useState('');
  const [tokenValid, setTokenValid] = useState(false);

  // ChatGPT Model Dropdown state
  const [selectedModel, setSelectedModel] = useState('4o');

  const renderView = () => {
    switch (view) {
      // case 'ChatAppDemo':
      //   return <ChatAppDemo />;
      case 'TwoChats':
        return <TwoChats />;
      case 'OneChat':
        return <OneChat />;
      default:
        return null;
    }
  };

  const handleLicenseSubmit = () => {
    // Example: Activate license if key is non-empty.
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
    // Example validation: token is valid if it starts with "sk-"
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
    <div className="App">
      <header style={styles.topbar}>
        <div style={styles.brand}>Merlin AI 🧙‍♂️</div>
        <nav style={styles.nav}>
          {/* <button style={styles.button} onClick={() => setView('ChatAppDemo')}>
            ChatAppDemo
          </button> */}
          <button style={styles.button} onClick={() => setView('TwoChats')}>
            TwoChats
          </button>
          <button style={styles.button} onClick={() => setView('OneChat')}>
            OneChat
          </button>
        </nav>
      </header>

      {/* Configuration Section: License (left) & ChatGPT Options (right) */}
      <div style={styles.configContainer}>
        {/* License Section */}
        <div style={styles.licenseContainer}>
          <input
            type="text"
            placeholder="Enter license key"
            value={licenseKey}
            onChange={(e) => setLicenseKey(e.target.value)}
            onKeyDown={handleLicenseKeyDown}
            style={styles.licenseInput}
          />
          <button style={styles.licenseButton} onClick={handleLicenseSubmit}>
            Submit
          </button>
          <div
            style={{
              ...styles.statusText,
              color: licenseActivated ? '#2E8B57' : '#FFBF00',
            }}
          >
            {licenseActivated ? 'License Activated' : 'License Not Activated'}
          </div>
        </div>

        {/* ChatGPT Section */}
        <div style={styles.chatGPTContainer}>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            style={styles.modelDropdown}
          >
            <option value="4o">4o</option>
            <option value="4o-mini">4o-mini</option>
            <option value="o3-mini">o3-mini</option>
            <option value="o3-mini-high">o3-mini-high</option>
          </select>
          <div style={styles.tokenContainer}>
            <input
              type="text"
              placeholder="Enter ChatGPT token"
              value={chatgptToken}
              onChange={(e) => setChatgptToken(e.target.value)}
              onKeyDown={handleTokenKeyDown}
              style={styles.tokenInput}
            />
            <button style={styles.tokenButton} onClick={handleTokenSubmit}>
              Submit
            </button>
            <div
              style={{
                ...styles.statusText,
                textAlign: 'right',
                color: tokenValid ? '#2E8B57' : '#FFBF00',
              }}
            >
              {tokenValid ? 'Valid OpenAI Token' : 'Invalid OpenAI Token'}
            </div>
          </div>
        </div>
      </div>

      <main style={styles.content}>{renderView()}</main>
    </div>
  );
}

// Inline styles
const styles = {
  topbar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#282c34',
    padding: '10px 20px',
    color: 'white',
  },
  brand: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
  },
  nav: {
    display: 'flex',
    gap: '10px',
  },
  button: {
    padding: '8px 12px',
    fontSize: '1rem',
    cursor: 'pointer',
    border: 'none',
    borderRadius: '4px',
  },
  content: {
    padding: '20px',
  },
  configContainer: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    margin: '10px 20px',
    flexWrap: 'wrap',
  },
  // License Styles (left side)
  licenseContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  licenseInput: {
    padding: '6px 10px',
    fontSize: '0.9rem',
    borderRadius: '4px',
    border: '1px solid #ccc',
    width: '200px',
  },
  licenseButton: {
    padding: '6px 10px',
    fontSize: '0.9rem',
    cursor: 'pointer',
    border: 'none',
    borderRadius: '4px',
    backgroundColor: '#007BFF',
    color: 'white',
  },
  // ChatGPT Styles (right side)
  chatGPTContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  modelDropdown: {
    padding: '6px 10px',
    fontSize: '0.9rem',
    borderRadius: '4px',
    border: '1px solid #ccc',
    backgroundColor: 'white',
  },
  tokenContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  tokenInput: {
    padding: '6px 10px',
    fontSize: '0.9rem',
    borderRadius: '4px',
    border: '1px solid #ccc',
    width: '200px',
  },
  tokenButton: {
    padding: '6px 10px',
    fontSize: '0.9rem',
    cursor: 'pointer',
    border: 'none',
    borderRadius: '4px',
    backgroundColor: '#007BFF',
    color: 'white',
  },
  statusText: {
    fontSize: '0.8rem',
    fontStyle: 'italic',
    margin: '0 5px',
  },
};

export default App;

