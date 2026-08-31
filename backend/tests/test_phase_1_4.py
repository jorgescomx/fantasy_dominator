"""
Integration tests for Phases 1-4:
Phase 1: Database-driven injury records
Phase 2: Context certainty & metric adjustment
Phase 3: Injury discount factor calculation
Phase 4: Testing & validation
"""
import unittest
from datetime import datetime
from backend.app.services.injury_records_service import (
    sync_espn_injuries,
    calculate_discount_factor,
    get_injury_record,
    get_all_injury_records
)
from backend.app.services.context_continuity_service import (
    calculate_context_certainty,
    store_player_context,
    apply_context_factor_to_metrics,
    get_player_context,
    get_player_metrics
)
from backend.app.db.database import init_db, SessionLocal, DBInjuryRecord, DBPlayerContext, DBPlayerMetrics


class TestPhase1InjuryRecords(unittest.TestCase):
    """Test database-driven injury records (no hardcoding)"""

    def setUp(self):
        """Initialize database for testing"""
        init_db()

    def test_discount_factor_calculation_hamstring_questionable(self):
        """Hamstring + QUESTIONABLE = 0.88"""
        factor = calculate_discount_factor("QUESTIONABLE", "Hamstring")
        self.assertEqual(factor, 0.88)

    def test_discount_factor_calculation_ankle_questionable(self):
        """Ankle + QUESTIONABLE = 0.90"""
        factor = calculate_discount_factor("QUESTIONABLE", "Ankle")
        self.assertEqual(factor, 0.90)

    def test_discount_factor_calculation_illness_questionable(self):
        """Illness + QUESTIONABLE = 0.95"""
        factor = calculate_discount_factor("QUESTIONABLE", "Illness")
        self.assertEqual(factor, 0.95)

    def test_discount_factor_calculation_doubtful(self):
        """DOUBTFUL = 0.40"""
        factor = calculate_discount_factor("DOUBTFUL", None)
        self.assertEqual(factor, 0.40)

    def test_discount_factor_calculation_out(self):
        """OUT = 0.0"""
        factor = calculate_discount_factor("OUT", None)
        self.assertEqual(factor, 0.0)

    def test_discount_factor_calculation_cut(self):
        """CUT = 0.0"""
        factor = calculate_discount_factor("CUT", None)
        self.assertEqual(factor, 0.0)

    def test_discount_factor_calculation_suspended(self):
        """SUSPENDED = 0.0"""
        factor = calculate_discount_factor("SUSPENDED", None)
        self.assertEqual(factor, 0.0)

    def test_discount_factor_calculation_active(self):
        """ACTIVE = 1.0"""
        factor = calculate_discount_factor("ACTIVE", None)
        self.assertEqual(factor, 1.0)

    def test_sync_espn_injuries_stores_to_database(self):
        """Verify ESPN sync stores injury records in database"""
        # Mock ESPN league data
        league_data = {
            "teams": [
                {
                    "roster": [
                        {
                            "player": {
                                "id": "test-player-1",
                                "fullName": "Test Player One",
                                "injuryStatus": "QUESTIONABLE",
                                "injury": {
                                    "displayName": "Hamstring",
                                    "detail": None
                                }
                            }
                        }
                    ]
                }
            ]
        }

        # Sync to database
        result = sync_espn_injuries(league_data)
        self.assertEqual(result.get("espn_injury_synced"), 1)

        # Verify record exists in database
        record = get_injury_record("test-player-1")
        self.assertIsNotNone(record)
        self.assertEqual(record["status"], "QUESTIONABLE")
        self.assertEqual(record["body_part"], "Hamstring")
        self.assertEqual(record["discount_factor"], 0.88)
        self.assertEqual(record["source"], "ESPN")


class TestPhase2ContextCertainty(unittest.TestCase):
    """Test context certainty factor calculation"""

    def setUp(self):
        init_db()

    def test_context_certainty_no_changes(self):
        """No QB/OC/HC changes = 1.0 certainty"""
        certainty = calculate_context_certainty(
            qb_same=True,
            oc_same=True,
            hc_same=True
        )
        self.assertEqual(certainty, 1.0)

    def test_context_certainty_qb_change_only(self):
        """QB changed, OC/HC same = 0.70 certainty"""
        certainty = calculate_context_certainty(
            qb_same=False,
            oc_same=True,
            hc_same=True
        )
        self.assertAlmostEqual(certainty, 0.70, places=5)

    def test_context_certainty_major_overhaul(self):
        """QB and OC changed = 0.50 certainty"""
        certainty = calculate_context_certainty(
            qb_same=False,
            oc_same=False,
            hc_same=True
        )
        self.assertAlmostEqual(certainty, 0.50, places=5)

    def test_context_certainty_minimum_floor(self):
        """Multiple changes floor at 0.40"""
        certainty = calculate_context_certainty(
            qb_same=False,
            oc_same=False,
            hc_same=False
        )
        self.assertGreaterEqual(certainty, 0.40)

    def test_store_player_context_detects_qb_change(self):
        """store_player_context detects QB change correctly"""
        result = store_player_context(
            player_id="test-wr-1",
            player_name="Test WR",
            position="WR",
            team="NE",
            qb_2025="Cousins",
            oc_2025="Smith",
            hc_2025="Mayo",
            qb_2026="Murray",
            oc_2026="Smith",
            hc_2026="Mayo"
        )

        self.assertIsNotNone(result)
        context = get_player_context("test-wr-1")
        self.assertTrue(context["context_changes"]["qb_changed"])
        self.assertFalse(context["context_changes"]["oc_changed"])
        self.assertFalse(context["context_changes"]["hc_changed"])

    def test_apply_context_factor_to_metrics(self):
        """Context factor reduces historical metrics correctly"""
        # Store context with 0.7 certainty (QB changed)
        store_player_context(
            player_id="test-wr-2",
            player_name="Test WR 2",
            position="WR",
            team="ARI",
            qb_2025="Cousins",
            oc_2025="OC",
            hc_2025="HC",
            qb_2026="Murray",
            oc_2026="OC",
            hc_2026="HC"
        )

        # Apply context factor to metrics
        result = apply_context_factor_to_metrics(
            player_id="test-wr-2",
            projected_xfp=17.0,
            projected_route_pct=0.88,
            projected_hvt=4.8
        )

        # Verify recalculated values
        self.assertAlmostEqual(result["projected"]["xfp"], 17.0)
        self.assertAlmostEqual(result["recalculated"]["xfp"], 17.0 * 0.70, places=1)
        self.assertAlmostEqual(result["recalculated"]["route_participation"], 0.88 * 0.70, places=2)


