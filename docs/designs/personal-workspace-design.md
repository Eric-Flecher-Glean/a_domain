# Personal Knowledge Workspace - Design Document

**Story ID:** P0-A2A-F5000
**Feature Set:** F5 - Personal Knowledge Workspace
**Target Users:** Individual contributors optimizing personal workflows
**Date:** 2026-02-05

---

## Executive Summary

The Personal Knowledge Workspace is a centralized hub that automatically maintains an inventory of user artifacts, builds a knowledge graph of relationships, detects behavioral patterns, suggests workflow automations, and provides productivity insights.

**Key Value Propositions:**
- **Automatic Discovery**: No manual cataloging - workspace discovers and tracks all artifacts
- **Relationship Mapping**: Knowledge graph shows connections between code, docs, people, projects
- **Pattern Recognition**: Identifies work habits, context switches, focus patterns
- **Intelligent Automation**: Suggests automations based on detected repetitive behaviors
- **Actionable Insights**: Dashboard highlights time allocation, bottlenecks, optimization opportunities

---

## 1. Data Inventory

### Purpose

Maintain a comprehensive catalog of all user artifacts with rich metadata for search, analysis, and relationship building.

### Artifact Types

**Code Artifacts:**
- Source files (.py, .js, .ts, .java, .go, etc.)
- Configuration files (.yaml, .json, .toml, .env)
- Build scripts (Makefile, package.json, requirements.txt)
- Git repositories (local clones)

**Documentation Artifacts:**
- Markdown files (.md)
- Architecture diagrams (.svg, .png, .drawio)
- API specifications (OpenAPI, Swagger)
- Design documents (PRDs, RFCs, ADRs)

**Project Management:**
- Backlog stories (IMPLEMENTATION_BACKLOG.yaml)
- Task lists (TODO.md, issues)
- Sprint plans
- Retrospectives

**Communication:**
- Meeting notes
- Slack threads (via export/API)
- Email threads (via export)
- PR/code review comments

### Metadata Schema

```yaml
artifact:
  id: UUID
  type: code|doc|project|communication
  path: /absolute/path/to/artifact
  name: filename.ext
  created_at: ISO8601 timestamp
  modified_at: ISO8601 timestamp
  accessed_at: ISO8601 timestamp (last opened/viewed)
  size_bytes: integer

  # Content metadata
  language: python|markdown|yaml|etc
  line_count: integer
  word_count: integer (for docs)

  # Ownership
  owner: user_id
  contributors: [user_ids]

  # Relationships
  related_artifacts: [artifact_ids]
  related_people: [user_ids]
  related_projects: [project_ids]

  # Tags & categorization
  tags: [string]
  category: feature|infrastructure|test|doc
  priority: P0|P1|P2|P3

  # Access patterns
  access_count: integer
  last_edit_context: story_id|meeting|task
  typical_edit_time: time_range (e.g., "9am-11am weekdays")
```

### Discovery Mechanisms

**File System Scanning:**
- Watch directories: `~/projects/`, `~/Documents/work/`
- Exclude patterns: `node_modules/`, `.git/objects/`, `*.pyc`
- Incremental updates via file system events (inotify, FSEvents)

**Git Integration:**
- Track repository metadata (remotes, branches, commit history)
- Associate files with commits, PRs, reviews
- Detect co-authors and reviewers

**IDE Integration:**
- VS Code extension: Track file opens, edits, navigation
- IntelliJ plugin: Capture context switches, refactorings
- Vim/Neovim plugin: Track buffer access patterns

**API Integrations:**
- GitHub API: Pull PRs, issues, reviews, comments
- Slack API: Export relevant channels/DMs
- Calendar API: Link meetings to artifacts worked on

### Storage

**Database:** SQLite (local-first)
- File: `~/.knowledge-workspace/inventory.db`
- Tables: `artifacts`, `relationships`, `access_log`, `metadata`
- Indexes: `path`, `type`, `modified_at`, `accessed_at`

**Full-text Search:**
- Embedded: SQLite FTS5 extension
- Alternative: Local Lucene index

**Caching:**
- In-memory LRU cache for frequently accessed artifact metadata
- Invalidation on file system events

---

## 2. Knowledge Graph

### Purpose

Visualize and navigate relationships between artifacts, people, projects, and concepts. Enables discovery of implicit connections and knowledge silos.

