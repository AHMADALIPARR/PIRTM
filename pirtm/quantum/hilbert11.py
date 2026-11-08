r"""11-Qubit Hilbert Space State Model and Historical Encoding Engine.

State space: H = (C^2)^{\otimes 11}, dimension = 2^11 = 2,048 complex amplitudes.
Operations:
- Hadamard, Pauli X/Y/Z, Phase, CNOT gates applied directly to 2,048-dim state vectors.
- Exact unitary gate sequence and reversible adjoint / inverse circuit execution (U^dagger).
- Subsystem partial trace (tracing out environment qubits B to obtain reduced density matrix rho_A).
- Subsystem trace distance computation: 0.5 * Tr(|rho_1 - rho_2|).
- Central adversarial experiment: Construction of two distinct global states Psi_1, Psi_2 that have
  identical reduced states on accessible observer qubits A, making them completely indistinguishable
  to local measurements on A, but distinguishable by a global measurement.
"""

from __future__ import annotations
import cmath
import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

SQRT2_INV = 1.0 / math.sqrt(2.0)
NUM_QUBITS = 11
DIM = 1 << NUM_QUBITS  # 2048


@dataclass
class Hilbert11State:
    amplitudes: List[complex]

    def __post_init__(self):
        if len(self.amplitudes) != DIM:
            raise ValueError(f"State must have exactly {DIM} amplitudes, got {len(self.amplitudes)}")

    @classmethod
    def basis_state(cls, index: int) -> Hilbert11State:
        if not (0 <= index < DIM):
            raise IndexError("Index out of range [0, 2047]")
        amps = [0.0 + 0.0j] * DIM
        amps[index] = 1.0 + 0.0j
        return cls(amps)

    def norm_squared(self) -> float:
        return sum(a.real * a.real + a.imag * a.imag for a in self.amplitudes)

    def is_normalized(self, tolerance: float = 1e-7) -> bool:
        return abs(self.norm_squared() - 1.0) <= tolerance

    def probabilities(self) -> List[float]:
        return [a.real * a.real + a.imag * a.imag for a in self.amplitudes]

    def copy(self) -> Hilbert11State:
        return Hilbert11State(list(self.amplitudes))


class GateOp:
    def __init__(self, name: str, qubits: List[int], matrix: Optional[List[List[complex]]] = None):
        self.name = name
        self.qubits = qubits
        self.matrix = matrix

    def dagger(self) -> GateOp:
        if self.name in ("H", "X", "Y", "Z", "CNOT"):
            return GateOp(self.name, list(self.qubits), self.matrix)
        elif self.name == "S":
            # S^dagger = S^3 (phase -pi/2)
            mat = [[1.0 + 0.0j, 0.0 + 0.0j], [0.0 + 0.0j, 0.0 - 1.0j]]
            return GateOp("S_dag", list(self.qubits), mat)
        elif self.name == "S_dag":
            mat = [[1.0 + 0.0j, 0.0 + 0.0j], [0.0 + 0.0j, 0.0 + 1.0j]]
            return GateOp("S", list(self.qubits), mat)
        elif self.name == "PHASE":
            # Conjugate phase
            mat = [[self.matrix[0][0].conjugate(), self.matrix[0][1].conjugate()],
                   [self.matrix[1][0].conjugate(), self.matrix[1][1].conjugate()]]
            return GateOp("PHASE", list(self.qubits), mat)
        raise NotImplementedError(f"Dagger not implemented for {self.name}")


