#!/usr/bin/env python3
"""
Random Turn Chess Game

A chess variant where the turn order is determined by coin flips
rather than alternating between players.
"""

import chess
import chess.engine
import random
import time
import subprocess
import sys
from typing import Optional, Tuple, List, Union


class RandomTurnChess:
    """
    A chess game where turns are determined by random coin flips.
    Each move, a coin is flipped to determine if it's black's or white's turn.
    """
    
    def __init__(self, white_engine: Optional[str] = None, black_engine: Optional[str] = None, 
                 engine_wait_time: float = 1.0, engine_pause: bool = False):
        self.board = chess.Board()
        self.move_history = []
        self.turn_history = []  # Track which player moved each turn
        self.game_over = False
        self.winner = None
        
        # Engine configuration
        self.white_engine = white_engine
        self.black_engine = black_engine
        self.engine_wait_time = engine_wait_time
        self.engine_pause = engine_pause
        
        # Engine processes
        self.white_engine_process = None
        self.black_engine_process = None
        
    def flip_coin(self) -> bool:
        """
        Flip a coin to determine the next player.
        Returns True for White, False for Black.
        """
        return random.choice([True, False])
    
    def start_engines(self):
        """
        Start the chess engines if configured.
        """
        if self.white_engine:
            try:
                self.white_engine_process = chess.engine.SimpleEngine.popen_uci(self.white_engine)
            except Exception as e:
                print(f"Warning: Could not start white engine '{self.white_engine}': {e}")
                self.white_engine = None
                
        if self.black_engine:
            try:
                self.black_engine_process = chess.engine.SimpleEngine.popen_uci(self.black_engine)
            except Exception as e:
                print(f"Warning: Could not start black engine '{self.black_engine}': {e}")
                self.black_engine = None
    
    def stop_engines(self):
        """
        Stop the chess engines if they are running.
        """
        if self.white_engine_process:
            try:
                self.white_engine_process.quit()
            except:
                pass
            self.white_engine_process = None
            
        if self.black_engine_process:
            try:
                self.black_engine_process.quit()
            except:
                pass
            self.black_engine_process = None
    
    def get_engine_move(self, is_white: bool) -> Optional[chess.Move]:
        """
        Get a move from the appropriate engine.
        Returns None if no engine is configured or if engine fails.
        """
        engine_name = self.white_engine if is_white else self.black_engine
        
        if not engine_name:
            return None
            
        try:
            # Create a fresh engine process to avoid state confusion
            with chess.engine.SimpleEngine.popen_uci(engine_name) as engine:
                # Create a fresh board copy and clear the move stack
                fresh_board = self.board.copy()
                fresh_board.clear_stack()
                
                # Get the best move from the engine using the fresh board
                result = engine.play(fresh_board, chess.engine.Limit(time=1.0))
                move = result.move
                
                # Verify the move is legal for the current player
                if not self.is_legal_move(move):
                    print(f"Engine made illegal move: {move} (expected {'White' if is_white else 'Black'} move)")
                    return None
                
                return move
        except Exception as e:
            print(f"Engine '{engine_name}' error: {e}")
            return None
    
    def get_current_player(self) -> str:
        """
        Get the current player based on the board's turn.
        Returns 'White' or 'Black'.
        """
        return 'White' if self.board.turn else 'Black'
    
    def get_legal_moves(self) -> List[chess.Move]:
        """
        Get all legal moves for the current player.
        """
        return list(self.board.legal_moves)
    
    def get_pseudo_legal_moves(self) -> List[chess.Move]:
        """
        Get all pseudo-legal moves for the current player.
        This allows moves that would normally be illegal (like moving into check).
        """
        return list(self.board.pseudo_legal_moves)
    
    def make_move(self, move: chess.Move) -> bool:
        """
        Attempt to make a move. The move must be pseudo-legal for the current player.
        Returns True if the move was successful, False otherwise.
        """
        if self.game_over:
            return False
            
        if move not in self.get_pseudo_legal_moves():
            return False
            
        # Record the move and which player made it
        self.move_history.append(move)
        self.turn_history.append(self.get_current_player())
        
        # Make the move
        self.board.push(move)
        
        # Check for game over conditions
        self._check_game_over()
        
        # Flip coin to determine next player
        if not self.game_over:
            next_player = self.flip_coin()
            # Set the turn based on the coin flip
            self.board.turn = next_player
        
        return True
    
    def get_move_for_current_player(self) -> Optional[chess.Move]:
        """
        Get a move for the current player (either from engine or return None for human input).
        Returns the move if it's an engine turn, None if it's a human turn.
        """
        is_white = self.board.turn
        engine_name = self.white_engine if is_white else self.black_engine
        
        if engine_name:
            print(f"\n{self.get_current_player()} (Engine: {engine_name}) is thinking...")
            move = self.get_engine_move(is_white)
            
            if move and self.is_legal_move(move):
                # Add wait time and/or pause
                if self.engine_wait_time > 0:
                    time.sleep(self.engine_wait_time)
                
                if self.engine_pause:
                    input("Press Enter to continue...")
                
                return move
            else:
                print(f"Engine failed or made illegal move, switching to human input for {self.get_current_player()}")
                return None
        
        return None
    
    def _check_game_over(self):
        """
        Check if the game is over and set the winner.
        Game ends only when a king is captured, not on checkmate.
        """
        # Check if a king has been captured
        if not self.board.king(chess.WHITE):
            self.game_over = True
            self.winner = 'Black'  # White king captured, Black wins
        elif not self.board.king(chess.BLACK):
            self.game_over = True
            self.winner = 'White'  # Black king captured, White wins
        elif self.board.is_stalemate():
            self.game_over = True
            self.winner = 'Draw'
        elif self.board.is_insufficient_material():
            self.game_over = True
            self.winner = 'Draw'
        elif self.board.is_seventyfive_moves():
            self.game_over = True
            self.winner = 'Draw'
        elif self.board.is_fivefold_repetition():
            self.game_over = True
            self.winner = 'Draw'
    
    def get_board_unicode(self) -> str:
        """
        Get a Unicode representation of the board.
        """
        return str(self.board)
    
    def get_fen(self) -> str:
        """
        Get the FEN representation of the current position.
        """
        return self.board.fen()
    
    def get_move_history(self) -> List[Tuple[str, chess.Move]]:
        """
        Get the move history with player information.
        Returns a list of (player, move) tuples.
        """
        return list(zip(self.turn_history, self.move_history))
    
    def is_legal_move(self, move: chess.Move) -> bool:
        """
        Check if a move is pseudo-legal for the current player.
        This allows moves that would normally be illegal (like moving into check).
        """
        return move in self.get_pseudo_legal_moves()
    
    def get_game_status(self) -> str:
        """
        Get the current game status.
        """
        if self.game_over:
            if self.winner == 'Draw':
                return "Game Over - Draw"
            else:
                return f"Game Over - {self.winner} wins!"
        else:
            current_player = self.get_current_player()
            if self.board.is_check():
                return f"{current_player} to move (CHECK!)"
            else:
                return f"{current_player} to move"
    
    def reset(self):
        """
        Reset the game to the starting position.
        """
        self.board = chess.Board()
        self.move_history = []
        self.turn_history = []
        self.game_over = False
        self.winner = None
    
    def cleanup(self):
        """
        Clean up resources (stop engines).
        """
        self.stop_engines()


