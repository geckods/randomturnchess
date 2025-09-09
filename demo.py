#!/usr/bin/env python3
"""
Demo script for Random Turn Chess

This script demonstrates all the different game modes available.
"""

import subprocess
import sys
import time

def run_demo():
    print("🎯 Random Turn Chess - Feature Demo")
    print("=" * 50)
    
    print("\n1. Human vs Human (PvP) Mode:")
    print("   python chess_ui.py --mode pvp")
    
    print("\n2. Human vs Engine (Black Engine) Mode:")
    print("   python chess_ui.py --mode pv-engine-black --black-engine stockfish")
    
    print("\n3. Human vs Engine (White Engine) Mode:")
    print("   python chess_ui.py --mode pv-engine-white --white-engine stockfish")
    
    print("\n4. Engine vs Engine Mode:")
    print("   python chess_ui.py --mode engine-vs-engine --white-engine stockfish --black-engine stockfish")
    
    print("\n5. Interactive Menu Mode:")
    print("   python chess_ui.py")
    
    print("\n6. With Custom Timing:")
    print("   python chess_ui.py --mode pv-engine-black --black-engine stockfish --wait-time 2.0 --pause")
    
    print("\n" + "=" * 50)
    print("All modes support the random turn mechanic where coin flips")
    print("determine which player moves next, making each game unique!")
    
    print("\nTry running any of these commands to start playing!")

if __name__ == "__main__":
    run_demo()
