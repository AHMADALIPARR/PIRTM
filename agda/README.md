# Agda Formal Invariants: PIRTM Ω-AKASHA XI

This directory hosts the formal Agda specification modules for PIRTM invariants:

- `PIRTM/Core.agda`: Constructive foundational types, equality, natural numbers, orderings, and logic.
- `PIRTM/Assumptions.agda`: Genuinely necessary mathematical assumptions and continuum / infinite-capacity boundaries, explicitly isolated from constructive proofs.
- `PIRTM/Invariants.agda`: Mechanically checkable formal invariant proofs I01 through I11:
  - **I01 — State preservation**: Valid transitions preserve well-formedness.
  - **I02 — Causal ordering**: A strictly ordered causal history cannot contain a cycle.
  - **I03 — Provenance integrity**: Every referenced artifact has a resolvable provenance entry.
  - **I04 — Immutability**: Published artifact versions are not silently overwritten.
  - **I05 — Termination**: Recursive inference consumes bounded fuel or reaches a defined fixed point.
  - **I06 — Quantum unitarity**: Supported exact gate representations preserve inner products.
  - **I07 — Probability normalization**: Supported quantum measurements produce normalized probabilities.
  - **I08 — Encoding integrity**: A decoder correctly reconstructs values within its formally specified reversible domain.
  - **I09 — Observation boundaries**: Non-injective observation maps cannot uniquely reconstruct arbitrary inputs.
  - **I10 — Agent isolation**: Independent agent results remain distinguishable during integration.
  - **I11 — Evidence classification**: Claims cannot acquire a verified status without the required certificate.

## Verification Status and Commands

Current environment status:
- `agda`: `NOT_RUN` (binary not found in sandbox environment).

To type-check the Agda modules when an Agda installation is available:

```bash
agda --no-libraries -i . PIRTM/Invariants.agda
```

All functions use total functions, explicit types, structural recursion, and constructive proofs without `postulate`, `{-# TERMINATING #-}`, unresolved metas (`?`), or fabricated certificates.
