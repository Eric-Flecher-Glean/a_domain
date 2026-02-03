#!/usr/bin/env python3
"""
Recast backlog to prioritize A/B agent development

Changes:
1. Add P0-AB-001: A/B Agent Demo POC (NEW)
2. Add P1-AB-002: Enhanced Journey Orchestration with A/B patterns (NEW)
3. Change P0-A2A-F2-002: DataOps Provisioning (P0 → P2)
4. Change P1-A2A-F7-003: Hyperlight Sandboxing (P1 → P2)
5. Promote P0-A2A-F4-001: Gong Intelligence (ready for Option 2)
6. Update backlog metadata
"""

import yaml
from datetime import datetime
from pathlib import Path

BACKLOG_PATH = Path('.sdlc/IMPLEMENTATION_BACKLOG.yaml')

# New stories to add
NEW_STORIES = [
    {
        'story_id': 'P0-AB-001',
        'priority': 'P0',
        'type': 'Proof of Concept',
        'title': 'A/B Agent Demo - Proof of Concept',
        'description': '''Build minimal working demo of A/B agent collaboration with observability.

Goal: Prove the agent-to-agent architecture works and can be observed in real-time.

Components:
- Agent A (Generator): Creates prompts/tasks/content
- Agent B (Validator): Reviews, validates, and provides feedback
- Observation Layer: Real-time visualization in Report Explorer

Implementation:
- Use existing ProtocolBrokerAgent for communication
- Use existing Journey Orchestration for workflow
- Add observability hooks to Report Explorer
- Create demo script showing A↔B interaction loop

Business Value:
- Validates architecture in days vs weeks
- Provides observable A/B pattern foundation
- Enables rapid iteration on agent collaboration
- Can evolve into production features

Success Criteria:
- Agent A and Agent B communicate via protocol bridge
- Message flow visible in Report Explorer
- Generate-validate-refine loop observable
- Can run demo and watch agents collaborate in real-time
''',
        'dependencies': [],
        'status': 'not_started',
        'estimated_effort': '10 points',
        'tasks': [
            'Task 1: Create AgentA (Generator) class extending ProtocolBrokerAgent',
            'Task 2: Create AgentB (Validator) class extending ProtocolBrokerAgent',
            'Task 3: Implement simple generate-validate workflow',
            'Task 4: Add observability hooks to Report Explorer',
            'Task 5: Create demo runner script with CLI interface',
            'Task 6: Add real-time visualization of A↔B messages'
        ],
        'acceptance_criteria': [
            'AC1: Agent A generates content and sends to Agent B via protocol bridge',
            'AC2: Agent B validates and responds with feedback',
            'AC3: Message flow appears in Report Explorer timeline',
            'AC4: Demo script runs end-to-end showing 3+ interaction cycles',
            'AC5: Can observe agent collaboration in web portal'
        ],
        'functional_test_plan': [
            {
                'acceptance_criterion': 'AC1',
                'test_description': 'Verify Agent A sends messages to Agent B',
                'test_commands': [
                    {
                        'command': 'python demo/ab_agents_demo.py --iterations=1',
                        'command_type': 'bash',
                        'expected_output': 'Agent A → Agent B: Message sent',
                        'success_criteria': 'Message successfully routed'
                    }
                ]
            },
            {
                'acceptance_criterion': 'AC4',
                'test_description': 'Verify full interaction loop',
                'test_commands': [
                    {
                        'command': 'python demo/ab_agents_demo.py --iterations=3',
                        'command_type': 'bash',
                        'expected_output': 'Completed 3 interaction cycles',
                        'success_criteria': 'All cycles complete successfully'
                    }
                ]
            }
        ],
        'roadmap_extensions': {
            'feature_id': 'AB-DEMO',
            'phase_id': 'phase-1',
            'week_range': '1',
            'business_impact': 'Validates A/B architecture, enables rapid development'
        }
    },
    {
        'story_id': 'P1-AB-002',
        'priority': 'P1',
        'type': 'Enhancement',
        'title': 'Enhanced Journey Orchestration with A/B Agent Patterns',
        'description': '''Extend Journey Orchestration framework with reusable A/B agent patterns.

Goal: Make A/B collaboration a first-class pattern in the orchestration framework.

Patterns to Implement:
1. Generate-Validate: One agent generates, another validates
2. Propose-Critique-Refine: Iterative improvement loop
3. Parallel-Consensus: Multiple agents propose, reach consensus
4. Sequential-Handoff: Chain of specialized agents

Implementation:
- Extend Unit of Work Executor with A/B workflow templates
- Add pattern definitions to workflow DSL
- Enhance observability to highlight A↔B interactions
- Create reusable agent base classes for each pattern

Business Value:
- Accelerates building new A/B features
- Provides proven patterns for agent collaboration
- Reduces implementation time by 50%
- Observable collaboration out of the box

Success Criteria:
- 4 A/B patterns available as templates
- Can create new A/B workflow in <1 hour
- All patterns include observability hooks
- Documentation with examples for each pattern
''',
        'dependencies': ['P0-AB-001'],
        'status': 'not_started',
        'estimated_effort': '20 points',
        'tasks': [
            'Task 1: Design A/B pattern workflow DSL',
            'Task 2: Implement Generate-Validate pattern',
            'Task 3: Implement Propose-Critique-Refine pattern',
            'Task 4: Add A/B-specific observability hooks',
            'Task 5: Create pattern documentation and examples',
            'Task 6: Refactor demo to use new patterns'
        ],
        'acceptance_criteria': [
            'AC1: Generate-Validate pattern available as workflow template',
            'AC2: Propose-Critique-Refine pattern supports iterative loops',
            'AC3: Pattern usage reduces boilerplate by 50%',
            'AC4: All patterns include built-in observability',
            'AC5: Documentation includes working example for each pattern'
        ],
        'functional_test_plan': [
            {
                'acceptance_criterion': 'AC1',
                'test_description': 'Verify Generate-Validate pattern',
                'test_commands': [
                    {
                        'command': 'python tests/test_ab_patterns.py TestGenerateValidate',
                        'command_type': 'bash',
                        'expected_output': 'test_generate_validate PASSED',
                        'success_criteria': 'Pattern executes successfully'
                    }
                ]
            }
        ],
        'roadmap_extensions': {
            'feature_id': 'AB-PATTERNS',
            'phase_id': 'phase-1',
            'week_range': '2-3',
            'business_impact': 'Accelerates A/B feature development by 50%'
        }
    }
]

