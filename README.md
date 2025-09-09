# Random Turn Chess

A chess variant where the turn order is determined by coin flips rather than alternating between players.

## Features

- **Random Turn Selection**: Each move, a coin is flipped to determine if it's Black's or White's turn
- **Full Chess Rules**: Uses the python-chess library for complete chess rule implementation
- **Multiple Game Modes**: 
  - Human vs Human (PvP)
  - Human vs Engine (White Human, Black Engine)
  - Human vs Engine (White Engine, Black Human)  
  - Engine vs Engine
- **Engine Support**: Play against chess engines with configurable wait times and pause options
- **Interactive UI**: Comprehensive menu system with engine configuration
- **Command Line Interface**: Direct game mode selection via command line arguments
- **Move History**: Track which player made each move
- **Game Status**: Real-time game state and check detection

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd randomturnchess
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## How to Play

### Interactive Menu Mode

Run the main UI:
```bash
python chess_ui.py
```

This will show a menu with the following options:
1. **Human vs Human (PvP)** - Two human players
2. **Human vs Engine (White Human, Black Engine)** - Human plays white, engine plays black
3. **Human vs Engine (White Engine, Black Human)** - Engine plays white, human plays black
4. **Engine vs Engine** - Both players are engines
5. **Configure Engine Settings** - Set up engine paths and timing
6. **Exit** - Quit the application

### Command Line Mode

You can also start games directly from the command line:

```bash
# Human vs Human
python chess_ui.py --mode pvp

# Human vs Engine (White Human, Black Engine)
python chess_ui.py --mode pv-engine-black --black-engine stockfish

# Human vs Engine (White Engine, Black Human)  
python chess_ui.py --mode pv-engine-white --white-engine stockfish

# Engine vs Engine
python chess_ui.py --mode engine-vs-engine --white-engine stockfish --black-engine stockfish

# Expectiminimax Bot vs Stockfish
python chess_ui.py --mode engine-vs-engine --white-engine expectiminimax --black-engine stockfish

# With custom timing
python chess_ui.py --mode pv-engine-black --black-engine stockfish --wait-time 2.0 --pause
```

### Quick Start Examples

Here are some ready-to-run examples:

```bash
# 1. Human vs Human (PvP) Mode
python chess_ui.py --mode pvp

# 2. Human vs Engine (Black Engine) Mode
python chess_ui.py --mode pv-engine-black --black-engine stockfish

# 3. Human vs Engine (White Engine) Mode
python chess_ui.py --mode pv-engine-white --white-engine stockfish

# 4. Engine vs Engine Mode
python chess_ui.py --mode engine-vs-engine --white-engine stockfish --black-engine stockfish

# 5. Interactive Menu Mode
python chess_ui.py

# 6. With Custom Timing
python chess_ui.py --mode pv-engine-black --black-engine stockfish --wait-time 2.0 --pause
```

All modes support the random turn mechanic where coin flips determine which player moves next, making each game unique!

### Command Line Arguments

- `--white-engine PATH` - Path to white engine executable
- `--black-engine PATH` - Path to black engine executable  
- `--wait-time SECONDS` - Engine wait time in seconds (default: 1.0)
- `--pause` - Pause after each engine move (press Enter to continue)
- `--mode MODE` - Game mode: `pvp`, `pv-engine-white`, `pv-engine-black`, `engine-vs-engine`

### In-Game Commands

- `<move>` - Make a move using UCI notation (e.g., 'e2e4', 'Nf3', 'O-O')
- `status` - Show current game status
- `history` - Display move history with player information
- `reset` - Reset the game to starting position
- `help` - Show available commands
- `quit` - Exit the game

### Game Rules

- Modified chess rules: **Game ends only when a king is captured, not on checkmate**
- Players can move into check and capture the king directly
- After each move, a coin is flipped to determine the next player
- The same player can move multiple times in a row if the coin flips favor them
- Game ends with king capture, stalemate, or other standard chess termination conditions

## Example Game Flow

```
1. White: e2e4
2. Black: e7e5  
3. White: Nf3 (coin flip favored White again)
4. Black: Nc6
5. White: Bb5 (another White turn)
...
```

## Engine Requirements

To use engine features, you need chess engines that support the UCI (Universal Chess Interface) protocol. Popular engines include:

- **Stockfish** - Free, open-source engine (recommended)
- **Leela Chess Zero** - Neural network engine
- **Komodo** - Commercial engine
- **Houdini** - Commercial engine

### Installing Stockfish (Ubuntu/Debian)
```bash
sudo apt install stockfish
```

### Installing Stockfish (macOS)
```bash
brew install stockfish
```

### Installing Stockfish (Windows)
Download from [Stockfish website](https://stockfishchess.org/download/) and extract to a folder.

## Technical Details

- Built with Python 3.6+
- Uses the `chess` library for game logic and engine communication
- Random turn selection via `random.choice()`
- Full FEN support for position representation
- Unicode board display
- UCI engine protocol support
- Configurable engine timing and pause options

## Files

- `random_turn_chess.py` - Core game logic and RandomTurnChess class
- `chess_ui.py` - Main UI with menu system and command line interface
- `expectiminimax_bot.py` - Custom expectiminimax bot for Random Turn Chess
- `requirements.txt` - Python dependencies
- `README.md` - This documentation

## License

This project is open source and available under the MIT License.
