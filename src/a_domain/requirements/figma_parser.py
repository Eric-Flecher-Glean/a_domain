"""
DesignParserAgent - Parses Figma design files and extracts components.

This agent analyzes Figma design files to extract UI components, properties,
annotations, and design intent for requirements-to-design pipeline.
"""

from typing import Dict, List, Optional

from .figma_models import (
    Annotation,
    Colors,
    ComponentProperties,
    ComponentType,
    DesignComponent,
    DesignSpec,
    Dimensions,
    Typography,
)


class DesignParserAgent:
    """
    Agent that parses Figma design files and extracts components.

    The agent performs:
    - Component tree traversal (DFS)
    - Property extraction (dimensions, colors, typography)
    - Annotation parsing
    - User flow detection
    - Design token extraction
    - Technical spec generation
    """

    # Component type detection patterns
    COMPONENT_TYPE_KEYWORDS = {
        ComponentType.BUTTON: ["button", "btn", "cta", "action"],
        ComponentType.INPUT: ["input", "textfield", "text field", "form field"],
        ComponentType.CHECKBOX: ["checkbox", "check"],
        ComponentType.RADIO: ["radio"],
        ComponentType.SELECT: ["select", "dropdown", "picker"],
        ComponentType.TEXT: ["text", "label", "heading", "paragraph"],
        ComponentType.ICON: ["icon", "symbol"],
        ComponentType.IMAGE: ["image", "img", "photo", "picture"],
        ComponentType.NAVIGATION: ["nav", "navigation", "menu"],
        ComponentType.CARD: ["card"],
        ComponentType.MODAL: ["modal", "dialog", "popup"],
        ComponentType.FRAME: ["frame", "container", "layout"],
    }

    def __init__(self):
        """Initialize the DesignParserAgent."""
        self.component_counter = 0

    def parse_figma_file(
        self, file_data: Dict, file_metadata: Optional[Dict] = None
    ) -> DesignSpec:
        """
        Parse a Figma file and extract design components.

        Args:
            file_data: Figma file JSON data (from API)
            file_metadata: Optional metadata (file_id, name, etc.)

        Returns:
            DesignSpec with extracted components and design tokens
        """
        file_id = file_metadata.get("file_id", "unknown") if file_metadata else "unknown"
        file_name = file_metadata.get("file_name", "Untitled") if file_metadata else "Untitled"

        spec = DesignSpec(file_id=file_id, file_name=file_name)

        # Parse document structure
        document = file_data.get("document", {})
        if document:
            # Traverse component tree
            self._traverse_nodes(document, spec)

            # Extract design tokens
            self._extract_design_tokens(file_data, spec)

        return spec

    def _traverse_nodes(
        self, node: Dict, spec: DesignSpec, parent_id: Optional[str] = None
    ) -> None:
        """
        Traverse Figma node tree using DFS.

        Args:
            node: Current node
            spec: Design spec being built
            parent_id: Parent component ID
        """
        node_type = node.get("type", "")
        node_name = node.get("name", "Untitled")
        node_id = node.get("id", "")

        # Check if this node should be extracted as a component
        if self._should_extract_component(node):
            component = self._extract_component(node, spec.file_name, parent_id)
            spec.components.append(component)
            parent_id = component.id  # This becomes parent for children

        # Traverse children
        children = node.get("children", [])
        for child in children:
            self._traverse_nodes(child, spec, parent_id)

    def _should_extract_component(self, node: Dict) -> bool:
        """Check if node should be extracted as a component."""
        node_type = node.get("type", "")
        node_name = node.get("name", "").lower()

        # Extract components, instances, and meaningful frames
        if node_type in ["COMPONENT", "INSTANCE", "COMPONENT_SET"]:
            return True

        # Extract frames that look like components (by name)
        if node_type in ["FRAME", "GROUP"]:
            for comp_type, keywords in self.COMPONENT_TYPE_KEYWORDS.items():
                if any(keyword in node_name for keyword in keywords):
                    return True

        return False

    def _extract_component(
        self, node: Dict, figma_file: str, parent_id: Optional[str]
    ) -> DesignComponent:
        """Extract a DesignComponent from a Figma node."""
        self.component_counter += 1
        comp_id = f"COMP-{self.component_counter:03d}"

        node_name = node.get("name", "Untitled")
        node_id = node.get("id", "")

        # Detect component type
        comp_type = self._detect_component_type(node_name, node)

        # Extract properties
        properties = self._extract_properties(node)

        # Extract annotations (from description field if present)
        annotations = self._extract_annotations(node)

        # Generate user story hints
        user_story_hints = self._generate_user_story_hints(node_name, comp_type)

        # Generate implementation notes
        implementation_notes = self._generate_implementation_notes(comp_type, properties)

        # Get children IDs
        children_ids = []
        for child in node.get("children", []):
            if self._should_extract_component(child):
                self.component_counter += 1
                children_ids.append(f"COMP-{self.component_counter:03d}")

        return DesignComponent(
            id=comp_id,
            figma_file=figma_file,
            figma_node_id=node_id,
            component_type=comp_type,
            name=node_name,
            properties=properties,
            annotations=annotations,
            user_story_hints=user_story_hints,
            implementation_notes=implementation_notes,
            parent_id=parent_id,
            children=children_ids,
        )

    def _detect_component_type(self, name: str, node: Dict) -> ComponentType:
        """Detect component type from name and node properties."""
        name_lower = name.lower()

        # Check keywords
        for comp_type, keywords in self.COMPONENT_TYPE_KEYWORDS.items():
            if any(keyword in name_lower for keyword in keywords):
                return comp_type

        # Check node type
        node_type = node.get("type", "")
        if node_type == "TEXT":
            return ComponentType.TEXT

        return ComponentType.UNKNOWN

    def _extract_properties(self, node: Dict) -> ComponentProperties:
        """Extract component properties from node."""
        properties = ComponentProperties()

        # Dimensions
        bounds = node.get("absoluteBoundingBox", {})
        if bounds:
            properties.dimensions = Dimensions(
                width=f"{bounds.get('width', 0):.0f}px",
                height=f"{bounds.get('height', 0):.0f}px",
            )

        # Colors (from fills and strokes)
        fills = node.get("fills", [])
        if fills and fills[0].get("type") == "SOLID":
            color = fills[0].get("color", {})
            properties.colors.background = self._rgb_to_hex(color)

        strokes = node.get("strokes", [])
        if strokes and strokes[0].get("type") == "SOLID":
            color = strokes[0].get("color", {})
            properties.colors.border = self._rgb_to_hex(color)

        # Typography (for text nodes)
        if node.get("type") == "TEXT":
            style = node.get("style", {})
            properties.typography = Typography(
                font=style.get("fontFamily", ""),
                size=f"{style.get('fontSize', 0):.0f}px",
                weight=style.get("fontWeight", 400),
                line_height=f"{style.get('lineHeightPx', 0):.0f}px",
            )

        # Border radius
        if "cornerRadius" in node:
            properties.border_radius = f"{node['cornerRadius']:.0f}px"

        # Opacity
        if "opacity" in node:
            properties.opacity = node["opacity"]

        # Variants (from component set)
        if "componentPropertyDefinitions" in node:
            prop_defs = node["componentPropertyDefinitions"]
            for prop_name, prop_def in prop_defs.items():
                if prop_def.get("type") == "VARIANT":
                    properties.variants.extend(
                        prop_def.get("variantOptions", [])
                    )

        return properties

    def _extract_annotations(self, node: Dict) -> List[Annotation]:
        """Extract annotations from node description."""
        annotations = []

        description = node.get("description", "")
        if description:
            # Simple annotation from description
            annotations.append(Annotation(text=description))

        # Could also parse comments from reactions/comments API
        # (would require additional API calls)

        return annotations

    def _generate_user_story_hints(
        self, component_name: str, component_type: ComponentType
    ) -> List[str]:
        """Generate user story hints from component."""
        hints = []

        type_templates = {
            ComponentType.BUTTON: [
                f"As a user, I want to interact with {component_name}",
                "Button should provide visual feedback on interaction",
            ],
            ComponentType.INPUT: [
                f"As a user, I want to input data via {component_name}",
                "Input should validate data and show errors",
            ],
            ComponentType.NAVIGATION: [
                f"As a user, I want to navigate using {component_name}",
                "Navigation should be accessible and keyboard-friendly",
            ],
            ComponentType.CARD: [
                f"As a user, I want to view information in {component_name}",
                "Card should be scannable and highlight key information",
            ],
        }

        hints.extend(type_templates.get(component_type, [
            f"As a user, I want to interact with {component_name}"
        ]))

        return hints

    def _generate_implementation_notes(
        self, component_type: ComponentType, properties: ComponentProperties
    ) -> List[str]:
        """Generate implementation guidance notes."""
        notes = []

        # General notes based on type
        if component_type == ComponentType.BUTTON:
            notes.append("Use existing Button component from design system")
            if "loading" in properties.variants:
                notes.append("Add loading state with spinner")
            # Always add WCAG note for buttons (they have color)
            if properties.colors.background:
                notes.append("Ensure 4.5:1 contrast ratio (WCAG AA)")

        elif component_type == ComponentType.INPUT:
            notes.append("Implement validation and error states")
            notes.append("Add aria-label for accessibility")

        elif component_type == ComponentType.NAVIGATION:
            notes.append("Ensure keyboard navigation support")
            notes.append("Add focus indicators")

        elif component_type == ComponentType.CARD:
            notes.append("Ensure card is scannable with clear visual hierarchy")
            notes.append("Consider hover/focus states for interactive cards")

        # Accessibility note if text color found
        if properties.colors.background and properties.colors.text:
            notes.append(f"Verify contrast ratio: {properties.colors.text} on {properties.colors.background}")

        # If no notes yet, add generic note
        if not notes:
            notes.append("Implement following design system guidelines")

        return notes

    def _extract_design_tokens(self, file_data: Dict, spec: DesignSpec) -> None:
        """Extract design tokens (colors, typography, spacing)."""
        # Color styles
        styles = file_data.get("styles", {})
        for style_key, style_data in styles.items():
            style_type = style_data.get("styleType", "")
            if style_type == "FILL":
                # Color style
                name = style_data.get("name", style_key)
                # Would extract color value from style definition
                spec.color_palette[name] = "#000000"  # Placeholder

        # Would also extract typography and spacing scales
        # from text styles and layout grids

    @staticmethod
    def _rgb_to_hex(color: Dict) -> str:
        """Convert RGB color dict to hex string."""
        r = int(color.get("r", 0) * 255)
        g = int(color.get("g", 0) * 255)
        b = int(color.get("b", 0) * 255)
        return f"#{r:02x}{g:02x}{b:02x}"
