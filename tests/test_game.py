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

"""Unit tests for werewolf game logic."""

from werewolf.game import GameMaster, get_max_bids
from werewolf.model import Round, RoundLog


class TestGetMaxBids:
    """Tests for the get_max_bids helper function."""

    def test_single_max_bid(self):
        """Test when there's a single highest bidder."""
        bids = {"Alice": 5, "Bob": 3, "Charlie": 2}
        result = get_max_bids(bids)
        assert result == ["Alice"]

    def test_multiple_max_bids(self):
        """Test when there are multiple highest bidders."""
        bids = {"Alice": 5, "Bob": 5, "Charlie": 2}
        result = get_max_bids(bids)
        assert set(result) == {"Alice", "Bob"}

    def test_all_same_bids(self):
        """Test when all players bid the same amount."""
        bids = {"Alice": 3, "Bob": 3, "Charlie": 3}
        result = get_max_bids(bids)
        assert set(result) == {"Alice", "Bob", "Charlie"}

    def test_single_bidder(self):
        """Test with only one bidder."""
        bids = {"Alice": 5}
        result = get_max_bids(bids)
        assert result == ["Alice"]

    def test_negative_bids(self):
        """Test with negative bid values."""
        bids = {"Alice": -1, "Bob": -5, "Charlie": -3}
        result = get_max_bids(bids)
        assert result == ["Alice"]


