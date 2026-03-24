import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../css/sidebar.css';
import { Checkmark } from 'react-checkmark';
import {ThreeDots} from 'react-loader-spinner';

function Sidebar({onChangeDelete}) {
  const [connectedToPG, setconnectedToPG] = useState(false);
  const [connectedToOracle, setconnectedToOracle] = useState(false);
  const [loadingPG, setLoadingPG] = useState(false);
  const [loadingOracle, setloadingOracle] = useState(false);

  useEffect(() => {
    onPageLoad()
  }, [])

  const onPageLoad = () => {
    setLoadingPG(true);
    axios.post('http://localhost:8000', 
      {
        'type': 'postgres'
      }, 
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }).then(function (response) {
        setLoadingPG(false);
        setconnectedToPG(true);
        console.log(response)
      })
      .catch(function (error) {
        console.log(error);
      });
  }

  const sendPostRequest = (endpoint, type) => {
    onChangeDelete(true)
    if (type === 'postgres') {
      setconnectedToPG(false);
      setLoadingPG(true);
    }
    else if (type === 'oracle') {
      setconnectedToOracle(false);
      setloadingOracle(true);
    }
    const {data} = axios.post('http://localhost:8000//' + endpoint, 
      {
        'type': type
      },
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }).then(function (response) {
        if (type === 'postgres') {
          setconnectedToOracle(false);
          setconnectedToPG(true);
          setLoadingPG(false);
        }
        else if (type === 'oracle') {
          setconnectedToPG(false);
          setconnectedToOracle(true);
          setloadingOracle(false);
        }
        console.log(response);
      })
      .catch(function (error) {
        console.log(error);
      });
  };

  return (
    <div className="sidebar">
      <h1>Odaberite bazu za povezivanje</h1>
      <a className="sidebar-item" onClick={() => sendPostRequest('db_connect', 'postgres')}>
        Banka (Postgres)
        {connectedToPG ? <Checkmark size='medium'/> : <ThreeDots
                                                          visible={loadingPG}
                                                          height="30"
                                                          width="30"
                                                          color="#4fa94d"
                                                          radius="9"
                                                          ariaLabel="three-dots-loading"
                                                          wrapperStyle={{}}
                                                          wrapperClass=""
        />}
      </a>
      <a className="sidebar-item" onClick={() => sendPostRequest('db_connect', 'oracle')}>
        ESG (OracleDB)
        {connectedToOracle ? <Checkmark size='medium'/> : <ThreeDots
                                                          visible={loadingOracle}
                                                          height="30"
                                                          width="30"
                                                          color="#4fa94d"
                                                          radius="9"
                                                          ariaLabel="three-dots-loading"
                                                          wrapperStyle={{}}
                                                          wrapperClass=""
        />}
      </a>
    </div>
  );
};

export default Sidebar;
