#!/usr/bin/env python3
"""Manual test script for Ollama integration.

This script tests the Ollama integration when Ollama is actually installed and running.
Run with: python3 test_ollama_manual.py

Prerequisites:
1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh
2. Start Ollama: ollama serve (in a separate terminal)
3. Pull a model: ollama pull qwen:0.5b (small model for testing)
"""

import sys

from werewolf.apis import generate_ollama


def test_ollama_connection() -> bool:
    """Test if Ollama server is running and accessible."""
    print("Testing Ollama connection...")
    try:
        # Try a simple generation with a tiny model
        response = generate_ollama(
            model="qwen:0.5b",
            prompt="Say 'hello' in JSON format with a 'message' key.",
            json_mode=True,
            max_tokens=50,
        )
        print("✓ Ollama connection successful!")
        print(f"  Response: {response[:100]}...")
    except RuntimeError as e:
        if "Could not connect to Ollama server" in str(e):
            print("✗ Ollama server is not running")
            print("  Start it with: ollama serve")
            return False
        if "model may not be available" in str(e):
            print("✗ Model not available")
            print("  Pull it with: ollama pull qwen:0.5b")
            return False
        print(f"✗ Unexpected error: {e}")
        return False
    return True


def test_ollama_with_game() -> bool:
    """Test Ollama with actual game initialization."""
    print("\nTesting Ollama with game initialization...")
    try:
        from werewolf.runner import initialize_players

        print("Initializing players with Ollama model...")
        seer, doctor, villagers, werewolves = initialize_players(
            villager_model="ollama:qwen:0.5b",
            werewolf_model="ollama:qwen:0.5b",
        )

        print("✓ Players initialized successfully!")
        print(f"  Seer: {seer.name} ({seer.model})")
        print(f"  Doctor: {doctor.name} ({doctor.model})")
        print(f"  Werewolves: {[w.name for w in werewolves]}")
        print(f"  Villagers: {[v.name for v in villagers]}")
    except Exception as e:
        print(f"✗ Failed to initialize game: {e}")
        return False
    return True


def main() -> None:
    """Run manual Ollama tests."""
    print("=" * 60)
    print("Ollama Integration Manual Test")
    print("=" * 60)
    print()

    # Test 1: Connection
    connection_ok = test_ollama_connection()

    if not connection_ok:
        print("\n" + "=" * 60)
        print("SETUP REQUIRED:")
        print("=" * 60)
        print("1. Install Ollama:")
        print("   curl -fsSL https://ollama.com/install.sh | sh")
        print()
        print("2. Start Ollama server (in a separate terminal):")
        print("   ollama serve")
        print()
        print("3. Pull a small test model:")
        print("   ollama pull qwen:0.5b")
        print()
        print("4. Run this test again:")
        print("   python3 test_ollama_manual.py")
        print("=" * 60)
        sys.exit(1)

    # Test 2: Game integration
    game_ok = test_ollama_with_game()

    print("\n" + "=" * 60)
    if connection_ok and game_ok:
        print("✓ All Ollama tests passed!")
        print("\nYou can now run a full game with:")
        print("  python3 main.py --run --v_models=qwen --w_models=qwen")
    else:
        print("✗ Some tests failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
