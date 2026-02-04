"""
Requirements extraction package for Requirements-to-Design Pipeline.

This package provides agents and utilities for extracting, consolidating,
and scoring requirements from multiple sources (Gong, Figma, manual input).
"""

from .extractor import RequirementExtractorAgent
from .figma_connector import FigmaConnector
from .figma_models import ComponentType, DesignComponent, DesignSpec
from .figma_output import FigmaOutputFormatter, export_design_spec
from .figma_parser import DesignParserAgent
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
    "DesignParserAgent",
    "FigmaConnector",
    "ComponentType",
    "DesignComponent",
    "DesignSpec",
    "FigmaOutputFormatter",
    "export_design_spec",
]
