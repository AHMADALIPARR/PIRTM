module PIRTM.Core where

-- Foundational types and constructive logic definitions for PIRTM

open import Agda.Primitive using (Level; lzero; lsuc)

-- Identity type
data _≡_ {a : Level} {A : Set a} (x : A) : A → Set a where
  refl : x ≡ x

infix 4 _≡_

-- Empty and Unit types
data ⊥ : Set where

record ⊤ : Set where
  constructor tt

-- Negation
¬ : Set → Set
¬ A = A → ⊥

-- Disjunction and Conjunction
data _⊎_ (A B : Set) : Set where
  inj₁ : A → A ⊎ B
  inj₂ : B → A ⊎ B

record _×_ (A B : Set) : Set where
  constructor _,_
  field
    fst : A
    snd : B

infixr 1 _⊎_
infixr 2 _×_

-- Natural numbers
data ℕ : Set where
  zero : ℕ
  suc  : ℕ → ℕ

{-# BUILTIN NATURAL ℕ #-}

-- Boolean
data Bool : Set where
  true  : Bool
  false : Bool

-- Strict inequality for causal partial ordering
data _<_ : ℕ → ℕ → Set where
  z<s : ∀ {n} → zero < suc n
  s<s : ∀ {m n} → m < n → suc m < suc n

-- Irreflexivity of strict natural order
<-irrefl : ∀ (n : ℕ) → ¬ (n < n)
<-irrefl zero ()
<-irrefl (suc n) (s<s p) = <-irrefl n p

-- Transitivity of strict natural order
<-trans : ∀ {i j k : ℕ} → i < j → j < k → i < k
<-trans z<s (s<s q) = z<s
<-trans (s<s p) (s<s q) = s<s (<-trans p q)

-- Finite strings / token hashes (symbolic model)
data List (A : Set) : Set where
  []  : List A
  _∷_ : A → List A → List A

infixr 5 _∷_

-- Decidable equality wrapper
data Dec (P : Set) : Set where
  yes : P → Dec P
  no  : ¬ P → Dec P
