"""
Unit tests for all 6 individual sensing consistency checks.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from saarthi.sensors import BoundingBox, SensingWindow
from saarthi.checks import (
    check_taxonomy,
    check_distance,
    check_trajectory,
    check_corridor,
    check_persistence,
    check_ambient,
)
from saarthi.simulate import create_window


class TestSensingChecks(unittest.TestCase):

    def test_taxonomy_check_clean(self):
        """Verify clean window with no hazardous objects passes taxonomy check."""
        w = create_window(0.0, 2.0)
        vote = check_taxonomy(w)
        self.assertTrue(vote.passed)
        self.assertEqual(vote.check_name, "taxonomy")
        self.assertGreaterEqual(vote.confidence, 0.5)

    def test_taxonomy_check_hazard_detected(self):
        """Verify detected auto-rickshaw flags taxonomy check."""
        dets = [BoundingBox("auto_rickshaw", 0.98, 0.3, 0.3, 0.8, 0.7, 2.0)]
        w = create_window(0.0, 2.0, detections_per_frame=[dets])
        vote = check_taxonomy(w)
        self.assertFalse(vote.passed)
        self.assertIn("auto_rickshaw", vote.reason)
        self.assertEqual(vote.confidence, 0.98)

    def test_distance_check_safe_vs_critical(self):
        """Verify distance check respects safe-stop walking threshold (2.5m)."""
        # Safe distance (4.0m)
        safe_dets = [BoundingBox("pole", 0.95, 0.2, 0.4, 0.8, 0.6, 4.0)]
        w_safe = create_window(0.0, 2.0, detections_per_frame=[safe_dets])
        vote_safe = check_distance(w_safe)
        self.assertTrue(vote_safe.passed)

        # Critical distance (1.2m)
        crit_dets = [BoundingBox("pole", 0.95, 0.2, 0.4, 0.8, 0.6, 1.2)]
        w_crit = create_window(0.0, 2.0, detections_per_frame=[crit_dets])
        vote_crit = check_distance(w_crit)
        self.assertFalse(vote_crit.passed)
        self.assertEqual(vote_crit.metadata["severity"], "CRITICAL")

    def test_trajectory_check_approaching(self):
        """Verify trajectory check detects closing velocity vectors."""
        f1_dets = [BoundingBox("scooter", 0.95, 0.3, 0.4, 0.7, 0.6, depth_meters=3.0)]
        f2_dets = [BoundingBox("scooter", 0.95, 0.3, 0.4, 0.7, 0.6, depth_meters=1.5)]
        w = create_window(0.0, 1.0, fps=2, detections_per_frame=[f1_dets, f2_dets])
        vote = check_trajectory(w)
        self.assertFalse(vote.passed)
        self.assertGreater(vote.metadata["max_closing_rate_mps"], 1.0)

    def test_corridor_check_in_path_vs_peripheral(self):
        """Verify walking corridor geometric filter ignores peripheral objects."""
        # Peripheral object on far left (xmin=0.05, xmax=0.15)
        periph_dets = [BoundingBox("tree", 0.90, 0.2, 0.05, 0.8, 0.15, 2.0)]
        w_periph = create_window(0.0, 2.0, detections_per_frame=[periph_dets])
        vote_periph = check_corridor(w_periph)
        self.assertTrue(vote_periph.passed)

        # Object directly in walking corridor (xmin=0.35, xmax=0.65)
        corridor_dets = [BoundingBox("pillar", 0.90, 0.2, 0.35, 0.8, 0.65, 2.0)]
        w_corridor = create_window(0.0, 2.0, detections_per_frame=[corridor_dets])
        vote_corridor = check_corridor(w_corridor)
        self.assertFalse(vote_corridor.passed)

    def test_persistence_check_suppresses_flicker(self):
        """Verify single-frame flicker is suppressed while multi-frame detection flags."""
        # Single-frame flicker (1 out of 10 frames)
        dets_flicker = [[] for _ in range(10)]
        dets_flicker[2] = [BoundingBox("vehicle", 0.9, 0.3, 0.4, 0.7, 0.6, 2.0)]
        w_flicker = create_window(0.0, 2.0, fps=5, detections_per_frame=dets_flicker)
        vote_flicker = check_persistence(w_flicker)
        self.assertTrue(vote_flicker.passed)
        self.assertIn("Suppressed transient", vote_flicker.reason)

        # Persistent detection (8 out of 10 frames)
        dets_persistent = [[BoundingBox("vehicle", 0.9, 0.3, 0.4, 0.7, 0.6, 2.0)]] * 8 + [[]] * 2
        w_pers = create_window(0.0, 2.0, fps=5, detections_per_frame=dets_persistent)
        vote_pers = check_persistence(w_pers)
        self.assertFalse(vote_pers.passed)

    def test_ambient_check_lighting_and_audio(self):
        """Verify ambient context check provides gain calibrations."""
        w = create_window(0.0, 2.0, db_level=85.0, luminance=0.15)
        vote = check_ambient(w)
        self.assertTrue(vote.passed)
        self.assertTrue(vote.metadata["is_low_light"])
        self.assertTrue(vote.metadata["is_high_noise"])


if __name__ == "__main__":
    unittest.main()
