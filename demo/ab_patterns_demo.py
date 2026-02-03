#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
A/B Pattern Demo

Demonstrates the reusable A/B collaboration patterns from P1-AB-002.

Usage:
    python demo/ab_patterns_demo.py --pattern generate-validate
    python demo/ab_patterns_demo.py --pattern propose-critique-refine
    python demo/ab_patterns_demo.py --pattern both
"""

import argparse
import sys
import os
from typing import Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.a_domain.protocol import ProtocolBrokerAgent
from src.a_domain.patterns import GenerateValidatePattern, ProposeCritiqueRefinePattern
from src.a_domain.patterns.observability import ABPatternObserver


def demo_generate_validate(observer: ABPatternObserver) -> None:
    """
    Demonstrate Generate-Validate pattern.

    Shows:
    - Content generation
    - Quality validation
    - Automatic refinement
    """
    print("=" * 70)
    print("DEMO: Generate-Validate Pattern")
    print("=" * 70)
    print()

    # Create broker
    broker = ProtocolBrokerAgent()

    # Create pattern with observability
    pattern = GenerateValidatePattern(
        broker=broker,
        observer=observer.observe
    )

    print(f"Pattern: {pattern.pattern_name}")
    print(f"Description: {pattern.pattern_description}")
    print(f"Roles: {', '.join(pattern.agent_roles)}")
    print()

    # Execute pattern
    print("🚀 Executing workflow...")
    print("   Task: Summarize meeting transcript")
    print()

    context = pattern.execute(
        input_data={"task": "Summarize the key points from the Q4 planning meeting transcript"},
        max_iterations=3
    )

    # Display results
    print("✅ Results:")
    print(f"   Completed: {context.is_complete}")
    print(f"   Iterations: {context.current_iteration}")
    print(f"   Duration: {context.total_duration_ms:.2f}ms")
    print()

    if context.final_output:
        output = context.final_output
        print(f"   Content: \"{output['content'][:80]}...\"")
        print(f"   Quality Score: {output['validation']['quality_score']:.2f}")
        print(f"   Valid: {output['validation']['valid']}")
        print()

    print("📊 Iteration History:")
    for iteration in context.iteration_history:
        print(f"   Iteration {iteration['iteration'] + 1}:")
        print(f"     - Quality: {iteration['quality_score']:.2f}")
        print(f"     - Valid: {iteration['valid']}")
        print(f"     - Duration: {iteration['duration_ms']:.2f}ms")
    print()


def demo_propose_critique_refine(observer: ABPatternObserver) -> None:
    """
    Demonstrate Propose-Critique-Refine pattern.

    Shows:
    - Iterative proposal creation
    - Critique and feedback
    - Progressive refinement
    - Convergence detection
    """
    print("=" * 70)
    print("DEMO: Propose-Critique-Refine Pattern")
    print("=" * 70)
    print()

    # Create broker
    broker = ProtocolBrokerAgent()

    # Create pattern with observability
    pattern = ProposeCritiqueRefinePattern(
        broker=broker,
        observer=observer.observe
    )

    print(f"Pattern: {pattern.pattern_name}")
    print(f"Description: {pattern.pattern_description}")
    print(f"Roles: {', '.join(pattern.agent_roles)}")
    print()

    # Execute pattern
    print("🚀 Executing workflow...")
    print("   Goal: Design user-friendly API for customer data export")
    print()

    context = pattern.execute(
        input_data={"goal": "Design a user-friendly API for exporting customer data with filtering and pagination"},
        max_iterations=5
    )

    # Display results
    print("✅ Results:")
    print(f"   Completed: {context.is_complete}")
    print(f"   Iterations: {context.current_iteration}")
    print(f"   Duration: {context.total_duration_ms:.2f}ms")
    print()

    if context.final_output:
        output = context.final_output
        print(f"   Best Proposal: \"{output['proposal'][:80]}...\"")
        print(f"   Final Score: {output['score']:.2f}")
        print()

    print("📊 Iteration History (Score Progression):")
    for iteration in context.iteration_history:
        score = iteration['score']
        improvement = iteration['improvement']
        bar_length = int(score * 40)
        bar = "█" * bar_length + "░" * (40 - bar_length)

        print(f"   Iteration {iteration['iteration'] + 1}: {bar} {score:.2f} ", end="")
        if improvement > 0:
            print(f"(+{improvement:.2f})")
        else:
            print()

    print()


def demo_both_patterns(observer: ABPatternObserver) -> None:
    """Run both pattern demos."""
    demo_generate_validate(observer)
    print("\n" + "=" * 70)
    print()
    demo_propose_critique_refine(observer)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="A/B Pattern Demo - Showcase reusable collaboration patterns"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        choices=["generate-validate", "propose-critique-refine", "both"],
        default="both",
        help="Which pattern to demonstrate (default: both)"
    )

    args = parser.parse_args()

    # Create observer for all demos
    observer = ABPatternObserver(session_id=f"pattern-demo-{args.pattern}")

    print()
    print("🤖 A/B Collaboration Pattern Demo")
    print("   Showcasing P1-AB-002: Enhanced Journey Orchestration")
    print()

    # Run selected demo
    if args.pattern == "generate-validate":
        demo_generate_validate(observer)
    elif args.pattern == "propose-critique-refine":
        demo_propose_critique_refine(observer)
    else:
        demo_both_patterns(observer)

    # Generate observability reports
    print("=" * 70)
    print("📊 Observability")
    print("=" * 70)
    print()

    observer.save_timeline()
    observer.generate_html_report()

    summary = observer.get_summary()
    print()
    print("Summary:")
    print(f"  Total Events: {summary['total_events']}")
    print(f"  Patterns Executed: {', '.join(summary['metrics']['patterns_executed'])}")
    print(f"  Total Iterations: {summary['metrics']['total_iterations']}")
    print(f"  Total Duration: {summary['duration_ms']:.2f}ms")
    print()

    print("💡 View full timeline at:")
    print(f"   http://localhost:3000/reports/{observer.session_id}-timeline.html")
    print()


if __name__ == "__main__":
    main()
