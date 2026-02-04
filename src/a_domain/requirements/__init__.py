"""
Requirements extraction package for Requirements-to-Design Pipeline.

This package provides agents and utilities for extracting, consolidating,
and scoring requirements from multiple sources (Gong, Figma, manual input).
"""

from .extractor import RequirementExtractorAgent
from .gong_connector import GongConnector
from .models import Requirement, RequirementType, PrioritySignal
from .nlp_patterns import NLPPatterns
from .output import RequirementOutputFormatter, export_requirements

__all__ = [
    "RequirementExtractorAgent",
    "GongConnector",
    "Requirement",
    "RequirementType",
    "PrioritySignal",
    "NLPPatterns",
    "RequirementOutputFormatter",
    "export_requirements",
]
