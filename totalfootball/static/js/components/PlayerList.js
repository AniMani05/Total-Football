// PlayerList.js
import React from 'react';

const PlayerList = ({ players, selectPlayer, selectedPosition }) => {
  return (
    <div className="player-list">
      <h3>Available Players</h3>
      {selectedPosition ? (
        players
          .filter((player) => player.position === selectedPosition.positionType)
          .map((player) => (
            <div key={player.id} className="player" onClick={() => selectPlayer(player)}>
              <p>{player.name} ({player.team}) - {player.position}</p>
            </div>
          ))
      ) : (
        <p>Select a position on the field</p>
      )}
    </div>
  );
};

export default PlayerList;
