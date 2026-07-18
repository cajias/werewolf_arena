# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Analysis tools for Werewolf Arena game statistics and evaluation."""

import json
from collections import defaultdict
from typing import Any, Dict, List, Optional

from werewolf.model import State

class GameStats:
    """Statistics for a single game."""

    def __init__(self, state: State) -> None:
        """Initialize game statistics from a game state.

        Args:
            state: The game state to analyze.
        """
        self.state = state
        self.winner = state.winner
        self.num_rounds = len(state.rounds)
        self.werewolf_model = state.werewolves[0].model if state.werewolves else None
        self.villager_model = state.seer.model

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary dictionary of game statistics.

        Returns:
            Dictionary containing game statistics.
        """
        return {
            "winner": self.winner,
            "num_rounds": self.num_rounds,
            "werewolf_model": self.werewolf_model,
            "villager_model": self.villager_model,
            "werewolves": [w.name for w in self.state.werewolves],
            "seer": self.state.seer.name,
            "doctor": self.state.doctor.name,
        }

    def get_player_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed statistics for each player.

        Returns:
            Dictionary mapping player names to their statistics.
        """
        player_stats = {}

        for player_name, player in self.state.players.items():
            survived = player_name in (self.state.rounds[-1].players if self.state.rounds else [])

            player_stats[player_name] = {
                "role": player.role,
                "model": player.model,
                "survived": survived,
                "num_observations": len(player.observations),
            }

        return player_stats

    def get_round_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for each round.

        Returns:
            List of dictionaries containing round statistics.
        """
        round_stats = []

        for idx, round_obj in enumerate(self.state.rounds):
            round_data = {
                "round_number": idx,
                "num_players": len(round_obj.players),
                "num_debates": len(round_obj.debate),
                "eliminated": round_obj.eliminated,
                "protected": round_obj.protected,
                "unmasked": round_obj.unmasked,
                "exiled": round_obj.exiled,
                "success": round_obj.success,
            }
            round_stats.append(round_data)

        return round_stats


class ExperimentAnalyzer:
    """Analyzer for multiple game experiments."""

    def __init__(self) -> None:
        """Initialize the experiment analyzer."""
        self.game_stats: List[GameStats] = []

    def add_game(self, state: State) -> None:
        """Add a game to the analysis.

        Args:
            state: The game state to add.
        """
        self.game_stats.append(GameStats(state))

    def get_win_rates(self) -> Dict[str, float]:
        """Calculate win rates for each faction.

        Returns:
            Dictionary with win rates for Werewolves and Villagers.
        """
        if not self.game_stats:
            return {"Werewolves": 0.0, "Villagers": 0.0}

        werewolf_wins = sum(1 for game in self.game_stats if game.winner == "Werewolves")
        villager_wins = sum(1 for game in self.game_stats if game.winner == "Villagers")
        total = len(self.game_stats)

        return {
            "Werewolves": werewolf_wins / total,
            "Villagers": villager_wins / total,
        }

    def get_model_performance(self) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by model.

        Returns:
            Dictionary mapping models to their performance statistics.
        """
        model_stats = defaultdict(lambda: {"wins": 0, "games": 0, "avg_rounds": 0})

        for game in self.game_stats:
            # Track werewolf model performance
            if game.werewolf_model:
                model_stats[game.werewolf_model]["games"] += 1
                model_stats[game.werewolf_model]["avg_rounds"] += game.num_rounds
                if game.winner == "Werewolves":
                    model_stats[game.werewolf_model]["wins"] += 1

            # Track villager model performance
            if game.villager_model:
                model_stats[game.villager_model]["games"] += 1
                model_stats[game.villager_model]["avg_rounds"] += game.num_rounds
                if game.winner == "Villagers":
                    model_stats[game.villager_model]["wins"] += 1

        # Calculate averages
        for stats in model_stats.values():
            if stats["games"] > 0:
                stats["win_rate"] = stats["wins"] / stats["games"]
                stats["avg_rounds"] = stats["avg_rounds"] / stats["games"]

        return dict(model_stats)

    def get_average_game_length(self) -> float:
        """Calculate average game length in rounds.

        Returns:
            Average number of rounds per game.
        """
        if not self.game_stats:
            return 0.0

        total_rounds = sum(game.num_rounds for game in self.game_stats)
        return total_rounds / len(self.game_stats)

    def get_summary_report(self) -> Dict[str, Any]:
        """Generate a comprehensive summary report.

        Returns:
            Dictionary containing all analysis results.
        """
        return {
            "total_games": len(self.game_stats),
            "win_rates": self.get_win_rates(),
            "average_game_length": self.get_average_game_length(),
            "model_performance": self.get_model_performance(),
        }

    def save_report(self, filepath: str) -> None:
        """Save the analysis report to a JSON file.

        Args:
            filepath: Path where the report should be saved.
        """
        report = self.get_summary_report()

        # Add individual game summaries
        report["games"] = [game.get_summary() for game in self.game_stats]

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

    def print_report(self) -> None:
        """Print a formatted summary report to console."""
        report = self.get_summary_report()

        print("\n" + "=" * 60)
        print("WEREWOLF ARENA ANALYSIS REPORT")
        print("=" * 60)
        print(f"\nTotal Games: {report['total_games']}")
        print(f"Average Game Length: {report['average_game_length']:.2f} rounds")

        print("\n--- Win Rates ---")
        for faction, rate in report["win_rates"].items():
            print(f"{faction}: {rate:.1%}")

        print("\n--- Model Performance ---")
        for model, stats in report["model_performance"].items():
            print(f"\n{model}:")
            print(f"  Games Played: {stats['games']}")
            print(f"  Win Rate: {stats['win_rate']:.1%}")
            print(f"  Avg Rounds: {stats['avg_rounds']:.2f}")

        print("\n" + "=" * 60)


def analyze_session_directory(session_dir: str) -> Optional[GameStats]:
    """Analyze a single game session from its directory.

    Args:
        session_dir: Path to the session directory.

    Returns:
        GameStats object if successful, None otherwise.
    """
    from werewolf import logging as ww_logging

    try:
        state, _logs = ww_logging.load_game(session_dir)
        return GameStats(state)
    except Exception as e:
        print(f"Error analyzing {session_dir}: {e}")
        return None


def analyze_multiple_sessions(session_dirs: List[str]) -> ExperimentAnalyzer:
    """Analyze multiple game sessions.

    Args:
        session_dirs: List of paths to session directories.

    Returns:
        ExperimentAnalyzer with results from all sessions.
    """
    from werewolf import logging as ww_logging

    analyzer = ExperimentAnalyzer()

    for session_dir in session_dirs:
        try:
            state, _logs = ww_logging.load_game(session_dir)
            analyzer.add_game(state)
        except Exception as e:
            print(f"Error loading {session_dir}: {e}")

    return analyzer
