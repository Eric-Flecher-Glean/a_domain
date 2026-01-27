# Claude Code Skills

This directory contains custom skills (slash commands) for the project.

## Skill Organization

Skills are organized into two namespaces for clarity:

### `project/` - a_domain Project Skills
Custom skills specific to the prompt engineering workflow:
- `/project-ux-review-timeline` - UX review of timeline reports
- `/project-generate-examples` - Generate workflow examples
- `/project-new-workflow` - Create new workflow patterns

### `sdlc/` - SDLC Framework Skills
Development lifecycle and governance skills (via symlink to `.sdlc/.sdlc/skills/`):
- `/sdlc-plan` - Query backlog and plan next work
- `/sdlc-implement` - Execute implementation tasks
- `/sdlc-test` - Run test suite and report results
- `/sdlc-quality` - Run governance + tests
- `/sdlc-status` - Display backlog and health status
- `/sdlc-session` - Session start/end workflows
- `/sdlc-artifact` - Search and process artifacts
- `/sdlc-deploy` - Deployment workflow
- `/sdlc-new-feature-chat` - Interactive TDD story creation
- `/sdlc-client-meetings` - Generate client meeting reports

## Available Skills

### `/ux-review-timeline`

**Purpose**: Comprehensive UX review of the Workflow Timeline Reports

**What it does**:
1. Analyzes the current HTML report implementation
2. Compares actual rendering vs. design expectations
3. Defines user personas (engineers, team leads, DevOps, etc.)
4. Maps critical user journeys
5. Evaluates against Nielsen's 10 Usability Heuristics
6. Creates prioritized user stories for improvements
7. Provides actionable design recommendations

**When to use**:
- After implementing new report features
- When gathering feedback from users
- Planning UX improvement sprints
- Before major UI changes
- Periodic quality reviews

**Output**:
- Comprehensive UX review document in `observability/reports/UX-REVIEW-{date}.md`
- 15-20 prioritized user stories
- Implementation roadmap (Quick Wins → Polish → Delight)
- Design system recommendations

**Example usage**:
```bash
/ux-review-timeline
```

The skill will automatically:
- Find the latest timeline report
- Read implementation specs
- Conduct full UX analysis
- Generate actionable stories

---

### `/generate-examples`

Generate example prompts and test cases for the prompt engineering workflow.

---

### `/new-workflow`

Create a new workflow orchestration pattern with agents, stages, and validation.

---

## Creating New Skills

To create a new skill, follow the proper Claude Code skill structure:

1. **Create a skill directory**:
   ```bash
   mkdir -p .claude/skills/my-skill
   ```

2. **Create a `SKILL.md` file** inside the directory:
   ```bash
   touch .claude/skills/my-skill/SKILL.md
   ```

3. **Add frontmatter** at the top of `SKILL.md`:
   ```yaml
   ---
   name: my-skill
   description: Brief description of what this skill does and when to use it
   ---

   # /my-skill - Skill Title

   Your skill instructions here...
   ```

4. **Use the skill** by typing:
   ```bash
   /my-skill
   ```

**Required Structure**:
```
.claude/skills/
└── my-skill/
    └── SKILL.md    # Must be named exactly "SKILL.md"
```

**Frontmatter Fields**:
- `name` (optional): Skill name (defaults to directory name)
- `description` (recommended): Helps Claude decide when to auto-invoke the skill

## Skill Best Practices

- **Clear purpose**: Each skill should solve one specific problem
- **Actionable output**: Generate files, documents, or concrete recommendations
- **Context-aware**: Use project files and structure
- **Reproducible**: Same input → same output
- **Documented**: Explain what, why, when, and how

## Skill Patterns

### Analysis Skills
- Read files/data
- Identify patterns and issues
- Generate reports
- Example: `/ux-review-timeline`

### Generation Skills
- Create new files
- Generate code or content
- Example: `/generate-examples`, `/new-workflow`

### Workflow Skills
- Orchestrate multiple steps
- Coordinate tools and processes
- Example: End-to-end testing workflows

### Review Skills
- Compare expected vs. actual
- Quality checks
- Compliance verification
- Example: `/ux-review-timeline`

## Tips

- Skills have access to all project files
- Skills can call other skills
- Skills can use any tools (Read, Write, Bash, etc.)
- Skills work best with specific, focused objectives
- Document expected inputs and outputs
