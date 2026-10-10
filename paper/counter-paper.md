<!--
  Copyright (C) 2026 Ahmad Ali Parr
  SPDX-License-Identifier: AGPL-3.0-only
-->

# On the Vacuity of Fact/Assert-Identical Verification

## An Alloy counter-paper on the HCALC verification logs

**PIRTM — Prime-Indexed Recursive Tensor Mathematics**
Ahmad Ali Parr · 2026-10-10

---

## 0. Abstract

The HCALC repository (`github.com/AHMADALIPARR/hcalc`) ships Alloy 6.2.0
verification logs in which every check — A1–A7, P1–P8, and ten `INV_*`
invariants — reports `UNSAT (PASS)`. We show that these results are
**vacuous**: in every case we examined, the assertion under check is
formula-identical to (a fragment of) a `fact` already enforced on the
model, so no counterexample is possible by construction. We prove the
method cannot distinguish true claims from false ones by exhibiting a
runnable Alloy model in which a **false** real-world claim passes with
`UNSAT` under the identical pattern. We close by crediting what is
genuinely verified (the Lean 4 formalization: 1968 jobs, zero `sorry`)
and stating what non-vacuous Alloy verification would require.

Nothing in this paper disputes the HCALC *definitions* (PRODUCTION.md).
It disputes what the Alloy logs *establish*.

---

## 1. The claim under test

`hcalc/alloy/logs/alloy-check.txt` (2026-10-07) reports, for Alloy 6.2.0:

```
=== A1-A7 sealed PROPERTY_MAP (UNSAT = pass) ===
A1_P64_cardinality_and_distinct              UNSAT (PASS)
...
A7_production_defined_records                UNSAT (PASS)

=== Production P1-P8 (UNSAT = pass) ===
P1_carrier_linf_dim                          UNSAT (PASS)
...
P8_contractalg_gershgorin_then_c             UNSAT (PASS)

=== INV_* checks (UNSAT = pass) ===
... (10 more) ...
```

The governing note reads: *"UNSAT = PASS for checks"*. The reader is
invited to conclude that Alloy verified the sealed properties. It did
not. It re-confirmed its own input.

---

## 2. The pattern

Every check we inspected follows one shape. Using A7 as the canonical
example (`alloy/HCALC.als`):

```alloy
fact A7_production_all_spec_defined {
  GapRecord_LambdaM.status = SpecDefined
  ...                                   -- P enforced on all instances
}

assert A7_production_defined_records {
  ...
  GapRecord_LambdaM.status = SpecDefined
  ...                                   -- P asserted
}

check A7_production_defined_records     -- UNSAT, logged as "PASS"
```

The `assert` is formula-identical to the `fact`. Alloy's `check`
searches for an instance satisfying all facts and violating the
assertion. The facts *define* the assertion's content, so the search
space of counterexamples is empty *a priori*. `UNSAT` is not a
discovery; it is a restatement of the input.

The same identity holds, verbatim, across the model:

| Check | Fact enforces | Assert restates | File |
|---|---|---|---|
| A1 | `P64Carrier.declaredCard = 64` | `declaredCard = 64` + index ranges | `modules/PrimeIndex.als` |
| P2 | `tp.isDiagonal = 1 ∧ tp.alphaLaw = SpecAlphaLaw` | identical formula | `modules/Transform.als` |
| INV_converge | `convergence_hyps_production` | `convergence_hyps_production` | `modules/Converge.als` |
| A6 | guardian verdict implications | identical implications | `modules/Converge.als` |
| INV_evolution_total | `all s: State \| some t: Time \| t.at = s` | identical formula | `modules/State.als` |
| A7 | all GapRecords `= SpecDefined` | identical conjunction | `HCALC.als` |

In no case does the assertion *derive* anything from independently
modeled structure. In no case could a counterexample exist without
contradicting a fact.

---

## 3. What the flags hide

Even where the pattern were sound, the model checks **flags, not
mathematics**:

- **A1** does not verify 64 primes. It sets the integer constant
  `declaredCard = 64` and checks the constant equals 64. The prime
  *values* are explicitly deferred: *"Numeric prime VALUES remain
  Lean L1; here we only constrain indices 0..63 distinct."* The
  comment is honest; the `UNSAT (PASS)` line is not.
- **P2** does not verify `αⱼ = 1/(1+log p_{j mod 64})`. No logarithm,
  no prime value, no real arithmetic appears in the model.
  `SpecAlphaLaw` is an uninterpreted atom; the check confirms the atom
  is attached where the fact attached it. That is bookkeeping.
- **A2** ("contractive ↔ Gershgorin bound") never computes a
  Gershgorin disc. The operator norm is an `Int` flag.
- **A6** ("guardian rejects spectral_radius ≥ 1") never computes a
  spectral radius. The radius is an `Int` flag (`spectralRadiusGeOne`).