### Entity Types

**Primary Entities:**
- **Artifacts**: Files, documents, code
- **People**: Contributors, reviewers, collaborators
- **Projects**: Repositories, features, epics
- **Concepts**: Topics, technologies, domains (e.g., "authentication", "React", "database")

**Relationship Types:**
1. **Imports/Dependencies** (code → code)
   - `file_a imports file_b`
   - `project_x depends_on library_y`

2. **References** (code → doc, doc → doc)
   - `code references design_doc`
   - `story links_to architecture_diagram`

3. **Collaboration** (person → artifact)
   - `person authored artifact`
   - `person reviewed artifact`
   - `person frequently_edits artifact`

4. **Temporal** (artifact → artifact)
   - `edited_together` (within same session)
   - `edited_sequentially` (file_a edited before file_b)

5. **Conceptual** (artifact → concept)
   - `artifact tagged_with concept`
   - `artifact implements pattern`

### Graph Schema

```yaml
node:
  id: UUID
  type: artifact|person|project|concept
  label: Display name
  properties:
    - key: value

edge:
  id: UUID
  source_id: UUID
  target_id: UUID
  type: imports|references|authored|edited_together|tagged_with
  weight: float (0.0-1.0, strength of relationship)
  properties:
    created_at: timestamp
    evidence: [supporting data points]
```

### Relationship Detection

**Code Analysis:**
- **AST Parsing**: Extract imports, function calls, class dependencies
- **Languages**: Python (ast), JavaScript (babel), TypeScript (tsc), Java (JavaParser)
- **Example**: `from module import func` → edge(current_file, module, type=imports)

**Documentation Parsing:**
- **Link Extraction**: Markdown links, references
- **Pattern**: `[text](path/to/file.md)` → edge(current_doc, target_doc, type=references)
- **Cross-references**: Story IDs mentioned in docs → edge(doc, story, type=references)

**Git History Analysis:**
- **Co-edited Files**: Files modified in same commit → edge(file_a, file_b, type=edited_together, weight=frequency)
- **Authorship**: Commit author → edge(person, file, type=authored)
- **Review Chains**: PR reviews → edge(reviewer, file, type=reviewed)

**Temporal Co-occurrence:**
- **Session Tracking**: Files edited within 30-minute window → edge(file_a, file_b, type=edited_in_session)
- **Context Switches**: Switching from file_a to file_b frequently → edge(file_a, file_b, type=context_switch, weight=frequency)

### Graph Storage

**Graph Database:** Neo4j (embedded) or NetworkX (in-process)

**Neo4j Schema:**
```cypher
// Create nodes
CREATE (a:Artifact {id: 'uuid', path: '/path/to/file.py', type: 'code'})
CREATE (p:Person {id: 'uuid', name: 'John Doe'})
CREATE (c:Concept {id: 'uuid', name: 'authentication'})

// Create relationships
MATCH (a:Artifact {id: 'file1'}), (b:Artifact {id: 'file2'})
CREATE (a)-[:IMPORTS {weight: 1.0, created_at: '2026-02-05'}]->(b)
```

**Queries:**
```cypher
// Find all artifacts related to a concept
MATCH (c:Concept {name: 'authentication'})<-[:TAGGED_WITH]-(a:Artifact)
RETURN a

// Find collaboration network
MATCH (p:Person)-[:AUTHORED]->(a:Artifact)<-[:REVIEWED]-(r:Person)
WHERE p.id = 'user123'
RETURN p, a, r

// Find frequently co-edited files
MATCH (a:Artifact)-[e:EDITED_TOGETHER]-(b:Artifact)
WHERE e.weight > 0.7
RETURN a, b, e.weight
ORDER BY e.weight DESC
```

### Visualization

**Web UI:**
- **Library**: D3.js force-directed graph
- **Interactions**:
  - Hover: Show metadata tooltip
  - Click: Navigate to artifact
  - Drag: Rearrange layout
  - Filter: By entity type, relationship type, time range

**Layout Algorithms:**
- Force-directed (default): Natural clustering
- Hierarchical: Project → files tree structure
- Circular: Show collaboration networks

---

## 3. Pattern Detection

### Purpose

Automatically identify recurring behavioral patterns in user workflows to enable automation suggestions and productivity insights.

### Pattern Categories

#### 3.1 Temporal Patterns

