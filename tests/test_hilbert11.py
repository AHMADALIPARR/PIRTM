"""Unit tests for 11-Qubit Hilbert Space Model and Adversarial Experiment."""

import unittest
from pirtm.quantum.hilbert11 import (
    DIM,
    NUM_QUBITS,
    GateOp,
    Hilbert11Simulator,
    Hilbert11State,
    density_matrix_trace_distance,
    partial_trace,
    run_central_adversarial_experiment,
    state_fidelity,
)


class TestHilbert11(unittest.TestCase):
    def test_dimensions_and_basis_initialization(self):
        self.assertEqual(NUM_QUBITS, 11)
        self.assertEqual(DIM, 2048)
        state = Hilbert11State.basis_state(0)
        self.assertEqual(len(state.amplitudes), 2048)
        self.assertTrue(state.is_normalized())
        self.assertEqual(state.amplitudes[0], 1.0 + 0.0j)
        self.assertEqual(state.amplitudes[1], 0.0j)

    def test_11qubit_reversible_roundtrip(self):
        state = Hilbert11State.basis_state(7)
        orig = state.copy()

        circuit = [
            GateOp("H", [0]),
            GateOp("CNOT", [0, 1]),
            GateOp("S", [1]),
            GateOp("CNOT", [1, 5]),
            GateOp("H", [5]),
            GateOp("CNOT", [5, 10]),
            GateOp("X", [10]),
        ]

        # Forward evolution
        Hilbert11Simulator.evolve(state, circuit)
        self.assertTrue(state.is_normalized())
        # Should not be equal to original basis state
        self.assertLess(state_fidelity(orig, state), 0.9)

        # Inverse evolution U^dagger
        Hilbert11Simulator.evolve_inverse(state, circuit)
        self.assertTrue(state.is_normalized())
        fid = state_fidelity(orig, state)
        self.assertAlmostEqual(fid, 1.0, places=6)

    def test_central_adversarial_experiment(self):
        res = run_central_adversarial_experiment()

        # Global observer check:
        # Global states are orthogonal (|overlap|^2 = 0)
        self.assertTrue(res["global_distinguishable"])
        self.assertAlmostEqual(res["global_overlap_fidelity"], 0.0, places=6)

        # Subsystem observer check:
        # Reduced density matrix on qubit 0 is identical (trace distance = 0)
        self.assertFalse(res["subsystem_distinguishable"])
        self.assertAlmostEqual(res["reduced_trace_distance"], 0.0, places=6)

        # Measurement probabilities on qubit 0 are identical [0.5, 0.5]
        p1 = res["observer_probabilities_psi1"]
        p2 = res["observer_probabilities_psi2"]
        self.assertAlmostEqual(p1[0], p2[0], places=6)
        self.assertAlmostEqual(p1[1], p2[1], places=6)


if __name__ == "__main__":
    unittest.main()
