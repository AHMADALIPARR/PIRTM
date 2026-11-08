"""PIRTM Agents module."""

from pirtm.agents.base import AgentReport, BaseAgentWorker, TestResults
from pirtm.agents.boundaries import (
    ScientificBoundaryAssessment,
    get_scientific_boundaries_registry,
)
from pirtm.agents.workers import (
    A01TemporalCausalityWorker,
    A02StringTheoryWorker,
    A03MTheoryWorker,
    A04QuantumCircuitsWorker,
    A05AkashicHypothesisWorker,
    A06NostradamusAnalysisWorker,
    A07RecursiveReasoningWorker,
    A08HolographyWorker,
    A09InformationTheoryWorker,
    A10AgdaVerificationWorker,
    A11AdversarialVerificationWorker,
)

ALL_WORKER_CLASSES = [
    A01TemporalCausalityWorker,
    A02StringTheoryWorker,
    A03MTheoryWorker,
    A04QuantumCircuitsWorker,
    A05AkashicHypothesisWorker,
    A06NostradamusAnalysisWorker,
    A07RecursiveReasoningWorker,
    A08HolographyWorker,
    A09InformationTheoryWorker,
    A10AgdaVerificationWorker,
    A11AdversarialVerificationWorker,
]

__all__ = [
    "AgentReport",
    "BaseAgentWorker",
    "TestResults",
    "ScientificBoundaryAssessment",
    "get_scientific_boundaries_registry",
    "ALL_WORKER_CLASSES",
    "A01TemporalCausalityWorker",
    "A02StringTheoryWorker",
    "A03MTheoryWorker",
    "A04QuantumCircuitsWorker",
    "A05AkashicHypothesisWorker",
    "A06NostradamusAnalysisWorker",
    "A07RecursiveReasoningWorker",
    "A08HolographyWorker",
    "A09InformationTheoryWorker",
    "A10AgdaVerificationWorker",
    "A11AdversarialVerificationWorker",
]
