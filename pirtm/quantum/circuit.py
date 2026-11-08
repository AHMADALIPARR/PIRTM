"""Quantum Circuit Engine and Classical Baseline for PIRTM.

Provides:
- QuantumState representation with normalization validation.
- QuantumCircuit composition (single-qubit gates, CNOT, general n-qubit unitaries).
- Measurement probabilities and state vector evolution.
- Classical comparison baseline: boolean logic simulation of reversible circuits (Toffoli / X / CNOT)
  without superposition to serve as an explicit classical benchmark.
"""

from __future__ import annotations
import math
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from pirtm.quantum.gates import (
    CNOT,
    HADAMARD,
    PAULI_X,
    PAULI_Y,
    PAULI_Z,
    Matrix,
    Vector,
    identity_matrix,
    is_unitary,
    matrix_dim,
    matrix_mult,
    tensor_product,
)


@dataclass
class QuantumState:
    num_qubits: int
    amplitudes: Vector

    def __post_init__(self):
        expected_dim = 1 << self.num_qubits
        if len(self.amplitudes) != expected_dim:
            raise ValueError(
                f"Expected {expected_dim} amplitudes for {self.num_qubits} qubits, got {len(self.amplitudes)}"
            )

    @classmethod
    def computational_basis_zero(cls, num_qubits: int) -> QuantumState:
        """Initialize state |0...0>."""
        dim = 1 << num_qubits
        amps = [1.0 + 0.0j] + [0.0 + 0.0j] * (dim - 1)
        return cls(num_qubits=num_qubits, amplitudes=amps)

    def norm_squared(self) -> float:
        return sum((a.real * a.real + a.imag * a.imag) for a in self.amplitudes)

    def is_normalized(self, tolerance: float = 1e-7) -> bool:
        return abs(self.norm_squared() - 1.0) <= tolerance

    def probabilities(self) -> List[float]:
        """Calculates measurement probabilities |c_i|^2."""
        probs = [(a.real * a.real + a.imag * a.imag) for a in self.amplitudes]
        total = sum(probs)
        if total > 0:
            probs = [p / total for p in probs]
        return probs

    def sample_measurement(self, rng: Optional[random.Random] = None) -> int:
        """Sample computational basis outcome according to Born rule probabilities."""
        r = (rng or random).random()
        cumulative = 0.0
        probs = self.probabilities()
        for idx, p in enumerate(probs):
            cumulative += p
            if r <= cumulative:
                return idx
        return len(probs) - 1


