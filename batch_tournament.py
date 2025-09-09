#!/usr/bin/env python3
"""
Batch Tournament Script for Random Turn Chess

Runs 100 games of expectiminimax depth 3 vs stockfish in parallel,
with half the games as white and half as black, and collates statistics.
"""

import asyncio
import concurrent.futures
import time
from collections import defaultdict
from random_turn_chess import RandomTurnChess
import chess
import sys
import os
import json
from datetime import datetime

class TournamentGame:
    """Represents a single tournament game."""
    
    def __init__(self, game_id, white_engine, black_engine, max_moves=100):
        self.game_id = game_id
        self.white_engine = white_engine
        self.black_engine = black_engine
        self.max_moves = max_moves
        self.result = None
        self.moves_played = 0
        self.winner = None
        self.error = None
        self.move_history = []
        self.start_time = None
        self.end_time = None
        self.duration = 0
        
    def play_game(self):
        """Play a single game and return the result."""
        self.start_time = time.time()
        try:
            # Create game instance
            game = RandomTurnChess(
                white_engine=self.white_engine,
                black_engine=self.black_engine,
                engine_wait_time=0  # No wait time for speed
            )
            
            # Play the game
            move_count = 0
            while not game.game_over and move_count < self.max_moves:
                move = game.get_move_for_current_player()
                if move:
                    game.make_move(move)
                    move_count += 1
                    # Record move history
                    self.move_history.append({
                        'move': str(move),
                        'move_number': move_count,
                        'player': game.get_current_player(),
                        'fen': game.board.fen()
                    })
                else:
                    break
                
                if game.game_over:
                    break
            
            # Record results
            self.moves_played = move_count
            if game.game_over:
                self.winner = game.winner
                if game.winner == "White":
                    self.result = "White"
                elif game.winner == "Black":
                    self.result = "Black"
                else:
                    self.result = "Draw"
            else:
                self.result = "Timeout"
                
        except Exception as e:
            self.error = str(e)
            self.result = "Error"
        finally:
            self.end_time = time.time()
            self.duration = self.end_time - self.start_time
            
        return self
    
    def to_dict(self):
        """Convert game to dictionary for JSON serialization."""
        return {
            'game_id': self.game_id,
            'white_engine': self.white_engine,
            'black_engine': self.black_engine,
            'result': self.result,
            'winner': self.winner,
            'moves_played': self.moves_played,
            'duration': self.duration,
            'error': self.error,
            'move_history': self.move_history,
            'start_time': self.start_time,
            'end_time': self.end_time
        }

def run_single_game(args):
    """Run a single game - wrapper for multiprocessing."""
    game_id, white_engine, black_engine, max_moves = args
    game = TournamentGame(game_id, white_engine, black_engine, max_moves)
    return game.play_game()

def print_progress_bar(completed, total, start_time, width=50):
    """Print a progress bar."""
    elapsed = time.time() - start_time
    percent = completed / total
    filled = int(width * percent)
    bar = '█' * filled + '░' * (width - filled)
    
    # Calculate ETA
    if completed > 0:
        eta = (elapsed / completed) * (total - completed)
        eta_str = f"ETA: {eta:.0f}s"
    else:
        eta_str = "ETA: --"
    
    print(f"\rProgress: |{bar}| {completed}/{total} ({percent:.1%}) {elapsed:.0f}s elapsed, {eta_str}", end='', flush=True)

