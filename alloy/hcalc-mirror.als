/*
 * hcalc-mirror.als — PIRTM counter-paper, Exhibit B
 *
 * A structural mirror of two real HCALC checks, annotated to show the
 * fact/assert identity. Names and shapes follow the originals:
 *   - A7 (HCALC.als): GapRecord statuses forced to SpecDefined by fact,
 *     then asserted SpecDefined.
 *   - P2 (modules/Transform.als): TpMap flags forced to (1, SpecAlphaLaw)
 *     by fact, then asserted identical.
 *
 * The substantive mathematics (prime values, log weights, operator norms)
 * never enters the Alloy model; it is replaced by Int/enum flags.
 * Alloy therefore checks flag bookkeeping, not mathematics.
 */

module hcalc_mirror

-- ============ Mirror of HCALC A7 ============
abstract sig DefStatus {}
one sig SpecDefined extends DefStatus {}

one sig GapRecord_Tp {
  status: one DefStatus
}

-- Original: "fact A7_production_all_spec_defined { GapRecord_Tp.status = SpecDefined ... }"
fact hcalc_A7_fact {
  GapRecord_Tp.status = SpecDefined
}

-- Original: "assert A7_production_defined_records { ... GapRecord_Tp.status = SpecDefined ... }"
assert hcalc_A7_assert {
  GapRecord_Tp.status = SpecDefined
}

check hcalc_A7_assert for 3
-- UNSAT. Inevitable: the fact admits no instance where status differs.

-- ============ Mirror of HCALC P2 ============
abstract sig AlphaLawKind {}
one sig SpecAlphaLaw extends AlphaLawKind {}

sig TpMap {
  isDiagonal: Int,
  alphaLaw: one AlphaLawKind
}

-- Original: "fact fact_P2_tp_diag_spec_alpha {
--              all tp: TpMap | tp.isDiagonal = 1 and tp.alphaLaw = SpecAlphaLaw }"
fact hcalc_P2_fact {
  all tp: TpMap | tp.isDiagonal = 1 and tp.alphaLaw = SpecAlphaLaw
}

-- Original: "assert P2_tp_diag_spec_alpha { tp_diag_spec_alpha_ok }"
-- where tp_diag_spec_alpha_ok is the identical formula.
assert hcalc_P2_assert {
  all tp: TpMap | tp.isDiagonal = 1 and tp.alphaLaw = SpecAlphaLaw
}

check hcalc_P2_assert for 3
-- UNSAT. Inevitable: same formula as the fact.
--
-- NOTE what is NOT modeled: alpha_j = 1/(1+log p_{j mod 64}).
-- No logarithm, no prime values, no real arithmetic appear anywhere.
-- "SpecAlphaLaw" is an uninterpreted atom. The check confirms the atom
-- is attached where the fact attached it. That is bookkeeping, not proof.

-- ============ What a non-vacuous check would look like ============
-- A real check would DERIVE the flag from independently modeled structure,
-- e.g.: model actual small primes, compute a weight law in Int arithmetic,
-- and assert the diagonal property FOLLOWS. Then a counterexample would be
-- possible in principle, and UNSAT would mean something.
--
-- Minimal sketch (integers stand in for the weight law):
sig Cell { w: Int }

-- Suppose the SPEC claims: every weight is positive.
-- A non-vacuous model does NOT fact this in; it facts the GENERATOR:
fact generator {
  all c: Cell | c.w = 2   -- stand-in for "computed by the weight law"
}
assert weights_positive {
  all c: Cell | c.w > 0
}
check weights_positive for 3
-- UNSAT, and this time it MEANS something: had the generator been
-- "c.w = -5", the check would have found the counterexample.
-- Falsifiability is the difference between verification and transcription.
