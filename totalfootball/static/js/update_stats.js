async function updatePlayerStats(playerId) {
    try {
        const response = await fetch(`/update-stats/${playerId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(), // Include CSRF token for Django security
            },
        });

        if (response.ok) {
            const data = await response.json();
            console.log(`Player ${playerId} stats updated:`, data);
        } else {
            console.error(`Error updating stats for player ${playerId}:`, response.statusText);
        }
    } catch (error) {
        console.error(`Error fetching stats for player ${playerId}:`, error);
    }
}

// Function to get CSRF token from cookies
function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return '';
}

// Update all players in intervals
function schedulePlayerUpdates(playerIds) {
    playerIds.forEach((playerId, index) => {
        setTimeout(() => {
            updatePlayerStats(playerId);
        }, index * 500); // Spread API calls to avoid overloading
    });
}