# AGENTS.md — PIRTM Eleven-Agent Execution Contract

## Architecture Overview

PIRTM implements an 11-worker logical decomposition operating over isolated namespaces with content-addressed provenance and deterministic merge contracts.

### Worker Roles

| ID | Domain | Required Implementation | Module |
|---|---|---|---|
| **A01** | Temporal causality | Event graphs, partial orders, temporal constraints | `pirtm/agents/workers.py` |
| **A02** | String theory | Finite symbolic worldsheet-inspired models | `pirtm/agents/workers.py` |
| **A03** | M-theory | 11-coordinate state representation and operators | `pirtm/agents/workers.py` |
| **A04** | Quantum circuits | Gate matrices, composition, measurement | `pirtm/agents/workers.py` |
| **A05** | Akashic hypothesis | Historical encoding and reconstruction models (metaphysical hypothesis) | `pirtm/agents/workers.py` |
| **A06** | Nostradamus analysis | Historical text parsing and blind evaluation (historical/speculative) | `pirtm/agents/workers.py` |
| **A07** | Recursive reasoning | Hypothesis updates and bounded fixed points | `pirtm/agents/workers.py` |
| **A08** | Holography | Finite-dimensional bulk/boundary encoding | `pirtm/agents/workers.py` |
| **A09** | Information theory | Entropy, reversible maps, information bounds | `pirtm/agents/workers.py` |
| **A10** | Agda verification | Definitions, invariants, proof obligations | `pirtm/agents/workers.py` |
| **A11** | Adversarial verification | Countermodels, contradictions, falsification | `pirtm/agents/workers.py` |

---

## Block 7 Reporting Contract

Every worker emits reports conforming strictly to the following JSON schema:

```json
{
  "agent": "A04",
  "block": 4,
  "artifacts": ["<sha256-hash>"],
  "invariants": ["I06 — Quantum unitarity"],
  "tests": {
    "passed": 3,
    "failed": 0,
    "not_run": 0
  },
  "proof_status": "VERIFIED_LOCALLY",
  "oracle_references": ["<sha256-hash>"],
  "blockers": [],
  "next_action": "..."
}
```

---

## Formal Invariants (Agda)

Foundational definitions and constructive invariant proofs I01–I11 are located in `agda/PIRTM/Invariants.agda`.
If Agda CLI is unavailable in the environment, proof status is strictly recorded as `NOT_RUN` (never fabricated).

---

## Scientific and Metaphysical Boundaries

Nostradamus writings and Akashic Records are historical or metaphysical subjects, not established mechanisms for quantum prediction. All such investigations are tracked under explicit research hypothesis classifications with strict epistemic warnings in `pirtm/agents/boundaries.py`. No agent may promote speculation into experimentally verified physics.

---

## Execution and Verification

Run the test suite:
```bash
python3 -m unittest discover tests -v
```

Run Alloy checks:
```bash
java -jar alloy.jar exec -f -t text alloy/vacuity-demo.als
java -jar alloy.jar exec -f -t text alloy/hcalc-mirror.als
```