**Work Schedule:**
- **Algorithm**: Time-binned frequency analysis
- **Detection**: Group file edits by hour-of-day, day-of-week
- **Threshold**: ≥ 60% of edits in same 2-hour window = "focused period"
- **Example**: "You typically code between 9am-11am on weekdays"

**Context Switch Frequency:**
- **Algorithm**: Session boundary detection
- **Detection**: Track switches between files/projects within 30-min windows
- **Threshold**: > 10 switches per hour = "high context switching"
- **Metric**: Calculate "focus score" = 1 / (switches per hour)

**Deep Work Periods:**
- **Algorithm**: Continuous editing detection
- **Detection**: Uninterrupted editing sessions (no other app opens, no context switches)
- **Threshold**: ≥ 90 minutes continuous = "deep work session"
- **Tracking**: Count per week, identify trends

#### 3.2 Workflow Patterns

**File Access Sequences:**
- **Algorithm**: Sequential pattern mining (SPADE algorithm)
- **Detection**: Identify file sequences that repeat
- **Threshold**: Sequence appears ≥ 5 times = "established pattern"
- **Example**: "You always open test_auth.py after editing auth.py"

**Task Sequences:**
- **Algorithm**: Process mining on task logs
- **Detection**: Track task completion order (e.g., write code → run tests → commit → push)
- **Threshold**: Sequence appears in ≥ 80% of sessions = "standard workflow"
- **Example**: "Your typical workflow: implement → test → review → merge"

**Pre/Post Conditions:**
- **Algorithm**: Association rule mining (Apriori)
- **Detection**: Find rules like "IF review PR from X, THEN edit tests"
- **Threshold**: Confidence ≥ 0.7, Support ≥ 0.3
- **Example**: "After standup meetings, you review PRs 85% of the time"

#### 3.3 Collaboration Patterns

**Review Patterns:**
- **Algorithm**: Temporal association analysis
- **Detection**: Track when you review PRs, from whom, and follow-up actions
- **Threshold**: ≥ 5 reviews from same person with same follow-up = pattern
- **Example**: "You always review Jane's frontend PRs within 2 hours of posting"

**Pair Programming:**
- **Algorithm**: Temporal co-editing detection
- **Detection**: Files edited by 2+ people in overlapping time windows
- **Threshold**: ≥ 3 overlapping sessions per week = "frequent pairing"
- **Example**: "You pair with Bob on database code every Tuesday"

**Handoff Patterns:**
- **Algorithm**: Sequential authorship analysis
- **Detection**: Track artifact ownership transitions
- **Threshold**: Consistent handoff (A → B → C) ≥ 3 times = pattern
- **Example**: "Backend work flows: You → QA → DevOps"

#### 3.4 Content Patterns

**Code Patterns:**
- **Algorithm**: AST similarity detection
- **Detection**: Identify repeated code structures
- **Threshold**: Structural similarity ≥ 0.8 (Levenshtein on AST)
- **Example**: "You write similar error handling in every service"

**Documentation Patterns:**
- **Algorithm**: Template detection via TF-IDF similarity
- **Detection**: Find recurring doc structures
- **Threshold**: Cosine similarity ≥ 0.75
- **Example**: "Your design docs always follow: Context → Proposal → Alternatives → Decision"

### Detection Algorithms

#### Algorithm 1: Time-Binned Frequency Analysis

```python
def detect_temporal_patterns(access_log: List[Access]) -> Dict:
    """
    Detect when user typically works on different artifact types.
    """
    # Bin by hour and day-of-week
    bins = defaultdict(lambda: defaultdict(int))

    for access in access_log:
        hour = access.timestamp.hour
        dow = access.timestamp.weekday()  # 0=Monday
        artifact_type = access.artifact.type

        bins[artifact_type][(hour, dow)] += 1

    # Find peak periods (top 20% of bins)
    patterns = {}
    for artifact_type, bin_counts in bins.items():
        sorted_bins = sorted(bin_counts.items(), key=lambda x: x[1], reverse=True)
        top_20_pct = int(len(sorted_bins) * 0.2)
        peak_periods = sorted_bins[:top_20_pct]

        patterns[artifact_type] = {
            'peak_hours': [h for (h, d), count in peak_periods],
            'peak_days': [d for (h, d), count in peak_periods],
            'concentration': sum(c for _, c in peak_periods) / sum(bin_counts.values())
        }

    return patterns
```

