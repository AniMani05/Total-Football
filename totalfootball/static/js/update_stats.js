// Function to get CSRF token from cookies
function getCSRFToken() {
    const name = 'csrftoken'; // Default name for CSRF cookie in Django
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return ''; // Return an empty string if not found
}

async function updatePlayerStats(playerId) {
    console.log(`Attempting to update stats for player ${playerId}...`);

    try {
        const response = await fetch(`/update-stats/${playerId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
        });

        if (response.ok) {
            const data = await response.json();
            console.log(`Player ${playerId} stats updated successfully:`, JSON.stringify(data.updated_stats, null, 2));
        } else {
            console.error(`Error updating stats for player ${playerId}: ${response.statusText}`);
        }
    } catch (error) {
        console.error(`Error fetching stats for player ${playerId}:`, error);
    }
}


// Function to schedule updates for multiple players
function schedulePlayerUpdates(playerIds) {
    console.log("Starting scheduled updates for players:", playerIds);

    // Run updates every 2 minutes (120,000 ms) for 5 iterations
    let iterations = 5;
    const interval = setInterval(() => {
        if (iterations <= 0) {
            console.log("Completed all scheduled updates.");
            clearInterval(interval); // Stop further iterations
            return;
        }

        console.log(`Test iteration ${6 - iterations}: Sending update requests for players.`);
        playerIds.forEach((playerId) => {
            updatePlayerStats(playerId); // Update stats for each player
        });

        iterations--;
    }, 2 * 60 * 1000); // 2 minutes in milliseconds
}

// List of test player IDs
const testPlayerIds = [86, 278, 1454, 217, 1100];

// Initiate testing
schedulePlayerUpdates(testPlayerIds);
