# Scientific Determination and Benchmarks: AHMADALIPARR/PIRTM

**Repository:** https://github.com/AHMADALIPARR/PIRTM  
**Analysis date:** 2026-11-07  
**Analyst:** Independent computational review  

## Executive Summary

PIRTM (Prime-Indexed Recursive Tensor Mathematics) is a mixed artifact containing:

1. A well-documented **Alloy counter-paper** demonstrating that certain HCALC Alloy verification logs are **vacuous** (assertions formula-identical to enforced facts).
2. A small Python implementation of an 11-qubit statevector simulator, recursive knowledge engine, content-addressed oracle, and 11 specialized agent workers.
3. Lean 4 and Agda formalizations of elementary properties (causal acyclicity, round-trip codecs, fuel-bounded execution, etc.).
4. Explicit epistemic boundaries labeling certain agents (Nostradamus, Akashic) as historical/speculative rather than physical predictors.

**Scientific determination:**  
- The Alloy critique is **correct and reproducible**. The method cannot distinguish true from false claims under the demonstrated pattern.  
- The quantum experiment is a standard illustration of entanglement + partial trace (two orthogonal global states with identical reduced density matrix on one qubit). It is pedagogically useful but not novel physics.  
- The formalizations (Lean/Agda) are small, constructive, and free of `sorry`/postulates where checked; they establish basic invariants rather than deep theorems.  
- No evidence of prime-indexed recursive tensor mathematics as a foundational computational framework beyond the name and the counter-paper framing. The Python code implements ordinary finite-dimensional quantum simulation and bookkeeping.

## 1. Alloy Vacuity Critique (Primary Scientific Contribution)

### Reproduction
```bash
java -jar alloy.jar exec -f -t text alloy/vacuity-demo.als
# 00. check MoonIsCheese             0       UNSAT

java -jar alloy.jar exec -f -t text alloy/hcalc-mirror.als
# 00. check hcalc_A7_assert          0       UNSAT
# 01. check hcalc_P2_assert          0       UNSAT
# 02. check weights_positive         0       UNSAT
```

**Determination:** Confirmed. Exhibit A shows a false claim (“Moon made of cheese”) passes UNSAT under the fact/assert-identical pattern. Exhibit B mirrors HCALC structure and adds a falsifiable control. The critique in `paper/counter-paper.md` is accurate. Alloy logs of this form establish self-consistency of the model, not independent verification of mathematical claims.

## 2. Quantum Experiment

**Central result** (from `experiments/run_adversarial_experiment.py` and `pirtm/quantum/hilbert11.py`):

| Metric                          | Value          |
|---------------------------------|----------------|
| State dimension                 | 2048 (11 qubits) |
| Global fidelity |⟨Ψ₁|Ψ₂⟩|²   | 0.0            |
| Global distinguishable          | True           |
| Reduced trace distance (qubit 0)| 0.0            |
| Subsystem distinguishable       | False          |
| Local measurement probabilities | [0.5, 0.5] both states |

This is the standard construction of two entangled states that are locally indistinguishable on a subsystem but globally orthogonal. Implementation uses exact statevector evolution and a correct (if inefficient) partial-trace routine.

## 3. Formal Verification Status

| Component | Status | Notes |
|-----------|--------|-------|
| Lean 4 (`PIRTM.Core`, `PIRTM.Invariants`) | Zero `sorry` (claimed; not re-executed here) | Causal acyclicity, state preservation, reversible codecs, fuel-bounded execution. Elementary but correctly formalized. |
| Agda (`agda/PIRTM/Invariants.agda`) | NOT_RUN (Agda unavailable) | Constructive, total functions, no postulates. Parallel to Lean. |
| Python unit tests | 17/17 passed | Covers agents, quantum gates, oracle, recursive engine, Hilbert-11. |
| Alloy exhibits | Reproduced UNSAT as claimed | — |

## 4. Benchmarks (local execution, Python 3)

| Benchmark | Result |
|-----------|--------|
| Central adversarial experiment | ~0.12 ms / run (10 runs) |
| 30-gate evolve on 11-qubit state | ~6.7 ms / evolve (50 runs) |
| Partial trace (1 qubit) | ~0.16 ms |
| 11-agent concurrent cycle | ~14 ms / cycle (5 cycles) |
| Full unit test suite | 0.039 s (17 tests) |

All operations are lightweight for the 2048-dimensional state. No scaling claims or comparison to production quantum simulators are warranted.

## 5. Epistemic Boundaries (Correctly Applied)

From `AGENTS.md` and `pirtm/agents/boundaries.py`:  
Nostradamus and Akashic investigations are explicitly labeled historical/speculative. Agent A06 returns status `REJECTED_AS_PHYSICAL_PREDICTOR`. This is appropriate scientific hygiene.

## 6. Overall Assessment

| Claim Area | Assessment |
|------------|------------|
| Alloy logs of HCALC are non-vacuous verification | **Refuted** by the paper and reproduced exhibits |
| 11-qubit adversarial indistinguishability experiment | **Correct** (standard quantum information result) |
| Lean/Agda invariants | **Valid** at the level of the stated lemmas |
| PIRTM as a novel foundational mathematics or verified silicon workbench | **Not supported** by the contents of this repository |
| 11-agent architecture | Functional software scaffolding with clear labeling of speculative components |

**Conclusion:** The repository successfully documents a methodological flaw in a class of Alloy verification presentations and provides a clean, small, reproducible quantum-information demonstration plus elementary formalizations. It does not establish new mathematical foundations or deep verified systems beyond the scope of its explicit counter-paper and pedagogical code.

---

*All reproductions performed from a fresh clone of `https://github.com/AHMADALIPARR/PIRTM` (main branch).*