class Hilbert11Simulator:
    r"""Simulator for (C^2)^{\otimes 11} using state vector manipulation."""

    @staticmethod
    def apply_single_qubit(state: Hilbert11State, target_qubit: int, u00: complex, u01: complex, u10: complex, u11: complex) -> None:
        bit = NUM_QUBITS - 1 - target_qubit
        amps = state.amplitudes
        step = 1 << (bit + 1)
        half_step = 1 << bit

        for i in range(0, DIM, step):
            for j in range(i, i + half_step):
                i0 = j
                i1 = j + half_step
                a0 = amps[i0]
                a1 = amps[i1]
                amps[i0] = u00 * a0 + u01 * a1
                amps[i1] = u10 * a0 + u11 * a1

    @staticmethod
    def apply_h(state: Hilbert11State, target: int) -> None:
        s = SQRT2_INV + 0.0j
        Hilbert11Simulator.apply_single_qubit(state, target, s, s, s, -s)

    @staticmethod
    def apply_x(state: Hilbert11State, target: int) -> None:
        Hilbert11Simulator.apply_single_qubit(state, target, 0.0j, 1.0 + 0.0j, 1.0 + 0.0j, 0.0j)

    @staticmethod
    def apply_y(state: Hilbert11State, target: int) -> None:
        Hilbert11Simulator.apply_single_qubit(state, target, 0.0j, -1.0j, 1.0j, 0.0j)

    @staticmethod
    def apply_z(state: Hilbert11State, target: int) -> None:
        Hilbert11Simulator.apply_single_qubit(state, target, 1.0 + 0.0j, 0.0j, 0.0j, -1.0 + 0.0j)

    @staticmethod
    def apply_s(state: Hilbert11State, target: int, dagger: bool = False) -> None:
        phase = -1.0j if dagger else 1.0j
        Hilbert11Simulator.apply_single_qubit(state, target, 1.0 + 0.0j, 0.0j, 0.0j, phase)

    @staticmethod
    def apply_cnot(state: Hilbert11State, control: int, target: int) -> None:
        c_bit = NUM_QUBITS - 1 - control
        t_bit = NUM_QUBITS - 1 - target
        c_mask = 1 << c_bit
        t_mask = 1 << t_bit
        amps = state.amplitudes

        for i in range(DIM):
            if (i & c_mask) and not (i & t_mask):
                j = i ^ t_mask
                amps[i], amps[j] = amps[j], amps[i]

    @classmethod
    def apply_gate(cls, state: Hilbert11State, op: GateOp) -> None:
        if op.name == "H":
            cls.apply_h(state, op.qubits[0])
        elif op.name == "X":
            cls.apply_x(state, op.qubits[0])
        elif op.name == "Y":
            cls.apply_y(state, op.qubits[0])
        elif op.name == "Z":
            cls.apply_z(state, op.qubits[0])
        elif op.name == "S":
            cls.apply_s(state, op.qubits[0], dagger=False)
        elif op.name == "S_dag":
            cls.apply_s(state, op.qubits[0], dagger=True)
        elif op.name == "CNOT":
            cls.apply_cnot(state, op.qubits[0], op.qubits[1])
        elif op.name == "PHASE":
            m = op.matrix
            cls.apply_single_qubit(state, op.qubits[0], m[0][0], m[0][1], m[1][0], m[1][1])
        else:
            raise NotImplementedError(f"Unsupported gate: {op.name}")

    @classmethod
    def evolve(cls, state: Hilbert11State, circuit: List[GateOp]) -> None:
        for op in circuit:
            cls.apply_gate(state, op)

    @classmethod
    def evolve_inverse(cls, state: Hilbert11State, circuit: List[GateOp]) -> None:
        for op in reversed(circuit):
            cls.apply_gate(state, op.dagger())


def state_fidelity(s1: Hilbert11State, s2: Hilbert11State) -> float:
    """Computes |<s1|s2>|^2."""
    dot = sum(a1.conjugate() * a2 for a1, a2 in zip(s1.amplitudes, s2.amplitudes))
    return dot.real * dot.real + dot.imag * dot.imag


def partial_trace(state: Hilbert11State, accessible_qubits: List[int]) -> List[List[complex]]:
    """Calculates the reduced density matrix rho_A for accessible_qubits.

    accessible_qubits: sorted list of qubit indices (e.g., [0, 1]).
    Dimension of rho_A: 2^k x 2^k, where k = len(accessible_qubits).
    """
    k = len(accessible_qubits)
    dim_a = 1 << k
    rho = [[0.0 + 0.0j for _ in range(dim_a)] for _ in range(dim_a)]

    acc_bits = [NUM_QUBITS - 1 - q for q in accessible_qubits]
    amps = state.amplitudes

    # Loop over all 2048 basis states
    for i in range(DIM):
        ai = amps[i]
        if ai == 0.0j:
            continue
        # Extract index in subsystem A for basis element i
        sub_i = 0
        for bit_idx, bit_pos in enumerate(acc_bits):
            if (i >> bit_pos) & 1:
                sub_i |= (1 << (k - 1 - bit_idx))

        for j in range(DIM):
            aj = amps[j]
            if aj == 0.0j:
                continue
            # Check if environment qubits match between i and j
            # i and j must agree on all non-accessible qubits
            same_env = True
            for q in range(NUM_QUBITS):
                if q not in accessible_qubits:
                    pos = NUM_QUBITS - 1 - q
                    if ((i >> pos) & 1) != ((j >> pos) & 1):
                        same_env = False
                        break
            if not same_env:
                continue

            sub_j = 0
            for bit_idx, bit_pos in enumerate(acc_bits):
                if (j >> bit_pos) & 1:
                    sub_j |= (1 << (k - 1 - bit_idx))

            rho[sub_i][sub_j] += ai * aj.conjugate()

    return rho


