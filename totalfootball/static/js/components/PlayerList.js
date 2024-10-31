// static/js/components/PlayerList.js
import React from 'react';

const PlayerList = ({ players, selectPlayer }) => {
  return (
    <div className="player-list">
      <h3>Available Players</h3>
      {players.map(player => (
        <div key={player.id} className="player" onClick={() => selectPlayer(player.position, player)}>
          <p>{player.name} ({player.team}) - {player.position}</p>
        </div>
      ))}
    </div>
  );
};

export default PlayerList;