#### Algorithm 2: Sequential Pattern Mining (Simplified SPADE)

```python
def detect_file_sequences(access_log: List[Access], min_support: int = 5) -> List[Sequence]:
    """
    Find frequently occurring file access sequences.
    """
    # Extract sessions (files accessed within 30-min windows)
    sessions = []
    current_session = []
    last_timestamp = None

    for access in sorted(access_log, key=lambda a: a.timestamp):
        if last_timestamp and (access.timestamp - last_timestamp).seconds > 1800:
            # New session (> 30 min gap)
            sessions.append(current_session)
            current_session = []

        current_session.append(access.artifact.path)
        last_timestamp = access.timestamp

    # Count n-grams (sequences of length 2, 3, 4)
    sequence_counts = defaultdict(int)

    for session in sessions:
        for n in [2, 3, 4]:
            for i in range(len(session) - n + 1):
                seq = tuple(session[i:i+n])
                sequence_counts[seq] += 1

    # Filter by min_support
    frequent_sequences = [
        {'sequence': seq, 'count': count}
        for seq, count in sequence_counts.items()
        if count >= min_support
    ]

    return sorted(frequent_sequences, key=lambda x: x['count'], reverse=True)
```

#### Algorithm 3: Association Rule Mining

```python
def detect_task_associations(task_log: List[Task], min_confidence: float = 0.7) -> List[Rule]:
    """
    Find association rules like "IF task_a THEN task_b (with 80% confidence)".
    """
    # Build co-occurrence matrix
    task_pairs = defaultdict(int)
    task_counts = defaultdict(int)

    # Group by day
    tasks_by_day = defaultdict(list)
    for task in task_log:
        day = task.timestamp.date()
        tasks_by_day[day].append(task.name)
        task_counts[task.name] += 1

    # Count co-occurrences
    for day, tasks in tasks_by_day.items():
        unique_tasks = set(tasks)
        for task_a in unique_tasks:
            for task_b in unique_tasks:
                if task_a != task_b:
                    task_pairs[(task_a, task_b)] += 1

    # Calculate confidence: P(B|A) = count(A,B) / count(A)
    rules = []
    for (task_a, task_b), cooccur_count in task_pairs.items():
        confidence = cooccur_count / task_counts[task_a]

        if confidence >= min_confidence:
            rules.append({
                'antecedent': task_a,
                'consequent': task_b,
                'confidence': confidence,
                'support': cooccur_count / len(tasks_by_day)  # % of days
            })

    return sorted(rules, key=lambda r: r['confidence'], reverse=True)
```

### Storage

**Pattern Database:**
```sql
CREATE TABLE detected_patterns (
    id UUID PRIMARY KEY,
    type VARCHAR(50),  -- temporal|workflow|collaboration|content
    category VARCHAR(50),  -- work_schedule|file_sequence|review|etc
    pattern_data JSONB,
    confidence FLOAT,
    support INT,  -- number of occurrences
    first_detected TIMESTAMP,
    last_detected TIMESTAMP,
    status VARCHAR(20)  -- active|dormant|obsolete
);
```

---

## 4. Automation Suggestions

### Purpose

Proactively suggest workflow automations based on detected patterns, reducing repetitive manual work and context switches.

### Suggestion Categories

#### 4.1 Task Automation

**Trigger-Action Suggestions:**

**Example 1: Post-Standup PR Reviews**
- **Pattern Detected**: "After standup meetings (10am daily), you review PRs from frontend team within 30 minutes (confidence: 0.85)"
- **Suggestion**: "Automate PR review workflow - fetch frontend PRs after standup and open in tabs?"
- **Automation**:
  ```bash
  # Cron job: 10:05 AM daily
  gh pr list --label frontend --state open --json number,title,author | \
    jq '.[] | "open https://github.com/org/repo/pull/\(.number)"' | \
    xargs -I {} open {}
  ```

**Example 2: Pre-Commit Test Running**
- **Pattern Detected**: "You run `pytest` before every git commit (100 commits, 98% compliance)"
- **Suggestion**: "Add pre-commit hook to auto-run pytest?"
- **Automation**:
  ```bash
  # .git/hooks/pre-commit
  #!/bin/bash
  pytest tests/ || exit 1
  ```

