module PIRTM.Assumptions where

-- Explicitly isolated mathematical assumptions and idealized abstractions.
-- In accordance with PIRTM guidelines:
-- Do not confuse mathematical proof of a toy model with experimental confirmation of a physical theory.

open import PIRTM.Core

-- Continuous real field and Hilbert space inner product assumptions
-- (isolated for finite-dimensional unitary models)
record ComplexInnerSpace : Set₁ where
  field
    Carrier : Set
    _inner_ : Carrier → Carrier → ℕ  -- Discrete/rational proxy inner product for finite dimension
    positiveDefinite : ∀ (v : Carrier) → (v inner v ≡ zero) → v ≡ v

-- Bulk/boundary correspondence boundary capacity assumption
record HolographicBoundAssumption : Set where
  field
    BulkDimension     : ℕ
    BoundaryDimension : ℕ
    boundDimensionLe  : BoundaryDimension < suc BulkDimension
