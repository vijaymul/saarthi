"""
End-to-end integration tests over synthetic traces.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from saarthi.sensors import HazardState
from saarthi.state_machine import HazardStateMachine
from saarthi.simulate import (
    generate_clean_trace,
    generate_hazard_scenario_trace,
    generate_single_frame_flicker_trace,
)


class TestIntegration(unittest.TestCase):

    def test_clean_trace_end_to_end(self):
        """Verify entire honest walking trace produces only CLEAR states."""
        sm = HazardStateMachine()
        trace = generate_clean_trace(num_windows=10)
        for window in trace:
            verdict = sm.process_window(window)
            self.assertEqual(verdict.state, HazardState.CLEAR)
            self.assertIsNone(verdict.primary_hazard)
            self.assertEqual(len(verdict.failed_checks), 0)

    def test_hazard_scenario_full_lifecycle(self):
        """
        Verify full life cycle:
        CLEAR -> HAZARD -> RECOVERING (1..4) -> CLEAR -> HAZARD (Relapse) -> RECOVERING -> CLEAR.
        """
        sm = HazardStateMachine()
        trace = generate_hazard_scenario_trace()
        states_observed = [sm.process_window(w).state for w in trace]

        # Verify key milestones
        self.assertEqual(states_observed[0], HazardState.CLEAR)
        self.assertEqual(states_observed[3], HazardState.HAZARD)  # Auto rickshaw injected
        self.assertEqual(states_observed[4], HazardState.HAZARD)
        self.assertEqual(states_observed[5], HazardState.RECOVERING)  # Window 1 of recovery
        self.assertEqual(states_observed[9], HazardState.CLEAR)  # Recovered after 5 windows
        self.assertEqual(states_observed[10], HazardState.HAZARD)  # Relapse obstacle
        self.assertEqual(states_observed[11], HazardState.RECOVERING)
        self.assertEqual(states_observed[-1], HazardState.CLEAR)

    def test_anti_flicker_suppression(self):
        """Verify single-frame flicker does not cause false-positive hazard alarm."""
        sm = HazardStateMachine()
        trace = generate_single_frame_flicker_trace()
        verdict = sm.process_window(trace[0])
        # Check persistence vote
        pers_vote = next(v for v in verdict.all_votes if v.check_name == "persistence")
        self.assertTrue(pers_vote.passed)
        self.assertIn("Suppressed transient", pers_vote.reason)


if __name__ == "__main__":
    unittest.main()
