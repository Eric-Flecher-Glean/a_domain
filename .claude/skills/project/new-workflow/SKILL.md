---
name: new-workflow
description: Interactive skill that guides users through creating new workflows. Discovers existing workflows and agents, helps select bounded contexts, designs workflow stages, configures validation rules, and generates all required configuration files.
---

# /new-workflow - Interactive Workflow Designer

## Description

Interactive skill that guides users through creating new workflows in the document-driven agent orchestration system. Discovers existing workflows and agents for reuse, helps select bounded contexts, designs workflow stages, configures validation rules, and generates all required configuration files.

## Usage

```
/new-workflow
```

Simply invoke the skill and answer the questions to design your workflow.

## Capabilities

- **Workflow Discovery**: Searches existing workflows to suggest reusable patterns
- **Agent Matching**: Finds existing agents by bounded context and capabilities
- **Bounded Context Guidance**: Helps select appropriate domain context
- **Stage Design**: Designs workflow stages with agent orchestration
- **Validation Configuration**: Sets up quality gates and feedback loops
- **File Generation**: Creates all required workflow configuration files
- **Design Validation**: Checks for errors before file creation
- **Documentation**: Generates README and usage instructions

## Workflow Creation Process

### Phase 1: Discovery
- Ask about the problem being solved
- Search for similar existing workflows
- Suggest reuse opportunities

### Phase 2: Context Selection
- Help select bounded context (PromptEngineering, WorkflowOrchestration, ContextDiscovery, GleanIntegration)
- Guide on creating new contexts if needed

### Phase 3: Agent Selection
- List available agents in selected context
- Suggest agents by capability match
- Support creating new agents if needed

### Phase 4: Pattern Selection
- Choose workflow pattern (stg-val-wkf, sequential, parallel, custom)
- Configure orchestration logic
- Set up feedback loops if applicable

### Phase 5: Stage Configuration
- Define each workflow stage
- Configure agent settings (model, temperature, tokens)
- Map inputs and outputs between stages

### Phase 6: Validation Setup
- Configure validation dimensions (structural, completeness, quality, context)
- Set success thresholds
- Define feedback generation rules

### Phase 7: Review & Generate
- Present complete workflow design
- Validate for errors (naming, circular dependencies, data flow)
- Generate all configuration files
- Create documentation

## Knowledge Base

This skill has access to comprehensive knowledge about:
- **Bounded Contexts**: All available contexts and when to use them
- **Agent Catalog**: All existing agents with capabilities and contracts
- **Workflow Patterns**: Common orchestration patterns and their use cases
- **Validation Dimensions**: Standard validation criteria and scoring

See `.claude/knowledge/workflow-creation/` for details.

## Templates

The skill uses templates to generate files:
- `workflow-metadata.template.json` - Workflow definition
- `stage-config.template.json` - Stage configuration
- `instructions.template.md` - Agent instructions
- `validation-rules.template.json` - Validation rules
- `agent-spec.template.yaml` - New agent specifications

Templates are located in `workflow-orchestration/templates/`.

## Output Files

A typical workflow generates:

```
workflow-orchestration/workflows/{workflow-id}/
├── workflow-metadata.json          # Master workflow definition
├── config/
│   └── workflow-settings.json      # Configuration overrides
├── stages/
│   ├── 01-{stage-name}/
│   │   ├── stage-config.json       # Agent and I/O config
│   │   ├── instructions.md         # Processing instructions
│   │   ├── validation-rules.json   # Quality validation rules
│   │   └── examples/               # Good/bad examples
│   │       ├── good/
│   │       └── bad/
│   └── 02-{next-stage}/
│       └── [same structure]
├── README.md                        # Workflow documentation
└── docs/
    └── architecture.md              # Design decisions

agents/{new-agent-id}/              # If new agents created
└── agent-spec.yaml                 # Agent specification
```

## Example Session