def main():
    """
    Simple command-line interface for the Random Turn Chess game.
    """
    game = RandomTurnChess()
    
    print("Welcome to Random Turn Chess!")
    print("In this variant, turns are determined by coin flips.")
    print("Type 'help' for commands, 'quit' to exit.")
    print()
    
    while not game.game_over:
        print(f"\n{game.get_board_unicode()}")
        print(f"\nStatus: {game.get_game_status()}")
        
        if game.game_over:
            break
            
        legal_moves = game.get_legal_moves()
        print(f"\nLegal moves: {len(legal_moves)}")
        
        # Show first 10 legal moves for reference
        if legal_moves:
            moves_display = [str(move) for move in legal_moves[:10]]
            print(f"Sample moves: {', '.join(moves_display)}")
            if len(legal_moves) > 10:
                print(f"... and {len(legal_moves) - 10} more")
        
        command = input("\nEnter move (e.g., 'e2e4') or command: ").strip().lower()
        
        if command == 'quit':
            break
        elif command == 'help':
            print("\nCommands:")
            print("  <move>     - Make a move (e.g., 'e2e4', 'Nf3', 'O-O')")
            print("  status     - Show game status")
            print("  history    - Show move history")
            print("  reset      - Reset the game")
            print("  help       - Show this help")
            print("  quit       - Exit the game")
        elif command == 'status':
            print(f"\n{game.get_game_status()}")
        elif command == 'history':
            history = game.get_move_history()
            if history:
                print("\nMove History:")
                for i, (player, move) in enumerate(history, 1):
                    print(f"  {i}. {player}: {move}")
            else:
                print("\nNo moves made yet.")
        elif command == 'reset':
            game.reset()
            print("\nGame reset to starting position.")
        else:
            # Try to parse as a move
            try:
                move = chess.Move.from_uci(command)
                if game.make_move(move):
                    print(f"Move {move} made by {game.turn_history[-1]}")
                else:
                    print("Illegal move! Try again.")
            except ValueError:
                print("Invalid move format. Use UCI notation (e.g., 'e2e4') or a command.")
    
    if game.game_over:
        print(f"\n{game.get_board_unicode()}")
        print(f"\n{game.get_game_status()}")
        
        history = game.get_move_history()
        if history:
            print("\nFinal Move History:")
            for i, (player, move) in enumerate(history, 1):
                print(f"  {i}. {player}: {move}")


if __name__ == "__main__":
    main()
