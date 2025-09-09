#!/usr/bin/env python3
"""
Expectiminimax Bot for Random Turn Chess

A custom chess engine that uses the expectiminimax algorithm to handle
the random turn mechanic in Random Turn Chess.
"""

import chess
import chess.engine
import math
from typing import Optional, List, Tuple
import sys


class ExpectiminimaxBot:
    """
    A chess bot that uses the expectiminimax algorithm for Random Turn Chess.
    
    The algorithm handles the random turn mechanic by considering both possible
    outcomes of the coin flip (current player or opponent gets the next turn)
    and taking the weighted average of the expected values.
    """
    
    def __init__(self, stockfish_path: str = "stockfish", depth: int = 3, debug: bool = False):
        """
        Initialize the expectiminimax bot.
        
        Args:
            stockfish_path: Path to Stockfish executable for evaluation
            depth: Search depth for the expectiminimax algorithm
            debug: Whether to print debug output
        """
        self.stockfish_path = stockfish_path
        self.depth = depth
        self.debug = debug
        self.stockfish_engine = None
        self.infinity = 1000000  # Large number for checkmate/king capture
        
    def start_engine(self):
        """Start the Stockfish engine for position evaluation."""
        try:
            self.stockfish_engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
        except Exception as e:
            print(f"Warning: Could not start Stockfish engine: {e}")
            self.stockfish_engine = None
    
    def stop_engine(self):
        """Stop the Stockfish engine."""
        if self.stockfish_engine:
            try:
                self.stockfish_engine.quit()
            except:
                pass
            self.stockfish_engine = None
    
    def evaluate_position(self, board: chess.Board) -> float:
        """
        Evaluate a position using Stockfish.
        
        Args:
            board: The chess position to evaluate
            
        Returns:
            Evaluation score from White's perspective (positive = White better)
        """
        if not self.stockfish_engine:
            # Fallback to simple material count if no engine
            return self._simple_evaluation(board)
        
        try:
            # Get Stockfish evaluation
            info = self.stockfish_engine.analyse(board, chess.engine.Limit(depth=1))
            
            # Extract score from info
            if 'score' in info and info['score'] is not None:
                score = info['score']
                if score.is_mate():
                    # Convert mate scores to large numbers
                    mate_score = score.mate()
                    if mate_score > 0:
                        return self.infinity - mate_score  # White winning
                    else:
                        return -self.infinity - mate_score  # Black winning
                else:
                    # Convert centipawns to a reasonable scale
                    return score.relative.score() / 100.0
            else:
                return self._simple_evaluation(board)
                
        except Exception as e:
            if self.debug:
                print(f"Engine evaluation error: {e}")
            return self._simple_evaluation(board)
    
    def _simple_evaluation(self, board: chess.Board) -> float:
        """
        Simple material-based evaluation as fallback.
        
        Args:
            board: The chess position to evaluate
            
        Returns:
            Material count from White's perspective
        """
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 100
        }
        
        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = piece_values[piece.piece_type]
                if piece.color == chess.WHITE:
                    score += value
                else:
                    score -= value
        
        return score
    
    def is_king_captured(self, board: chess.Board, color: chess.Color) -> bool:
        """
        Check if a king of the given color has been captured.
        
        Args:
            board: The chess position to check
            color: The color to check (chess.WHITE or chess.BLACK)
            
        Returns:
            True if the king has been captured, False otherwise
        """
        return board.king(color) is None
    
    def move_captures_king(self, board: chess.Board, move: chess.Move, opponent_color: chess.Color) -> bool:
        """
        Check if a move captures the opponent's king.
        
        Args:
            board: The chess position
            move: The move to check
            opponent_color: The color of the opponent's king
            
        Returns:
            True if the move captures the opponent's king, False otherwise
        """
        captured_piece = board.piece_at(move.to_square)
        return captured_piece and captured_piece.piece_type == chess.KING and captured_piece.color == opponent_color
    
    def get_pseudo_legal_moves(self, board: chess.Board) -> List[chess.Move]:
        """
        Get all pseudo-legal moves for the current player.
        In Random Turn Chess, we use pseudo-legal moves since the game only ends on king capture.
        
        Args:
            board: The chess position
            
        Returns:
            List of pseudo-legal moves
        """
        return list(board.pseudo_legal_moves)
    
    def expectiminimax(self, board: chess.Board, depth: int, is_maximizing: bool, indent: str = "") -> float:
        """
        The core expectiminimax algorithm.
        
        Args:
            board: Current chess position
            depth: Remaining search depth
            is_maximizing: True if current player is maximizer (White), False if minimizer (Black)
            indent: Indentation string for debug output
            
        Returns:
            Expected value of the position
        """
        # Check for king capture (immediate win/loss) - this takes priority over everything
        if is_maximizing and self.is_king_captured(board, chess.BLACK):
            if self.debug:
                print(f"{indent}Depth {depth}: Black king captured! White wins (+∞)")
            return self.infinity  # White wins
        elif not is_maximizing and self.is_king_captured(board, chess.WHITE):
            if self.debug:
                print(f"{indent}Depth {depth}: White king captured! Black wins (-∞)")
            return -self.infinity  # Black wins
        
        # Terminal conditions
        if depth == 0:
            eval_score = self.evaluate_position(board)
            if self.debug:
                print(f"{indent}Depth {depth}: Terminal evaluation = {eval_score:.2f}")
            return eval_score
        
        # Get all possible moves
        moves = self.get_pseudo_legal_moves(board)
        if not moves:
            # No moves available (stalemate or similar)
            if self.debug:
                print(f"{indent}Depth {depth}: No moves available (stalemate) = 0.0")
            return 0
        
        if self.debug:
            print(f"{indent}Depth {depth}: Evaluating {len(moves)} moves for {'White' if is_maximizing else 'Black'}")
        
        # Determine opponent color
        opponent_color = chess.BLACK if is_maximizing else chess.WHITE
        
        # First, check if any move captures the opponent's king (immediate win)
        king_capture_moves = []
        for move in moves:
            if self.move_captures_king(board, move, opponent_color):
                king_capture_moves.append(move)
        
        if king_capture_moves:
            if self.debug:
                print(f"{indent}Found {len(king_capture_moves)} king capture moves: {king_capture_moves}")
            return self.infinity if is_maximizing else -self.infinity
        
        # Calculate expected value considering random turn mechanic
        total_value = 0
        
        for i, move in enumerate(moves):
            if self.debug:
                print(f"{indent}  Move {i+1}: {move.uci()}")
            
            # Create a fresh board copy for this move evaluation
            board_copy = board.copy()
            board_copy.push(move)
            
            # Calculate value for this move considering both possible outcomes
            # of the coin flip (50-50 probability each)
            
            # Case 1: Coin flip gives turn back to original player (50% probability)
            # Create a board copy with the original player's turn
            board_same_player = board_copy.copy()
            board_same_player.turn = board.turn  # Set turn back to original player
            board_same_player.clear_stack()  # Clear stack for Stockfish
            
            if is_maximizing:
                # Original player is maximizer, so they would maximize
                value_if_same_player = self.expectiminimax(board_same_player, depth - 1, True, indent + "    ")
            else:
                # Original player is minimizer, so they would minimize
                value_if_same_player = self.expectiminimax(board_same_player, depth - 1, False, indent + "    ")
            
            # Case 2: Coin flip keeps turn with current player (opponent) (50% probability)
            # Board copy already has opponent's turn, just clear the stack
            board_opponent = board_copy.copy()
            board_opponent.clear_stack()  # Clear stack for Stockfish
            
            if is_maximizing:
                # Opponent is minimizer, so they would minimize
                value_if_opponent = self.expectiminimax(board_opponent, depth - 1, False, indent + "    ")
            else:
                # Opponent is maximizer, so they would maximize
                value_if_opponent = self.expectiminimax(board_opponent, depth - 1, True, indent + "    ")
            
            # Expected value is the weighted average (50-50 in this case)
            expected_value = 0.5 * value_if_same_player + 0.5 * value_if_opponent
            
            if self.debug:
                print(f"{indent}    Same player: {value_if_same_player:.2f}, Opponent: {value_if_opponent:.2f} → Expected: {expected_value:.2f}")
            
            total_value += expected_value
        
        # Return average expected value across all moves
        avg_value = total_value / len(moves)
        if self.debug:
            print(f"{indent}Depth {depth}: Average expected value = {avg_value:.2f}")
        return avg_value
    
    def get_best_move(self, board: chess.Board) -> Optional[chess.Move]:
        """
        Get the best move using expectiminimax algorithm.
        
        Args:
            board: Current chess position
            
        Returns:
            Best move found, or None if no moves available
        """
        moves = self.get_pseudo_legal_moves(board)
        if not moves:
            return None
        
        is_maximizing = board.turn == chess.WHITE
        best_move = None
        best_value = -self.infinity if is_maximizing else self.infinity
        
        if self.debug:
            print(f"\n{'='*60}")
            print(f"EXPECTIMINIMAX ANALYSIS - {'White' if is_maximizing else 'Black'} to move")
            print(f"Search depth: {self.depth}")
            print(f"{'='*60}")
        
        move_scores = []
        
        for i, move in enumerate(moves):
            if self.debug and i % 5 == 0:  # Show progress every 5 moves
                print(f"    Evaluating move {i+1}/{len(moves)}: {move.uci()}")
            
            # Create a fresh board copy for this move evaluation
            board_copy = board.copy()
            board_copy.push(move)
            
            # Calculate expected value for this move considering both possible outcomes
            # of the coin flip (50-50 probability each)
            
            # Case 1: Coin flip gives turn back to original player (50% probability)
            # Create a board copy with the original player's turn
            board_same_player = board_copy.copy()
            board_same_player.turn = board.turn  # Set turn back to original player
            board_same_player.clear_stack()  # Clear stack for Stockfish
            
            if is_maximizing:
                # Original player is maximizer, so they would maximize
                value_if_same_player = self.expectiminimax(board_same_player, self.depth - 1, True, "    ")
            else:
                # Original player is minimizer, so they would minimize
                value_if_same_player = self.expectiminimax(board_same_player, self.depth - 1, False, "    ")
            
            # Case 2: Coin flip keeps turn with current player (opponent) (50% probability)
            # Board copy already has opponent's turn, just clear the stack
            board_opponent = board_copy.copy()
            board_opponent.clear_stack()  # Clear stack for Stockfish
            
            if is_maximizing:
                # Opponent is minimizer, so they would minimize
                value_if_opponent = self.expectiminimax(board_opponent, self.depth - 1, False, "    ")
            else:
                # Opponent is maximizer, so they would maximize
                value_if_opponent = self.expectiminimax(board_opponent, self.depth - 1, True, "    ")
            
            # Expected value is the weighted average (50-50)
            expected_value = 0.5 * value_if_same_player + 0.5 * value_if_opponent
            
            # Store move info for sorting
            move_info = {
                'move': move,
                'expected_value': expected_value,
                'value_if_same_player': value_if_same_player,
                'value_if_opponent': value_if_opponent
            }
            move_scores.append(move_info)
            
            if self.debug:
                print(f"Move {i+1:2d}: {move.uci():5s} | "
                      f"Same player: {value_if_same_player:8.2f} | "
                      f"Opponent: {value_if_opponent:8.2f} | "
                      f"Expected: {expected_value:8.2f}")
            
            # Update best move
            if is_maximizing:
                if expected_value > best_value:
                    best_value = expected_value
                    best_move = move
            else:
                if expected_value < best_value:
                    best_value = expected_value
                    best_move = move
        
        # Sort moves by expected value for display
        move_scores.sort(key=lambda x: x['expected_value'], reverse=is_maximizing)
        
        if self.debug:
            print(f"\n{'='*60}")
            print("MOVE RANKING (sorted by expected value):")
            print(f"{'='*60}")
            for i, move_info in enumerate(move_scores):
                marker = " <-- BEST" if move_info['move'] == best_move else ""
                print(f"{i+1:2d}. {move_info['move'].uci():5s} | "
                      f"Expected: {move_info['expected_value']:8.2f}{marker}")
            
            print(f"\nSelected move: {best_move.uci() if best_move else 'None'}")
            print(f"Expected value: {best_value:.2f}")
            print(f"{'='*60}\n")
        
        return best_move
    
    def play(self, board: chess.Board, limit: chess.engine.Limit) -> chess.engine.PlayResult:
        """
        Play a move using the expectiminimax algorithm.
        
        Args:
            board: Current chess position
            limit: Time/depth limit (not used in this implementation)
            
        Returns:
            PlayResult with the chosen move
        """
        move = self.get_best_move(board)
        if move is None:
            # No moves available, return a null move
            move = chess.Move.null()
        
        return chess.engine.PlayResult(move=move, ponder=None)


def main():
    """
    Test the expectiminimax bot.
    """
    bot = ExpectiminimaxBot(depth=2, debug=True)  # Enable debug for testing
    bot.start_engine()
    
    try:
        # Test with a simple position
        board = chess.Board()
        print("Initial position:")
        print(board)
        
        move = bot.get_best_move(board)
        print(f"\nBest move: {move}")
        
        if move:
            board.push(move)
            print("\nAfter move:")
            print(board)
    
    finally:
        bot.stop_engine()


if __name__ == "__main__":
    main()
