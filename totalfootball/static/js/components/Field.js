// Field.js
import React from 'react';

const positions = [
    { name: 'GK', top: '80%', left: '45%', positionType: 'GK' },
    { name: 'DEF1', top: '65%', left: '20%', positionType: 'DEF' },
    { name: 'DEF2', top: '65%', left: '35%', positionType: 'DEF' },
    { name: 'DEF3', top: '65%', left: '55%', positionType: 'DEF' },
    { name: 'DEF4', top: '65%', left: '70%', positionType: 'DEF' },
    { name: 'MID1', top: '50%', left: '30%', positionType: 'MID' },
    { name: 'MID2', top: '50%', left: '45%', positionType: 'MID' },
    { name: 'MID3', top: '50%', left: '60%', positionType: 'MID' },
    { name: 'FWD1', top: '35%', left: '30%', positionType: 'FWD' },
    { name: 'FWD2', top: '35%', left: '45%', positionType: 'FWD' },
    { name: 'FWD3', top: '35%', left: '60%', positionType: 'FWD' },
  ];

const Field = ({ selectedPlayers, selectPosition }) => {
  return (
    <div className="field">
      {positions.map((pos) => (
        <div
          key={pos.name}
          className="position"
          style={{ top: pos.top, left: pos.left }}
          onClick={() => selectPosition(pos)}
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