**Example 3: Meeting Note Template**
- **Pattern Detected**: "You create meeting notes in docs/meetings/ with same structure every Monday 1:1"
- **Suggestion**: "Auto-generate meeting note template for Monday 1:1s?"
- **Automation**:
  ```bash
  # Script: generate_meeting_note.sh
  DATE=$(date +%Y-%m-%d)
  cat > "docs/meetings/1:1-manager-${DATE}.md" <<EOF
  # 1:1 with Manager - ${DATE}

  ## Updates
  -

  ## Blockers
  -

  ## Action Items
  - [ ]
  EOF
  ```

#### 4.2 Context Switching Reduction

**Example 4: File Bundling**
- **Pattern Detected**: "You always edit auth.py, test_auth.py, and auth_schema.yaml together (15 sessions)"
- **Suggestion**: "Open these 3 files as a workspace/session?"
- **Automation**:
  ```json
  // .vscode/auth-workflow.code-workspace
  {
    "folders": [
      {"path": "src/auth/auth.py"},
      {"path": "tests/test_auth.py"},
      {"path": "schemas/auth_schema.yaml"}
    ]
  }
  ```

**Example 5: Terminal Command Sequences**
- **Pattern Detected**: "You always run `git pull && npm install && npm test` after switching branches (20 times)"
- **Suggestion**: "Create alias for post-branch-switch workflow?"
- **Automation**:
  ```bash
  # Add to .bashrc
  alias branch-refresh='git pull && npm install && npm test'
  ```

#### 4.3 Notification Optimization

**Example 6: Focused Review Notifications**
- **Pattern Detected**: "You only review PRs from 3 specific people, ignore 80% of other PR notifications"
- **Suggestion**: "Filter GitHub notifications to only show PRs from Alice, Bob, Carol?"
- **Automation**:
  ```yaml
  # GitHub notification filter rule
  filters:
    - from: [alice, bob, carol]
      type: pull_request
      action: notify_immediately
    - from: others
      type: pull_request
      action: digest_daily
  ```

#### 4.4 Documentation Automation

**Example 7: Changelog Generation**
- **Pattern Detected**: "You manually update CHANGELOG.md after every release, copy-pasting from git log (12 releases)"
- **Suggestion**: "Auto-generate changelog from conventional commits?"
- **Automation**:
  ```bash
  # Script: generate_changelog.sh
  git log --pretty=format:'- %s (%h)' $(git describe --tags --abbrev=0)..HEAD > CHANGELOG.new.md
  ```

### Suggestion Criteria

**Minimum Thresholds for Automation Suggestions:**

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| **Pattern Frequency** | ≥ 5 occurrences | Ensures it's a real pattern, not coincidence |
| **Pattern Confidence** | ≥ 0.7 | 70%+ consistency indicates reliable behavior |
| **Time Savings** | ≥ 2 min/occurrence | Must save meaningful time |
| **Total Time Saved** | ≥ 30 min/month | Cumulative savings justify setup effort |
| **Automation Complexity** | ≤ "Medium" | Must be implementable with scripts/hooks/aliases |
| **Risk Level** | "Low" or "Medium" | Avoid automations that could break critical workflows |

**Scoring Formula:**
```python
def calculate_suggestion_score(pattern: Pattern) -> float:
    """
    Score automation suggestion from 0-100.
    Higher score = higher priority suggestion.
    """
    # Frequency score (0-30 points)
    freq_score = min(pattern.frequency / 20, 1.0) * 30

    # Confidence score (0-20 points)
    conf_score = pattern.confidence * 20

    # Time savings score (0-30 points)
    monthly_savings_min = pattern.time_per_occurrence * pattern.frequency * 4
    time_score = min(monthly_savings_min / 120, 1.0) * 30

    # Ease of automation (0-20 points)
    ease_score = {
        'trivial': 20,  # Alias, env var
        'simple': 15,   # Script, hook
        'medium': 10,   # Multi-step automation
        'complex': 5    # Requires infrastructure
    }[pattern.automation_complexity]

    total_score = freq_score + conf_score + time_score + ease_score
    return total_score
```

### Suggestion Delivery

**UI Presentation:**
- **Dashboard Widget**: "Suggested Automations" panel
- **Notification**: Toast on pattern detection threshold
- **Weekly Digest**: Email with top 3 suggestions

