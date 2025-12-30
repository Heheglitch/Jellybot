Jellybot Chess Engine ♟️
Jellybot is a lightweight, efficient chess engine written in Python. It uses the python-chess library for game logic and implements several classic AI algorithms to provide a challenging experience for amateur players.

🚀 Features
Minimax Algorithm: The core decision-making engine.

Alpha-Beta Pruning: Optimizes search speed by skipping irrelevant branches of the move tree.

Quiescence Search: Prevents "The Horizon Effect" by continuing to search during piece exchanges, ensuring tactical stability.

Transposition Table: A memory system using Zobrist Hashing (via Polyglot) to store and reuse previously calculated board positions.

Piece-Square Tables (PST): Heuristic "heatmaps" that encourage the bot to control the center, develop pieces, and protect the King.

🛠️ Installation
Clone the repository:
(This projet is made in the Pycharm
1.Bash
git clone https://github.com/heheglitch/jellybot.git
cd jellybot

2.Install dependencies: Jellybot requires the python-chess library.

Bash
"pip install python-chess"

🎮 How to Play
Run the main script:

Bash
"python main.py"

Controls:
Move: Enter moves in UCI format (e.g., e2e4, g1f3).

Undo: Type undo to take back your last move and the bot's last move.

Quit: Type quit to exit the game.

🧠 Technical Details
Evaluation Function
The bot evaluates positions based on:

Material Weight: * Pawn: 100

Knight/Bishop: 320/330

Rook: 500

Queen: 900

Positional Bonus: Bonuses or penalties based on the square a piece occupies (e.g., Knights are penalized for being on the edge of the board).

Search Depth
The default search depth is set to 3.

Depth 2: Instant moves, beginner level.

Depth 3: Balanced speed and strength.

Depth 4: Stronger play, but requires more processing time in Python.

📜 License
This project is open-source and available under the MIT License.