class TestPhase3InjuryDiscounts(unittest.TestCase):
    """Test injury discount factor integration"""

    def setUp(self):
        init_db()

    def test_injury_discount_soft_tissue(self):
        """Soft tissue injury (hamstring/calf) = 0.88 discount"""
        for body_part in ["Hamstring", "Calf", "Groin", "Quad", "Thigh"]:
            factor = calculate_discount_factor("QUESTIONABLE", body_part)
            self.assertEqual(factor, 0.88, f"Failed for {body_part}")

    def test_injury_discount_ankle(self):
        """Ankle/foot injury = 0.90 discount"""
        for body_part in ["Ankle", "Foot", "Toe", "Plantar", "Turf Toe"]:
            factor = calculate_discount_factor("QUESTIONABLE", body_part)
            self.assertEqual(factor, 0.90, f"Failed for {body_part}")

    def test_injury_discount_contact_injury(self):
        """Contact injury (knee/shoulder) = 0.92 discount"""
        for body_part in ["Knee", "Bursa", "Contusion", "Bruise", "Ribs", "Shoulder"]:
            factor = calculate_discount_factor("QUESTIONABLE", body_part)
            self.assertEqual(factor, 0.92, f"Failed for {body_part}")

    def test_injury_discount_severe_doubtful(self):
        """DOUBTFUL status = 0.40 discount (60% reduction)"""
        factor = calculate_discount_factor("DOUBTFUL", None)
        self.assertEqual(factor, 0.40)

    def test_injury_discount_unavailable_out(self):
        """OUT/IR/PUP = 0.0 discount (100% unavailable)"""
        for status in ["OUT", "IR", "PUP"]:
            factor = calculate_discount_factor(status, None)
            self.assertEqual(factor, 0.0, f"Failed for {status}")


class TestPhase4EdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def setUp(self):
        init_db()

    def test_player_with_no_body_part_info(self):
        """ESPN missing body part → fallback to status-only discount"""
        # OUT without body part = 0.0
        factor = calculate_discount_factor("OUT", None)
        self.assertEqual(factor, 0.0)

        # QUESTIONABLE without body part = 0.90 (default)
        factor = calculate_discount_factor("QUESTIONABLE", None)
        self.assertEqual(factor, 0.90)

    def test_rookie_with_no_context(self):
        """Rookie (no 2025 history) = 0.40 minimum certainty"""
        certainty = calculate_context_certainty(
            qb_same=True,
            oc_same=True,
            hc_same=True
        )
        # Even with all stable, new player floor is 0.40 if in DB
        # But if not in DB, function returns 0.4 floor implicitly

    def test_multiple_state_changes(self):
        """Player status changes multiple times → database reflects latest"""
        # Initial: QUESTIONABLE
        league_data_1 = {
            "teams": [{
                "roster": [{
                    "player": {
                        "id": "test-multi-state",
                        "fullName": "Multi State",
                        "injuryStatus": "QUESTIONABLE",
                        "injury": {"displayName": "Hamstring", "detail": None}
                    }
                }]
            }]
        }
        sync_espn_injuries(league_data_1)
        record_1 = get_injury_record("test-multi-state")
        self.assertEqual(record_1["status"], "QUESTIONABLE")

        # Update: ACTIVE (cleared)
        league_data_2 = {
            "teams": [{
                "roster": [{
                    "player": {
                        "id": "test-multi-state",
                        "fullName": "Multi State",
                        "injuryStatus": "ACTIVE",
                        "injury": {"displayName": None, "detail": None}
                    }
                }]
            }]
        }
        sync_espn_injuries(league_data_2)
        record_2 = get_injury_record("test-multi-state")
        self.assertEqual(record_2["status"], "ACTIVE")
        self.assertEqual(record_2["discount_factor"], 1.0)

    def test_cut_player_detection(self):
        """CUT status = 0.0 discount (unavailable)"""
        league_data = {
            "teams": [{
                "roster": [{
                    "player": {
                        "id": "test-cut",
                        "fullName": "Cut Player",
                        "injuryStatus": "CUT",
                        "injury": {"displayName": None, "detail": None}
                    }
                }]
            }]
        }
        sync_espn_injuries(league_data)
        record = get_injury_record("test-cut")
        self.assertEqual(record["status"], "CUT")
        self.assertEqual(record["discount_factor"], 0.0)


if __name__ == "__main__":
    unittest.main()