**Suggestion Format:**
```yaml
suggestion:
  id: UUID
  title: "Automate post-standup PR reviews"
  pattern_id: UUID
  category: task_automation
  description: "After standup meetings, you review frontend PRs. We can automate fetching and opening them."

  detected_pattern:
    trigger: "After standup meeting (10am daily)"
    action: "Review PRs from @frontend team"
    frequency: 20 occurrences
    confidence: 0.85

  proposed_automation:
    type: cron_job
    script: |
      #!/bin/bash
      gh pr list --label frontend --state open --json number,title,author | \
        jq '.[] | "open https://github.com/org/repo/pull/\(.number)"' | \
        xargs -I {} open {}

  effort_estimate: "5 minutes to set up"
  time_savings: "~10 min/day = 3.5 hours/month"
  risk: low

  score: 85.5
  status: pending  # pending|accepted|rejected|implemented
```

---

## 5. Productivity Insights Dashboard

### Purpose

Provide actionable insights into time allocation, focus patterns, collaboration efficiency, and workflow bottlenecks.

### Dashboard Sections

#### 5.1 Time Allocation

**Visualization:** Sunburst chart or treemap

**Metrics:**
- **Time by Project**: % of work time per repository/project
- **Time by Activity**: Coding (60%), Reviews (15%), Meetings (15%), Docs (10%)
- **Time by Feature Area**: Auth (25%), API (40%), Frontend (20%), DevOps (15%)

**Data Collection:**
- IDE time tracking (active editing time)
- Git commit timestamps (coding sessions)
- Calendar API (meeting time)
- File access logs (documentation time)

**Insights:**
```
"You spent 40% of this week on API work, up from 25% average.
 Consider: Is this expected for current sprint goals?"

"Documentation time: 5% (vs 10% target).
 Suggestion: Block 1 hour Friday for doc updates."
```

#### 5.2 Focus Analysis

**Visualization:** Timeline heatmap

**Metrics:**
- **Deep Work Hours**: Uninterrupted 90+ min sessions
- **Focus Score**: 1 / (context switches per hour)
- **Optimal Work Windows**: Time periods with highest focus score
- **Distraction Sources**: Meetings, notifications, chat

**Focus Score Calculation:**
```python
def calculate_focus_score(hour: Hour) -> float:
    """
    Calculate focus quality for a given hour (0-100).
    """
    # Factors
    context_switches = count_context_switches(hour)  # File/app switches
    interruptions = count_interruptions(hour)  # Notifications, meetings
    continuous_work_min = longest_continuous_work_period(hour)

    # Base score
    base_score = 100

    # Penalties
    base_score -= context_switches * 5  # -5 per switch
    base_score -= interruptions * 10  # -10 per interruption

    # Bonuses
    if continuous_work_min >= 25:  # Pomodoro threshold
        base_score += 20

    return max(0, min(100, base_score))
```

**Insights:**
```
"Your best focus hours: 9-11am (avg score: 85).
 Your worst: 2-4pm (avg score: 35, high meeting density).

 Suggestion: Schedule deep work tasks for mornings,
             move meetings to afternoons."
```

#### 5.3 Collaboration Metrics

**Visualization:** Network graph + bar charts

**Metrics:**
- **Review Turnaround Time**: Avg time to review others' PRs
- **Review Received Time**: Avg time for your PRs to get reviewed
- **Collaboration Network Size**: # of unique collaborators
- **Collaboration Frequency**: Reviews/week, pair sessions/week
- **Knowledge Silos**: Projects with <2 collaborators

**Insights:**
```
"You reviewed 12 PRs this week, avg turnaround: 4 hours.
 This is faster than team average (6 hours). Great job!

 Warning: 'auth-service' has only 1 contributor (you).
 Suggestion: Pair with teammate to reduce bus factor."
```

#### 5.4 Workflow Efficiency

**Visualization:** Sankey diagram (workflow flows)

**Metrics:**
- **Cycle Time**: Time from first commit to merge
- **Rework Rate**: % of code rewritten within 7 days
- **Test-to-Code Ratio**: Lines of test vs. production code
- **Bottleneck Tasks**: Tasks that consistently take longer than estimated

