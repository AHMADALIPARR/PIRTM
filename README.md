<!--
  Copyright (C) 2026 Ahmad Ali Parr
  SPDX-License-Identifier: AGPL-3.0-only
-->

# PIRTM

**Prime-Indexed Recursive Tensor Mathematics** — a compiler IR for tensor
programs lowering to Goldilocks field arithmetic circuits (`p = 2⁶⁴ − 2³² + 1`).

## This repo calls out: the HCALC Alloy verification logs

`github.com/AHMADALIPARR/hcalc` ships Alloy 6.2.0 logs where every check
(A1–A7, P1–P8, ten `INV_*` invariants) reports `UNSAT (PASS)` — presented
as verification of the sealed properties.

**The flaw:** every assertion is formula-identical to a `fact` already
enforced on the model. Alloy searches for instances satisfying the facts
and violating the assertion; the facts *define* the assertion's content,
so no counterexample can exist by construction. `UNSAT` here means "the
facts were read successfully," not "the property was verified."

We prove the method is vacuous, not just suspicious:

- **Exhibit A** (`alloy/vacuity-demo.als`): the exact HCALC pattern —
  `fact { Moon.madeOfCheese = 1 }`, `assert { Moon.madeOfCheese = 1 }` —
  returns `UNSAT` for a **false** claim. The method cannot distinguish
  truth from falsehood.
- **Exhibit B** (`alloy/hcalc-mirror.als`): structural mirrors of the
  real HCALC A7 and P2 fact/assert pairs, plus a falsifiable control
  showing what a real check looks like.

The full argument is in [`paper/counter-paper.md`](paper/counter-paper.md).

## What we are NOT disputing

- The HCALC **definitions** (PRODUCTION.md) — the nested recurrence,
  the prime-indexed weights, the `InstanceBridge` non-identity morphism.
- The **Lean 4** formalization: 1968 jobs built, zero `sorry`. That is
  genuine machine-checked proof, and it stands.
- The author's mathematics. The flaw is in what the *Alloy logs* are
  claimed to establish — nothing else.

## Reproduce it

```sh
java -jar alloy.jar exec -f -t text alloy/vacuity-demo.als
java -jar alloy.jar exec -f -t text alloy/hcalc-mirror.als
```

Alloy 6.2.0 jar bundled. Expected: every check `UNSAT` — including the
false claim. That is the point.

## License

AGPL-3.0-only. See [LICENSE](LICENSE).