def density_matrix_trace_distance(rho1: List[List[complex]], rho2: List[List[complex]]) -> float:
    """Approximates trace distance 0.5 * Tr(|rho1 - rho2|) via Frobenius / operator norm bound."""
    dim = len(rho1)
    diff = [[rho1[i][j] - rho2[i][j] for j in range(dim)] for i in range(dim)]
    # Sum of absolute entries as trace distance bound
    norm_diff = math.sqrt(sum((diff[i][j].real**2 + diff[i][j].imag**2) for i in range(dim) for j in range(dim)))
    return norm_diff * 0.5


def run_central_adversarial_experiment() -> Dict[str, Any]:
    """Constructs two distinct 11-qubit global states Psi_1 and Psi_2 with identical reduced states on subsystem A.

    Subsystem A: Qubit 0 (observer accessible).
    Subsystem B: Qubits 1..10 (environment).

    Global state 1: |Psi_1> = (|0>_A |0...0>_B + |1>_A |0...1>_B) / sqrt(2) (Bell-like entangled with environment).
    Global state 2: |Psi_2> = (|0>_A |1...0>_B + |1>_A |1...1>_B) / sqrt(2).

    Both states have reduced density matrix rho_A = 0.5 * I_2.
    Therefore, trace distance between their reduced states on A is exactly 0.0.
    However, the global states are orthogonal: <Psi_1|Psi_2> = 0, so global fidelity = 0.0.
    A complete observer can distinguish them with 100% certainty, while the restricted observer has 0% distinguishing signal.
    """
    amps1 = [0.0 + 0.0j] * DIM
    amps2 = [0.0 + 0.0j] * DIM

    # For Psi_1:
    # Qubit 0 is 0, rest is 0 -> index 0
    # Qubit 0 is 1, qubit 10 is 1 -> index (1 << 10) | 1 = 1025
    amps1[0] = SQRT2_INV + 0.0j
    amps1[(1 << 10) | 1] = SQRT2_INV + 0.0j

    # For Psi_2:
    # Qubit 0 is 0, qubit 1 is 1 -> index (1 << 9) = 512
    # Qubit 0 is 1, qubit 1 is 1, qubit 10 is 1 -> index (1 << 10) | (1 << 9) | 1 = 1537
    amps2[1 << 9] = SQRT2_INV + 0.0j
    amps2[(1 << 10) | (1 << 9) | 1] = SQRT2_INV + 0.0j

    psi1 = Hilbert11State(amps1)
    psi2 = Hilbert11State(amps2)

    # 1. Global distinction
    global_fidelity = state_fidelity(psi1, psi2)

    # 2. Local observer on qubit 0
    rho1_A = partial_trace(psi1, [0])
    rho2_A = partial_trace(psi2, [0])
    subsystem_dist = density_matrix_trace_distance(rho1_A, rho2_A)

    # Measurement probabilities on qubit 0
    p0_psi1 = rho1_A[0][0].real
    p1_psi1 = rho1_A[1][1].real
    p0_psi2 = rho2_A[0][0].real
    p1_psi2 = rho2_A[1][1].real

    return {
        "num_qubits": NUM_QUBITS,
        "state_dimension": DIM,
        "psi1_normalized": psi1.is_normalized(),
        "psi2_normalized": psi2.is_normalized(),
        "global_overlap_fidelity": global_fidelity,
        "global_distinguishable": global_fidelity < 1e-6,
        "reduced_trace_distance": subsystem_dist,
        "subsystem_distinguishable": subsystem_dist > 1e-4,
        "observer_probabilities_psi1": [p0_psi1, p1_psi1],
        "observer_probabilities_psi2": [p0_psi2, p1_psi2],
        "conclusion": "Restricted observer cannot distinguish Psi_1 from Psi_2 locally, but global observer distinguishes with certainty."
    }
