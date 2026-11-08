"""Bounded Concurrent Scheduler for 11 Logical Workers.

Dispatches the 11 logical workers independently with bounded concurrency,
isolated namespaces, deterministic merge contracts, and ledger tracking.
"""

from __future__ import annotations
import concurrent.futures
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
from pirtm.agents.base import AgentReport, BaseAgentWorker
from pirtm.agents import ALL_WORKER_CLASSES
from pirtm.oracle.retrieval import EmbeddingOracle


@dataclass
class ScheduleCycleResult:
    cycle: int
    reports: Dict[str, AgentReport]
    merged_artifacts: List[str]
    invariants_asserted: List[str]
    total_tests_passed: int
    total_tests_failed: int
    ledger_integrity_valid: bool


class BoundedConcurrentScheduler:
    """Dispatches 11 logical agent workers concurrently or sequentially."""

    def __init__(
        self,
        oracle: EmbeddingOracle,
        max_workers: int = 4,
    ):
        self.oracle = oracle
        self.max_workers = max_workers
        self.workers: Dict[str, BaseAgentWorker] = {}
        for worker_cls in ALL_WORKER_CLASSES:
            w = worker_cls(self.oracle)
            self.workers[w.agent_id] = w

    def _execute_worker_task(
        self,
        agent_id: str,
        round_num: int,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentReport:
        worker = self.workers[agent_id]
        return worker.execute(round_num=round_num, context=context)

    def dispatch_cycle(
        self,
        round_num: int = 1,
        context: Optional[Dict[str, Any]] = None,
    ) -> ScheduleCycleResult:
        """Dispatches all 11 agents in parallel using a ThreadPoolExecutor."""
        reports: Dict[str, AgentReport] = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_agent = {
                executor.submit(self._execute_worker_task, agent_id, round_num, context): agent_id
                for agent_id in sorted(self.workers.keys())
            }

            for future in concurrent.futures.as_completed(future_to_agent):
                agent_id = future_to_agent[future]
                try:
                    report = future.result()
                    reports[agent_id] = report
                except Exception as e:
                    # Isolate worker failure; do not crash entire cycle
                    reports[agent_id] = AgentReport(
                        agent=agent_id,
                        block=0,
                        artifacts=[],
                        invariants=[],
                        proof_status="EXECUTION_ERROR",
                        blockers=[str(e)],
                    )

        # Deterministic merge contract
        merged_artifacts: List[str] = []
        invariants_set: set[str] = set()
        tests_passed = 0
        tests_failed = 0

        for agent_id in sorted(reports.keys()):
            r = reports[agent_id]
            merged_artifacts.extend(r.artifacts)
            for inv in r.invariants:
                invariants_set.add(inv)
            tests_passed += r.tests.passed
            tests_failed += r.tests.failed

        # Ledger integrity check: resolve and verify all merged artifacts in oracle
        ledger_valid = True
        for art in merged_artifacts:
            v = self.oracle.verify(art)
            if not v.get("integrity_valid", False):
                ledger_valid = False
                break

        return ScheduleCycleResult(
            cycle=round_num,
            reports=reports,
            merged_artifacts=merged_artifacts,
            invariants_asserted=sorted(list(invariants_set)),
            total_tests_passed=tests_passed,
            total_tests_failed=tests_failed,
            ledger_integrity_valid=ledger_valid,
        )
