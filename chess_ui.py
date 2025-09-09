#!/usr/bin/env python3
"""
Random Turn Chess UI

A comprehensive user interface for the Random Turn Chess game with support for
human vs human, human vs engine, and engine vs engine gameplay.
"""

import argparse
import sys
import os
from random_turn_chess import RandomTurnChess
import chess


class ChessUI:
    """
    Main UI class for Random Turn Chess with multiple game modes.
    """
    
    def __init__(self):
        self.game = None
        self.game_mode = None
        
    def display_main_menu(self):
        """
        Display the main menu and get user selection.
        """
        print("\n" + "="*50)
        print("    RANDOM TURN CHESS - MAIN MENU")
        print("="*50)
        print("1. Human vs Human (PvP)")
        print("2. Human vs Engine (White Human, Black Engine)")
        print("3. Human vs Engine (White Engine, Black Human)")
        print("4. Engine vs Engine")
        print("5. Configure Engine Settings")
        print("6. Exit")
        print("="*50)
        
        while True:
            try:
                choice = input("Select an option (1-6): ").strip()
                if choice in ['1', '2', '3', '4', '5', '6']:
                    return int(choice)
                else:
                    print("Please enter a number between 1 and 6.")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                sys.exit(0)
            except:
                print("Invalid input. Please try again.")
    
    def configure_engine_settings(self):
        """
        Configure engine settings.
        """
        print("\n" + "="*40)
        print("    ENGINE CONFIGURATION")
        print("="*40)
        
        # Get engine paths
        print("Engine options:")
        print("1. Stockfish (default)")
        print("2. Expectiminimax bot (custom Random Turn Chess bot)")
        print("3. Custom engine path")
        print("4. None (human player)")
        
        white_choice = input("White engine choice (1-4, default 1): ").strip()
        if white_choice == "2":
            white_engine = "expectiminimax"
        elif white_choice == "3":
            white_engine = input("White engine path: ").strip()
            if not white_engine:
                white_engine = "stockfish"
        elif white_choice == "4":
            white_engine = None
        else:
            white_engine = "stockfish"
            
        black_choice = input("Black engine choice (1-4, default 1): ").strip()
        if black_choice == "2":
            black_engine = "expectiminimax"
        elif black_choice == "3":
            black_engine = input("Black engine path: ").strip()
            if not black_engine:
                black_engine = "stockfish"
        elif black_choice == "4":
            black_engine = None
        else:
            black_engine = "stockfish"
        
        # Get wait time
        while True:
            try:
                wait_time = input("Engine wait time in seconds (default 1.0): ").strip()
                if not wait_time:
                    wait_time = 1.0
                else:
                    wait_time = float(wait_time)
                if wait_time >= 0:
                    break
                else:
                    print("Wait time must be non-negative.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get pause setting
        pause_input = input("Pause after each engine move? (y/n, default n): ").strip().lower()
        pause = pause_input in ['y', 'yes', '1', 'true']
        
        return white_engine, black_engine, wait_time, pause
    
    def start_game(self, white_engine=None, black_engine=None, wait_time=1.0, pause=False):
        """
        Start a new game with the specified configuration.
        """
        self.game = RandomTurnChess(
            white_engine=white_engine,
            black_engine=black_engine,
            engine_wait_time=wait_time,
            engine_pause=pause
        )
        
        # Start engines if configured
        if white_engine or black_engine:
            self.game.start_engines()
        
        print(f"\nStarting new game...")
        if white_engine:
            print(f"White: Engine ({white_engine})")
        else:
            print("White: Human")
            
        if black_engine:
            print(f"Black: Engine ({black_engine})")
        else:
            print("Black: Human")
        
        print(f"Engine wait time: {wait_time}s")
        print(f"Engine pause: {'Yes' if pause else 'No'}")
        print()
    
    def play_game(self):
        """
        Main game loop.
        """
        if not self.game:
            print("No game started!")
            return
        
        try:
            while not self.game.game_over:
                print(f"\n{self.game.get_board_unicode()}")
                print(f"\nStatus: {self.game.get_game_status()}")
                
                # Check if current player is an engine
                engine_move = self.game.get_move_for_current_player()
                
                if engine_move:
                    # Engine move
                    if self.game.make_move(engine_move):
                        print(f"Engine played: {engine_move}")
                    else:
                        print("Engine made an illegal move!")
                        break
                else:
                    # Human move
                    pseudo_legal_moves = self.game.get_pseudo_legal_moves()
                    print(f"\nPseudo-legal moves: {len(pseudo_legal_moves)}")
                    
                    # Show first 10 pseudo-legal moves for reference
                    if pseudo_legal_moves:
                        moves_display = [str(move) for move in pseudo_legal_moves[:10]]
                        print(f"Sample moves: {', '.join(moves_display)}")
                        if len(pseudo_legal_moves) > 10:
                            print(f"... and {len(pseudo_legal_moves) - 10} more")
                    
                    while True:
                        command = input(f"\n{self.game.get_current_player()} to move: ").strip()
                        
                        if command.lower() == 'quit':
                            return
                        elif command.lower() == 'help':
                            self.show_help()
                            continue
                        elif command.lower() == 'status':
                            print(f"\n{self.game.get_game_status()}")
                            continue
                        elif command.lower() == 'history':
                            self.show_history()
                            continue
                        elif command.lower() == 'reset':
                            self.game.reset()
                            print("\nGame reset to starting position.")
                            return
                        else:
                            # Try to parse as a move
                            try:
                                move = chess.Move.from_uci(command)
                                if self.game.make_move(move):
                                    print(f"Move {move} made by {self.game.turn_history[-1]}")
                                    break
                                else:
                                    print("Illegal move! Try again.")
                            except ValueError:
                                print("Invalid move format. Use UCI notation (e.g., 'e2e4') or a command.")
            
            # Game over
            print(f"\n{self.game.get_board_unicode()}")
            print(f"\n{self.game.get_game_status()}")
            self.show_history()
            
        except KeyboardInterrupt:
            print("\nGame interrupted.")
        finally:
            if self.game:
                self.game.cleanup()
    
    def show_help(self):
        """
        Show help information.
        """
        print("\nCommands:")
        print("  <move>     - Make a move (e.g., 'e2e4', 'Nf3', 'O-O')")
        print("  status     - Show game status")
        print("  history    - Show move history")
        print("  reset      - Reset the game")
        print("  help       - Show this help")
        print("  quit       - Exit the game")
    
    def show_history(self):
        """
        Show move history.
        """
        history = self.game.get_move_history()
        if history:
            print("\nMove History:")
            for i, (player, move) in enumerate(history, 1):
                print(f"  {i}. {player}: {move}")
        else:
            print("\nNo moves made yet.")
    
    def run(self):
        """
        Main UI loop.
        """
        print("Welcome to Random Turn Chess!")
        print("In this variant, turns are determined by coin flips.")
        
        # Default engine settings
        white_engine = None
        black_engine = None
        wait_time = 1.0
        pause = False
        
        while True:
            choice = self.display_main_menu()
            
            if choice == 1:
                # Human vs Human
                self.start_game()
                self.play_game()
                
            elif choice == 2:
                # Human vs Engine (White Human, Black Engine)
                if not black_engine:
                    print("\nNo black engine configured. Please configure engine settings first.")
                    continue
                self.start_game(black_engine=black_engine, wait_time=wait_time, pause=pause)
                self.play_game()
                
            elif choice == 3:
                # Human vs Engine (White Engine, Black Human)
                if not white_engine:
                    print("\nNo white engine configured. Please configure engine settings first.")
                    continue
                self.start_game(white_engine=white_engine, wait_time=wait_time, pause=pause)
                self.play_game()
                
            elif choice == 4:
                # Engine vs Engine
                if not white_engine or not black_engine:
                    print("\nBoth engines must be configured for engine vs engine mode.")
                    continue
                self.start_game(white_engine=white_engine, black_engine=black_engine, 
                              wait_time=wait_time, pause=pause)
                self.play_game()
                
            elif choice == 5:
                # Configure Engine Settings
                white_engine, black_engine, wait_time, pause = self.configure_engine_settings()
                print("\nEngine settings updated!")
                
            elif choice == 6:
                # Exit
                print("\nGoodbye!")
                break


def main():
    """
    Main entry point with command line argument support.
    """
    parser = argparse.ArgumentParser(description='Random Turn Chess with Engine Support')
    parser.add_argument('--white-engine', type=str, help='Path to white engine executable (or "expectiminimax" for custom bot)')
    parser.add_argument('--black-engine', type=str, help='Path to black engine executable (or "expectiminimax" for custom bot)')
    parser.add_argument('--wait-time', type=float, default=1.0, help='Engine wait time in seconds (default: 1.0)')
    parser.add_argument('--pause', action='store_true', help='Pause after each engine move')
    parser.add_argument('--mode', type=str, choices=['pvp', 'pv-engine-white', 'pv-engine-black', 'engine-vs-engine'],
                       help='Game mode (overrides menu selection)')
    
    args = parser.parse_args()
    
    ui = ChessUI()
    
    # If mode is specified via command line, start game directly
    if args.mode:
        if args.mode == 'pvp':
            ui.start_game()
        elif args.mode == 'pv-engine-white':
            if not args.white_engine:
                print("Error: --white-engine required for pv-engine-white mode")
                sys.exit(1)
            ui.start_game(white_engine=args.white_engine, wait_time=args.wait_time, pause=args.pause)
        elif args.mode == 'pv-engine-black':
            if not args.black_engine:
                print("Error: --black-engine required for pv-engine-black mode")
                sys.exit(1)
            ui.start_game(black_engine=args.black_engine, wait_time=args.wait_time, pause=args.pause)
        elif args.mode == 'engine-vs-engine':
            if not args.white_engine or not args.black_engine:
                print("Error: Both --white-engine and --black-engine required for engine-vs-engine mode")
                sys.exit(1)
            ui.start_game(white_engine=args.white_engine, black_engine=args.black_engine,
                         wait_time=args.wait_time, pause=args.pause)
        
        ui.play_game()
    else:
        # Run interactive menu
        ui.run()


if __name__ == "__main__":
    main()