A check that cannot see the mathematics cannot verify the
mathematics. What Alloy verified, at most, is that the flag
bookkeeping is self-consistent — which the facts already guaranteed.

---

## 4. Exhibit A — the method passes a false claim

`alloy/vacuity-demo.als` (runnable, Alloy 6.2.0):

```alloy
one sig Moon { madeOfCheese: Int }

fact claim_as_fact { Moon.madeOfCheese = 1 }   -- the HCALC move

assert MoonIsCheese { Moon.madeOfCheese = 1 }  -- the HCALC "verification"

check MoonIsCheese for 3
```

Result, reproduced 2026-10-10:

```
00. check MoonIsCheese             0       UNSAT
```

The moon is not made of cheese. The check "passed." **Any** claim
installed as a fact passes. The HCALC `UNSAT (PASS)` lines therefore
carry zero bits of information about the world, the primes, the
contraction bounds, or the guardian. They carry exactly one bit: *the
facts were read successfully.*

---

## 5. Exhibit B — structural mirrors of A7 and P2

`alloy/hcalc-mirror.als` reproduces the A7 and P2 fact/assert pairs
with renamed signatures and the identical logical shape, plus a
non-vacuous control:

```
00. check hcalc_A7_assert          0       UNSAT
01. check hcalc_P2_assert          0       UNSAT
02. check weights_positive         0       UNSAT
```

Checks 00 and 01 are the tautologies. Check 02 is different: its fact
models a *generator* (`c.w = 2`, standing in for a computed weight
law) while the assertion (`all c: Cell | c.w > 0`) is *not* among the
facts. Had the generator been `c.w = -5`, Alloy would have produced a
counterexample. **Falsifiability is the difference between
verification and transcription.** Checks 00/01 (and every HCALC check
in §2) lack it; check 02 has it.

---

## 6. What is genuinely verified — credited in full

The Lean 4 formalization is the real thing:

- `lean/build.log`: **build completed successfully (1968 jobs)**
- `grep -rn "sorry"`: **zero** occurrences
- Toolchain pinned: `leanprover/lean4:v4.34.1`

A zero-`sorry` Lean build is machine-checked proof, not bookkeeping.
The convergence lemmas (L5), the `InstanceBridge` non-identity
morphism (L7), and the prime-indexed definitions (L1/L6) stand on this
ground. This paper does not touch them. The flaw is localized
entirely to what the *Alloy logs* are claimed to establish — and,
by extension, to any downstream claim that "Alloy verified" the
sealed properties A1–A7 / P1–P8.

---

## 7. What non-vacuous Alloy verification would require

1. **Facts model generators, not conclusions.** Model the prime list
   (or a faithful finite fragment), the weight-law computation, the
   norm estimates — then assert the *consequences*.
2. **Assertions must be falsifiable in principle.** For each `check`,
   exhibit (or argue) an instance class the facts admit in which the
   assertion fails. If none exists, the check is transcription.
3. **No flag-encoding of the thing to be proved.** An uninterpreted
   atom named `SpecAlphaLaw` cannot verify `αⱼ = 1/(1+log pⱼ)`.
4. **Separate the harness from the honor.** A log line `UNSAT (PASS)`
   must mean "no counterexample exists in scope," not "the fact was
   restated correctly."

---

## 8. Conclusion

The HCALC Alloy logs prove that the HCALC Alloy model is consistent
with itself. They do not verify A1–A7, P1–P8, or any `INV_*`
invariant in any sense that could fail. Exhibit A shows the method
passes false claims; Exhibit B shows the exact structural identity
between HCALC's facts and its assertions, alongside a falsifiable
control that demonstrates what the missing property looks like.

The mathematics may well be correct — the Lean build suggests much
of it is — but correctness *of the definitions* and verification
*by the Alloy logs* are different claims, and only the first is
earned. Until the Alloy model is rewritten so its checks can fail,
every `UNSAT (PASS)` should be read as `TAUTOLOGY (UNINFORMATIVE)`.

---

## Reproduction

```sh
# Exhibits A and B (Alloy 6.2.0, bundled jar):
java -jar alloy.jar exec -f -t text alloy/vacuity-demo.als
java -jar alloy.jar exec -f -t text alloy/hcalc-mirror.als

# Expected:
#   00. check MoonIsCheese             0       UNSAT
#   00. check hcalc_A7_assert          0       UNSAT
#   01. check hcalc_P2_assert          0       UNSAT
#   02. check weights_positive         0       UNSAT
```

Model under test: `github.com/AHMADALIPARR/hcalc` (Alloy sources as of
2026-10-07; log `alloy/logs/alloy-check.txt`).

---

*PIRTM is Prime-Indexed Recursive Tensor Mathematics: the compiler IR
for tensor programs lowering to Goldilocks field arithmetic. This
paper is issued from inside that program, against the HCALC
instantiation's verification claims — not against its definitions,
its Lean proofs, or its authors' mathematics.*
