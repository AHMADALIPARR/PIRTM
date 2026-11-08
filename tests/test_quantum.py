"""Unit tests for PIRTM Quantum Circuit Engine and Gates."""

import math
import unittest
from pirtm.quantum.circuit import (
    ClassicalReversibleBaseline,
    QuantumCircuit,
    QuantumState,
)
from pirtm.quantum.gates import (
    CNOT,
    HADAMARD,
    PAULI_X,
    PAULI_Y,
    PAULI_Z,
    PHASE_S,
    PHASE_T,
    is_unitary,
    matrix_mult,
    tensor_product,
)


class TestQuantumCircuit(unittest.TestCase):
    def test_single_qubit_unitarity(self):
        for name, gate in [
            ("H", HADAMARD),
            ("X", PAULI_X),
            ("Y", PAULI_Y),
            ("Z", PAULI_Z),
            ("S", PHASE_S),
            ("T", PHASE_T),
        ]:
            self.assertTrue(is_unitary(gate), f"Gate {name} failed unitarity check")

    def test_cnot_unitarity(self):
        self.assertTrue(is_unitary(CNOT), "CNOT gate failed unitarity check")

    def test_bell_state_generation(self):
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cnot(0, 1)

        u = qc.to_unitary()
        self.assertTrue(is_unitary(u))

        out_state = qc.run()
        self.assertTrue(out_state.is_normalized())
        probs = out_state.probabilities()
        self.assertAlmostEqual(probs[0], 0.5, places=5)
        self.assertAlmostEqual(probs[1], 0.0, places=5)
        self.assertAlmostEqual(probs[2], 0.0, places=5)
        self.assertAlmostEqual(probs[3], 0.5, places=5)

    def test_pauli_algebra_and_tensor(self):
        # X * X = I
        x_sq = matrix_mult(PAULI_X, PAULI_X)
        self.assertAlmostEqual(x_sq[0][0].real, 1.0)
        self.assertAlmostEqual(x_sq[0][1].real, 0.0)
        self.assertAlmostEqual(x_sq[1][0].real, 0.0)
        self.assertAlmostEqual(x_sq[1][1].real, 1.0)

        # Tensor product dimension
        h_kron_x = tensor_product(HADAMARD, PAULI_X)
        self.assertEqual(len(h_kron_x), 4)
        self.assertEqual(len(h_kron_x[0]), 4)
        self.assertTrue(is_unitary(h_kron_x))

    def test_classical_reversible_baseline(self):
        cr = ClassicalReversibleBaseline(3)
        cr.set_state("101")
        self.assertEqual(cr.get_state_string(), "101")
        cr.not_gate(1)
        self.assertEqual(cr.get_state_string(), "111")
        cr.toffoli_gate(0, 1, 2)  # 1 and 1 -> flip bit 2: 1 -> 0
        self.assertEqual(cr.get_state_string(), "110")


if __name__ == "__main__":
    unittest.main()