def update_backlog():
    """Update the backlog with new priorities and stories"""

    # Load existing backlog
    with open(BACKLOG_PATH) as f:
        backlog = yaml.safe_load(f)

    print("📝 Updating backlog for A/B agent prioritization...")
    print()

    # 1. Add new stories
    print("✅ Adding new stories:")
    for story in NEW_STORIES:
        backlog['stories'].insert(0, story)  # Add at beginning for high priority
        print(f"   + {story['story_id']}: {story['title']}")
    print()

    # 2. Update priorities and status
    print("🔄 Updating story priorities:")
    changes = []

    for story in backlog['stories']:
        # Deprioritize DataOps data generation
        if story['story_id'] == 'P0-A2A-F2-002':
            old_priority = story['priority']
            story['priority'] = 'P2'
            # Update story ID to reflect new priority
            story['story_id'] = 'P2-A2A-F2-002'
            changes.append(f"   • P0-A2A-F2-002 → P2-A2A-F2-002 (DataOps - deprioritized)")
            # Update status to not_started since we're deprioritizing
            story['status'] = 'not_started'

        # Deprioritize Hyperlight VM
        elif story['story_id'] == 'P1-A2A-F7-003':
            story['priority'] = 'P2'
            story['story_id'] = 'P2-A2A-F7-003'
            changes.append(f"   • P1-A2A-F7-003 → P2-A2A-F7-003 (Hyperlight - deprioritized)")

        # Update dependencies that referenced old story IDs
        if 'dependencies' in story:
            deps = story['dependencies']
            if 'P0-A2A-F2-002' in deps:
                deps[deps.index('P0-A2A-F2-002')] = 'P2-A2A-F2-002'
            if 'P1-A2A-F7-003' in deps:
                deps[deps.index('P1-A2A-F7-003')] = 'P2-A2A-F7-003'

    for change in changes:
        print(change)
    print()

    # 3. Update metadata
    print("📊 Updating backlog metadata...")
    backlog['backlog_metadata']['version'] += 1
    backlog['backlog_metadata']['last_updated'] = datetime.utcnow().isoformat() + 'Z'

    # Update production readiness
    total_stories = len(backlog['stories'])
    completed_stories = len([s for s in backlog['stories'] if s['status'] == 'completed'])
    backlog['backlog_metadata']['production_readiness']['current'] = f"{completed_stories}/{total_stories} stories completed ({int(completed_stories/total_stories*100)}%)"

    # Add changelog entry
    changelog_entry = {
        'version': backlog['backlog_metadata']['version'],
        'date': datetime.utcnow().isoformat().split('T')[0] + 'T00:00:00Z',
        'author': 'Claude Code',
        'changes': [
            'Added P0-AB-001 - A/B Agent Demo POC (10 points)',
            'Added P1-AB-002 - Enhanced Journey Orchestration with A/B patterns (20 points)',
            'Deprioritized P0-A2A-F2-002 → P2-A2A-F2-002 (DataOps data generation)',
            'Deprioritized P1-A2A-F7-003 → P2-A2A-F7-003 (Hyperlight VM sandboxing)',
            'Recast backlog to prioritize A/B agent development',
            'Option 1: Demo POC (P0-AB-001) - FASTEST PATH',
            'Option 2: Production features (P0-A2A-F4-001+) - NEXT',
            'Option 3: Enhanced patterns (P1-AB-002) - FOUNDATION'
        ],
        'mode': 'recast',
        'stories_added': 2,
        'priority_breakdown': f'P0: {len([s for s in backlog["stories"] if s["priority"] == "P0"])}, P1: {len([s for s in backlog["stories"] if s["priority"] == "P1"])}, P2: {len([s for s in backlog["stories"] if s["priority"] == "P2"])}',
        'status_breakdown': f'completed: {len([s for s in backlog["stories"] if s["status"] == "completed"])}, in_progress: {len([s for s in backlog["stories"] if s["status"] == "in_progress"])}, not_started: {len([s for s in backlog["stories"] if s["status"] == "not_started"])}'
    }

    backlog['backlog_metadata']['changelog'].insert(0, changelog_entry)

    print(f"   Version: {backlog['backlog_metadata']['version']}")
    print(f"   Stories: {total_stories} total, {completed_stories} completed")
    print()

    # 4. Save updated backlog
    print("💾 Saving updated backlog...")
    with open(BACKLOG_PATH, 'w') as f:
        yaml.dump(backlog, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print("✅ Backlog updated successfully!")
    print()

    # Print summary
    print("="*70)
    print("📊 BACKLOG RECAST SUMMARY")
    print("="*70)
    print()
    print("NEW STORIES (A/B Agent Focus):")
    print("  🎯 P0-AB-001: A/B Agent Demo POC (10 points) - NEXT UP")
    print("  🔧 P1-AB-002: Enhanced A/B Patterns (20 points) - AFTER DEMO")
    print()
    print("DEPRIORITIZED STORIES:")
    print("  ⬇️  P2-A2A-F2-002: DataOps data generation (was P0)")
    print("  ⬇️  P2-A2A-F7-003: Hyperlight VM (was P1)")
    print()
    print("NEXT STEPS:")
    print("  1. Start P0-AB-001 (A/B Agent Demo)")
    print("  2. Then P0-A2A-F4-001 (Gong Intelligence - production A/B)")
    print("  3. Then P1-AB-002 (Enhanced patterns)")
    print()
    print("Run: make backlog-next")
    print()

    return backlog

if __name__ == '__main__':
    update_backlog()
