import React, { useState, useRef, useEffect } from 'react';
import './css/App.css';
import './css/confirm-dialog.css';
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import Sidebar from './components/sidebar';
import axios from 'axios';
import Spinner from './components/spinner';
import VoiceRecorder from './components/voiceRecorder';
import ResultTable from './components/resultTable';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [spinner, setSpinner] = useState(false);

  const scrollToRef = useRef(null);

  useEffect(() => {
    if (scrollToRef.current) {
      scrollToRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);
  
  const handleSend = (e) => {
    e.preventDefault();
    if (input.trim() !== '') {
      const startTime = performance.now();
      setMessages(messages => [...messages, { text: input, sender: 'user' }]);
      setSpinner(true);
      const {data} = axios.post('http://localhost:8000//messages/', 
      {
        'message': input
      }, 
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }).then(function (response) {
        
        const endTime = performance.now();
        const duration = (endTime - startTime) / 1000;

        setSpinner(false);
        if (response.data.content['SQL'] === 'None' || response.data.content['SQL'] === '' || response.data.content["SQL"] === "SELECT * FROM YOUR_BAG") {
          setMessages(messages => [...messages, { text: response.data.content['replyToUser'],sender: 'model', sqlQuery: response.data.content['SQL'], result: "None", duration:duration.toFixed(2)}]);
        }
        else {
          setMessages(messages => [...messages, { text: JSON.stringify(response.data.result), sender: 'model', sqlQuery: response.data.content['SQL'], result: response.data.result, duration:duration.toFixed(2)}]);
        }
        

        
      }).catch(function (error) {
        console.log(error);
      });
      setInput('');
    }
  };

  const handleDelete = () => {
      setMessages([]);
  }

  const confirm = () => {
    confirmDialog({
      message: 'Are you sure you want to delete chat history?',
      header: 'Confirm Action',
      acceptClassName: 'custom-button custom-accept-button',
      acceptLabel: 'Yes',
      rejectClassName: 'custom-button custom-reject-button',
      rejectLabel: 'No',
      accept: () => setMessages([]),
      className: 'custom-confirm-dialog', // Custom class for the dialog
      draggable: false
    });
  };

  return (
    <div className="chat-container">
      <Sidebar onChangeDelete={handleDelete} />
      <div className="chat-header">
        <h2>Chat</h2>
      </div>
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`chat-message ${message.sender}`}>
            {(message.sender === 'model' && message.result !== "None") ? <ResultTable result={message.result} /> : message.text}
            {message.sender === 'model' ? <div key={index} className='line' style={{'padding-top': '5px'}}></div>: null}           
            {message.sender === 'model' ? <div key={index}>SQL message: {message.sqlQuery}</div>: null}
            {message.sender === 'model' && <div className="timer"> <p>Response Time: {message.duration} s</p> </div>}
          </div>
        ))}
        {spinner ? <div style={{"background-color": "#F0F0F0"}} className="chat-message model"> <Spinner /> </div> : null}
        <div ref={scrollToRef} />
      </div>
      <form onSubmit={handleSend} onReset={confirm} className="chat-input-form">
        <TextField
          fullWidth 
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <VoiceRecorder onRecordPost={message => setMessages(messages => [...messages, { text: message, sender: 'user', sqlQuery: null}])}
                                onRecordWaiting={spinner => setSpinner(spinner)} waitingForReply={spinner}/>
              </InputAdornment>
            ),
          }}
          label="Enter message"
          variant="outlined"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        {spinner ? <button type="submit" disabled>Send</button> :
        <button type="submit">Send</button>}
        <button type='reset'>Delete</button>
        <ConfirmDialog />
      </form>
    </div>
  );
}

export default App;
