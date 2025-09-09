# Random Turn Chess

A chess variant where the turn order is determined by coin flips rather than alternating between players.

## Features

- **Random Turn Selection**: Each move, a coin is flipped to determine if it's Black's or White's turn
- **Full Chess Rules**: Uses the python-chess library for complete chess rule implementation
- **Interactive CLI**: Simple command-line interface for playing
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

Run the game:
```bash
python random_turn_chess.py
```

### Commands

- `<move>` - Make a move using UCI notation (e.g., 'e2e4', 'Nf3', 'O-O')
- `status` - Show current game status
- `history` - Display move history with player information
- `reset` - Reset the game to starting position
- `help` - Show available commands
- `quit` - Exit the game

### Game Rules

- Standard chess rules apply
- After each move, a coin is flipped to determine the next player
- The same player can move multiple times in a row if the coin flips favor them
- Game ends with checkmate, stalemate, or other standard chess termination conditions

## Example Game Flow

```
1. White: e2e4
2. Black: e7e5  
3. White: Nf3 (coin flip favored White again)
4. Black: Nc6
5. White: Bb5 (another White turn)
...
```

## Technical Details

- Built with Python 3.6+
- Uses the `chess` library for game logic
- Random turn selection via `random.choice()`
- Full FEN support for position representation
- Unicode board display

## License

This project is open source and available under the MIT License.
