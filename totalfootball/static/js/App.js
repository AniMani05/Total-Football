import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import PlayerList from './components/Playerlist';
import Field from './components/Field';
import '../Players.css';

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const App = () => {
  const [selectedPlayers, setSelectedPlayers] = useState({});
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [captain, setCaptain] = useState(null);
  const [isLineupComplete, setIsLineupComplete] = useState(false);

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

  // Filter out players already selected
  const availablePlayers = players.filter(
    player => !Object.values(selectedPlayers).some(selectedPlayer => selectedPlayer.id === player.id)
  );

  const handleSelectPosition = (position) => {
    setSelectedPosition(position);
  };

  const handleSelectPlayer = (player) => {
    if (selectedPosition && player.position === selectedPosition.positionType) {
      const updatedPlayers = { ...selectedPlayers, [selectedPosition.name]: player };
      setSelectedPlayers(updatedPlayers);
      setSelectedPosition(null);

      if (Object.keys(updatedPlayers).length === 11) {
        console.log("All positions filled, enabling captain selection.");
        setIsLineupComplete(true);
      }
    } else {
      alert(`Select a player with position: ${selectedPosition.positionType}`);
    }
  };

  const handleCaptainSelection = (event) => {
    const selectedPlayerId = parseInt(event.target.value);
    const selectedCaptain = Object.values(selectedPlayers).find(player => player.id === selectedPlayerId);
    setCaptain(selectedCaptain);
  };

  const handleSubmitLineup = async () => {
    if (isLineupComplete && captain) {
      try {
        const response = await fetch('/select-lineup/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: JSON.stringify({
            players: Object.values(selectedPlayers).map(player => player.id),
            captain_id: captain.id,
          }),
        });

        const result = await response.json();
        if (response.ok) {
          alert(result.message);
          console.log("Lineup submitted:", selectedPlayers, "Captain:", captain);

          setSelectedPlayers({});
          setCaptain(null);
          setIsLineupComplete(false);
          setSelectedPosition(null);
        } else {
          alert(result.error || 'Failed to save lineup');
        }
      } catch (error) {
        console.error("Error submitting lineup:", error);
        alert("There was an error submitting your lineup.");
      }
    } else {
      alert("Please select all 11 players and choose a captain.");
    }
  };

  return (
    <div className="app">
      <PlayerList
        players={availablePlayers}  // Pass only unselected players
        selectPlayer={handleSelectPlayer}
        selectedPosition={selectedPosition}
      />
      <Field
        selectedPlayers={selectedPlayers}
        selectPosition={handleSelectPosition}
      />

      {isLineupComplete && (
        <div>
          <h3>Select Your Captain:</h3>
          <select onChange={handleCaptainSelection} value={captain ? captain.id : ''}>
            <option value="" disabled>Select a captain</option>
            {Object.values(selectedPlayers).map(player => (
              <option key={player.id} value={player.id}>
                {player.name} ({player.team})
              </option>
            ))}
          </select>
        </div>
      )}

      <button onClick={handleSubmitLineup} disabled={!isLineupComplete || !captain}>
        Submit Lineup
      </button>
    </div>
  );
};

const root = createRoot(document.getElementById('root'));
root.render(<App />);
