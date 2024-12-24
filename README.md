# Welcome to TotalFootball!

**TotalFootball** is your ultimate destination for an exciting and user-friendly fantasy soccer experience. This application allows users to create, manage, and compete with fantasy soccer teams featuring players from the top European leagues.

> **Note:** The exact implementation code is not provided here, but if you're interested in discussing the project or seeing specific details, feel free to reach out to **anirudhm@andrew.cmu.edu** or **smfisher@andrew.cmu.edu**!


---

## Purpose of This Project

This project aims to provide a platform for fantasy soccer enthusiasts to:
- Create and manage personalized fantasy soccer teams.
- Compete in customizable leagues with friends or other participants.
- Stay up-to-date with real-time player statistics and performance tracking.

TotalFootball leverages real-life player performances to provide a competitive and engaging experience for users.

---

## What is Fantasy Soccer?

Fantasy soccer allows you to create and manage a team of players from the **top five European soccer leagues**:

- **Premier League**
- **Serie A**
- **La Liga**
- **Bundesliga**
- **Ligue 1**

In real-life matches, players earn points based on their performances. For example:
- **Goals Scored**
- **Assists Provided**
- **Tackles Made**
- **Saves Completed (Goalkeepers)**

Your fantasy team earns points based on these real-life performances. The goal is to accumulate more points than other teams in your league and become the season champion.

---

## How Does TotalFootball Work?

### Team Composition
Each fantasy team consists of **15 players**, including:
- **11 Starters**:
  - 1 Goalkeeper
  - 4 Defenders
  - 4 Midfielders
  - 2 Forwards
- **4 Bench Players**:
  - Substitutes to replace starters if needed.

---

### Player Selection
- Players are selected during a **snake draft**, where participants take turns choosing players.
- The draft order reverses after each round to ensure fairness.

---

### Player Performance and Scoring
Points are assigned based on real-life player performance during league matches. Key metrics include:
- **Goals Scored**: Earn points for your team.
- **Assists Provided**: Boost your score.
- **Defensive Actions**: Tackles, saves, and other defensive stats.

---

### Live Updates
- Player statistics are fetched from the **Rapid Football API**.
- **AJAX requests** are made every six hours to update player stats, ensuring you always have the latest performance data.

---

### The Waiver Wire
- Replace players on your team by picking up available players from the **waiver wire**—a pool of unselected or dropped players.
- Submit claims to add new players to your team.

---

### Winning the League
The winner is determined by the total points accumulated by their team over the season. Manage your lineup strategically to maximize your score and become the league champion!

---

## Why Choose TotalFootball?

- **Real-Time Updates**: Stay on top of player stats with frequent updates.
- **Fair Draft System**: The snake draft ensures an equitable selection process.
- **Customizable Leagues**: Play with friends or join public leagues.
- **Intuitive Interface**: Easily draft players, manage lineups, and track scores.
- **Diverse Pool of Players**: Choose from a wide range of players from the top 5 European soccer leagues.
- **Player Valuation**: Each player has a monetary value attached, adding another strategic layer to team management.

---
## Key Code Features

1. **Backend Framework**:
   - Developed using **Django**, a powerful Python web framework, for managing the backend logic, data models, and APIs.

2. **Frontend Development**:
   - Designed the user interface with **HTML/CSS** for layout and styling.
   - Implemented dynamic, interactive elements using **JavaScript**.

3. **AJAX Integration**:
   - Leveraged **AJAX** to make asynchronous requests for fetching and updating real-time player statistics from the Rapid Football API.

4. **React for Interactivity**:
   - Used **React** to build dynamic components, such as the live stats tracker and player selection interface.

5. **Database Management**:
   - Utilized Django’s ORM for database interactions, ensuring efficient and secure handling of user and team data.

6. **Real-Time Updates**:
   - Periodic API calls to fetch live player statistics every six hours, keeping data accurate and up-to-date.

---

## Acknowledgments

I would like to thank **Spencer Fisher** for his invaluable contributions and collaboration on this project. His insights and efforts were instrumental in the successful implementation of TotalFootball.

---
