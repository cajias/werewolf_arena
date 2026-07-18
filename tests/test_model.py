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

"""Unit tests for player models and game state."""

import pytest

from werewolf.model import (
    DOCTOR,
    SEER,
    VILLAGER,
    WEREWOLF,
    Doctor,
    GameView,
    Round,
    Seer,
    State,
    Villager,
    Werewolf,
    group_and_format_observations,
)

class TestGameView:
    """Tests for the GameView class."""

    def test_init(self, mock_player_names):
        """Test GameView initialization."""
        game_view = GameView(
            round_number=1,
            current_players=mock_player_names[:4],
        )
        assert game_view.round_number == 1
        assert len(game_view.current_players) == 4
        assert game_view.debate == []
        assert game_view.other_wolf is None

    def test_init_with_other_wolf(self, mock_player_names):
        """Test GameView initialization with other_wolf."""
        game_view = GameView(
            round_number=0,
            current_players=mock_player_names,
            other_wolf="WolfBuddy",
        )
        assert game_view.other_wolf == "WolfBuddy"

    def test_update_debate(self, mock_player_names):
        """Test updating debate with new dialogue."""
        game_view = GameView(round_number=1, current_players=mock_player_names)

        game_view.update_debate("Alice", "I think Bob is suspicious.")
        game_view.update_debate("Bob", "No, I'm a villager!")

        assert len(game_view.debate) == 2
        assert game_view.debate[0] == ("Alice", "I think Bob is suspicious.")
        assert game_view.debate[1] == ("Bob", "No, I'm a villager!")

    def test_clear_debate(self, mock_player_names):
        """Test clearing the debate."""
        game_view = GameView(round_number=1, current_players=mock_player_names)
        game_view.update_debate("Alice", "Test")

        game_view.clear_debate()

        assert game_view.debate == []

    def test_remove_player(self, mock_player_names):
        """Test removing a player from the game."""
        game_view = GameView(round_number=1, current_players=mock_player_names.copy())
        initial_count = len(game_view.current_players)

        game_view.remove_player("Alice")

        assert "Alice" not in game_view.current_players
        assert len(game_view.current_players) == initial_count - 1


class TestPlayer:
    """Tests for Player classes."""

    def test_villager_init(self):
        """Test Villager initialization."""
        villager = Villager(name="Alice", model="test-model")
        assert villager.name == "Alice"
        assert villager.role == VILLAGER
        assert villager.model == "test-model"
        assert villager.observations == []
        assert villager.gamestate is None

    def test_werewolf_init(self):
        """Test Werewolf initialization."""
        werewolf = Werewolf(name="Wolf1", model="test-model")
        assert werewolf.name == "Wolf1"
        assert werewolf.role == WEREWOLF
        assert werewolf.model == "test-model"

    def test_seer_init(self):
        """Test Seer initialization."""
        seer = Seer(name="MySeer", model="test-model")
        assert seer.name == "MySeer"
        assert seer.role == SEER
        assert seer.model == "test-model"

    def test_doctor_init(self):
        """Test Doctor initialization."""
        doctor = Doctor(name="MyDoctor", model="test-model")
        assert doctor.name == "MyDoctor"
        assert doctor.role == DOCTOR
        assert doctor.model == "test-model"

    def test_player_with_personality(self):
        """Test player initialization with personality."""
        villager = Villager(
            name="Alice",
            model="test-model",
            personality="You are very cautious.",
        )
        assert villager.personality == "You are very cautious."

    def test_initialize_game_view(self, mock_player_names):
        """Test initializing a player's game view."""
        villager = Villager(name="Alice", model="test-model")

        villager.initialize_game_view(
            round_number=0,
            current_players=mock_player_names,
        )

        assert villager.gamestate is not None
        assert villager.gamestate.round_number == 0
        assert villager.gamestate.current_players == mock_player_names

    def test_add_observation(self, mock_player_names):
        """Test adding observations to a player."""
        villager = Villager(name="Alice", model="test-model")
        villager.initialize_game_view(round_number=1, current_players=mock_player_names)

        villager._add_observation("Bob was eliminated.")

        assert len(villager.observations) == 1
        assert "Round 1: Bob was eliminated." in villager.observations

    def test_add_observation_without_gamestate(self):
        """Test that adding observation without gamestate raises error."""
        villager = Villager(name="Alice", model="test-model")

        with pytest.raises(ValueError, match="GameView not initialized"):
            villager._add_observation("Test observation")

    def test_add_announcement(self, mock_player_names):
        """Test adding announcements to a player."""
        villager = Villager(name="Alice", model="test-model")
        villager.initialize_game_view(round_number=2, current_players=mock_player_names)

        villager.add_announcement("Charlie was removed from the game.")

        assert len(villager.observations) == 1
        assert "Round 2: Moderator Announcement: Charlie was removed" in villager.observations[0]