def run_tournament(num_games=100, max_workers=10, max_moves=100):
    """Run the tournament with parallel execution."""
    
    print(f"🏆 RANDOM TURN CHESS TOURNAMENT")
    print(f"{'='*50}")
    print(f"Expectiminimax (Depth 3) vs Stockfish")
    print(f"Total Games: {num_games}")
    print(f"Parallel Workers: {max_workers}")
    print(f"Max Moves per Game: {max_moves}")
    print(f"{'='*50}")
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"tournament_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare game configurations
    # Half games with expectiminimax as white, half as black
    games_config = []
    
    for i in range(num_games):
        if i < num_games // 2:
            # Expectiminimax as white
            games_config.append((i+1, "expectiminimax", "stockfish", max_moves))
        else:
            # Expectiminimax as black
            games_config.append((i+1, "stockfish", "expectiminimax", max_moves))
    
    # Shuffle the order to mix white/black games
    import random
    random.shuffle(games_config)
    
    print(f"Starting tournament...")
    print(f"Output directory: {output_dir}")
    start_time = time.time()
    
    # Run games in parallel
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all games
        future_to_game = {executor.submit(run_single_game, config): config[0] for config in games_config}
        
        # Collect results as they complete
        completed = 0
        for future in concurrent.futures.as_completed(future_to_game):
            game_id = future_to_game[future]
            try:
                result = future.result()
                results.append(result)
                completed += 1
                
                # Write individual game to file
                game_file = os.path.join(output_dir, f"game_{game_id:03d}.json")
                with open(game_file, 'w') as f:
                    json.dump(result.to_dict(), f, indent=2)
                
                # Progress bar
                print_progress_bar(completed, num_games, start_time)
                    
            except Exception as e:
                print(f"\nGame {game_id} failed: {e}")
                # Create a failed game result
                failed_game = TournamentGame(game_id, "expectiminimax", "stockfish", max_moves)
                failed_game.result = "Error"
                failed_game.error = str(e)
                results.append(failed_game)
                completed += 1
                
                # Write failed game to file
                game_file = os.path.join(output_dir, f"game_{game_id:03d}.json")
                with open(game_file, 'w') as f:
                    json.dump(failed_game.to_dict(), f, indent=2)
                
                print_progress_bar(completed, num_games, start_time)
    
    print()  # New line after progress bar
    end_time = time.time()
    total_time = end_time - start_time
    
    # Write summary to file
    summary_file = os.path.join(output_dir, "tournament_summary.json")
    summary_data = {
        'tournament_info': {
            'total_games': num_games,
            'max_workers': max_workers,
            'max_moves': max_moves,
            'start_time': start_time,
            'end_time': end_time,
            'total_duration': total_time
        },
        'results': [game.to_dict() for game in results]
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    print(f"Tournament data saved to: {output_dir}")
    print(f"Summary file: {summary_file}")
    
    # Analyze results
    analyze_results(results, total_time, output_dir)

def analyze_results(results, total_time, output_dir):
    """Analyze and display tournament results."""
    
    print(f"\n{'='*60}")
    print(f"TOURNAMENT RESULTS")
    print(f"{'='*60}")
    
    # Basic statistics
    total_games = len(results)
    print(f"Total Games: {total_games}")
    print(f"Total Time: {total_time:.1f} seconds")
    print(f"Average Time per Game: {total_time/total_games:.1f} seconds")
    
    # Count results
    result_counts = defaultdict(int)
    error_games = []
    move_counts = []
    duration_counts = []
    
    for game in results:
        result_counts[game.result] += 1
        if game.error:
            error_games.append(game)
        if game.moves_played > 0:
            move_counts.append(game.moves_played)
        if game.duration > 0:
            duration_counts.append(game.duration)
    
    # Display results
    print(f"\n📊 RESULT BREAKDOWN:")
    print(f"{'='*30}")
    for result, count in sorted(result_counts.items()):
        percentage = (count / total_games) * 100
        print(f"{result:12}: {count:3d} games ({percentage:5.1f}%)")
    
    # Expectiminimax performance analysis
    expectiminimax_wins = 0
    stockfish_wins = 0
    draws = 0
    errors = 0
    
    for game in results:
        if game.result == "Error":
            errors += 1
        elif game.result == "White":
            if game.white_engine == "expectiminimax":
                expectiminimax_wins += 1
            else:
                stockfish_wins += 1
        elif game.result == "Black":
            if game.black_engine == "expectiminimax":
                expectiminimax_wins += 1
            else:
                stockfish_wins += 1
        elif game.result == "Draw":
            draws += 1
    
    print(f"\n🤖 EXPECTIMINIMAX vs STOCKFISH:")
    print(f"{'='*35}")
    print(f"Expectiminimax Wins: {expectiminimax_wins:3d} ({expectiminimax_wins/total_games*100:5.1f}%)")
    print(f"Stockfish Wins:      {stockfish_wins:3d} ({stockfish_wins/total_games*100:5.1f}%)")
    print(f"Draws:               {draws:3d} ({draws/total_games*100:5.1f}%)")
    print(f"Errors:              {errors:3d} ({errors/total_games*100:5.1f}%)")
    
    # Move statistics
    if move_counts:
        avg_moves = sum(move_counts) / len(move_counts)
        min_moves = min(move_counts)
        max_moves = max(move_counts)
        print(f"\n📈 MOVE STATISTICS:")
        print(f"{'='*20}")
        print(f"Average Moves: {avg_moves:.1f}")
        print(f"Min Moves:     {min_moves}")
        print(f"Max Moves:     {max_moves}")
    
    # Duration statistics
    if duration_counts:
        avg_duration = sum(duration_counts) / len(duration_counts)
        min_duration = min(duration_counts)
        max_duration = max(duration_counts)
        print(f"\n⏱️  DURATION STATISTICS:")
        print(f"{'='*25}")
        print(f"Average Duration: {avg_duration:.1f}s")
        print(f"Min Duration:     {min_duration:.1f}s")
        print(f"Max Duration:     {max_duration:.1f}s")
    
    # Error details
    if error_games:
        print(f"\n❌ ERRORS ({len(error_games)} games):")
        print(f"{'='*25}")
        for game in error_games[:5]:  # Show first 5 errors
            print(f"Game {game.game_id}: {game.error}")
        if len(error_games) > 5:
            print(f"... and {len(error_games) - 5} more errors")
    
    # Performance summary
    print(f"\n🏆 PERFORMANCE SUMMARY:")
    print(f"{'='*25}")
    if expectiminimax_wins > stockfish_wins:
        print(f"🎉 EXPECTIMINIMAX WINS THE TOURNAMENT!")
        print(f"   {expectiminimax_wins} - {stockfish_wins} ({expectiminimax_wins/total_games*100:.1f}% win rate)")
    elif stockfish_wins > expectiminimax_wins:
        print(f"🤖 STOCKFISH WINS THE TOURNAMENT!")
        print(f"   {stockfish_wins} - {expectiminimax_wins} ({stockfish_wins/total_games*100:.1f}% win rate)")
    else:
        print(f"🤝 TOURNAMENT ENDS IN A TIE!")
        print(f"   {expectiminimax_wins} - {stockfish_wins}")
    
    print(f"\n{'='*60}")
    
    # Write detailed summary to file
    summary_text_file = os.path.join(output_dir, "tournament_summary.txt")
    with open(summary_text_file, 'w') as f:
        f.write("RANDOM TURN CHESS TOURNAMENT RESULTS\n")
        f.write("="*50 + "\n\n")
        f.write(f"Total Games: {total_games}\n")
        f.write(f"Total Time: {total_time:.1f} seconds\n")
        f.write(f"Average Time per Game: {total_time/total_games:.1f} seconds\n\n")
        
        f.write("RESULT BREAKDOWN:\n")
        f.write("-" * 20 + "\n")
        for result, count in sorted(result_counts.items()):
            percentage = (count / total_games) * 100
            f.write(f"{result:12}: {count:3d} games ({percentage:5.1f}%)\n")
        
        f.write(f"\nEXPECTIMINIMAX vs STOCKFISH:\n")
        f.write("-" * 30 + "\n")
        f.write(f"Expectiminimax Wins: {expectiminimax_wins:3d} ({expectiminimax_wins/total_games*100:5.1f}%)\n")
        f.write(f"Stockfish Wins:      {stockfish_wins:3d} ({stockfish_wins/total_games*100:5.1f}%)\n")
        f.write(f"Draws:               {draws:3d} ({draws/total_games*100:5.1f}%)\n")
        f.write(f"Errors:              {errors:3d} ({errors/total_games*100:5.1f}%)\n")
        
        if move_counts:
            avg_moves = sum(move_counts) / len(move_counts)
            min_moves = min(move_counts)
            max_moves = max(move_counts)
            f.write(f"\nMOVE STATISTICS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Average Moves: {avg_moves:.1f}\n")
            f.write(f"Min Moves:     {min_moves}\n")
            f.write(f"Max Moves:     {max_moves}\n")
        
        if duration_counts:
            avg_duration = sum(duration_counts) / len(duration_counts)
            min_duration = min(duration_counts)
            max_duration = max(duration_counts)
            f.write(f"\nDURATION STATISTICS:\n")
            f.write("-" * 25 + "\n")
            f.write(f"Average Duration: {avg_duration:.1f}s\n")
            f.write(f"Min Duration:     {min_duration:.1f}s\n")
            f.write(f"Max Duration:     {max_duration:.1f}s\n")
        
        if error_games:
            f.write(f"\nERRORS ({len(error_games)} games):\n")
            f.write("-" * 25 + "\n")
            for game in error_games:
                f.write(f"Game {game.game_id}: {game.error}\n")
        
        f.write(f"\nPERFORMANCE SUMMARY:\n")
        f.write("-" * 25 + "\n")
        if expectiminimax_wins > stockfish_wins:
            f.write(f"EXPECTIMINIMAX WINS THE TOURNAMENT!\n")
            f.write(f"   {expectiminimax_wins} - {stockfish_wins} ({expectiminimax_wins/total_games*100:.1f}% win rate)\n")
        elif stockfish_wins > expectiminimax_wins:
            f.write(f"STOCKFISH WINS THE TOURNAMENT!\n")
            f.write(f"   {stockfish_wins} - {expectiminimax_wins} ({stockfish_wins/total_games*100:.1f}% win rate)\n")
        else:
            f.write(f"TOURNAMENT ENDS IN A TIE!\n")
            f.write(f"   {expectiminimax_wins} - {stockfish_wins}\n")
    
    print(f"Detailed summary saved to: {summary_text_file}")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Random Turn Chess tournament")
    parser.add_argument("--games", type=int, default=100, help="Number of games to play (default: 100)")
    parser.add_argument("--workers", type=int, default=10, help="Number of parallel workers (default: 10)")
    parser.add_argument("--max-moves", type=int, default=100, help="Maximum moves per game (default: 100)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.games < 1:
        print("Error: Number of games must be at least 1")
        sys.exit(1)
    
    if args.workers < 1:
        print("Error: Number of workers must be at least 1")
        sys.exit(1)
    
    if args.max_moves < 1:
        print("Error: Maximum moves must be at least 1")
        sys.exit(1)
    
    # Run tournament
    try:
        run_tournament(args.games, args.workers, args.max_moves)
    except KeyboardInterrupt:
        print("\n\nTournament interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nTournament failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
