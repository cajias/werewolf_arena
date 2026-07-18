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

"""Integration tests for Werewolf Arena game flow."""

from werewolf.config import get_player_names
from werewolf.model import Doctor, Round, Seer, State, Villager, Werewolf


class TestGameFlow:
    """Integration tests for complete game workflows."""

    def test_create_full_game_state(self):
        """Test creating a complete game state with all player types."""
        player_names = get_player_names()

        seer = Seer(name=player_names[0], model="test-model")
        doctor = Doctor(name=player_names[1], model="test-model")
        werewolves = [
            Werewolf(name=player_names[2], model="test-model"),
            Werewolf(name=player_names[3], model="test-model"),
        ]
        villagers = [Villager(name=name, model="test-model") for name in player_names[4:8]]

        state = State(
            session_id="test_session",
            seer=seer,
            doctor=doctor,
            villagers=villagers,
            werewolves=werewolves,
        )

        # Verify all players are in the state
        assert len(state.players) == 8
        assert state.seer.role == "Seer"
        assert state.doctor.role == "Doctor"
        assert all(w.role == "Werewolf" for w in state.werewolves)
        assert all(v.role == "Villager" for v in state.villagers)

    def test_initialize_all_players(self):
        """Test initializing game view for all players."""
        player_names = get_player_names()

        seer = Seer(name=player_names[0], model="test-model")
        doctor = Doctor(name=player_names[1], model="test-model")
        werewolves = [
            Werewolf(name=player_names[2], model="test-model"),
            Werewolf(name=player_names[3], model="test-model"),
        ]
        villagers = [Villager(name=name, model="test-model") for name in player_names[4:8]]

        all_players = [seer, doctor, *werewolves, *villagers]
        all_names = [p.name for p in all_players]

        # Initialize all players
        for player in all_players:
            other_wolf = None
            if isinstance(player, Werewolf):
                other_wolf = next(
                    (w.name for w in werewolves if w != player),
                    None,
                )

            player.initialize_game_view(
                round_number=0,
                current_players=all_names,
                other_wolf=other_wolf,
            )

        # Verify all players have gamestate
        for player in all_players:
            assert player.gamestate is not None
            assert player.gamestate.round_number == 0
            assert len(player.gamestate.current_players) == 8

        # Verify werewolves know about each other
        assert werewolves[0].gamestate.other_wolf == werewolves[1].name
        assert werewolves[1].gamestate.other_wolf == werewolves[0].name

    def test_round_progression(self):
        """Test that rounds are properly created and tracked."""
        player_names = get_player_names()

        seer = Seer(name=player_names[0], model="test-model")
        doctor = Doctor(name=player_names[1], model="test-model")
        werewolves = [
            Werewolf(name=player_names[2], model="test-model"),
            Werewolf(name=player_names[3], model="test-model"),
        ]
        villagers = [Villager(name=name, model="test-model") for name in player_names[4:8]]

        state = State(
            session_id="test_session",
            seer=seer,
            doctor=doctor,
            villagers=villagers,
            werewolves=werewolves,
        )

        # Add multiple rounds
        for _i in range(3):
            round_obj = Round()
            round_obj.players = list(state.players.keys())
            state.rounds.append(round_obj)

        assert len(state.rounds) == 3
        assert all(isinstance(r, Round) for r in state.rounds)

    def test_player_elimination_flow(self):
        """Test the flow of eliminating players from the game."""
        player_names = get_player_names()

        seer = Seer(name=player_names[0], model="test-model")
        doctor = Doctor(name=player_names[1], model="test-model")
        werewolves = [
            Werewolf(name=player_names[2], model="test-model"),
            Werewolf(name=player_names[3], model="test-model"),
        ]
        villagers = [Villager(name=name, model="test-model") for name in player_names[4:8]]

        all_players = [seer, doctor, *werewolves, *villagers]
        all_names = [p.name for p in all_players]

        # Initialize all players
        for player in all_players:
            player.initialize_game_view(
                round_number=0,
                current_players=all_names.copy(),
            )

        # Simulate elimination
        eliminated_player = villagers[0].name
        for player in all_players:
            if player.gamestate:
                player.gamestate.remove_player(eliminated_player)

        # Verify player was removed from all game views
        for player in all_players:
            assert eliminated_player not in player.gamestate.current_players
            assert len(player.gamestate.current_players) == 7

    def test_debate_synchronization(self):
        """Test that debate updates are synchronized across players."""
        player_names = get_player_names()

        seer = Seer(name=player_names[0], model="test-model")
        doctor = Doctor(name=player_names[1], model="test-model")
        werewolves = [
            Werewolf(name=player_names[2], model="test-model"),
            Werewolf(name=player_names[3], model="test-model"),
        ]
        villagers = [Villager(name=name, model="test-model") for name in player_names[4:8]]

        all_players = [seer, doctor, *werewolves, *villagers]
        all_names = [p.name for p in all_players]

        # Initialize all players
        for player in all_players:
            player.initialize_game_view(
                round_number=0,
                current_players=all_names,
            )

        # Simulate debate
        speaker = seer.name
        dialogue = "I think we should carefully consider who to vote for."

        for player in all_players:
            player.gamestate.update_debate(speaker, dialogue)

        # Verify all players have the same debate
        for player in all_players:
            assert len(player.gamestate.debate) == 1
            assert player.gamestate.debate[0] == (speaker, dialogue)

    def test_observations_tracking(self):
        """Test that player observations are properly tracked."""
        player_names = get_player_names()

        villager = Villager(name=player_names[0], model="test-model")
        villager.initialize_game_view(
            round_number=0,
            current_players=player_names,
        )

        # Add multiple observations
        villager.add_announcement("The game has started.")
        villager._add_observation("Alice seems suspicious.")

        # Move to next round
        villager.gamestate.round_number = 1
        villager.add_announcement("Bob was eliminated.")

        # Verify observations
        assert len(villager.observations) == 3
        assert "Round 0:" in villager.observations[0]
        assert "Round 0:" in villager.observations[1]
        assert "Round 1:" in villager.observations[2]
