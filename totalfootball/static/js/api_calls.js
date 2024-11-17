// JavaScript to handle dynamic behavior in the Django application

// Fetch live player stats
function fetchPlayerStats(playerIds) {
    // Show loading indicator
    document.getElementById('loading').style.display = 'block';

    fetch('/get-live-player-stats/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(), // Ensure CSRF token is included
        },
        body: JSON.stringify({ player_ids: playerIds }),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then((data) => {
            updatePlayerStatsUI(data);
        })
        .catch((error) => {
            console.error('Error fetching player stats:', error);
        })
        .finally(() => {
            // Hide loading indicator
            document.getElementById('loading').style.display = 'none';
        });
}

// Update the UI with fetched player stats
function updatePlayerStatsUI(playerStats) {
    for (const [playerId, stats] of Object.entries(playerStats)) {
        const playerRow = document.getElementById(`player-${playerId}`);
        if (playerRow) {
            playerRow.querySelector('.goals').textContent = stats.goals || 0;
            playerRow.querySelector('.assists').textContent = stats.assists || 0;
            playerRow.querySelector('.matches-played').textContent = stats.matches_played || 0;
            playerRow.querySelector('.points').textContent = stats.points || 0;
        }
    }
}

// Utility function to get CSRF token from cookies
function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return '';
}

// Example: Fetch stats for the current team when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const playerIds = Array.from(document.querySelectorAll('.player-row')).map((row) =>
        row.getAttribute('data-player-id')
    );
    if (playerIds.length > 0) {
        fetchPlayerStats(playerIds);
    }
});