```
User: /new-workflow

Claude: I'll help you create a new workflow. Let's start by understanding what you're building.

**Question 1:** What problem are you trying to solve? Describe the workflow in natural language.

User: I want to create a workflow that analyzes customer feedback from support tickets and generates sentiment reports with action items.

Claude: Great! Let me search for similar existing workflows...

I found these similar workflows:
- **prompt-generation** (58% match) - Uses staged validation pattern

**Question 2:** Which bounded context does this belong to?
- [ ] PromptEngineering (XML prompt generation/validation)
- [ ] WorkflowOrchestration (coordinating agents)
- [ ] ContextDiscovery (task analysis, input mapping)
- [ ] GleanIntegration (Glean MCP integration)
- [x] New domain (describe...)

User: New domain - CustomerAnalytics

Claude: Creating a new bounded context: CustomerAnalytics (Supporting Domain)

**Question 3:** What agents do you need?

Existing agents available:
- prompt-generator-001 (PromptEngineering)
- prompt-validator-001 (PromptEngineering)

Do you need to create new agents? [y/n]

User: Yes, I need:
1. Feedback analyzer (analyzes sentiment)
2. Report generator (creates action items)

Claude: **Question 4:** What pattern should this workflow follow?
- [x] stg-val-wkf (Staged validation with feedback loops) - Recommended
- [ ] sequential (Linear stages, no feedback)
- [ ] parallel (Multiple stages run concurrently)

User: stg-val-wkf

Claude: Perfect! Now let's configure your stages.

**Stage 1 - Feedback Analysis:**
- Agent: feedback-analyzer-001 (new)
- Validation required? yes
- Success threshold: 85
- Max attempts: 3

**Stage 2 - Report Generation:**
- Agent: report-generator-001 (new)
- Validation required? yes
- Success threshold: 90
- Max attempts: 2

[After configuration...]

Claude: Here's your workflow design:

**Workflow:** customer-feedback-analysis
**Bounded Context:** CustomerAnalytics
**Pattern:** stg-val-wkf

**Stages:**
1. feedback-analysis (Agent: feedback-analyzer-001)
   - Validates: Structural, Completeness, Quality
   - Threshold: 85/100
2. report-generation (Agent: report-generator-001)
   - Validates: Structural, Completeness, Quality
   - Threshold: 90/100

**Validation Results:**
✓ No naming conflicts
✓ No circular dependencies
✓ Data mappings valid
⚠ Warning: Creating new bounded context 'CustomerAnalytics' - ensure architectural approval

Proceed with generation? [y/n]

User: y

Claude: ✓ Generated all workflow files
✓ Generated agent specifications
✓ Created directory structure

**Next steps:**
1. Review files in `workflow-orchestration/workflows/customer-feedback-analysis/`
2. Customize agent instructions
3. Test: `make test-workflow WORKFLOW=customer-feedback-analysis`
4. Register agents in Glean Agent Builder
```

## Implementation Notes

This skill is implemented as an interactive conversation flow that:
1. Reads existing workflows and agents from the filesystem
2. Uses the knowledge base to guide users
3. Validates designs before file generation
4. Uses templates to generate configuration files
5. Provides clear next steps for testing

## Validation Checks

Before generating files, the skill validates:
- **Naming conventions**: workflow-id matches `^[a-z0-9-]+$`
- **Bounded context alignment**: Agents match workflow context
- **Data flow**: Input/output mappings are valid
- **Circular dependencies**: No infinite loops in feedback logic
- **Schema compliance**: All required fields present
- **Uniqueness**: No conflicts with existing workflows

## Error Handling

If validation fails:
- Show specific errors with fix suggestions
- Allow user to correct before proceeding
- Prevent file generation until all errors resolved

## Next Steps After Generation

After creating a workflow with `/new-workflow`, follow these steps:

### 1. Generate Examples (Recommended)
**Run `/generate-examples` to populate example directories:**
```
/generate-examples
```

This skill will:
- Analyze your workflow configuration
- Generate 2-3 good examples per stage
- Generate 2-3 bad examples per stage
- Create end-to-end workflow examples
- Add clear explanations and documentation

See `.claude/skills/generate-examples.md` for details.

### 2. Validate Structure
**Run the validation script:**
```bash
./scripts/validate-workflow-structure.sh workflow-orchestration/workflows/{workflow-id}
```

Ensures all required files are present and properly formatted.

### 3. Review and Customize
- Review generated configuration files
- Customize agent instructions in `stages/*/instructions.md`
- Tune validation rules in `stages/*/validation-rules.json`
- Adjust workflow settings in `config/workflow-settings.json`
- Refine examples if needed

### 4. Test the Workflow
- Use generated examples as test cases
- Test validation feedback loops (if stg-val-wkf pattern)
- Verify metrics collection
- Test error handling and escalation

### 5. Register Agents
- Register agents in Glean Agent Builder
- Include examples from `stages/*/examples/good/`
- Configure Glean integration if needed
- Deploy agents to production

### 6. Deploy MCP Server (if applicable)
- Deploy workflow orchestration service
- Configure environment variables
- Set up monitoring and logging
- Test end-to-end execution

## Related Skills

- **`/generate-examples`**: Populate example directories with realistic good/bad examples
- **`/validate-workflow`**: Validate workflow configuration and structure
- **`/test-workflow`**: Run workflow with test inputs

## Related Documentation

- **Development Guide**: `workflow-orchestration/WORKFLOW-DEVELOPMENT-GUIDE.md`
- **Structure Standard**: `workflow-orchestration/WORKFLOW-STRUCTURE-STANDARD.md`
- **Bounded Contexts**: `.claude/knowledge/workflow-creation/bounded-contexts.md`
- **Agent Catalog**: `.claude/knowledge/workflow-creation/agent-catalog.md`
- **Workflow Patterns**: `.claude/knowledge/workflow-creation/workflow-patterns.md`
- **Validation Dimensions**: `.claude/knowledge/workflow-creation/validation-dimensions.md`

## Technical Details

**Templates Used:**
- Handlebars-style syntax with `{{variables}}`
- Support for conditionals: `{{#if condition}}...{{/if}}`
- Support for loops: `{{#each array}}...{{/each}}`

**File Generation:**
- Creates directory structure first
- Generates JSON files with proper indentation
- Generates YAML files with correct formatting
- Creates placeholder directories for examples

**Quality Assurance:**
- Validates all JSON is well-formed
- Validates all YAML is parseable
- Checks file paths are valid
- Verifies no file overwrites without confirmation
