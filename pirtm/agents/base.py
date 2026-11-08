"""Base Worker Definition and Block 7 Reporting Contract for PIRTM.

Strict Block 7 Reporting Contract:
{
  "agent": "A04",
  "block": 4,
  "artifacts": [],
  "invariants": [],
  "tests": {
    "passed": 0,
    "failed": 0,
    "not_run": 0
  },
  "proof_status": "NOT_RUN",
  "oracle_references": [],
  "blockers": [],
  "next_action": ""
}
"""

from __future__ import annotations
import abc
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
from pirtm.oracle.retrieval import EmbeddingOracle


@dataclass
class TestResults:
    passed: int = 0
    failed: int = 0
    not_run: int = 0


@dataclass
class AgentReport:
    agent: str
    block: int
    artifacts: List[str] = field(default_factory=list)
    invariants: List[str] = field(default_factory=list)
    tests: TestResults = field(default_factory=TestResults)
    proof_status: str = "NOT_RUN"
    oracle_references: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    next_action: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent,
            "block": self.block,
            "artifacts": self.artifacts,
            "invariants": self.invariants,
            "tests": asdict(self.tests),
            "proof_status": self.proof_status,
            "oracle_references": self.oracle_references,
            "blockers": self.blockers,
            "next_action": self.next_action,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class BaseAgentWorker(abc.ABC):
    """Abstract base class for all 11 isolated logical workers."""

    def __init__(self, agent_id: str, domain: str, oracle: EmbeddingOracle):
        self.agent_id = agent_id
        self.domain = domain
        self.oracle = oracle
        self.namespace = f"agent::{agent_id.lower()}"

    @abc.abstractmethod
    def execute(self, round_num: int = 1, context: Optional[Dict[str, Any]] = None) -> AgentReport:
        """Executes the worker's domain logic deterministically and returns an AgentReport."""
        raise NotImplementedError
