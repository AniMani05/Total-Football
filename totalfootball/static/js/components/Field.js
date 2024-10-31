// static/js/components/Field.js
import React from 'react';

const positions = [
  { name: 'GK', top: '80%', left: '45%' },
  { name: 'DEF1', top: '60%', left: '30%' },
  { name: 'DEF2', top: '60%', left: '45%' },
  { name: 'DEF3', top: '60%', left: '60%' },
  { name: 'MID1', top: '40%', left: '25%' },
  { name: 'MID2', top: '40%', left: '45%' },
  { name: 'MID3', top: '40%', left: '65%' },
  { name: 'FWD1', top: '20%', left: '35%' },
  { name: 'FWD2', top: '20%', left: '55%' },
];

const Field = ({ selectedPlayers, selectPlayer }) => {
  return (
    <div className="field">
      {positions.map((pos) => (
        <div
          key={pos.name}
          className="position"
          style={{ top: pos.top, left: pos.left }}
          onClick={() => selectPlayer(pos.name, null)}
        >
          {selectedPlayers[pos.name] ? (
            <div className="player-box">
              {selectedPlayers[pos.name].name} ({selectedPlayers[pos.name].team})
            </div>
          ) : (
            <div className="placeholder">Select {pos.name}</div>
          )}
        </div>
      ))}
    </div>
  );
};

export default Field;
