#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Example: XML Prompt Agent - Acceptance Criteria Extractor

Demonstrates the XML Prompt Agent implementation pattern:
1. Load XML prompt from file/repository
2. Execute prompt with input text
3. Parse structured output
4. Integrate into requirements workflow

Pattern: XML Prompt Agent
Reference: ADR-006 (docs/architecture/ddd-specification.md)
Story: P1-EXAMPLE-002
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class PromptMetadata:
    """Metadata from XML prompt."""
    name: str
    version: str
    domain: str
    author: str = ""
    created: str = ""
    tags: List[str] = None
    description: str = ""

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class XMLPrompt:
    """Parsed XML prompt structure."""
    metadata: PromptMetadata
    role: str
    task: str
    instructions: List[str]
    output_format: str
    constraints: List[str]
    examples: List[Dict[str, str]]
    validation_rules: List[str]


class XMLPromptLoader:
    """Load and parse XML prompt files."""

    @staticmethod
    def load_from_file(file_path: str) -> XMLPrompt:
        """
        Load XML prompt from local file.

        In production, this would load from Eric-Flecher-Glean/prompts repository.

        Args:
            file_path: Path to XML prompt file

        Returns:
            Parsed XMLPrompt object
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        tree = ET.parse(path)
        root = tree.getroot()

        # Parse metadata
        metadata_elem = root.find('metadata')
        tags = [tag.text for tag in metadata_elem.findall('.//tag')] if metadata_elem.find('.//tag') is not None else []

        metadata = PromptMetadata(
            name=metadata_elem.findtext('name', ''),
            version=metadata_elem.findtext('version', ''),
            domain=metadata_elem.findtext('domain', ''),
            author=metadata_elem.findtext('author', ''),
            created=metadata_elem.findtext('created', ''),
            tags=tags,
            description=metadata_elem.findtext('description', '').strip()
        )

        # Parse instructions
        instructions_elem = root.find('instructions')
        instructions = []
        if instructions_elem is not None:
            for step in instructions_elem:
                instructions.append(step.text.strip())

        # Parse constraints
        constraints_elem = root.find('constraints')
        constraints = []
        if constraints_elem is not None:
            for constraint in constraints_elem.findall('constraint'):
                constraints.append(constraint.text.strip())

        # Parse examples
        examples_elem = root.find('examples')
        examples = []
        if examples_elem is not None:
            for example in examples_elem.findall('example'):
                example_dict = {
                    'input': example.findtext('input', '').strip(),
                    'output': example.findtext('output', '').strip()
                }
                examples.append(example_dict)

        # Parse validation rules
        validation_elem = root.find('validation_rules')
        validation_rules = []
        if validation_elem is not None:
            for rule in validation_elem.findall('rule'):
                validation_rules.append(rule.text.strip())

        return XMLPrompt(
            metadata=metadata,
            role=root.findtext('role', '').strip(),
            task=root.findtext('task', '').strip(),
            instructions=instructions,
            output_format=root.findtext('output_format', '').strip(),
            constraints=constraints,
            examples=examples,
            validation_rules=validation_rules
        )

    @staticmethod
    def load_from_repository(repo: str, path: str, version: str = "latest") -> XMLPrompt:
        """
        Load XML prompt from Git repository.

        In production implementation, this would:
        1. Clone/pull Eric-Flecher-Glean/prompts repository
        2. Checkout specific version tag
        3. Load prompt from repository path

        Args:
            repo: Repository name (e.g., "Eric-Flecher-Glean/prompts")
            path: Path within repository (e.g., "sdlc/requirements/extract-acceptance-criteria.xml")
            version: Version tag (e.g., "1.0.0" or "latest")

        Returns:
            Parsed XMLPrompt object
        """
        # For demo, we load from local examples directory
        print(f"📦 Loading prompt from repository: {repo}")
        print(f"   Path: {path}")
        print(f"   Version: {version}")
        print()

        # In production:
        # 1. git clone/pull {repo}
        # 2. git checkout prompts/{path}/v{version}
        # 3. Load file from cloned repo

        # Demo: Load from local examples
        local_path = Path("examples/prompts/extract-acceptance-criteria.xml")
        return XMLPromptLoader.load_from_file(str(local_path))


class AcceptanceCriteriaExtractor:
    """Execute XML prompt to extract acceptance criteria."""

    def __init__(self, prompt: XMLPrompt):
        """
        Initialize extractor with XML prompt.

        Args:
            prompt: Loaded XMLPrompt object
        """
        self.prompt = prompt

    def extract(self, user_story: str) -> Dict[str, Any]:
        """
        Extract acceptance criteria from user story.

        In production, this would:
        1. Construct full prompt from XML structure
        2. Send to LLM (Claude, GPT-4, etc.)
        3. Parse LLM response according to output_format
        4. Validate against validation_rules

        Args:
            user_story: User story text

        Returns:
            Dictionary containing extracted acceptance criteria
        """
        print(f"🔍 Executing XML Prompt: {self.prompt.metadata.name} (v{self.prompt.metadata.version})")
        print(f"   Domain: {self.prompt.metadata.domain}")
        print(f"   Role: {self.prompt.role[:80]}...")
        print()

        # In production, this would call an LLM:
        # prompt_text = self._build_prompt(user_story)
        # response = llm.complete(prompt_text)
        # result = self._parse_response(response)

        # Demo: Return simulated extraction
        result = self._simulate_extraction(user_story)

        return result

    def _simulate_extraction(self, user_story: str) -> Dict[str, Any]:
        """
        Simulate LLM extraction for demo purposes.

        Args:
            user_story: User story text

        Returns:
            Simulated extraction result
        """
        # Analyze story for key elements
        has_search = 'search' in user_story.lower()
        has_filter = 'filter' in user_story.lower()
        has_display = 'display' in user_story.lower() or 'show' in user_story.lower()

        criteria = []
        criterion_id = 1

        # Functional criteria
        if has_search:
            criteria.append({
                'id': f'AC{criterion_id}',
                'description': 'System returns matching results when search query is entered',
                'type': 'Functional',
                'priority': 'P0',
                'test_approach': 'Integration',
                'example_test': 'Given 10 items in database, When user searches for "test", Then matching items are returned'
            })
            criterion_id += 1

        if has_filter:
            criteria.append({
                'id': f'AC{criterion_id}',
                'description': 'System filters results based on selected criteria',
                'type': 'Functional',
                'priority': 'P0',
                'test_approach': 'Integration',
                'example_test': 'Given 100 results, When user applies filter "category=books", Then only books are shown'
            })
            criterion_id += 1

        if has_display:
            criteria.append({
                'id': f'AC{criterion_id}',
                'description': 'System displays results in user-specified format',
                'type': 'Functional',
                'priority': 'P1',
                'test_approach': 'UI',
                'example_test': 'Given search results, When user selects "grid view", Then results display in grid layout'
            })
            criterion_id += 1

        # Always add edge case
        criteria.append({
            'id': f'AC{criterion_id}',
            'description': 'System displays empty state message when no results match',
            'type': 'Edge Case',
            'priority': 'P0',
            'test_approach': 'Integration',
            'example_test': 'Given no matching results, When search completes, Then "No results found" message is shown'
        })
        criterion_id += 1

        # Non-functional criteria
        criteria.append({
            'id': f'AC{criterion_id}',
            'description': 'Search response time is under 500ms for 1000 items',
            'type': 'Non-functional',
            'priority': 'P1',
            'test_approach': 'Performance',
            'example_test': 'Given 1000 items in database, When user searches, Then response time is measured at <500ms'
        })

        # Calculate summary
        by_type = {}
        by_priority = {}
        for criterion in criteria:
            by_type[criterion['type']] = by_type.get(criterion['type'], 0) + 1
            by_priority[criterion['priority']] = by_priority.get(criterion['priority'], 0) + 1

        return {
            'acceptance_criteria': criteria,
            'summary': {
                'total': len(criteria),
                'by_type': by_type,
                'by_priority': by_priority,
                'coverage': '95%'
            },
            'potential_gaps': [
                'No criteria for pagination behavior',
                'No criteria for sorting order',
                'Consider adding criteria for accessibility (ARIA labels, keyboard navigation)'
            ],
            'metadata': {
                'prompt_version': self.prompt.metadata.version,
                'extracted_at': '2026-02-04T01:00:00Z',
                'processing_time_ms': 250
            }
        }


def format_output(result: Dict[str, Any]) -> None:
    """
    Format and display extracted acceptance criteria.

    Args:
        result: Extraction result from AcceptanceCriteriaExtractor
    """
    print("=" * 80)
    print("📋 ACCEPTANCE CRITERIA EXTRACTION RESULTS")
    print("=" * 80)
    print()

    # Summary
    summary = result['summary']
    print("📊 SUMMARY")
    print("-" * 80)
    print(f"Total Criteria: {summary['total']}")
    print(f"Coverage: {summary['coverage']}")
    print()

    print("By Type:")
    for type_name, count in summary['by_type'].items():
        print(f"  {type_name}: {count}")
    print()

    print("By Priority:")
    for priority, count in summary['by_priority'].items():
        print(f"  {priority}: {count}")
    print()

    # Acceptance Criteria
    print("✅ ACCEPTANCE CRITERIA")
    print("-" * 80)
    for i, criterion in enumerate(result['acceptance_criteria'], 1):
        print(f"\n{criterion['id']}: {criterion['description']}")
        print(f"  Type: {criterion['type']}")
        print(f"  Priority: {criterion['priority']}")
        print(f"  Test Approach: {criterion['test_approach']}")
        print(f"  Example Test:")
        print(f"    {criterion['example_test']}")

    # Potential Gaps
    print("\n⚠️  POTENTIAL GAPS")
    print("-" * 80)
    for gap in result['potential_gaps']:
        print(f"  • {gap}")

    # Metadata
    print("\n📊 METADATA")
    print("-" * 80)
    metadata = result['metadata']
    print(f"Prompt Version: {metadata['prompt_version']}")
    print(f"Extracted At: {metadata['extracted_at']}")
    print(f"Processing Time: {metadata['processing_time_ms']}ms")

    print("\n" + "=" * 80)


def integrate_into_story(criteria: List[Dict[str, Any]], story_id: str) -> None:
    """
    Demonstrate how to integrate extracted criteria into backlog story.

    Args:
        criteria: List of acceptance criteria
        story_id: Story ID (e.g., "P0-FEATURE-042")
    """
    print("\n🔗 BACKLOG INTEGRATION")
    print("-" * 80)
    print(f"Story ID: {story_id}")
    print()

    print("YAML format for IMPLEMENTATION_BACKLOG.yaml:")
    print()
    print("acceptance_criteria:")
    for criterion in criteria:
        print(f"  - '{criterion['id']}: {criterion['description']}'")

    print()
    print("functional_test_plan:")
    for criterion in criteria:
        print(f"  - acceptance_criterion: {criterion['id']}")
        print(f"    test_description: Verify {criterion['id'].lower()}")
        print(f"    test_commands:")
        print(f"      - command: uv run tests/integration/test_{story_id.lower().replace('-', '_')}.py")
        print(f"        command_type: uv")
        print(f"        expected_output: {criterion['id']} PASSED")
        print(f"        expected_exit_code: 0")
        print(f"        success_criteria: 'Exit code 0: {criterion['description']}'")
        print()

    print("✅ Acceptance criteria ready to add to backlog")


def main():
    """
    Main demonstration of XML Prompt Agent pattern.
    """
    print("🎯 XML PROMPT AGENT EXAMPLE")
    print("   Pattern: XML Prompt Agent")
    print("   Prompt: Extract Acceptance Criteria")
    print("   Story: P1-EXAMPLE-002\n")

    # Step 1: Load XML prompt
    print("=" * 80)
    print("STEP 1: Load XML Prompt")
    print("=" * 80)
    print()

    prompt = XMLPromptLoader.load_from_repository(
        repo="Eric-Flecher-Glean/prompts",
        path="sdlc/requirements/extract-acceptance-criteria.xml",
        version="1.0.0"
    )

    print("✅ Prompt loaded successfully!")
    print(f"   Name: {prompt.metadata.name}")
    print(f"   Version: {prompt.metadata.version}")
    print(f"   Domain: {prompt.metadata.domain}")
    print(f"   Tags: {', '.join(prompt.metadata.tags)}")
    print(f"   Instructions: {len(prompt.instructions)} steps")
    print(f"   Constraints: {len(prompt.constraints)} rules")
    print(f"   Validation Rules: {len(prompt.validation_rules)} checks")
    print()

    # Step 2: Execute prompt with user story
    print("=" * 80)
    print("STEP 2: Execute Prompt with User Story")
    print("=" * 80)
    print()

    user_story = """
    As a developer, I want to search for agents by bounded context
    so that I can find relevant agents quickly.

    The search should filter agents based on the bounded context name,
    support partial matching, and display results with agent metadata.
    """

    print("📝 Input User Story:")
    print(user_story.strip())
    print()

    extractor = AcceptanceCriteriaExtractor(prompt)
    result = extractor.extract(user_story)

    print("✅ Extraction complete!")
    print()

    # Step 3: Format and display results
    print("=" * 80)
    print("STEP 3: Parse and Display Results")
    print("=" * 80)
    print()

    format_output(result)

    # Step 4: Show integration
    print("\n" + "=" * 80)
    print("STEP 4: Integrate into Backlog")
    print("=" * 80)
    print()

    integrate_into_story(result['acceptance_criteria'], "P0-FEATURE-042")

    # Conclusion
    print("\n" + "=" * 80)
    print("✅ EXAMPLE COMPLETE")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("  1. XML prompts are version-controlled and reusable")
    print("  2. Structured format ensures consistency across extractions")
    print("  3. Rapid iteration: edit XML, re-run, validate (minutes vs. days)")
    print("  4. Fine-grained control over role, task, instructions, constraints")
    print("  5. Output integrates directly into backlog YAML")
    print("\nNext Steps:")
    print("  • Review docs/guides/xml-prompt-agent-pattern.md")
    print("  • Store prompts in Eric-Flecher-Glean/prompts repository")
    print("  • Register agent capability in Domain Registry")
    print()


if __name__ == "__main__":
    main()
