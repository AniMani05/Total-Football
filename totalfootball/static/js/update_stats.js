// Function to fetch all player IDs from the backend
async function fetchAllPlayerIds() {
    try {
        const response = await fetch('/get-all-player-ids/'); // Endpoint to return all player IDs
        if (response.ok) {
            const data = await response.json();
            return data.player_ids; // Assume the server sends a JSON object with `player_ids` as an array
        } else {
            console.error("Failed to fetch player IDs:", response.statusText);
        }
    } catch (error) {
        console.error("Error fetching player IDs:", error);
    }
    return []; // Return an empty array if something goes wrong
}

// Function to get CSRF token
function getCSRFToken() {
    let cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim();
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length);
        }
    }
    return "unknown";
}

// Function to update player stats via API call
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

// Function to schedule updates for multiple players indefinitely
function schedulePlayerUpdates(playerIds) {
    console.log("Starting scheduled updates for players:", playerIds);

    // Run updates every 2 minutes (120,000 ms)
    setInterval(() => {
        console.log("Sending update requests for players.");
        playerIds.forEach((playerId) => {
            updatePlayerStats(playerId); // Update stats for each player
        });
    }, 60 * 60 * 1000); // 2 minutes in milliseconds
}

// Fetch all player IDs and start the schedule
fetchAllPlayerIds().then((playerIds) => {
    if (playerIds.length > 0) {
        schedulePlayerUpdates(playerIds);
    } else {
        console.error("No player IDs found to update.");
    }
});
