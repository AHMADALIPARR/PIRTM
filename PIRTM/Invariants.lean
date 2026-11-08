/-
  PIRTM Formal Invariant Lemmas and Proofs in Lean 4
  Every lemma is verified with constructive machine proofs.
-/

import PIRTM.Core

namespace PIRTM.Invariants

open PIRTM.Core

/-- Reversible codec structure. -/
structure ReversibleCodec (α β : Type) where
  encode : α → β
  decode : β → α
  roundtrip : ∀ (x : α), decode (encode x) = x

/-- Lemma I08: Encoder/decoder round-trip correctness. -/
theorem codec_roundtrip_lemma {α β : Type} (codec : ReversibleCodec α β) (x : α) :
    codec.decode (codec.encode x) = x :=
  codec.roundtrip x

/-- Reversible gate operation involution (e.g. Pauli X, H). -/
def bit_flip (b : Bool) : Bool := !b

theorem bit_flip_involutive (b : Bool) : bit_flip (bit_flip b) = b := by
  cases b <;> rfl

/-- Invertible operator structure. -/
structure InvertibleOp (α : Type) where
  forward : α → α
  inverse : α → α
  left_inv : ∀ (x : α), inverse (forward x) = x
  right_inv : ∀ (x : α), forward (inverse x) = x

/-- Composition of invertible operators preserves invertibility. -/
def compose_ops {α : Type} (op1 op2 : InvertibleOp α) : InvertibleOp α where
  forward := op2.forward ∘ op1.forward
  inverse := op1.inverse ∘ op2.inverse
  left_inv := by
    intro x
    simp [Function.comp]
    rw [op2.left_inv]
    rw [op1.left_inv]
  right_inv := by
    intro x
    simp [Function.comp]
    rw [op1.right_inv]
    rw [op2.right_inv]

/-- Observation Boundary: Non-injective projection cannot uniquely invert. -/
structure NonInjectiveMap (Bulk Boundary : Type) where
  project : Bulk → Boundary
  w1 : Bulk
  w2 : Bulk
  distinct : w1 ≠ w2
  collapse : project w1 = project w2

theorem observation_non_unique {Bulk Boundary : Type}
    (obs : NonInjectiveMap Bulk Boundary) (reconstruct : Boundary → Bulk) :
    ¬ (∀ (b : Bulk), reconstruct (obs.project b) = b) := by
  intro h_all
  have h1 : reconstruct (obs.project obs.w1) = obs.w1 := h_all obs.w1
  have h2 : reconstruct (obs.project obs.w2) = obs.w2 := h_all obs.w2
  have h_coll : reconstruct (obs.project obs.w1) = reconstruct (obs.project obs.w2) := by
    rw [obs.collapse]
  have h_eq : obs.w1 = obs.w2 := by
    rw [← h1, ← h2, h_coll]
  exact obs.distinct h_eq

/-- Central Adversarial Lemma:
    Two distinct states with identical projection to a restricted observer.
    Restricted observer cannot distinguish them; complete observer distinguishes them. -/
structure AdversarialStates (Global Subsystem : Type) where
  psi1 : Global
  psi2 : Global
  global_distinct : psi1 ≠ psi2
  local_obs : Global → Subsystem
  local_identical : local_obs psi1 = local_obs psi2

theorem adversarial_subsystem_indistinguishable {Global Subsystem : Type}
    (adv : AdversarialStates Global Subsystem) (local_measurement : Subsystem → Bool) :
    local_measurement (adv.local_obs adv.psi1) = local_measurement (adv.local_obs adv.psi2) := by
  rw [adv.local_identical]

theorem adversarial_global_distinguishable {Global Subsystem : Type}
    (adv : AdversarialStates Global Subsystem) :
    adv.psi1 ≠ adv.psi2 :=
  adv.global_distinct

/-- Deterministic aggregation preserves worker isolation. -/
structure WorkerResult where
  agent_id : Nat
  payload : Nat

theorem worker_isolation_lemma (r1 r2 : WorkerResult) :
    r1.agent_id ≠ r2.agent_id → r1 ≠ r2 := by
  intro h_id h_eq
  subst h_eq
  exact h_id rfl

end PIRTM.Invariants
