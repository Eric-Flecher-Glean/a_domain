# Agent Catalog

This document lists all available agents in the system with their capabilities, bounded contexts, and use cases.

## PromptEngineering Agents

### prompt-generator-001
**Name:** XML Prompt Generator
**Bounded Context:** PromptEngineering
**Status:** Active
**Version:** 1.0.0

**Capabilities:**
- Parse semantic requests into structured components
- Generate XML with proper tag hierarchy
- Apply cognitive containerization for examples
- Refine prompts based on validation feedback
- Generate unique prompt names (xxx-xxx-xxx format)
- Handle multi-attempt refinement loops
- Analyze tasks to identify required inputs
- Identify context sources from Glean
- Generate input specifications and context requirements

**Input Contract:**
- `user_request` (string, required) - Natural language prompt request
- `analyze_context` (boolean, optional) - Enable context analysis
- `feedback` (array, optional) - Validation feedback from previous attempt
- `previous_attempt` (object, optional) - Previous generation for refinement
- `attempt_number` (integer, optional) - Current attempt in validation loop

**Output Contract:**
- `xml_prompt` (string, required) - Complete XML-structured prompt
- `prompt_name` (string, required) - Unique identifier (xxx-xxx-xxx)
- `components_extracted` (object, optional) - Parsed components
- `input_analysis` (object, optional) - Required inputs and context sources
- `generation_metadata` (object, optional) - Attempt tracking

**Model Configuration:**
- Model: claude-sonnet-4
- Temperature: 0.3
- Max Tokens: 4000
- Top P: 0.9

**Performance:**
- Expected Latency: 3000ms
- Max Latency: 120000ms

**Use Cases:**
- Generate XML prompts from natural language
- Refine prompts based on validation feedback
- Analyze tasks to identify required inputs
- Map context sources from Glean

---

### prompt-validator-001
**Name:** Prompt Quality Validator
**Bounded Context:** PromptEngineering
**Status:** Active
**Version:** 1.0.0

**Capabilities:**
- Parse and validate XML structure
- Check tag hierarchy and nesting depth
- Verify completeness of required sections
- Calculate quality scores (0-100)
- Generate actionable feedback
- Compare against good/bad example patterns
- Track validation across multiple attempts
- Validate input specifications and context requirements
- Verify Glean integration specifications

**Input Contract:**
- `xml_prompt` (string, required) - XML prompt to validate
- `previous_validation_results` (array, optional) - Previous attempts
- `attempt_number` (integer, optional) - Current validation attempt

**Output Contract:**
- `isValid` (boolean, required) - Overall result (score ≥ threshold, no errors)
- `qualityScore` (number, required) - Calculated score (0-100)
- `checks` (array, required) - Individual validation check results
- `feedback` (array, required) - Actionable feedback for refinement
- `recommendations` (array, optional) - Improvement suggestions
- `scoreBreakdown` (object, optional) - Structural/completeness/quality scores
- `examplesAnalysis` (object, optional) - Examples quality metrics
- `contextValidation` (object, optional) - Input/context validation results

**Model Configuration:**
- Model: claude-sonnet-4
- Temperature: 0
- Max Tokens: 2000
- Top P: 1.0

**Performance:**
- Expected Latency: 2000ms
- Max Latency: 60000ms

**Validation Dimensions:**
- Structural (35%): XML well-formed, required sections, tag hierarchy
- Completeness (30%): Section content, examples quality, instructions
- Quality (25%): Clarity, examples effectiveness, coherence
- Context Quality (10%): Input specs, Glean integration validity

**Success Threshold:** 90/100

**Use Cases:**
- Validate XML prompt structure
- Calculate quality scores
- Generate improvement feedback
- Track validation across refinement loops
- Verify Glean integration specifications

---

## Agent Reuse Guidelines

### When to Reuse Existing Agents

1. **Same Bounded Context + Similar Capability**
   - If an agent in the same bounded context has 70%+ capability overlap, reuse it
   - Example: Using `prompt-generator-001` for any XML generation task

2. **Existing Agent Can Be Extended**
   - If capability can be added via configuration or instructions
   - Avoid creating near-duplicate agents

3. **Agent Output Matches Required Input**
   - Check input/output contracts for compatibility
   - Use data mapping to transform as needed

### When to Create New Agents

1. **Different Bounded Context**
   - New domain requires different business rules
   - Example: Creating a customer feedback analyzer (different from prompt generation)

2. **Fundamentally Different Capability**
   - Agent performs a distinct function with <50% overlap
   - Example: Code analysis vs. text summarization

3. **Different Quality Requirements**
   - Success criteria or validation needs are incompatible
   - Example: Real-time vs. batch processing agents

4. **Different Model Requirements**
   - Needs different model, temperature, or token limits
   - Example: Creative generation (high temp) vs. validation (zero temp)

### Agent Naming Convention

Format: `{capability}-{version}`

Examples:
- `prompt-generator-001`
- `prompt-validator-001`
- `feedback-analyzer-001`
- `report-generator-001`

Rules:
- Lowercase with hyphens
- Descriptive capability name
- Version as 3-digit suffix (001, 002, etc.)
- Keep names concise (2-3 words max for capability)

### Agent Version Management

- **001**: Initial version
- **002**: Minor updates (new capabilities, config changes)
- **003+**: Ongoing iterations

When to increment version:
- Breaking changes to input/output contracts
- Significant capability additions
- Major model or configuration changes

When NOT to increment:
- Instruction refinements
- Example updates
- Bug fixes that don't change contracts