**Workflow Analysis:**
```python
def analyze_workflow_efficiency(tasks: List[Task]) -> Dict:
    """
    Identify bottlenecks in development workflow.
    """
    stages = ['implement', 'test', 'review', 'merge']
    stage_durations = defaultdict(list)

    for task in tasks:
        for stage in stages:
            duration = task.get_stage_duration(stage)
            stage_durations[stage].append(duration)

    bottlenecks = []
    for stage, durations in stage_durations.items():
        avg_duration = statistics.mean(durations)
        p90_duration = statistics.quantiles(durations, n=10)[8]  # 90th percentile

        if p90_duration > avg_duration * 2:
            bottlenecks.append({
                'stage': stage,
                'avg_duration_hours': avg_duration / 3600,
                'p90_duration_hours': p90_duration / 3600,
                'recommendation': get_recommendation(stage)
            })

    return {'bottlenecks': bottlenecks}
```

**Insights:**
```
"Bottleneck detected: 'review' stage.
 Avg: 8 hours, P90: 24 hours

 Your PRs spend 3x longer in review than team average.
 Suggestions:
   - Smaller PRs (your avg: 500 lines, team avg: 200)
   - Request reviews from specific people
   - Add more context to PR descriptions"
```

#### 5.5 Trends & Comparisons

**Visualization:** Line charts, sparklines

**Metrics:**
- **Week-over-week Changes**: Commits, PRs, reviews, focus hours
- **Month-over-month Trends**: Project time allocation shifts
- **Personal Baselines**: Compare current week to your 4-week average
- **Team Comparisons** (optional): Percentile rankings (anonymized)

**Insights:**
```
"This week vs last week:
 ✅ Focus hours: +15% (12h → 14h)
 ⚠️  Context switches: +25% (80 → 100)
 ✅ PR reviews: +3 (9 → 12)
 ❌ Deep work sessions: -2 (5 → 3)

 Overall: Productivity stable, but fragmentation increasing.
 Action: Review notification settings."
```

### Dashboard UI Mockup

