#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyyaml>=6.0",
# ]
# ///

"""
Query IMPLEMENTATION_BACKLOG.yaml for story status and next priorities

Usage:
    uv run scripts/backlog_query.py next         # Show next priority story
    uv run scripts/backlog_query.py status       # Show overall backlog status
    uv run scripts/backlog_query.py in-progress  # Show in-progress stories
    uv run scripts/backlog_query.py blocked      # Show blocked stories
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

BACKLOG_PATH = Path('.sdlc/IMPLEMENTATION_BACKLOG.yaml')

# ANSI color codes
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
BOLD = '\033[1m'
RESET = '\033[0m'


def load_backlog() -> Dict[str, Any]:
    """Load the backlog YAML"""
    if not BACKLOG_PATH.exists():
        print(f"{RED}❌ Error: Backlog not found at {BACKLOG_PATH}{RESET}")
        sys.exit(1)

    with open(BACKLOG_PATH) as f:
        return yaml.safe_load(f)


def get_story_display_name(story: Dict) -> str:
    """Get formatted story display name"""
    story_id = story.get('story_id', 'UNKNOWN')
    title = story.get('title', 'Untitled')
    # Truncate title if too long
    if len(title) > 60:
        title = title[:57] + "..."
    return f"{story_id}: {title}"


def get_priority_order(priority: str) -> int:
    """Convert priority to sort order"""
    priority_map = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
    return priority_map.get(priority, 99)


def show_next_story(backlog: Dict):
    """Show the next priority story to work on"""
    stories = backlog.get('stories', [])

    # Find in-progress stories
    in_progress = [s for s in stories if s.get('status') == 'in_progress']

    if in_progress:
        print(f"{YELLOW}⏳ In-Progress Stories:{RESET}\n")
        for story in in_progress:
            print(f"  {BOLD}{get_story_display_name(story)}{RESET}")
            print(f"  Priority: {story.get('priority', 'N/A')}")
            print(f"  Effort: {story.get('estimated_effort', 'N/A')}")
            print()
        print(f"{CYAN}💡 Continue working on the story above{RESET}")
        print(f"{CYAN}   Run: /implement {in_progress[0].get('story_id')}{RESET}")
        return

    # Find next not_started story by priority
    not_started = [s for s in stories if s.get('status') == 'not_started']

    if not not_started:
        print(f"{GREEN}🎉 All stories completed!{RESET}")
        return

    # Sort by priority, then by story_id
    not_started.sort(key=lambda s: (
        get_priority_order(s.get('priority', 'P3')),
        s.get('story_id', '')
    ))

    next_story = not_started[0]

    print(f"{GREEN}🎯 Next Priority Story:{RESET}\n")
    print(f"  {BOLD}{get_story_display_name(next_story)}{RESET}")
    print(f"  Priority: {next_story.get('priority', 'N/A')}")
    print(f"  Type: {next_story.get('type', 'N/A')}")
    print(f"  Effort: {next_story.get('estimated_effort', 'N/A')}")

    # Show description preview
    description = next_story.get('description', '')
    if description:
        # Get first line or first 100 chars
        preview = description.split('\n')[0][:100]
        print(f"  Description: {preview}...")

    print()
    print(f"{CYAN}💡 To start this story:{RESET}")
    print(f"{CYAN}   Run: /implement {next_story.get('story_id')}{RESET}")

    # Show next 3 stories in queue
    if len(not_started) > 1:
        print(f"\n{YELLOW}📋 Next 3 in Queue:{RESET}")
        for story in not_started[1:4]:
            print(f"  • {story.get('priority', 'N/A')} - {story.get('story_id', 'N/A')}")


def show_status(backlog: Dict):
    """Show overall backlog status"""
    stories = backlog.get('stories', [])
    metadata = backlog.get('backlog_metadata', {})

    # Count by status
    status_counts = {}
    for story in stories:
        status = story.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

    # Count by priority
    priority_counts = {}
    for story in stories:
        priority = story.get('priority', 'unknown')
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    # Calculate completion percentage
    completed = status_counts.get('completed', 0)
    total = len(stories)
    pct_complete = int((completed / total * 100)) if total > 0 else 0

    print(f"{GREEN}═══════════════════════════════════════{RESET}")
    print(f"{GREEN}   a_domain Backlog Status{RESET}")
    print(f"{GREEN}═══════════════════════════════════════{RESET}\n")

    print(f"{BOLD}Overall Progress:{RESET}")
    print(f"  Total Stories: {total}")
    print(f"  Completed: {completed} ({pct_complete}%)")
    print(f"  In Progress: {status_counts.get('in_progress', 0)}")
    print(f"  Not Started: {status_counts.get('not_started', 0)}")
    print(f"  Blocked: {status_counts.get('blocked', 0)}")

    print(f"\n{BOLD}By Priority:{RESET}")
    for priority in ['P0', 'P1', 'P2', 'P3']:
        count = priority_counts.get(priority, 0)
        if count > 0:
            print(f"  {priority}: {count} stories")

    print(f"\n{BOLD}Backlog Metadata:{RESET}")
    print(f"  Version: {metadata.get('version', 'unknown')}")
    print(f"  Last Updated: {metadata.get('last_updated', 'unknown')}")

    production_readiness = metadata.get('production_readiness', {})
    if production_readiness:
        print(f"\n{BOLD}Production Readiness:{RESET}")
        print(f"  {production_readiness.get('current', 'N/A')}")

    print()


def show_in_progress(backlog: Dict):
    """Show all in-progress stories"""
    stories = backlog.get('stories', [])
    in_progress = [s for s in stories if s.get('status') == 'in_progress']

    if not in_progress:
        print(f"{YELLOW}No stories currently in progress{RESET}")
        print(f"{CYAN}Run: make backlog-next to see next priority{RESET}")
        return

    print(f"{YELLOW}⏳ In-Progress Stories ({len(in_progress)}):{RESET}\n")

    for story in in_progress:
        print(f"  {BOLD}{get_story_display_name(story)}{RESET}")
        print(f"  Priority: {story.get('priority', 'N/A')}")
        print(f"  Effort: {story.get('estimated_effort', 'N/A')}")

        # Show tasks if available
        tasks = story.get('tasks', [])
        if tasks:
            print(f"  Tasks: {len(tasks)} total")

        print()


def show_blocked(backlog: Dict):
    """Show all blocked stories"""
    stories = backlog.get('stories', [])
    blocked = [s for s in stories if s.get('status') == 'blocked']

    if not blocked:
        print(f"{GREEN}✅ No blocked stories{RESET}")
        return

    print(f"{RED}🚫 Blocked Stories ({len(blocked)}):{RESET}\n")

    for story in blocked:
        print(f"  {BOLD}{get_story_display_name(story)}{RESET}")
        print(f"  Priority: {story.get('priority', 'N/A')}")

        # Show blocker reason if available
        blocker = story.get('blocker_reason', 'Unknown')
        print(f"  Blocker: {blocker}")

        # Show dependencies
        deps = story.get('dependencies', [])
        if deps:
            print(f"  Depends on: {', '.join(deps)}")

        print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python backlog_query.py {next|status|in-progress|blocked}")
        sys.exit(1)

    command = sys.argv[1]
    backlog = load_backlog()

    if command == 'next':
        show_next_story(backlog)
    elif command == 'status':
        show_status(backlog)
    elif command == 'in-progress':
        show_in_progress(backlog)
    elif command == 'blocked':
        show_blocked(backlog)
    else:
        print(f"Unknown command: {command}")
        print("Available commands: next, status, in-progress, blocked")
        sys.exit(1)


if __name__ == '__main__':
    main()
