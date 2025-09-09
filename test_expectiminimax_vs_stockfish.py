#!/usr/bin/env python3
"""
Test script: Expectiminimax bot (depth 4) vs Stockfish in Random Turn Chess
"""

from random_turn_chess import RandomTurnChess
import chess

def test_expectiminimax_vs_stockfish():
    """Test expectiminimax bot vs stockfish in Random Turn Chess."""
    
    print("="*80)
    print("EXPECTIMINIMAX BOT (Depth 4) vs STOCKFISH - RANDOM TURN CHESS")
    print("="*80)
    
    # Create a game with expectiminimax bot vs stockfish
    game = RandomTurnChess(
        white_engine='expectiminimax', 
        black_engine='stockfish', 
        engine_wait_time=0.5
    )
    
    print("Initial position:")
    print(game.board)
    print()
    
    move_count = 0
    max_moves = 50  # Limit to prevent infinite games
    
    # Play the game
    while not game.game_over and move_count < max_moves:
        move_count += 1
        
        print(f"\n{'='*60}")
        print(f"MOVE {move_count}")
        print(f"{'='*60}")
        print(f"Current player: {game.get_current_player()}")
        
        # Get and make a move
        move = game.get_move_for_current_player()
        if move:
            game.make_move(move)
            print(f"Move made: {move}")
            print("Position after move:")
            print(game.board)
        else:
            print("No move available")
            break
        
        if game.game_over:
            print(f"\n🎉 Game over! Winner: {game.winner}")
            break
    
    if move_count >= max_moves:
        print(f"\n⚠️  Game stopped after {max_moves} moves (max limit reached)")
    
    print(f"\n{'='*80}")
    print("GAME COMPLETED")
    print(f"{'='*80}")

if __name__ == "__main__":
    test_expectiminimax_vs_stockfish()