class TestState:
    """Tests for the State class."""

    def test_state_init(self, mock_seer, mock_doctor, mock_villagers, mock_werewolves):
        """Test State initialization."""
        state = State(
            session_id="test_session",
            seer=mock_seer,
            doctor=mock_doctor,
            villagers=mock_villagers,
            werewolves=mock_werewolves,
        )

        assert state.seer == mock_seer
        assert state.doctor == mock_doctor
        assert len(state.villagers) == 4
        assert len(state.werewolves) == 2
        assert state.rounds == []
        assert state.winner == ""

    def test_state_players_dict(self, game_state):
        """Test that state creates proper players dictionary."""
        assert "TestSeer" in game_state.players
        assert "TestDoctor" in game_state.players
        assert "Wolf1" in game_state.players
        assert "Wolf2" in game_state.players
        assert "Villager1" in game_state.players

        # Total should be 8 (1 seer + 1 doctor + 4 villagers + 2 werewolves)
        assert len(game_state.players) == 8


class TestRound:
    """Tests for the Round class."""

    def test_round_init(self):
        """Test Round initialization."""
        round_obj = Round()

        assert round_obj.players == []
        assert round_obj.debate == []
        assert round_obj.bids == []
        assert round_obj.votes == []
        assert round_obj.eliminated is None
        assert round_obj.protected is None
        assert round_obj.unmasked is None
        assert round_obj.exiled is None
        assert round_obj.success is False


class TestGroupAndFormatObservations:
    """Tests for the group_and_format_observations helper function."""

    def test_single_round_single_observation(self):
        """Test formatting a single observation from one round."""
        observations = ["Round 0: Bob was eliminated."]
        result = group_and_format_observations(observations)

        assert len(result) == 1
        assert "Round 0:" in result[0]
        assert "Bob was eliminated." in result[0]

    def test_multiple_rounds(self):
        """Test formatting observations from multiple rounds."""
        observations = [
            "Round 0: Bob was eliminated.",
            "Round 1: Alice was protected.",
            "Round 0: Charlie voted for Bob.",
        ]
        result = group_and_format_observations(observations)

        assert len(result) == 2
        # Check that Round 0 has both observations
        round_0 = next(r for r in result if "Round 0:" in r)
        assert "Bob was eliminated." in round_0
        assert "Charlie voted for Bob." in round_0

    def test_observations_with_quotes(self):
        """Test that quotes are removed from observations."""
        observations = ['Round 0: "Bob is suspicious."']
        result = group_and_format_observations(observations)

        assert len(result) == 1
        assert '"' not in result[0]
        assert "Bob is suspicious." in result[0]

    def test_sorted_by_round(self):
        """Test that observations are sorted by round number."""
        observations = [
            "Round 2: Late game action.",
            "Round 0: Early game action.",
            "Round 1: Mid game action.",
        ]
        result = group_and_format_observations(observations)

        assert len(result) == 3
        assert "Round 0:" in result[0]
        assert "Round 1:" in result[1]
        assert "Round 2:" in result[2]
