"""Unit tests for the 11 logical agent workers and concurrent scheduler."""

import json
import unittest
from pirtm.agents import ALL_WORKER_CLASSES, get_scientific_boundaries_registry
from pirtm.oracle.retrieval import EmbeddingOracle
from pirtm.scheduler import BoundedConcurrentScheduler


class TestAgentsAndScheduler(unittest.TestCase):
    def setUp(self):
        self.oracle = EmbeddingOracle()

    def test_eleven_agents_instantiation_and_contract(self):
        self.assertEqual(len(ALL_WORKER_CLASSES), 11)
        expected_ids = [f"A{i:02d}" for i in range(1, 12)]

        for worker_cls, expected_id in zip(ALL_WORKER_CLASSES, expected_ids):
            worker = worker_cls(self.oracle)
            self.assertEqual(worker.agent_id, expected_id)
            report = worker.execute(round_num=1)

            # Contract verification
            rep_dict = report.to_dict()
            self.assertEqual(rep_dict["agent"], expected_id)
            self.assertIn("block", rep_dict)
            self.assertIn("artifacts", rep_dict)
            self.assertIn("invariants", rep_dict)
            self.assertIn("tests", rep_dict)
            self.assertIn("proof_status", rep_dict)
            self.assertIn("oracle_references", rep_dict)
            self.assertIn("blockers", rep_dict)
            self.assertIn("next_action", rep_dict)

            # Check JSON roundtrip
            rep_json = report.to_json()
            parsed = json.loads(rep_json)
            self.assertEqual(parsed["agent"], expected_id)

    def test_concurrent_scheduler_dispatch(self):
        scheduler = BoundedConcurrentScheduler(self.oracle, max_workers=4)
        cycle_res = scheduler.dispatch_cycle(round_num=1)

        self.assertEqual(len(cycle_res.reports), 11)
        self.assertTrue(cycle_res.ledger_integrity_valid)
        self.assertTrue(cycle_res.total_tests_passed > 0)
        self.assertEqual(cycle_res.total_tests_failed, 0)
        self.assertTrue(len(cycle_res.merged_artifacts) >= 11)
        self.assertTrue(len(cycle_res.invariants_asserted) >= 5)

    def test_scientific_boundaries_registry(self):
        reg = get_scientific_boundaries_registry()
        self.assertIn("akashic_hypothesis", reg)
        self.assertIn("nostradamus_historical_analysis", reg)
        self.assertIn("unitary_quantum_preservation", reg)

        akashic = reg["akashic_hypothesis"]
        self.assertEqual(akashic.status, "METAPHYSICAL_HYPOTHESIS")
        self.assertFalse(akashic.unitary_preservation)

        nostradamus = reg["nostradamus_historical_analysis"]
        self.assertEqual(nostradamus.status, "SPECULATION")
        self.assertIn("Texas sharpshooter", nostradamus.empirical_status)


if __name__ == "__main__":
    unittest.main()
