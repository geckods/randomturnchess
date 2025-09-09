#!/usr/bin/env python3
"""
Test script for the Expectiminimax bot in Random Turn Chess
"""

from random_turn_chess import RandomTurnChess
import chess

def test_expectiminimax_bot():
    """Test the expectiminimax bot in a Random Turn Chess game."""
    
    print("="*60)
    print("TESTING EXPECTIMINIMAX BOT IN RANDOM TURN CHESS")
    print("="*60)
    
    # Create a game with expectiminimax bots
    game = RandomTurnChess(
        white_engine='expectiminimax', 
        black_engine='expectiminimax', 
        engine_wait_time=0.1
    )
    
    print("Initial position:")
    print(game.board)
    print()
    
    # Play a few moves to see the bot in action
    for i in range(5):  # Play 5 moves
        print(f"\n{'='*40}")
        print(f"MOVE {i+1}")
        print(f"{'='*40}")
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
    
    print(f"\n{'='*60}")
    print("TEST COMPLETED")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_expectiminimax_bot()
