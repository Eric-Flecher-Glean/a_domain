# Claude Code Skills

This directory contains custom skills (slash commands) for the project.

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

To create a new skill:

1. **Create a markdown file** in `.claude/skills/`
   ```bash
   touch .claude/skills/my-skill.md
   ```

2. **Define the skill behavior** using natural language instructions

3. **Use the skill** by typing:
   ```bash
   /my-skill
   ```

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
