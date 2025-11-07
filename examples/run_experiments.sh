#!/bin/bash
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

# Sample experiment script for running batch Werewolf Arena evaluations
# This script demonstrates how to run systematic experiments comparing different LLM models

set -e  # Exit on error

# Configuration
NUM_GAMES=5
THREADS=4
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="results_${TIMESTAMP}"

# Create results directory
mkdir -p "${RESULTS_DIR}"

echo "Starting Werewolf Arena experiments at ${TIMESTAMP}"
echo "Results will be saved to: ${RESULTS_DIR}"
echo "======================================================"

# Experiment 1: GPT-4 vs GPT-4 (baseline)
echo ""
echo "Experiment 1: GPT-4 villagers vs GPT-4 werewolves (baseline)"
python3 main.py --eval \
    --num_games=${NUM_GAMES} \
    --v_models=gpt4 \
    --w_models=gpt4 \
    --threads=${THREADS}

# Experiment 2: Gemini Pro 1.5 vs GPT-4
echo ""
echo "Experiment 2: Gemini Pro 1.5 villagers vs GPT-4 werewolves"
python3 main.py --eval \
    --num_games=${NUM_GAMES} \
    --v_models=pro1.5 \
    --w_models=gpt4 \
    --threads=${THREADS}

# Experiment 3: Arena mode - all combinations
echo ""
echo "Experiment 3: Arena mode - comparing multiple model combinations"
python3 main.py --eval \
    --arena \
    --num_games=${NUM_GAMES} \
    --v_models=pro1.5,flash \
    --w_models=gpt4,gpt4o \
    --threads=${THREADS}

# Experiment 4: Budget-friendly evaluation with Flash and GPT-3.5
echo ""
echo "Experiment 4: Budget evaluation - Gemini Flash vs GPT-3.5"
python3 main.py --eval \
    --num_games=${NUM_GAMES} \
    --v_models=flash \
    --w_models=gpt3.5 \
    --threads=${THREADS}

echo ""
echo "======================================================"
echo "Experiments completed at $(date +%Y%m%d_%H%M%S)"
echo "Check the session directories for detailed game logs"
echo ""
echo "To view results in the interactive viewer:"
echo "  1. npm install"
echo "  2. npm run start"
echo "  3. Open http://localhost:8080/?session_id=<session_id>"
