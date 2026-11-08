/-
  PIRTM: 11-Coordinate Quantum State Space & 11 Reasoning Worker Models in Lean 4
-/

import PIRTM.Core

namespace PIRTM.Quantum11

/-- 11 coordinates represented as Fin 11. -/
def Coord11 := Fin 11

/-- Total dimension of (C^2)^{\otimes 11} is 2^11 = 2048. -/
def StateDim : Nat := 2048

theorem state_dim_eq : 2 ^ 11 = StateDim := by
  rfl

/-- Single qubit discrete gate alphabet: Identity, Pauli X, Pauli Z, Hadamard. -/
inductive Gate11 where
  | id   : Coord11 → Gate11
  | x    : Coord11 → Gate11
  | z    : Coord11 → Gate11
  | h    : Coord11 → Gate11
  | cnot : Coord11 → Coord11 → Gate11

/-- Exact inverse gate mapping. -/
def gate_inverse : Gate11 → Gate11
  | Gate11.id q => Gate11.id q
  | Gate11.x q => Gate11.x q
  | Gate11.z q => Gate11.z q
  | Gate11.h q => Gate11.h q
  | Gate11.cnot c t => Gate11.cnot c t

/-- Every basic quantum gate in our alphabet is its own inverse (self-adjoint involution). -/
theorem gate_inv_self (g : Gate11) : gate_inverse (gate_inverse g) = g := by
  cases g <;> rfl

/-- Circuit is a sequence of gates. -/
abbrev Circuit11 := List Gate11

def circuit_inverse (c : Circuit11) : Circuit11 :=
  c.reverse.map gate_inverse

theorem circuit_inverse_involutive (c : Circuit11) :
    circuit_inverse (circuit_inverse c) = c := by
  dsimp [circuit_inverse]
  have h1 : ∀ (l : List Gate11), List.map gate_inverse (List.map gate_inverse l) = l := by
    intro l
    induction l with
    | nil => rfl
    | cons g rest ih =>
      simp [gate_inv_self g, ih]
  rw [List.map_reverse]
  rw [h1]
  exact List.reverse_reverse c

/-- 11-worker role decomposition modeled constructively. -/
inductive WorkerRole where
  | A01_temporal
  | A02_reversible
  | A03_coords
  | A04_measurement
  | A05_encoding
  | A06_ambiguity
  | A07_recursive
  | A08_restricted_observer
  | A09_entropy
  | A10_agda
  | A11_adversarial

def worker_count : Nat := 11

def worker_index : WorkerRole → Fin 11
  | .A01_temporal => ⟨0, by decide⟩
  | .A02_reversible => ⟨1, by decide⟩
  | .A03_coords => ⟨2, by decide⟩
  | .A04_measurement => ⟨3, by decide⟩
  | .A05_encoding => ⟨4, by decide⟩
  | .A06_ambiguity => ⟨5, by decide⟩
  | .A07_recursive => ⟨6, by decide⟩
  | .A08_restricted_observer => ⟨7, by decide⟩
  | .A09_entropy => ⟨8, by decide⟩
  | .A10_agda => ⟨9, by decide⟩
  | .A11_adversarial => ⟨10, by decide⟩

theorem worker_roles_distinct (w1 w2 : WorkerRole) :
    worker_index w1 = worker_index w2 → w1 = w2 := by
  intro h
  cases w1 <;> cases w2 <;> first | rfl | contradiction

end PIRTM.Quantum11