class TestGameMaster:
    """Tests for the GameMaster class."""

    def test_init_new_game(self, game_state):
        """Test GameMaster initialization with a new game."""
        gm = GameMaster(game_state)
        assert gm.state == game_state
        assert gm.current_round_num == 0
        assert gm.num_threads == 1
        assert gm.logs == []

    def test_init_resumed_game(self, game_state):
        """Test GameMaster initialization with a resumed game."""
        # Add some rounds to simulate a game in progress
        game_state.rounds = [Round(), Round()]
        gm = GameMaster(game_state)
        assert gm.current_round_num == 2

    def test_get_winner_werewolves_win_equal(self, game_state):
        """Test winner detection when werewolves equal villagers."""
        gm = GameMaster(game_state)
        game_state.rounds.append(Round())

        # Set up scenario: 2 werewolves, 2 villagers
        gm.this_round.players = ["Wolf1", "Wolf2", "Villager1", "Villager2"]

        winner = gm.get_winner()
        assert winner == "Werewolves"

    def test_get_winner_werewolves_win_majority(self, game_state):
        """Test winner detection when werewolves outnumber villagers."""
        gm = GameMaster(game_state)
        game_state.rounds.append(Round())

        # Set up scenario: 2 werewolves, 1 villager
        gm.this_round.players = ["Wolf1", "Wolf2", "Villager1"]

        winner = gm.get_winner()
        assert winner == "Werewolves"

    def test_get_winner_no_werewolves(self, game_state):
        """Test winner detection when all werewolves are eliminated."""
        gm = GameMaster(game_state)
        game_state.rounds.append(Round())

        # Set up scenario: no werewolves remaining
        gm.this_round.players = ["Villager1", "Villager2", "TestSeer", "TestDoctor"]

        winner = gm.get_winner()
        assert winner == "Villagers"

    def test_get_winner_game_ongoing(self, game_state):
        """Test winner detection when game is still ongoing."""
        gm = GameMaster(game_state)
        game_state.rounds.append(Round())

        # Set up scenario: 2 werewolves, 4 villagers (game continues)
        gm.this_round.players = [
            "Wolf1", "Wolf2", "Villager1", "Villager2",
            "Villager3", "TestSeer"
        ]

        winner = gm.get_winner()
        assert winner == ""

    def test_this_round_property(self, game_state):
        """Test the this_round property."""
        gm = GameMaster(game_state)
        game_state.rounds.append(Round())

        assert gm.this_round == game_state.rounds[0]

    def test_this_round_log_property(self, game_state):
        """Test the this_round_log property."""
        gm = GameMaster(game_state)
        gm.logs.append(RoundLog())

        assert gm.this_round_log == gm.logs[0]

    def test_check_for_winner_sets_winner(self, game_state):
        """Test that check_for_winner updates state."""
        gm = GameMaster(game_state)
        game_state.rounds.append(Round())

        # Set up a winning condition
        gm.this_round.players = ["Villager1", "TestSeer"]

        gm.check_for_winner()
        assert gm.state.winner == "Villagers"

    def test_exile_with_majority(self, game_state):
        """Test exile when a player has majority votes."""
        gm = GameMaster(game_state)
        game_state.rounds.append(Round())
        gm.logs.append(RoundLog())

        # Setup players and votes
        gm.this_round.players = ["Wolf1", "Wolf2", "Villager1", "Villager2", "TestSeer"]

        # Initialize gamestates for all players
        for player in game_state.players.values():
            player.initialize_game_view(
                round_number=0,
                current_players=gm.this_round.players.copy(),
            )

        gm.this_round.votes.append({
            "Wolf1": "Villager1",
            "Wolf2": "Villager1",
            "Villager1": "Wolf1",
            "Villager2": "Villager1",
            "TestSeer": "Villager1",
        })

        gm.exile()

        # Villager1 should be exiled (got 4 votes out of 5 players)
        assert gm.this_round.exiled == "Villager1"
        assert "Villager1" not in gm.this_round.players

    def test_exile_without_majority(self, game_state):
        """Test exile when no player has majority votes."""
        gm = GameMaster(game_state)
        game_state.rounds.append(Round())
        gm.logs.append(RoundLog())

        # Setup players and votes (tie - no majority)
        gm.this_round.players = ["Wolf1", "Wolf2", "Villager1", "Villager2"]

        # Initialize gamestates for all players
        for player in game_state.players.values():
            player.initialize_game_view(
                round_number=0,
                current_players=gm.this_round.players.copy(),
            )

        gm.this_round.votes.append({
            "Wolf1": "Villager1",
            "Wolf2": "Villager1",
            "Villager1": "Wolf1",
            "Villager2": "Wolf1",
        })

        gm.exile()

        # No one should be exiled (2 votes out of 4 is not > 50%)
        assert gm.this_round.exiled is None
        # All players should remain
        assert len(gm.this_round.players) == 4

    def test_resolve_night_phase_elimination(self, game_state):
        """Test night phase resolution when elimination succeeds."""
        gm = GameMaster(game_state)
        game_state.rounds.append(Round())

        gm.this_round.players = ["Wolf1", "Wolf2", "Villager1", "Villager2", "TestSeer"]

        # Initialize gamestates for all players
        for player in game_state.players.values():
            player.initialize_game_view(
                round_number=0,
                current_players=gm.this_round.players.copy(),
            )

        gm.this_round.eliminated = "Villager1"
        gm.this_round.protected = "Villager2"  # Different from eliminated

        gm.resolve_night_phase()

        assert "Villager1" not in gm.this_round.players
        assert len(gm.this_round.players) == 4

    def test_resolve_night_phase_protection(self, game_state):
        """Test night phase resolution when doctor saves the target."""
        gm = GameMaster(game_state)
        game_state.rounds.append(Round())

        gm.this_round.players = ["Wolf1", "Wolf2", "Villager1", "Villager2", "TestSeer"]

        # Initialize gamestates for all players
        for player in game_state.players.values():
            player.initialize_game_view(
                round_number=0,
                current_players=gm.this_round.players.copy(),
            )

        gm.this_round.eliminated = "Villager1"
        gm.this_round.protected = "Villager1"  # Same as eliminated

        gm.resolve_night_phase()

        # Villager1 should still be alive
        assert "Villager1" in gm.this_round.players
        assert len(gm.this_round.players) == 5
