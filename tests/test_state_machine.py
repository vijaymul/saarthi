"""
Unit tests for the Deterministic Hazard State Machine.
Tests state transitions, 5-window recovery hysteresis rule, and instant relapse.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from saarthi.sensors import HazardState, BoundingBox
from saarthi.state_machine import HazardStateMachine
from saarthi.simulate import create_window


class TestStateMachine(unittest.TestCase):

    def test_clean_stay_clear(self):
        """Verify state machine stays in CLEAR on clean windows."""
        sm = HazardStateMachine()
        w = create_window(0.0, 2.0)
        for _ in range(5):
            verdict = sm.process_window(w)
            self.assertEqual(verdict.state, HazardState.CLEAR)

    def test_hazard_trigger_and_no_direct_clear(self):
        """Verify HAZARD never transitions directly to CLEAR, must go through RECOVERING."""
        sm = HazardStateMachine()

        # Inject critical hazard (Rickshaw at 1.5m)
        dets = [BoundingBox("auto_rickshaw", 0.98, 0.2, 0.3, 0.8, 0.7, 1.5)]
        w_hazard = create_window(0.0, 2.0, detections_per_frame=[dets] * 10)
        v1 = sm.process_window(w_hazard)
        self.assertEqual(v1.state, HazardState.HAZARD)

        # Next window is clean -> Must enter RECOVERING, NOT CLEAR!
        w_clean = create_window(2.0, 4.0)
        v2 = sm.process_window(w_clean)
        self.assertEqual(v2.state, HazardState.RECOVERING)
        self.assertEqual(sm.clean_windows_count, 1)

    def test_recovery_hysteresis_requires_five_clean_windows(self):
        """Verify full recovery requires exactly 5 consecutive clean windows (hysteresis)."""
        sm = HazardStateMachine()

        # Step 1: Trigger HAZARD
        dets = [BoundingBox("auto_rickshaw", 0.98, 0.2, 0.3, 0.8, 0.7, 1.5)]
        w_hazard = create_window(0.0, 2.0, detections_per_frame=[dets] * 10)
        sm.process_window(w_hazard)

        # Windows 1 to 4 of recovery -> Must stay in RECOVERING
        w_clean = create_window(2.0, 4.0)
        for i in range(1, 5):
            v = sm.process_window(w_clean)
            self.assertEqual(v.state, HazardState.RECOVERING)
            self.assertEqual(sm.clean_windows_count, i)

        # Window 5 of recovery -> Transitions to CLEAR
        v5 = sm.process_window(w_clean)
        self.assertEqual(v5.state, HazardState.CLEAR)
        self.assertEqual(sm.clean_windows_count, 0)

    def test_relapse_during_recovery(self):
        """Verify a relapse during recovery immediately drops back to HAZARD and resets recovery count."""
        sm = HazardStateMachine()

        # Step 1: Trigger HAZARD
        dets_hazard = [BoundingBox("auto_rickshaw", 0.98, 0.2, 0.3, 0.8, 0.7, 1.5)]
        w_hazard = create_window(0.0, 2.0, detections_per_frame=[dets_hazard] * 10)
        sm.process_window(w_hazard)

        # Clean window 1 and 2 (RECOVERING)
        w_clean = create_window(2.0, 4.0)
        sm.process_window(w_clean)
        sm.process_window(w_clean)
        self.assertEqual(sm.current_state, HazardState.RECOVERING)
        self.assertEqual(sm.clean_windows_count, 2)

        # Injected relapse on window 3 (New obstacle: step_down)
        dets_step = [BoundingBox("step_down", 0.95, 0.6, 0.3, 0.9, 0.7, 0.8)]
        w_relapse = create_window(6.0, 8.0, detections_per_frame=[dets_step] * 10)
        v_relapse = sm.process_window(w_relapse)

        # Must drop straight to HAZARD and reset clean_windows_count to 0
        self.assertEqual(v_relapse.state, HazardState.HAZARD)
        self.assertEqual(sm.clean_windows_count, 0)


if __name__ == "__main__":
    unittest.main()
