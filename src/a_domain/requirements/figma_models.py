"""
Data models for Figma design parsing.

Defines data structures for representing Figma components, properties,
annotations, and design specifications extracted from Figma files.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class ComponentType(Enum):
    """Types of Figma components."""

    BUTTON = "Button"
    INPUT = "Input"
    CHECKBOX = "Checkbox"
    RADIO = "Radio"
    SELECT = "Select"
    FRAME = "Frame"
    TEXT = "Text"
    ICON = "Icon"
    IMAGE = "Image"
    CONTAINER = "Container"
    NAVIGATION = "Navigation"
    CARD = "Card"
    MODAL = "Modal"
    UNKNOWN = "Unknown"


@dataclass
class Dimensions:
    """Component dimensions."""

    width: Optional[str] = None
    height: Optional[str] = None


@dataclass
class Colors:
    """Component colors."""

    background: Optional[str] = None
    text: Optional[str] = None
    border: Optional[str] = None
    hover_background: Optional[str] = None
    hover_text: Optional[str] = None
    active_background: Optional[str] = None
    active_text: Optional[str] = None


@dataclass
class Typography:
    """Typography properties."""

    font: Optional[str] = None
    size: Optional[str] = None
    weight: Optional[int] = None
    line_height: Optional[str] = None
    letter_spacing: Optional[str] = None


@dataclass
class ComponentProperties:
    """Properties of a Figma component."""

    variants: List[str] = field(default_factory=list)
    dimensions: Dimensions = field(default_factory=Dimensions)
    colors: Colors = field(default_factory=Colors)
    typography: Typography = field(default_factory=Typography)
    spacing: Dict[str, str] = field(default_factory=dict)
    border_radius: Optional[str] = None
    shadow: Optional[str] = None
    opacity: Optional[float] = None


@dataclass
class Annotation:
    """Design annotation or comment."""

    text: str
    author: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class DesignComponent:
    """
    A single Figma design component.

    Represents a UI component extracted from Figma with all its
    properties, annotations, and implementation guidance.
    """

    id: str
    figma_file: str
    figma_node_id: str
    component_type: ComponentType
    name: str

    # Properties
    properties: ComponentProperties = field(default_factory=ComponentProperties)
    annotations: List[Annotation] = field(default_factory=list)
    user_story_hints: List[str] = field(default_factory=list)
    implementation_notes: List[str] = field(default_factory=list)

    # Metadata
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    extracted_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert component to dictionary for serialization."""
        return {
            "id": self.id,
            "figma_file": self.figma_file,
            "figma_node_id": self.figma_node_id,
            "component_type": self.component_type.value,
            "name": self.name,
            "properties": {
                "variants": self.properties.variants,
                "dimensions": {
                    k: v for k, v in vars(self.properties.dimensions).items() if v
                },
                "colors": {
                    k: v for k, v in vars(self.properties.colors).items() if v
                },
                "typography": {
                    k: v for k, v in vars(self.properties.typography).items() if v
                },
                "spacing": self.properties.spacing,
                "border_radius": self.properties.border_radius,
                "shadow": self.properties.shadow,
                "opacity": self.properties.opacity,
            },
            "annotations": [
                {k: v for k, v in vars(ann).items() if v}
                for ann in self.annotations
            ],
            "user_story_hints": self.user_story_hints,
            "implementation_notes": self.implementation_notes,
            "parent_id": self.parent_id,
            "children": self.children,
            "extracted_at": self.extracted_at.isoformat(),
        }


@dataclass
class DesignSpec:
    """
    Technical design specification generated from Figma components.

    Consolidates component information into actionable specs for
    development teams.
    """

    file_id: str
    file_name: str
    components: List[DesignComponent] = field(default_factory=list)

    # Design tokens
    color_palette: Dict[str, str] = field(default_factory=dict)
    typography_scale: Dict[str, Dict] = field(default_factory=dict)
    spacing_scale: Dict[str, str] = field(default_factory=dict)

    # User flows
    user_flows: List[Dict] = field(default_factory=list)

    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert spec to dictionary for serialization."""
        return {
            "file_id": self.file_id,
            "file_name": self.file_name,
            "components": [comp.to_dict() for comp in self.components],
            "color_palette": self.color_palette,
            "typography_scale": self.typography_scale,
            "spacing_scale": self.spacing_scale,
            "user_flows": self.user_flows,
            "generated_at": self.generated_at.isoformat(),
        }