class QuantumCircuit:
    """Finite-dimensional n-qubit quantum circuit simulator."""

    def __init__(self, num_qubits: int):
        if num_qubits < 1:
            raise ValueError("Circuit must have at least 1 qubit")
        self.num_qubits = num_qubits
        self.dim = 1 << num_qubits
        self._gates: List[Tuple[str, List[int], Matrix]] = []

    def apply_single_qubit_gate(self, gate_name: str, target_qubit: int, matrix: Matrix) -> QuantumCircuit:
        """Applies a 2x2 unitary gate to target_qubit (0-indexed, MSB qubit 0)."""
        if not (0 <= target_qubit < self.num_qubits):
            raise IndexError(f"Target qubit {target_qubit} out of range [0, {self.num_qubits - 1}]")
        r, c = matrix_dim(matrix)
        if r != 2 or c != 2:
            raise ValueError(f"Gate {gate_name} must be 2x2")
        self._gates.append((gate_name, [target_qubit], matrix))
        return self

    def h(self, target: int) -> QuantumCircuit:
        return self.apply_single_qubit_gate("H", target, HADAMARD)

    def x(self, target: int) -> QuantumCircuit:
        return self.apply_single_qubit_gate("X", target, PAULI_X)

    def y(self, target: int) -> QuantumCircuit:
        return self.apply_single_qubit_gate("Y", target, PAULI_Y)

    def z(self, target: int) -> QuantumCircuit:
        return self.apply_single_qubit_gate("Z", target, PAULI_Z)

    def cnot(self, control: int, target: int) -> QuantumCircuit:
        """Applies CNOT between control and target qubits."""
        if control == target:
            raise ValueError("Control and target qubits cannot be the same")
        if not (0 <= control < self.num_qubits and 0 <= target < self.num_qubits):
            raise IndexError("Qubit indices out of range")
        self._gates.append(("CNOT", [control, target], CNOT))
        return self

    def _build_full_gate_matrix(self, gate_name: str, qubits: List[int], sub_matrix: Matrix) -> Matrix:
        """Expands a sub-gate acting on specific qubits into full 2^n x 2^n unitary."""
        full_u = [[0.0 + 0.0j for _ in range(self.dim)] for _ in range(self.dim)]

        if len(qubits) == 1:
            target = qubits[0]
            # Bit shift: target is at position (num_qubits - 1 - target)
            bit_pos = self.num_qubits - 1 - target
            for i in range(self.dim):
                bit_val = (i >> bit_pos) & 1
                for new_bit in (0, 1):
                    # Compute output index
                    j = (i & ~(1 << bit_pos)) | (new_bit << bit_pos)
                    full_u[j][i] += sub_matrix[new_bit][bit_val]
        elif len(qubits) == 2 and gate_name == "CNOT":
            ctrl, tgt = qubits[0], qubits[1]
            ctrl_pos = self.num_qubits - 1 - ctrl
            tgt_pos = self.num_qubits - 1 - tgt
            for i in range(self.dim):
                c_val = (i >> ctrl_pos) & 1
                t_val = (i >> tgt_pos) & 1
                if c_val == 1:
                    # Target flips
                    j = i ^ (1 << tgt_pos)
                else:
                    j = i
                full_u[j][i] = 1.0 + 0.0j
        else:
            raise NotImplementedError(f"Unsupported gate expansion: {gate_name}")

        return full_u

    def to_unitary(self) -> Matrix:
        """Computes the total unitary matrix of the circuit."""
        u = identity_matrix(self.dim)
        for name, qubits, mat in self._gates:
            gate_mat = self._build_full_gate_matrix(name, qubits, mat)
            u = matrix_mult(gate_mat, u)
        return u

    def run(self, initial_state: Optional[QuantumState] = None) -> QuantumState:
        """Executes the circuit on an initial state."""
        state = initial_state or QuantumState.computational_basis_zero(self.num_qubits)
        if state.num_qubits != self.num_qubits:
            raise ValueError(f"State qubits {state.num_qubits} != circuit qubits {self.num_qubits}")

        amps = list(state.amplitudes)
        for name, qubits, mat in self._gates:
            gate_mat = self._build_full_gate_matrix(name, qubits, mat)
            # Matrix-vector multiply
            new_amps = [0.0 + 0.0j] * self.dim
            for r in range(self.dim):
                row = gate_mat[r]
                s = sum(row[c] * amps[c] for c in range(self.dim) if row[c] != 0.0)
                new_amps[r] = s
            amps = new_amps

        res = QuantumState(num_qubits=self.num_qubits, amplitudes=amps)
        if not res.is_normalized(tolerance=1e-5):
            raise ValueError("State normalization violated after circuit execution")
        return res


class ClassicalReversibleBaseline:
    """Classical baseline simulator for reversible permutation circuits (no superposition)."""

    def __init__(self, num_bits: int):
        self.num_bits = num_bits
        self.state = [0] * num_bits

    def set_state(self, bitstring: str) -> None:
        if len(bitstring) != self.num_bits:
            raise ValueError("Bitstring length mismatch")
        self.state = [int(c) for c in bitstring]

    def not_gate(self, bit: int) -> None:
        self.state[bit] ^= 1

    def cnot_gate(self, control: int, target: int) -> None:
        if self.state[control] == 1:
            self.state[target] ^= 1

    def toffoli_gate(self, control1: int, control2: int, target: int) -> None:
        if self.state[control1] == 1 and self.state[control2] == 1:
            self.state[target] ^= 1

    def get_state_int(self) -> int:
        val = 0
        for b in self.state:
            val = (val << 1) | b
        return val

    def get_state_string(self) -> str:
        return "".join(str(b) for b in self.state)
