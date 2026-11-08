"""Unit tests for the Bounded Recursive Knowledge Engine."""

import unittest
from pirtm.oracle.retrieval import EmbeddingOracle
from pirtm.recursive.engine import RecursiveKnowledgeEngine


class TestRecursiveKnowledgeEngine(unittest.TestCase):
    def setUp(self):
        self.oracle = EmbeddingOracle()
        self.engine = RecursiveKnowledgeEngine(self.oracle, max_fuel=4)

    def test_bounded_execution_and_fuel_depletion(self):
        self.engine.propose_hypothesis("Causal graphs are acyclic")
        results = self.engine.run_until_convergence()
        self.assertLessEqual(len(results), 4)
        self.assertLessEqual(self.engine.fuel, 4)

    def test_contradiction_preservation_and_countermodel(self):
        hypo = self.engine.propose_hypothesis("Moon.madeOfCheese is asserted as true")
        self.engine.step_round()

        self.assertEqual(hypo.status, "COUNTERMODEL_FOUND")
        self.assertTrue(len(hypo.countermodels) >= 1)
        self.assertTrue(len(hypo.contradictions) >= 1)
        # Verify contradiction was recorded and preserved
        self.assertTrue(len(self.engine.contradiction_log) >= 1)
        self.assertTrue(self.engine.contradiction_log[0]["preserved"])

    def test_deduplication(self):
        h1 = self.engine.propose_hypothesis("Unitary gates preserve inner products")
        h2 = self.engine.propose_hypothesis("Unitary gates preserve inner products")
        self.assertEqual(h1.hypothesis_id, h2.hypothesis_id)


if __name__ == "__main__":
    unittest.main()
