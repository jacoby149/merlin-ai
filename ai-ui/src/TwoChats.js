
import React from 'react';
import './TwoChats.css';
import ChatBox from './ChatBox'


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

export default TwoChats;

