"""Compatibility imports for action benchmarks; new callers use npc.benchmarks."""

from npc.benchmarks.action_ranking import BenchmarkCase, load_cases, run_benchmark
from npc.benchmarks.runner import USEFULNESS_THRESHOLD

__all__ = ["BenchmarkCase", "USEFULNESS_THRESHOLD", "load_cases", "run_benchmark"]
