#!/usr/bin/env python3
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

"""Sample script for analyzing Werewolf Arena game results.

This script demonstrates how to use the analysis module to generate
statistics and reports from completed games.

Usage:
    python analyze_games.py session_dir1 session_dir2 session_dir3 ...

Example:
    python analyze_games.py session_20240610_084702 session_20240610_091234
"""

import sys
from pathlib import Path

from werewolf.analysis import analyze_multiple_sessions


def main() -> None:
    """Analyze games from command-line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_games.py <session_dir1> [session_dir2] ...")
        print("\nExample:")
        print("  python analyze_games.py session_20240610_*")
        sys.exit(1)

    session_dirs = sys.argv[1:]

    # Verify directories exist
    valid_dirs = []
    for session_dir in session_dirs:
        if Path(session_dir).exists():
            valid_dirs.append(session_dir)
        else:
            print(f"Warning: Directory not found: {session_dir}")

    if not valid_dirs:
        print("Error: No valid session directories found.")
        sys.exit(1)

    print(f"Analyzing {len(valid_dirs)} game session(s)...")

    # Analyze all sessions
    analyzer = analyze_multiple_sessions(valid_dirs)

    # Print report to console
    analyzer.print_report()

    # Save detailed report to file
    report_path = "analysis_report.json"
    analyzer.save_report(report_path)
    print(f"\nDetailed report saved to: {report_path}")


if __name__ == "__main__":
    main()
