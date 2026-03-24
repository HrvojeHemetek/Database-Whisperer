import React, { useState } from 'react';
import { AudioRecorder, useAudioRecorder } from 'react-audio-voice-recorder';
import axios from 'axios';
import { Rings } from 'react-loader-spinner';
import { FaMicrophone } from 'react-icons/fa';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import '../css/confirm-dialog.css';

function VoiceRecorder({onRecordPost, onRecordWaiting, waitingForReply}) {
  const [isRecording, setIsRecording] = useState(false);
  const [showForm, setShowForm] = useState(false);

  const recorderControls = useAudioRecorder();

  const confirm = (blob) => {
    confirmDialog({
      message: 'Do you want to post the recording?',
      header: 'Confirm Action',
      acceptClassName: 'custom-button custom-accept-button',
      acceptLabel: 'Yes',
      rejectClassName: 'custom-button custom-reject-button',
      rejectLabel: 'No',
      accept: () => {
        setShowForm(false);
        onRecordWaiting(true);
        addAudioElement(blob);
      },
      reject: () => {
        setShowForm(false);
      },
      className: 'custom-confirm-dialog', // Custom class for the dialog
      draggable: false
    });
  };

  const addAudioElement = (blob) => {
      onRecordWaiting(true);
      // const url = URL.createObjectURL(blob);
      // const audio = document.createElement("audio");
      // audio.src = url;
      // audio.controls = true;
      // document.body.appendChild(audio);
      sendAudioToServer(blob);
  };

  const sendAudioToServer = (blob) => {
    let formData = new FormData();
    formData.append('file', blob, 'voice-message.webm');

    const {data} = axios.post('http://localhost:8000//audio', formData, 
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
      }).then(function (response) {
        onRecordWaiting(false);
        if (response.data.success) {
          onRecordPost(response.data.content);
        }
        else {
          onRecordPost('Unsuccessful translation');
        }
        console.log(response);
      }).catch(function (error) {
      console.log(error);
    });
  };

  const startRecording = () => {
    recorderControls.startRecording();
    setIsRecording(true);
  };

  const stopRecording = () => {
    recorderControls.stopRecording();
    setIsRecording(false);
    setShowForm(true);
  };

  return (
    <div>
      {isRecording && !waitingForReply ? (
        <div className="voice-record-button" onClick={stopRecording}>
          <Rings
            height="25"
            width="25"
            color="#4fa94d"
            radius="6"
            wrapperStyle={{}}
            wrapperClass=""
            visible={true}
            ariaLabel="rings-loading"
          />
        </div>
      ) : (
        <div className="voice-record-button" onClick={startRecording}>
          <FaMicrophone size={25}/>
        </div>
      )}
      <div style={{ display: 'none' }}>
        <AudioRecorder onRecordingComplete={confirm} recorderControls={recorderControls} audioTrackConstraints={{
              noiseSuppression: true,
              echoCancellation: true,
            }}
            downloadOnSavePress={false}/>
      </div>
      {showForm ? <ConfirmDialog /> : null}
    </div>
  );
};

export default VoiceRecorder;
