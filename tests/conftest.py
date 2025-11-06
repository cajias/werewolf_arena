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

"""Pytest configuration and fixtures for Werewolf Arena tests."""

import pytest

from werewolf.model import Doctor, Seer, State, Villager, Werewolf


@pytest.fixture
def mock_player_names():
    """Fixture providing a list of player names for testing."""
    return [
        "Alice",
        "Bob",
        "Charlie",
        "David",
        "Eve",
        "Frank",
        "Grace",
        "Henry",
    ]


@pytest.fixture
def mock_seer():
    """Fixture providing a mock Seer player."""
    return Seer(name="TestSeer", model="mock")


@pytest.fixture
def mock_doctor():
    """Fixture providing a mock Doctor player."""
    return Doctor(name="TestDoctor", model="mock")


@pytest.fixture
def mock_villagers():
    """Fixture providing mock Villager players."""
    return [
        Villager(name="Villager1", model="mock"),
        Villager(name="Villager2", model="mock"),
        Villager(name="Villager3", model="mock"),
        Villager(name="Villager4", model="mock"),
    ]


@pytest.fixture
def mock_werewolves():
    """Fixture providing mock Werewolf players."""
    return [
        Werewolf(name="Wolf1", model="mock"),
        Werewolf(name="Wolf2", model="mock"),
    ]


@pytest.fixture
def game_state(mock_seer, mock_doctor, mock_villagers, mock_werewolves):
    """Fixture providing a basic game state."""
    return State(
        session_id="test_session",
        seer=mock_seer,
        doctor=mock_doctor,
        villagers=mock_villagers,
        werewolves=mock_werewolves,
    )
