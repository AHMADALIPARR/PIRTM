/*
 * vacuity-demo.als — PIRTM counter-paper, Exhibit A
 *
 * Demonstrates that the verification pattern used in the HCALC Alloy model
 * (github.com/AHMADALIPARR/hcalc) cannot distinguish true claims from false
 * ones, because every "check" asserts a formula already enforced as a fact.
 *
 * Pattern under test (one instance per HCALC check A1-A7, P1-P8, INV_*):
 *   fact  F { P }      -- P enforced on all instances, no counterexample possible
 *   assert A { P }      -- the "verification": is P true in all instances?
 *   check A            -- UNSAT, reported as "PASS"
 *
 * Here P is a claim about the real world that is FALSE. If the pattern still
 * reports UNSAT ("PASS"), the pattern verifies nothing.
 */

module vacuity_demo

-- A false real-world claim, encoded exactly the way HCALC encodes its
-- "source-claims": as an Int flag on a singleton signature.
one sig Moon {
  madeOfCheese: Int
}

-- Step 1, the HCALC move: install the claim as an uncheckable fact.
-- (Compare: hcalc alloy/modules/PrimeIndex.als,
--  "fact A1_declared_cardinality_64 { P64Carrier.declaredCard = 64 }".)
fact claim_as_fact {
  Moon.madeOfCheese = 1
}

-- Step 2, the HCALC "verification": assert the identical formula.
-- (Compare: "assert A1_P64_cardinality_and_distinct { prime_index_integrity }"
--  where prime_index_integrity restates the fact's content.)
assert MoonIsCheese {
  Moon.madeOfCheese = 1
}

check MoonIsCheese for 3
-- EXPECTED: UNSAT. The log will say "no counterexample found".
-- CONCLUSION: the check passed for a false claim. The method is vacuous:
-- it can only ever re-confirm the facts it was given.

-- Control experiment: WITHOUT the fact, the same assertion is refutable.
-- (Uncomment the fact above -> check passes; comment it out -> check fails.
--  That is the whole content of every HCALC "UNSAT (PASS)" line.)
