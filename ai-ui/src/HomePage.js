
import React, { useState, useEffect } from 'react';
import ChatBox from './ChatBox'; // Ensure ChatBox is exported from its own file.
import { FaDiscord, FaGithub, FaEnvelope } from 'react-icons/fa';
import './HomePage.css'; // Homepage-specific styles
import Vanilla from './Vanilla'

function HomePage() {
  const [isDarkMode, setIsDarkMode] = useState(true);

  // Load and persist theme preference
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setIsDarkMode(savedTheme === 'dark');
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  return (
    <div className={`App ${isDarkMode ? 'dark' : 'light'}`}>
      {/* Neon Topbar */}
      <header className="topbar">
        <div className="leftSection">
          <div className="brand">
            <img
              src="/Merlin-no-back-small.png"
              alt="Merlin logo"
              className="brand-logo"
            />
            Merlin AI
          </div>
          <nav className="nav">
            <ul className="nav-menu">
              <li className="nav-item">
                <a href="#" className="nav-link">Home</a>
              </li>
              <li className="nav-item dropdown">
                <a href="#" className="nav-link">About</a>
                <ul className="dropdown-menu">
                  <li><a href="#">Our Story</a></li>
                  <li><a href="#">Team</a></li>
                  <li><a href="#">Careers</a></li>
                </ul>
              </li>
              <li className="nav-item dropdown">
                <a href="#" className="nav-link">Features</a>
                <ul className="dropdown-menu">
                  <li><a href="#">Feature 1</a></li>
                  <li><a href="#">Feature 2</a></li>
                  <li><a href="#">Feature 3</a></li>
                </ul>
              </li>
              <li className="nav-item">
                <a href="#" className="nav-link">Contact</a>
              </li>
            </ul>
          </nav>
        </div>
        <button className="toggleButton" onClick={() => setIsDarkMode(prev => !prev)}>
          {isDarkMode ? '🌙' : '☀️'}
        </button>
      </header>

      {/* Main Content */}
      <div className="homepage-content">
        {/* Left Pane: Demo ChatBox */}
        <div className="leftPane">
          <ChatBox 
            apiEndpoint="/auto_coder/ui_mod"
title="Merlin AI Coder" 
        message="Type what you would like the agent to code." 
          />
        </div>

        {/* Right Pane: Embedded Vanilla React App */}
        <div className="rightPane">
          {/* <Vanilla/> */}
          <iframe
            src="http://localhost:3000"
            title="Vanilla React App Demo"
            frameBorder="0"
            className="iframeDemo"
          />
        </div>
      </div>

      {/* Floating Purchase License Button & Social Media Icons */}
      <a
        href="https://licenses.merlinai.cloud"
        target="_blank"
        rel="noopener noreferrer"
      >
        <button className="purchaseLicenseButton">Purchase License</button>
      </a>
      <div className="bottomIconsContainer">
        <a
          href="https://discord.gg/upggguqpx7"
          target="_blank"
          rel="noopener noreferrer"
          title="Join us on Discord"
        >
          <FaDiscord />
        </a>
        <a
          href="https://github.com/jacoby149/merlin-ai"
          target="_blank"
          rel="noopener noreferrer"
          title="Star us on GitHub"
        >
          <FaGithub />
        </a>
        <a href="mailto:support@merlinai.cloud" title="Email Support">
          <FaEnvelope />
        </a>
      </div>
    </div>
  );
}

export default HomePage;

