// static/js/App.js
/*import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import PlayerList from './components/PlayerList';
import Field from './components/Field';
import './styles.css';

const App = () => {
  const [selectedPlayers, setSelectedPlayers] = useState({});
  const players = [
    { id: 1, name: "Thibaut Courtois", team: "Real Madrid", position: "GK" },
    { id: 2, name: "Marc-Andre ter Stegen", team: "Barcelona", position: "GK" },
    { id: 3, name: "Keylor Navas", team: "PSG", position: "GK" },
    { id: 4, name: "Manuel Neuer", team: "Bayern Munich", position: "GK" },
    { id: 5, name: "Jordi Alba", team: "Inter Miami", position: "DEF" },
    { id: 6, name: "Achraf Hakimi", team: "PSG", position: "DEF" },
    { id: 7, name: "David Alaba", team: "Real Madrid", position: "DEF" },
    { id: 8, name: "Mats Hummels", team: "Borussia Dortmund", position: "DEF" },
    { id: 9, name: "Kalidou Koulibaly", team: "Al Hilal", position: "DEF" },
    { id: 10, name: "Ben Chilwell", team: "Chelsea", position: "DEF" },
    { id: 11, name: "Federico Valverde", team: "Real Madrid", position: "MID" },
    { id: 12, name: "Mason Mount", team: "Manchester United", position: "MID" },
    { id: 13, name: "Phil Foden", team: "Manchester City", position: "MID" },
    { id: 14, name: "Serge Gnabry", team: "Bayern Munich", position: "MID" },
    { id: 15, name: "Bernardo Silva", team: "Manchester City", position: "MID" },
    { id: 16, name: "Rodri", team: "Manchester City", position: "MID" },
    { id: 17, name: "Lautaro Martinez", team: "Inter Milan", position: "FWD" },
    { id: 18, name: "Victor Osimhen", team: "Napoli", position: "FWD" },
    { id: 19, name: "Paulo Dybala", team: "AS Roma", position: "FWD" },
    { id: 20, name: "Gabriel Jesus", team: "Arsenal", position: "FWD" },
    { id: 21, name: "Rafael Leao", team: "AC Milan", position: "FWD" },
    { id: 22, name: "Antoine Griezmann", team: "Atletico Madrid", position: "FWD" },
    { id: 23, name: "Mohamed Salah", team: "Liverpool", position: "FWD" },
    { id: 24, name: "Marcus Rashford", team: "Manchester United", position: "FWD" },
  ];

  const selectPlayer = (position, player) => {
    setSelectedPlayers({ ...selectedPlayers, [position]: player });
  };

  return (
    <div className="app">
      <PlayerList players={players} selectPlayer={selectPlayer} />
      <Field selectedPlayers={selectedPlayers} selectPlayer={selectPlayer} />
    </div>
  );
};

ReactDOM.render(<App />, document.getElementById('root'));*/

import React from 'react';
import ReactDOM from 'react-dom';

const App = () => {
  return (
    <h1>Hello from React</h1>
  );
};

ReactDOM.render(<App />, document.getElementById('root'));
