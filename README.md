🏆 MTG Swiss Event Manager
A lightweight Swiss pairing and standings tracker built for Magic: The Gathering.
______________________________________________________________________________________________________________________________________________________________________________
🌟 Features

True Swiss Pairings: Pairs players based on match points and tiebreakers (OMWP/GWP).
Rematch Prevention: Ensures players don't face the same opponent twice.
Smart Reporting: Clean "Scorecard" style entry with ± buttons and automatic BYE handling.
Live Standings: Real-time leaderboard updates with 3-decimal MTR tiebreaker math.
Match History: View and edit previous round results to fix entry errors.
Data Export: Save your final standings to a CSV file for your records.
______________________________________________________________________________________________________________________________________________________________________________
🛠️ First-Time Setup (IMPORTANT)
1. Install Python
The app requires Python 3.10 or newer.
Go to python.org/downloads and click the yellow Download Python button.
CRITICAL STEP: When the installer opens, you must check the box at the bottom that says "Add Python to PATH".
If you miss this, the "Setup" and "Run" files will not work.
Click Install Now.

2. Fix "Add to PATH" (If you already installed Python)
If you click the .bat files and the window vanishes instantly or says "Python is not recognized," follow these steps:
Re-run the Python Installer you downloaded.
Choose Modify.
Click Next until you see "Advanced Options."
Check Add Python to environment variables and click Install.

3. Initialize the App
Open the app folder and double-click SETUP.bat.
This will open a black window and install the necessary libraries (Streamlit and Pandas).
Once it says "Setup Complete," you can close that window.
______________________________________________________________________________________________________________________________________________________________________________
⚔️ How to Run a Tournament
Double-click RUNMTGAPP.bat. A browser window will open automatically.

Registration: Type player names in the sidebar and hit Enter to add them quickly.

Pairings: Click "Start Tournament." Round 1 is randomized; subsequent rounds follow Swiss logic.

Scoring: Enter the game wins for each player. The app locks wins at a maximum of 2.

Finalize: Click "Finalize Round Results" and confirm the pop-up to advance the tournament.

Note: Do not refresh the browser page during a tournament, as data is stored in temporary memory. Use the Export CSV button in the Standings tab to record results!