```
┌─────────────────────────────────────────────────────────────────┐
│  Personal Knowledge Workspace - Dashboard                       │
│  Week of Feb 3-9, 2026                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐  ┌──────────────────────────────────┐ │
│  │ Time Allocation     │  │ Focus Analysis                   │ │
│  │                     │  │                                  │ │
│  │ [Sunburst Chart]    │  │ Best Focus: 9-11am (score: 85) │ │
│  │                     │  │ Worst Focus: 2-4pm (score: 35) │ │
│  │ API: 40%            │  │                                  │ │
│  │ Auth: 25%           │  │ [Heatmap Timeline]              │ │
│  │ Frontend: 20%       │  │                                  │ │
│  │ DevOps: 15%         │  │ Deep Work Sessions: 3           │ │
│  └─────────────────────┘  └──────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Suggested Automations (3)                                │  │
│  │                                                           │  │
│  │ 1. [Score: 85] Automate post-standup PR reviews          │  │
│  │    ⏱ Saves 3.5 hrs/month • 🔧 5 min setup • ⚠️ Low risk   │  │
│  │    [Accept] [Reject] [Details]                            │  │
│  │                                                           │  │
│  │ 2. [Score: 78] Pre-commit test hook                       │  │
│  │ 3. [Score: 65] Monday 1:1 note template                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────┐  ┌──────────────────────────────────┐ │
│  │ Collaboration       │  │ Workflow Efficiency              │ │
│  │                     │  │                                  │ │
│  │ PRs Reviewed: 12    │  │ Bottleneck: Review stage        │ │
│  │ Turnaround: 4h      │  │ Avg: 8h, P90: 24h               │ │
│  │                     │  │                                  │ │
│  │ [Network Graph]     │  │ [Sankey Diagram]                │ │
│  │                     │  │                                  │ │
│  │ Knowledge Silos: 1  │  │ Suggestion: Smaller PRs         │ │
│  └─────────────────────┘  └──────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Trends                                                    │  │
│  │                                                           │  │
│  │ This week vs last:                                        │  │
│  │ ✅ Focus hours: +15% (12h → 14h)                          │  │
│  │ ⚠️  Context switches: +25% (80 → 100)                      │  │
│  │ ✅ PR reviews: +3 (9 → 12)                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Roadmap

### Phase 1: Data Inventory (F5-001)
**Duration:** 2 weeks

**Deliverables:**
- SQLite database schema for artifacts
- File system scanner with incremental updates
- Git integration for repository metadata
- Basic REST API for querying inventory

**Acceptance Criteria:**
- Scans user directories and discovers all artifacts
- Metadata includes file stats, git info, access patterns
- API returns artifact list with filters

### Phase 2: Knowledge Graph (F5-002)
**Duration:** 3 weeks

**Deliverables:**
- Neo4j/NetworkX graph database setup
- Code analysis for import/dependency relationships
- Documentation parser for cross-references
- Web UI for graph visualization (D3.js)

**Acceptance Criteria:**
- Graph contains nodes for artifacts, people, projects, concepts
- Relationships detected from code imports, git history, doc links
- UI allows navigation and filtering

### Phase 3: Pattern Detection & Automation (F5-003)
**Duration:** 3 weeks

**Deliverables:**
- Time-binned frequency analysis implementation
- Sequential pattern mining (SPADE)
- Association rule mining (Apriori)
- Automation suggestion engine
- Suggestion UI in dashboard

**Acceptance Criteria:**
- Detects temporal, workflow, collaboration patterns
- Generates automation suggestions with scores
- Users can accept/reject/implement suggestions

### Phase 4: Productivity Insights Dashboard (F5-004)
**Duration:** 2 weeks

**Deliverables:**
- Dashboard web UI with 5 sections
- Time allocation visualization (sunburst)
- Focus analysis heatmap
- Collaboration network graph
- Workflow efficiency Sankey diagram
- Trends line charts

**Acceptance Criteria:**
- Dashboard displays all metrics
- Updates in real-time or daily
- Provides actionable insights and recommendations

---

## Technical Stack

**Backend:**
- **Language**: Python 3.10+
- **Web Framework**: FastAPI
- **Database**: SQLite (inventory), Neo4j (graph)
- **Background Tasks**: Celery + Redis
- **File Watching**: watchdog library

**Frontend:**
- **Framework**: React + TypeScript
- **Visualization**: D3.js, Recharts
- **State Management**: Zustand
- **Styling**: Tailwind CSS

**Analysis:**
- **Code Parsing**: ast (Python), babel (JavaScript), tree-sitter
- **NLP**: spaCy (concept extraction)
- **Graph Algorithms**: NetworkX, Neo4j Cypher
- **Time Series**: Pandas, NumPy

**Infrastructure:**
- **Deployment**: Docker, docker-compose
- **API Docs**: OpenAPI/Swagger
- **Testing**: pytest, Jest

---

## Privacy & Security

**Data Ownership:**
- All data stored locally on user's machine
- No cloud sync unless explicitly enabled
- User can export/delete all data

**Sensitive Data Handling:**
- Exclude patterns: `.env`, `credentials.json`, `secrets/`
- Sanitize code before sending to LLM (if AI features added)
- Never track content of confidential files

**Access Control:**
- Workspace data accessible only to user
- Optional: Share anonymized insights with team (opt-in)

---

## Success Metrics

**Adoption:**
- % of workspace features used weekly
- Daily active users (if team deployment)

**Impact:**
- Time saved via accepted automations
- Reduction in context switches (baseline vs. post-adoption)
- Increase in deep work hours
- Improvement in PR review turnaround time

**Satisfaction:**
- User survey: "How valuable is this workspace?" (1-5 scale)
- Feature requests and usage feedback

---

## Future Enhancements

**AI Integration:**
- Natural language queries: "What did I work on related to auth last week?"
- Predictive automation: Suggest automations before pattern fully forms
- Smart scheduling: "Best time to work on X based on your patterns"

**Team Features:**
- Team knowledge graph (shared artifacts)
- Collaboration recommendations: "You should pair with Alice on Y"
- Team productivity benchmarks (anonymized)

**IDE Plugins:**
- VS Code extension for real-time workspace insights
- IntelliJ plugin for automation triggers
- Vim plugin for pattern notifications

**Integrations:**
- Jira/Linear: Link tasks to artifacts
- Slack: Automation suggestions in DMs
- Notion/Obsidian: Sync knowledge graph

---

## Conclusion

The Personal Knowledge Workspace transforms passive artifact management into an active intelligence system. By automatically discovering, relating, analyzing, and optimizing user workflows, it enables individual contributors to work smarter, reduce friction, and maximize deep work time.

**Next Steps:**
1. Review and approve this design document
2. Refine implementation stories F5-001 through F5-004
3. Begin Phase 1 (Data Inventory) development
4. Iterate based on user feedback

