/-
  PIRTM Core Definitions in Lean 4
-/

namespace PIRTM.Core

/-- Strict causal ordering and path definitions. -/
inductive CausalPath : Nat → Nat → Type where
  | direct : ∀ {a b : Nat}, a < b → CausalPath a b
  | step   : ∀ {a b c : Nat}, a < b → CausalPath b c → CausalPath a c

/-- Lemma: CausalPath implies strictly less than. -/
theorem causal_strict : ∀ {a b : Nat}, CausalPath a b → a < b
  | _, _, CausalPath.direct h => h
  | _, _, CausalPath.step h rest => Nat.lt_trans h (causal_strict rest)

/-- Irreflexivity of causal history: no cycle exists. -/
theorem causal_acyclic (n : Nat) : CausalPath n n → False := by
  intro h
  have hlt := causal_strict h
  exact Nat.lt_irrefl n hlt

/-- State preservation model. -/
structure SystemState where
  version : Nat
  wellFormed : Bool

inductive ValidTransition : SystemState → SystemState → Prop where
  | step_valid : ∀ (v : Nat), ValidTransition ⟨v, true⟩ ⟨v + 1, true⟩

theorem state_preservation (s1 s2 : SystemState) :
    s1.wellFormed = true → ValidTransition s1 s2 → s2.wellFormed = true := by
  intro _ htrans
  cases htrans
  rfl

/-- Bounded recursive inference and fixed points. -/
inductive InferenceStep (α : Type) where
  | continue : α → InferenceStep α
  | fixedPoint : α → InferenceStep α

inductive FuelBoundedExecution {α : Type} (step : α → InferenceStep α) : Nat → α → α → Prop where
  | halt_fixed : ∀ (fuel : Nat) (x : α), step x = InferenceStep.fixedPoint x → FuelBoundedExecution step fuel x x
  | halt_exhausted : ∀ (x : α), FuelBoundedExecution step 0 x x
  | recurse : ∀ (fuel : Nat) (x y z : α),
      step x = InferenceStep.continue y →
      FuelBoundedExecution step fuel y z →
      FuelBoundedExecution step (fuel + 1) x z

end PIRTM.Core
