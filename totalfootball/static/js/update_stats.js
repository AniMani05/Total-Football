// Function that fetches all the player ids we want to re-compute stats for
async function fetchAllPlayerIds() {
    try {
        const response = await fetch('/get-all-player-ids/'); // Function defined in views that returns JSON object with player ids
        if (response.ok) {
            const data = await response.json();
            return data.player_ids; 
        } else {
            console.error("Failed to fetch player IDs:", response.statusText);
        }
    } catch (error) {
        console.error("Error fetching player IDs:", error);
    }
    return []; // base case if we aren't able to collect player data
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
            // Sanity check statement
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

    // Obtain updates every 1 hour by calling updatePlayerStats
    setInterval(() => {
        playerIds.forEach((playerId) => {
            updatePlayerStats(playerId); 
        });
    }, 60 * 60 * 1000); 
}

// Fetch all player IDs and start updating every one hour
fetchAllPlayerIds().then((playerIds) => {
    if (playerIds.length > 0) {
        schedulePlayerUpdates(playerIds);
    } else {
        console.error("No player IDs found to update.");
    }
});
