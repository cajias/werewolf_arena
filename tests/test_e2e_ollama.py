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

"""End-to-end tests for Werewolf Arena with Ollama support."""

from unittest.mock import Mock, patch

import pytest

from werewolf.config import get_player_names
from werewolf.game import GameMaster
from werewolf.model import Doctor, Seer, State, Villager, Werewolf
from werewolf.runner import initialize_players


class TestOllamaE2E:
    """End-to-end tests using Ollama models (mocked)."""

    @pytest.fixture
    def mock_ollama_response(self) -> Mock:
        """Fixture that mocks Ollama API responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": '{"action": "vote", "target": "Alice", "reasoning": "Test reasoning"}'
        }
        return mock_response

    @pytest.fixture
    def ollama_state(self) -> State:
        """Create a game state with Ollama models."""
        player_names = get_player_names()

        seer = Seer(name=player_names[0], model="ollama:deepseek-r1:latest")
        doctor = Doctor(name=player_names[1], model="ollama:deepseek-r1:latest")
        werewolves = [
            Werewolf(name=player_names[2], model="ollama:deepseek-r1:latest"),
            Werewolf(name=player_names[3], model="ollama:deepseek-r1:latest"),
        ]
        villagers = [
            Villager(name=name, model="ollama:deepseek-r1:latest")
            for name in player_names[4:8]
        ]

        state = State(
            session_id="test_ollama_session",
            seer=seer,
            doctor=doctor,
            villagers=villagers,
            werewolves=werewolves,
        )

        return state

    def test_ollama_model_initialization(self, ollama_state: State) -> None:
        """Test that Ollama models are properly initialized in game state."""
        # Verify all players have Ollama models
        for player in ollama_state.players.values():
            assert player.model == "ollama:deepseek-r1:latest"

        # Verify correct number of players
        assert len(ollama_state.players) == 8
        assert len(ollama_state.werewolves) == 2
        assert len(ollama_state.villagers) == 4

    @patch("requests.post")
    def test_ollama_game_initialization(
        self, mock_post: Mock, mock_ollama_response: Mock, ollama_state: State
    ) -> None:
        """Test initializing a game with Ollama models."""
        mock_post.return_value = mock_ollama_response

        # Initialize game master
        gm = GameMaster(ollama_state)

        # Verify game state is properly set up
        assert gm.state.session_id == "test_ollama_session"
        assert len(gm.state.players) == 8
        assert gm.state.winner == ""

    @patch("requests.post")
    def test_ollama_player_initialization(
        self, mock_post: Mock, mock_ollama_response: Mock
    ) -> None:
        """Test initialize_players function with Ollama models."""
        mock_post.return_value = mock_ollama_response

        # Initialize players using the runner function
        seer, doctor, villagers, werewolves = initialize_players(
            villager_model="ollama:deepseek-r1:latest",
            werewolf_model="ollama:deepseek-r1:latest",
        )

        # Verify all players are initialized with correct models
        all_players = [seer, doctor] + werewolves + villagers
        assert all(p.model == "ollama:deepseek-r1:latest" for p in all_players)

        # Verify werewolves know about each other
        assert werewolves[0].gamestate.other_wolf == werewolves[1].name
        assert werewolves[1].gamestate.other_wolf == werewolves[0].name

    @patch("requests.post")
    def test_ollama_api_error_handling(self, mock_post: Mock) -> None:
        """Test that Ollama API errors are properly handled."""
        import requests

        from werewolf.apis import generate_ollama

        # Test connection error
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        with pytest.raises(RuntimeError, match="Could not connect to Ollama server"):
            generate_ollama("deepseek-r1:latest", "test prompt")

        # Test timeout error
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        with pytest.raises(RuntimeError, match="timed out"):
            generate_ollama("deepseek-r1:latest", "test prompt")

    @patch("requests.post")
    def test_ollama_json_mode(self, mock_post: Mock) -> None:
        """Test that JSON mode is properly handled for Ollama."""
        from werewolf.apis import generate_ollama

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": '{"key": "value"}'}
        mock_post.return_value = mock_response

        result = generate_ollama("deepseek-r1:latest", "test prompt", json_mode=True)

        # Verify the request was made with format=json
        call_args = mock_post.call_args
        request_body = call_args[1]["json"]
        assert request_body["format"] == "json"
        assert result == '{"key": "value"}'

    @patch("requests.post")
    def test_ollama_non_json_mode(self, mock_post: Mock) -> None:
        """Test that non-JSON mode works for Ollama."""
        from werewolf.apis import generate_ollama

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Plain text response"}
        mock_post.return_value = mock_response

        result = generate_ollama("deepseek-r1:latest", "test prompt", json_mode=False)

        # Verify the request was made without format parameter
        call_args = mock_post.call_args
        request_body = call_args[1]["json"]
        assert "format" not in request_body
        assert result == "Plain text response"

    @patch("requests.post")
    def test_ollama_custom_parameters(self, mock_post: Mock) -> None:
        """Test that custom parameters are passed to Ollama."""
        from werewolf.apis import generate_ollama

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "test"}
        mock_post.return_value = mock_response

        generate_ollama(
            "deepseek-r1:latest",
            "test prompt",
            max_tokens=2048,
            temperature=0.5,
        )

        # Verify custom parameters were passed
        call_args = mock_post.call_args
        request_body = call_args[1]["json"]
        assert request_body["options"]["num_predict"] == 2048
        assert request_body["options"]["temperature"] == 0.5
