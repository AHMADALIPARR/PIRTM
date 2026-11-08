"""Quantum Gate Representations and Matrix Operations for PIRTM.

Provides:
- Hadamard (H)
- Pauli X, Y, Z
- Phase (S, T, arbitrary phase R_phi)
- Controlled-NOT (CNOT)
- Matrix multiplication, dagger (conjugate transpose), tensor products (Kronecker product)
- Unitarity checks with explicit numeric tolerance specifications.
"""

from __future__ import annotations
import cmath
import math
from typing import List

# Matrix type alias: 2D list of complex numbers
Matrix = List[List[complex]]
Vector = List[complex]


def matrix_dim(m: Matrix) -> tuple[int, int]:
    return len(m), len(m[0]) if m else 0


def identity_matrix(n: int) -> Matrix:
    return [[1.0 + 0.0j if i == j else 0.0 + 0.0j for j in range(n)] for i in range(n)]


def matrix_mult(a: Matrix, b: Matrix) -> Matrix:
    ra, ca = matrix_dim(a)
    rb, cb = matrix_dim(b)
    if ca != rb:
        raise ValueError(f"Matrix dimension mismatch for multiplication: ({ra}x{ca}) vs ({rb}x{cb})")
    out = [[0.0 + 0.0j for _ in range(cb)] for _ in range(ra)]
    for i in range(ra):
        for k in range(ca):
            aik = a[i][k]
            if aik == 0.0:
                continue
            for j in range(cb):
                out[i][j] += aik * b[k][j]
    return out


def matrix_dagger(m: Matrix) -> Matrix:
    """Conjugate transpose."""
    r, c = matrix_dim(m)
    return [[m[j][i].conjugate() for j in range(r)] for i in range(c)]


def tensor_product(a: Matrix, b: Matrix) -> Matrix:
    """Kronecker tensor product of two matrices."""
    ra, ca = matrix_dim(a)
    rb, cb = matrix_dim(b)
    out = [[0.0 + 0.0j for _ in range(ca * cb)] for _ in range(ra * rb)]
    for i in range(ra):
        for j in range(ca):
            for k in range(rb):
                for l in range(cb):
                    out[i * rb + k][j * cb + l] = a[i][j] * b[k][l]
    return out


def is_unitary(m: Matrix, tolerance: float = 1e-9) -> bool:
    """Check if M * M^† = I within numerical tolerance."""
    r, c = matrix_dim(m)
    if r != c:
        return False
    m_dag = matrix_dagger(m)
    prod = matrix_mult(m, m_dag)
    for i in range(r):
        for j in range(c):
            expected = 1.0 if i == j else 0.0
            diff = abs(prod[i][j] - expected)
            if diff > tolerance:
                return False
    return True


# Standard single-qubit gates
SQRT2_INV = 1.0 / math.sqrt(2.0)

HADAMARD: Matrix = [
    [SQRT2_INV + 0.0j, SQRT2_INV + 0.0j],
    [SQRT2_INV + 0.0j, -SQRT2_INV + 0.0j],
]

PAULI_X: Matrix = [
    [0.0 + 0.0j, 1.0 + 0.0j],
    [1.0 + 0.0j, 0.0 + 0.0j],
]

PAULI_Y: Matrix = [
    [0.0 + 0.0j, 0.0 - 1.0j],
    [0.0 + 1.0j, 0.0 + 0.0j],
]

PAULI_Z: Matrix = [
    [1.0 + 0.0j, 0.0 + 0.0j],
    [0.0 + 0.0j, -1.0 + 0.0j],
]

PHASE_S: Matrix = [
    [1.0 + 0.0j, 0.0 + 0.0j],
    [0.0 + 0.0j, 0.0 + 1.0j],
]

PHASE_T: Matrix = [
    [1.0 + 0.0j, 0.0 + 0.0j],
    [0.0 + 0.0j, cmath.exp(1j * math.pi / 4.0)],
]


def phase_gate(phi: float) -> Matrix:
    """Arbitrary single-qubit phase gate R(phi)."""
    return [
        [1.0 + 0.0j, 0.0 + 0.0j],
        [0.0 + 0.0j, cmath.exp(1j * phi)],
    ]


CNOT: Matrix = [
    [1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
    [0.0 + 0.0j, 1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
    [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 1.0 + 0.0j],
    [0.0 + 0.0j, 0.0 + 0.0j, 1.0 + 0.0j, 0.0 + 0.0j],
]
