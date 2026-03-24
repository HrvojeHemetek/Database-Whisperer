import React from 'react';
import '../css/spinner.css';

const Spinner = () => {
  return (
    <div className="spinner-container">
      <div className="spinner">
        <div className="double-bounce1"></div>
        <div className="double-bounce2"></div>
      </div>
      <div className="spinner-text">Waiting for response...</div>
    </div>
  );
};

export default Spinner;