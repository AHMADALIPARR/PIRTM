#!/usr/bin/env python3
r"""PIRTM Central Adversarial Experiment Runner.

Executes the central experiment in 11-qubit Hilbert space:
- State model: H = (C^2)^{\otimes 11}, 2048 complex amplitudes.
- Complete observer vs restricted observer.
- Demonstrates indistinguishability under partial observation (trace distance = 0)
  versus complete distinguishability under global measurement (overlap fidelity = 0).
"""

import json
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pirtm.quantum.hilbert11 import run_central_adversarial_experiment
from pirtm.scheduler import BoundedConcurrentScheduler
from pirtm.oracle import EmbeddingOracle


def main():
    print("=" * 70)
    print("PIRTM Ω-AKASHA XI: CENTRAL ADVERSARIAL COMPUTATIONAL EXPERIMENT")
    print("State space: 11 qubits, 2,048 complex amplitudes")
    print("=" * 70)

    # 1. Run central adversarial quantum experiment
    res = run_central_adversarial_experiment()
    print("\n[CENTRAL ADVERSARIAL EXPERIMENT RESULTS]")
    print(f"State Dimension: {res['state_dimension']}")
    print(f"Global overlap fidelity |<Psi_1|Psi_2>|^2: {res['global_overlap_fidelity']:.6e}")
    print(f"Global observer distinguishable: {res['global_distinguishable']} (100% distinguishable)")
    print(f"Reduced trace distance on Qubit 0: {res['reduced_trace_distance']:.6e}")
    print(f"Subsystem observer distinguishable: {res['subsystem_distinguishable']} (0% distinguishable)")
    print(f"Observer probabilities for Psi_1: {res['observer_probabilities_psi1']}")
    print(f"Observer probabilities for Psi_2: {res['observer_probabilities_psi2']}")
    print(f"\nConclusion: {res['conclusion']}")

    # 2. Run 11-worker concurrent dispatch
    print("\n" + "=" * 70)
    print("EXECUTING 11 CONCURRENT REASONING WORKERS")
    print("=" * 70)
    oracle = EmbeddingOracle()
    scheduler = BoundedConcurrentScheduler(oracle, max_workers=4)
    cycle = scheduler.dispatch_cycle(round_num=1)

    for aid in sorted(cycle.reports.keys()):
        rep = cycle.reports[aid]
        worker = scheduler.workers[aid]
        print(f"[{aid}] {worker.domain:<40} Tests: {rep.tests.passed} passed | Status: {rep.proof_status}")

    print("\nTotal Artifacts Generated & Indexed in CAS:", len(cycle.merged_artifacts))
    print("Ledger Integrity Validated:", cycle.ledger_integrity_valid)
    print("=" * 70)


if __name__ == "__main__":
    main()
