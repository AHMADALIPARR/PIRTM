<!--
  Copyright (C) 2026 Ahmad Ali Parr
  SPDX-License-Identifier: AGPL-3.0-only
-->

# PIRTM

[![License: AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](LICENSE)
[![Alloy 6.2.0](https://img.shields.io/badge/Alloy-6.2.0-orange.svg)](https://alloytools.org/)
[![Reproducible](https://img.shields.io/badge/reproducible-yes-green.svg)](paper/counter-paper.md#reproduction)

**Prime-Indexed Recursive Tensor Mathematics** — a compiler IR for tensor
programs lowering to Goldilocks field arithmetic circuits (`p = 2⁶⁴ − 2³² + 1`).

This repo hosts an Alloy counter-paper against the HCALC verification logs.

---

## The claim, in full

`github.com/AHMADALIPARR/hcalc` ships Alloy 6.2.0 logs reporting
`UNSAT (PASS)` for **A1–A7**, **P1–P8**, and ten **`INV_*`** invariants —
presented as verification of the sealed properties.

**Documented findings** (all reproduced, see
[`paper/counter-paper.md`](paper/counter-paper.md)):

1. **Every assertion is formula-identical to an enforced fact.** A1 asserts
   `declaredCard = 64`; the fact sets `declaredCard = 64`. P2 asserts
   `isDiagonal = 1 ∧ alphaLaw = SpecAlphaLaw`; the fact sets both. Same
   for A6, A7, P4, INV_converge, INV_evolution_total — see §2 of the paper.
2. **The model checks flags, not mathematics.** The 64 primes are an Int
   constant; the "Gershgorin bound" and "operator norm ≤ 1−ε" are Int
   flags (`opBoundOK = 1`); `αⱼ = 1/(1+log pⱼ)` is an uninterpreted atom
   `SpecAlphaLaw`. No prime value, logarithm, or norm is ever computed.
3. **The method cannot distinguish truth from falsehood.** Exhibit A
   (`alloy/vacuity-demo.als`) runs the identical pattern on a **false**
   claim — `Moon.madeOfCheese = 1` — and Alloy returns `UNSAT`.
4. **Falsifiability is what's missing.** Exhibit B
   (`alloy/hcalc-mirror.als`) mirrors the real A7/P2 pairs and adds a
   control check whose fact models a *generator*, not the conclusion —
   the shape a genuine verification takes.
5. **What is NOT disputed:** the HCALC definitions, the mathematics, or
   the Lean 4 formalization (1968 jobs, zero `sorry` — genuine proof,
   credited in full). Only what the *Alloy logs* are claimed to establish.

Until the checks can fail, every `UNSAT (PASS)` reads as
`TAUTOLOGY (UNINFORMATIVE)`.

---

## Reproduce

```sh
java -jar alloy.jar exec -f -t text alloy/vacuity-demo.als
java -jar alloy.jar exec -f -t text alloy/hcalc-mirror.als
```

Alloy 6.2.0 jar bundled. Full argument:
[`paper/counter-paper.md`](paper/counter-paper.md).

## License

[AGPL-3.0-only](LICENSE). Copyright (C) 2026 Ahmad Ali Parr.
