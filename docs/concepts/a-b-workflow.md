Analysis
Components Identified:

Core Function: Staged, gated workflow execution with validation loops
Key Features: Document-driven stage configuration, good/bad example validation, iterative refinement, TDD-style agent calling
Complexity Level: Complex
Special Requirements: Loop logic, conditional gating, document reference system, multi-stage validation architecture
XML-Structured Prompt
<metadata>
  <name>stg-val-wkf</name>
  <version>1.0</version>
</metadata>

<primary_goal>
  Execute a multi-stage, gated workflow process with validation loops at each stage, using document-driven instructions and examples to ensure output quality and enable iterative process tuning.
  <audience>Automated agents, workflow orchestrators, quality assurance systems</audience>
  <tone>Systematic, methodical, validation-focused</tone>
</primary_goal>

<role>Staged workflow orchestrator with built-in validation gates and iterative refinement capabilities</role>

<task>Process input through multiple sequential stages, validating output against documented criteria at each gate, looping back for corrections when validation fails, and advancing only when output meets expectations</task>

<context>
  This workflow architecture implements test-driven development (TDD) principles through agent calling. Each stage maintains independence through document-based configuration, allowing individual stage tuning without system-wide changes. Validation gates prevent cascading errors by ensuring quality at each step before progression.
</context>

<instructions>
  <stage_execution>
    For each defined stage in the workflow:
    1. Load stage-specific instruction document(s)
    2. Review good and bad output examples from documentation
    3. Execute stage logic on current input
    4. Apply validation gate using documented success criteria
    5. If validation passes: proceed to next stage
    6. If validation fails: loop back to step 3 with failure feedback
    7. Limit loop iterations per stage (default: 3 attempts)
  </stage_execution>

  <document_integration>
    Each stage references:
    - **Instruction document**: Contains stage-specific processing rules and requirements
    - **Examples document**: Provides good examples (target patterns) and bad examples (anti-patterns)
    - **Validation criteria**: Defines pass/fail conditions for the stage gate
  </document_integration>

  <validation_gate_logic>
    At each gate, compare output against:
    - Structural requirements from instruction document
    - Pattern matching with good examples (similarity check)
    - Anti-pattern detection from bad examples (avoidance check)
    - Explicit validation rules defined for the stage
  </validation_gate_logic>

  <loop_management>
    When validation fails:
    - Capture specific failure reasons
    - Provide detailed feedback to stage executor
    - Increment attempt counter
    - If max attempts reached: escalate to human review or halt workflow
    - If attempts remain: retry with enriched context
  </loop_management>

  <process_tuning>
    The document-driven architecture enables:
    - Independent refinement of individual stages
    - A/B testing of instruction variations
    - Example library expansion without code changes
    - Validation criteria adjustment based on outcomes
  </process_tuning>
</instructions>

<constraints>
  <constraint>Never skip a validation gate, even if previous stages passed</constraint>
  <constraint>Maximum loop iterations per stage must be enforced to prevent infinite loops</constraint>
  <constraint>Each stage must have at least one referenced instruction document</constraint>
  <constraint>Stage order must be maintained; no parallel execution unless explicitly configured</constraint>
  <constraint>Validation failures must include actionable feedback for correction</constraint>
  <constraint>Document references must be validated at workflow initialization</constraint>
</constraints>

<validation_rules>
  <rule>All stage instruction documents are accessible before workflow begins</rule>
  <rule>Each validation gate produces a clear pass/fail decision with reasoning</rule>
  <rule>Loop iterations are tracked and logged for each stage</rule>
  <rule>Final output has passed all stage gates without escalation</rule>
  <rule>Workflow state is recoverable at any stage for debugging</rule>
</validation_rules>

<output_format>
  <workflow_result>
    <stage_results>
      For each stage, report:
      - Stage name and sequence number
      - Attempts required (1-N)
      - Validation status (PASS/FAIL/ESCALATED)
      - Key validation points checked
      - Output produced by stage
    </stage_results>

    <final_output>
      The complete validated output after all stages
    </final_output>

    <workflow_metrics>
      - Total stages executed
      - Total validation attempts across all stages
      - Any escalations or manual interventions
      - Processing time per stage
    </workflow_metrics>
  </workflow_result>
</output_format>

<steps>
  <step1>Initialize workflow: validate all document references and stage configurations</step1>
  <step2>Load first stage instruction document and examples</step2>
  <step3>Execute stage logic on input</step3>
  <step4>Apply validation gate using documented criteria</step4>
  <step5>If pass: advance to next stage; If fail: loop to step3 with feedback (max 3 attempts)</step5>
  <step6>Repeat steps 2-5 for each subsequent stage</step6>
  <step7>Return final validated output with complete workflow metrics</step7>
</steps>

<examples>
  <good_example>
    Stage: "Content Sanitization"
    Document: "sanitization-rules.md"
    Input: "User data with PII: John Doe, SSN 123-45-6789"
    Attempt 1: Output with partial masking
    Validation: FAIL - SSN pattern still detectable
    Attempt 2: Output with full masking
    Validation: PASS - meets all criteria from examples
    Result: Advance to next stage
  </good_example>

  <good_example>
    Stage: "Format Validation"
    Document: "json-schema-rules.md"
    Input: Malformed JSON string
    Attempt 1: Attempted parse fails
    Validation: FAIL - not valid JSON
    Attempt 2: Corrected structure
    Validation: PASS - validates against schema
    Attempt 3: Not needed
    Result: Advance to next stage
  </good_example>

  <bad_example>
    Stage: "Quality Check"
    Input: Low-quality output
    Attempt 1: FAIL
    Attempt 2: FAIL
    Attempt 3: FAIL
    Action: Skip validation gate and proceed anyway
    Issue: Violates constraint - gates must never be skipped; should escalate instead
  </bad_example>

  <bad_example>
    Stage: "Text Processing"
    Validation: FAIL (no specific reason provided)
    Loop: Retry with same input and no feedback
    Issue: Validation failure must include actionable feedback; blind retries waste iterations
  </bad_example>
</examples>

<domain_knowledge>Workflow orchestration, test-driven development (TDD), validation patterns, iterative refinement, gate-based quality control, document-driven configuration, agent-based systems, feedback loop design</domain_knowledge>
xml

Usage Notes
This XML structure transforms the conceptual workflow into an executable specification with clear stage progression, validation gates, and loop logic. The hierarchical organization separates stage execution logic from validation rules and document integration, enabling independent tuning of each component. The document-driven architecture allows process refinement through content updates rather than code changes, supporting the TDD-style iteration described in the original request.





Now design a folder structure that I can use to define the variable workflows, global, each step, good bad example for global and each step, the expectation is that the xml above will be able to progress through the workflow loading instructions and guidance from an external gdrive folder so that the system is dynamic and flexible

Show work
Analysis
Components Identified:

Core Function: Design hierarchical folder structure for workflow configuration storage
Key Features: Global configurations, workflow-specific settings, per-stage instructions, example libraries, GDrive integration compatibility
Complexity Level: Medium
Special Requirements: Dynamic document loading, scalability for multiple workflows, clear separation between global/local/stage-level configs, example isolation
XML-Structured Prompt
<metadata>
  <name>wkf-fld-str</name>
  <version>1.0</version>
</metadata>

<primary_goal>
  Design a hierarchical folder structure for Google Drive that organizes workflow configurations, enabling the staged validation workflow system to dynamically load instructions, validation criteria, and examples at global, workflow, and stage levels.
  <audience>Workflow architects, system administrators, DevOps engineers</audience>
  <tone>Structured, practical, implementation-focused</tone>
</primary_goal>

<role>Folder architecture designer specializing in document-driven workflow configuration systems</role>

<task>Create a comprehensive folder hierarchy that supports multiple workflows, global configurations, stage-specific instructions, and example libraries while maintaining flexibility for dynamic loading and independent component tuning</task>

<context>
  The folder structure will be hosted on Google Drive and accessed by the staged validation workflow system (stg-val-wkf). Each workflow may have different stages, and each stage requires its own instructions and examples. Global configurations apply across all workflows, while workflow-specific and stage-specific configurations override or extend global settings. The system must support multiple concurrent workflows and allow process tuning through document updates without code changes.
</context>

<instructions>
  <hierarchy_design>
    Design a folder structure with these levels:
    1. **Root level**: Contains global configurations and workflow directories
    2. **Global level**: Shared configurations, standards, and reusable components
    3. **Workflow level**: Individual workflow definitions and metadata
    4. **Stage level**: Stage-specific instructions and validation criteria
    5. **Examples level**: Good and bad example libraries organized by scope
  </hierarchy_design>

  <folder_organization>
    Structure folders to support:
    - Clear naming conventions (lowercase, hyphens, semantic)
    - Logical grouping by scope (global vs. workflow-specific)
    - Version control through folder or file naming
    - Easy navigation for both humans and automated systems
    - Separation of instructions from examples
    - Metadata files for workflow registration
  </folder_organization>

  <file_type_specification>
    Define standard file types for each folder:
    - **Instructions**: .md (Markdown) or .txt for human readability
    - **Examples**: .json, .xml, .md depending on example content type
    - **Validation criteria**: .json or .yaml for structured rules
    - **Metadata**: .json or .yaml for workflow/stage configuration
    - **README files**: .md for documentation at each level
  </file_type_specification>

  <path_resolution_logic>
    Design structure to support this loading sequence:
    1. Load global configurations first (baseline)
    2. Load workflow-specific configurations (override/extend global)
    3. Load stage-specific configurations (override/extend workflow)
    4. Merge example libraries (global + workflow + stage)
    5. Resolve conflicts with stage > workflow > global precedence
  </path_resolution_logic>

  <scalability_considerations>
    Ensure structure supports:
    - Adding new workflows without restructuring
    - Adding new stages to existing workflows
    - Sharing common stages across workflows
    - Archiving deprecated workflows
    - A/B testing through parallel workflow versions
  </scalability_considerations>
</instructions>

<constraints>
  <constraint>Folder depth should not exceed 5 levels for maintainability</constraint>
  <constraint>Each stage folder must contain at minimum: instructions file and examples subfolder</constraint>
  <constraint>Global, workflow, and stage levels must have consistent structure patterns</constraint>
  <constraint>Folder and file names must be filesystem-safe and URL-safe</constraint>
  <constraint>No duplicate naming between workflow IDs to prevent conflicts</constraint>
  <constraint>Examples must be clearly separated into "good" and "bad" categories</constraint>
</constraints>

<validation_rules>
  <rule>Every workflow folder contains a workflow-metadata.json or similar manifest</rule>
  <rule>Global folder contains at least: global-config, global-examples, shared-stages</rule>
  <rule>Stage folders follow consistent naming convention across all workflows</rule>
  <rule>Example files include metadata (description, use case, version)</rule>
  <rule>README.md exists at root and workflow levels explaining structure</rule>
  <rule>Path references are resolvable through relative or absolute addressing</rule>
</validation_rules>

<output_format>
  <folder_structure_diagram>
    Provide ASCII tree diagram showing complete hierarchy with:
    - All folder levels
    - Key file examples at each level
    - Annotations explaining purpose
    - Path notation for reference (e.g., /global/examples/good/)
  </folder_structure_diagram>

  <folder_descriptions>
    For each major folder, provide:
    - **Name**: Exact folder name
    - **Purpose**: What it contains and why
    - **Contents**: Types of files and subfolders
    - **Access Pattern**: How the workflow system loads from it
  </folder_descriptions>

  <file_templates>
    Provide example content structure for:
    - workflow-metadata.json
    - stage-config.json
    - example-metadata.json
    - global-config file
  </file_templates>

  <implementation_guide>
    Step-by-step instructions for:
    1. Setting up the initial folder structure
    2. Adding a new workflow
    3. Adding a new stage to existing workflow
    4. Updating examples without breaking existing workflows
  </implementation_guide>
</output_format>

<steps>
  <step1>Define root folder name and purpose (e.g., "workflow-orchestration")</step1>
  <step2>Design global configuration folder structure with subfolders for config, examples, shared stages</step2>
  <step3>Design workflow folder template structure (repeatable for each workflow)</step3>
  <step4>Design stage folder template structure (repeatable for each stage within workflows)</step4>
  <step5>Design example organization (good/bad separation at each scope level)</step5>
  <step6>Define file naming conventions and metadata file schemas</step6>
  <step7>Create README documentation strategy for self-documenting structure</step7>
  <step8>Validate against all constraints and rules</step8>
</steps>

<examples>
  <good_example>
    Workflow: "data-sanitization-workflow"
    Path: /workflows/data-sanitization-workflow/stages/01-pii-detection/
    Contains:
    - instructions.md (stage-specific processing rules)
    - validation-rules.json (pass/fail criteria)
    - examples/good/ (folder with 3+ good example files)
    - examples/bad/ (folder with 3+ bad example files)
    - stage-metadata.json (stage configuration)

    Result: Well-organized, self-contained stage configuration
  </good_example>

  <good_example>
    Global Examples Path: /global/examples/good/json-formatting/
    Contains:
    - example-001-simple-object.json
    - example-002-nested-array.json
    - example-003-complex-structure.json
    - _metadata.json (describes all examples in folder)

    Result: Reusable across any workflow requiring JSON validation
  </good_example>

  <bad_example>
    Path: /workflows/workflow1/stage1/good_examples_and_bad_examples/
    Contains: Mixed good and bad examples in same folder
    Issue: Violates separation constraint; makes automated loading ambiguous
  </bad_example>

  <bad_example>
    Path: /workflows/myWorkflow/stages/DataCleaning/
    Issue: Inconsistent naming (camelCase vs. kebab-case); not URL-safe for all systems
    Should be: /workflows/my-workflow/stages/data-cleaning/
  </bad_example>
</examples>

<domain_knowledge>Folder hierarchy design, document-driven architecture, configuration management, Google Drive organization patterns, workflow orchestration systems, template-based structures, metadata schemas, path resolution logic, separation of concerns</domain_knowledge>
xml

Usage Notes
This XML prompt transforms the folder structure design task into a systematic specification with clear hierarchy levels, naming conventions, and loading patterns. The structure separates global concerns from workflow-specific and stage-specific configurations, enabling the stg-val-wkf system to dynamically load and merge configurations. The document-driven approach allows independent tuning at any level without affecting other components.

Supplemental: Actual Folder Structure Design
Since you'll need to implement this immediately, here's the executable folder structure:

workflow-orchestration/
│
├── README.md                          # System overview and navigation guide
├── global/                            # Global configurations (apply to all workflows)
│   ├── config/
│   │   ├── global-settings.json      # System-wide defaults
│   │   ├── validation-standards.json  # Common validation patterns
│   │   └── error-handling.json        # Global error/retry policies
│   │
│   ├── examples/
│   │   ├── good/
│   │   │   ├── _README.md             # Good examples index
│   │   │   ├── json-formatting/
│   │   │   ├── text-sanitization/
│   │   │   └── data-validation/
│   │   └── bad/
│   │       ├── _README.md             # Bad examples index
│   │       ├── json-formatting/
│   │       ├── text-sanitization/
│   │       └── data-validation/
│   │
│   └── shared-stages/                 # Reusable stage definitions
│       ├── input-validation/
│       ├── output-formatting/
│       └── quality-check/
│
├── workflows/                         # Individual workflow definitions
│   │
│   ├── data-sanitization/             # Example Workflow 1
│   │   ├── workflow-metadata.json     # Workflow config & stage sequence
│   │   ├── README.md                  # Workflow documentation
│   │   │
│   │   ├── config/
│   │   │   └── workflow-settings.json # Workflow-level overrides
│   │   │
│   │   ├── examples/                  # Workflow-level examples
│   │   │   ├── good/
│   │   │   └── bad/
│   │   │
│   │   └── stages/
│   │       ├── 01-pii-detection/
│   │       │   ├── instructions.md
│   │       │   ├── validation-rules.json
│   │       │   ├── stage-config.json
│   │       │   └── examples/
│   │       │       ├── good/
│   │       │       │   ├── example-001.json
│   │       │       │   ├── example-002.json
│   │       │       │   └── _metadata.json
│   │       │       └── bad/
│   │       │           ├── example-001.json
│   │       │           ├── example-002.json
│   │       │           └── _metadata.json
│   │       │
│   │       ├── 02-data-masking/
│   │       │   ├── instructions.md
│   │       │   ├── validation-rules.json
│   │       │   ├── stage-config.json
│   │       │   └── examples/
│   │       │       ├── good/
│   │       │       └── bad/
│   │       │
│   │       └── 03-output-validation/
│   │           ├── instructions.md
│   │           ├── validation-rules.json
│   │           ├── stage-config.json
│   │           └── examples/
│   │               ├── good/
│   │               └── bad/
│   │
│   ├── content-moderation/            # Example Workflow 2
│   │   ├── workflow-metadata.json
│   │   ├── README.md
│   │   ├── config/
│   │   ├── examples/
│   │   └── stages/
│   │       ├── 01-toxicity-detection/
│   │       ├── 02-sentiment-analysis/
│   │       └── 03-flagging-logic/
│   │
│   └── report-generation/             # Example Workflow 3
│       ├── workflow-metadata.json
│       ├── README.md
│       ├── config/
│       ├── examples/
│       └── stages/
│           ├── 01-data-extraction/
│           ├── 02-analysis/
│           └── 03-formatting/
│
├── templates/                         # Templates for creating new workflows/stages
│   ├── workflow-template/
│   │   ├── workflow-metadata.json
│   │   ├── README.md
│   │   ├── config/
│   │   ├── examples/
│   │   └── stages/
│   │       └── stage-template/
│   │           ├── instructions.md
│   │           ├── validation-rules.json
│   │           ├── stage-config.json
│   │           └── examples/
│   │
│   └── documentation/
│       ├── how-to-add-workflow.md
│       ├── how-to-add-stage.md
│       └── metadata-schema-reference.md
│
└── archive/                           # Deprecated workflows (keep for reference)
    └── legacy-workflow-v1/

Key File Templates
workflow-metadata.json

{
  "workflow_id": "data-sanitization",
  "version": "1.0.0",
  "description": "Multi-stage data sanitization with PII detection",
  "stages": [
    {
      "stage_id": "01-pii-detection",
      "name": "PII Detection",
      "path": "stages/01-pii-detection",
      "max_attempts": 3,
      "required": true
    },
    {
      "stage_id": "02-data-masking",
      "name": "Data Masking",
      "path": "stages/02-data-masking",
      "max_attempts": 3,
      "required": true
    }
  ],
  "global_config_overrides": {
    "timeout_seconds": 300
  }
}
json

stage-config.json

{
  "stage_id": "01-pii-detection",
  "instruction_file": "instructions.md",
  "validation_file": "validation-rules.json",
  "examples_path": "examples",
  "max_loop_attempts": 3,
  "validation_mode": "strict",
  "dependencies": []
}
json

Path Resolution Example:

Stage execution loads in this order:
1. /global/config/global-settings.json
2. /global/config/validation-standards.json
3. /workflows/data-sanitization/workflow-metadata.json
4. /workflows/data-sanitization/config/workflow-settings.json
5. /workflows/data-sanitization/stages/01-pii-detection/stage-config.json
6. /workflows/data-sanitization/stages/01-pii-detection/instructions.md
7. Examples: merged from global/ + workflow/ + stage/ paths

This structure is ready for Google Drive implementation and supports the dynamic loading requirements of your stg-val-wkf system.





Now rebuild the original xml prompt so that on set I can 1) build and document the system in gdrive, and with this new xml promo I can point it to a folder, it will run all logice and process from the documentation in that folder

Show work
Analysis
Components Identified:

Core Function: Document-driven staged workflow executor with dynamic folder-based configuration loading
Key Features: GDrive folder path input, automatic workflow discovery, dynamic instruction loading, hierarchical config merging (global > workflow > stage), validation gates with loops, self-documenting system
Complexity Level: Complex
Special Requirements: File I/O operations, path resolution, JSON/YAML parsing, hierarchical config merging, workflow orchestration, validation loops, fallback handling
XML-Structured Prompt
<metadata>
  <name>doc-drv-wkf</name>
  <version>2.0</version>
  <description>Document-driven workflow orchestrator that loads all configuration, instructions, and examples from Google Drive folder structure</description>
</metadata>

<primary_goal>
  Execute staged validation workflows by dynamically loading all configurations, instructions, validation rules, and examples from a Google Drive folder structure, enabling fully externalized and tunable workflow systems without code changes.
  <audience>Workflow automation systems, AI agents, process orchestrators</audience>
  <tone>Systematic, adaptive, document-driven</tone>
</primary_goal>

<role>Dynamic workflow orchestrator with document discovery, hierarchical configuration loading, and staged validation execution capabilities</role>

<task>Accept a Google Drive folder path as input, discover and load workflow configurations, dynamically construct the workflow execution plan, and process input through all stages while validating against documentation-defined criteria</task>

<context>
  This system implements a fully externalized workflow architecture where all logic, rules, and examples reside in Google Drive folders. The orchestrator reads the folder structure designed in wkf-fld-str, discovers available workflows, loads hierarchical configurations (global → workflow → stage), and executes staged validation with loop-back capability. This approach enables non-technical users to tune processes by editing documents rather than code, supports A/B testing through folder variations, and maintains full auditability through version-controlled documentation.
</context>

<inputs>
  <required>
    <workflow_root_path>
      Google Drive folder path to workflow-orchestration root directory.
      Example: "https://drive.google.com/drive/folders/ABC123..." or "/My Drive/workflow-orchestration"
    </workflow_root_path>

    <workflow_id>
      Identifier of the specific workflow to execute (must match folder name in /workflows/).
      Example: "data-sanitization" or "content-moderation"
    </workflow_id>

    <input_data>
      The data to process through the workflow stages.
      Can be text, JSON, file reference, or structured data depending on workflow requirements.
    </input_data>
  </required>

  <optional>
    <execution_mode>
      Mode of operation: "execute" (run workflow), "validate_structure" (check folder structure only), "dry_run" (simulate without validation)
      Default: "execute"
    </execution_mode>

    <override_max_attempts>
      Override global max loop attempts per stage.
      Default: loaded from global config or 3
    </override_max_attempts>

    <debug_mode>
      Enable verbose logging of document loading and validation steps.
      Default: false
    </debug_mode>
  </optional>
</inputs>

<instructions>
  <phase1_initialization>
    <step>Validate workflow_root_path is accessible</step>
    <step>Check for required folder structure: /global/, /workflows/, /templates/</step>
    <step>Read /README.md from root for system documentation</step>
    <step>Load global configurations from /global/config/</step>
    <step>Establish baseline settings: validation standards, error handling, retry policies</step>
    <step>Log initialization status and loaded global configs</step>
  </phase1_initialization>

  <phase2_workflow_discovery>
    <step>Navigate to /workflows/{workflow_id}/ folder</step>
    <step>Verify workflow folder exists; if not, list available workflows and error</step>
    <step>Read workflow-metadata.json to get workflow configuration</step>
    <step>Extract: workflow version, description, stage sequence, dependencies, overrides</step>
    <step>Load workflow-level config from /workflows/{workflow_id}/config/</step>
    <step>Merge workflow config with global config (workflow takes precedence)</step>
    <step>Read workflow README.md for context and special instructions</step>
  </phase2_workflow_discovery>

  <phase3_stage_loading>
    For each stage defined in workflow-metadata.json (in sequence order):

    <step>Navigate to stage folder: /workflows/{workflow_id}/stages/{stage_id}/</step>
    <step>Read stage-config.json for stage-specific settings</step>
    <step>Load instructions.md - parse for processing rules and requirements</step>
    <step>Load validation-rules.json - parse validation criteria and pass/fail conditions</step>
    <step>Discover examples:
      - Load all files from examples/good/ subfolder
      - Load all files from examples/bad/ subfolder
      - Read _metadata.json in each examples subfolder if present
    </step>
    <step>Check for shared stage reference: if stage references /global/shared-stages/, load from there instead</step>
    <step>Merge stage config with workflow config (stage takes precedence)</step>
    <step>Build complete stage execution context: instructions + validation rules + examples + merged config</step>
  </phase3_stage_loading>

  <phase4_example_aggregation>
    For each stage, aggregate examples hierarchically:

    <step>Start with global examples: /global/examples/good/ and /global/examples/bad/</step>
    <step>Add workflow-level examples: /workflows/{workflow_id}/examples/good/ and bad/</step>
    <step>Add stage-specific examples: /workflows/{workflow_id}/stages/{stage_id}/examples/</step>
    <step>Create merged example library with precedence: stage > workflow > global</step>
    <step>Tag each example with its source level for debugging</step>
  </phase4_example_aggregation>

  <phase5_workflow_execution>
    Execute stages in sequence defined by workflow-metadata.json:

    <stage_execution_loop>
      <step>Set current_input to input_data (for first stage) or previous_stage_output</step>
      <step>Initialize attempt_counter = 0</step>
      <step>Load stage execution context (instructions, validation rules, examples)</step>

      <processing_loop max_iterations="from stage config or global default">
        <step>Increment attempt_counter</step>
        <step>Apply stage instructions to current_input</step>
        <step>Generate stage_output based on instructions.md guidance</step>
        <step>Run validation gate:
          - Check structural requirements from validation-rules.json
          - Compare against good examples (pattern matching)
          - Check for bad example anti-patterns (avoidance)
          - Apply explicit validation rules
          - Generate validation_result: PASS/FAIL with detailed reasoning
        </step>

        <conditional_logic>
          IF validation_result == PASS:
            - Log successful validation
            - Set previous_stage_output = stage_output
            - Break processing_loop
            - Advance to next stage

          ELSE IF validation_result == FAIL AND attempt_counter < max_attempts:
            - Log failure reason and attempt number
            - Generate feedback from validation failure details
            - Enrich current_input with feedback
            - Continue processing_loop (retry)

          ELSE IF validation_result == FAIL AND attempt_counter >= max_attempts:
            - Log escalation: max attempts reached
            - Halt workflow OR escalate to human review (based on config)
            - Return partial results with failure report
        </conditional_logic>
      </processing_loop>
    </stage_execution_loop>

    <step>After all stages complete successfully, compile final_output</step>
    <step>Generate workflow execution report with metrics</step>
  </phase5_workflow_execution>
</instructions>

<document_loading_specifications>
  <file_format_handlers>
    <markdown>
      Parse .md files as instruction text.
      Extract structured sections if using headers (##, ###).
      Preserve formatting for human-readable context.
    </markdown>

    <json>
      Parse .json files as structured data.
      Use for: metadata, config, validation rules, structured examples.
      Validate JSON schema before processing.
    </json>

    <yaml>
      Parse .yaml/.yml files as alternative to JSON.
      Use for: config files with comments, complex hierarchies.
    </yaml>

    <text>
      Parse .txt files as plain text instructions.
      Use for simple rules or free-form guidance.
    </text>
  </file_format_handlers>

  <path_resolution>
    Support both absolute and relative paths:
    - Absolute: Full GDrive URL or path from root
    - Relative: From workflow_root_path

    Path construction pattern:
    {workflow_root_path}/workflows/{workflow_id}/stages/{stage_id}/{file}

    Fallback logic:
    If file not found at stage level → check workflow level → check global level
  </path_resolution>

  <caching_strategy>
    Cache loaded documents during single workflow execution to avoid redundant reads.
    Clear cache between workflow executions to ensure fresh data.
    Log cache hits/misses in debug mode.
  </caching_strategy>
</document_loading_specifications>

<validation_gate_implementation>
  <structural_validation>
    Check output structure against requirements in validation-rules.json:
    - Required fields present
    - Data types correct
    - Format specifications met (e.g., JSON valid, specific schema)
    - Length/size constraints satisfied
  </structural_validation>

  <pattern_matching>
    Compare output against good examples:
    - Structural similarity score
    - Key element presence
    - Format consistency
    - Semantic alignment (if using embeddings/NLP)

    Threshold: configurable in validation-rules.json (e.g., 80% similarity)
  </pattern_matching>

  <anti_pattern_detection>
    Compare output against bad examples:
    - Flag if output matches known failure patterns
    - Identify specific anti-pattern triggered
    - Include anti-pattern description from bad example metadata

    Any match to bad example = automatic FAIL
  </anti_pattern_detection>

  <explicit_rules>
    Apply custom validation logic from validation-rules.json:
    - Regular expression matching
    - Numeric thresholds
    - Business logic checks
    - Custom validation functions (if supported)
  </explicit_rules>

  <validation_result_format>
    {
      "status": "PASS" | "FAIL",
      "timestamp": "ISO 8601",
      "attempt_number": integer,
      "checks_performed": [
        {
          "check_type": "structural" | "pattern" | "anti_pattern" | "explicit",
          "check_name": "string",
          "result": "pass" | "fail",
          "details": "string",
          "score": float (optional)
        }
      ],
      "overall_score": float (optional),
      "failure_reasons": ["string"] (if FAIL),
      "recommendations": ["string"] (if FAIL)
    }
  </validation_result_format>
</validation_gate_implementation>

<constraints>
  <constraint>All file paths must be validated before read operations</constraint>
  <constraint>Missing required files (workflow-metadata.json, stage instructions.md) must cause graceful failure with clear error messages</constraint>
  <constraint>Maximum folder depth for traversal: 6 levels from workflow_root_path</constraint>
  <constraint>Document parsing errors must not crash the workflow; log and skip with warning</constraint>
  <constraint>Configuration merging follows strict precedence: stage > workflow > global</constraint>
  <constraint>Validation gates cannot be skipped; max attempts must be enforced</constraint>
  <constraint>All document loads must be logged in debug mode with timestamps and file sizes</constraint>
  <constraint>Workflow execution must be stateless between runs (no persistent state except logs)</constraint>
</constraints>

<error_handling>
  <folder_not_found>
    Log error with missing path.
    List available folders at parent level.
    Return error response with suggestions.
  </folder_not_found>

  <file_not_found>
    Check fallback locations (workflow → global).
    If still not found and file is required: halt with error.
    If optional: log warning and continue with defaults.
  </file_not_found>

  <parse_error>
    Log file path and parse error details.
    Attempt alternative parser if applicable (e.g., JSON vs YAML).
    If critical file: halt workflow.
    If example file: skip and log warning.
  </parse_error>

  <validation_failure>
    Log detailed failure reasons.
    Increment attempt counter.
    Generate actionable feedback.
    Retry if attempts remain, escalate if max reached.
  </validation_failure>

  <access_denied>
    Log permission error with file path.
    Check if workflow_root_path is accessible.
    Return clear error about permissions.
  </access_denied>
</error_handling>

<output_format>
  <execution_report>
    {
      "workflow_id": "string",
      "execution_timestamp": "ISO 8601",
      "execution_mode": "execute | validate_structure | dry_run",
      "status": "completed | failed | escalated",

      "configuration_loaded": {
        "global_config_files": ["file paths"],
        "workflow_config_files": ["file paths"],
        "total_stages": integer,
        "total_examples_loaded": integer
      },

      "stage_results": [
        {
          "stage_id": "string",
          "stage_name": "string",
          "sequence_number": integer,
          "attempts_required": integer,
          "validation_status": "PASS | FAIL | ESCALATED",
          "execution_time_ms": integer,
          "input_preview": "string (truncated)",
          "output_preview": "string (truncated)",
          "validation_details": {validation_result_format},
          "documents_loaded": {
            "instructions": "file path",
            "validation_rules": "file path",
            "examples_good": ["file paths"],
            "examples_bad": ["file paths"]
          }
        }
      ],

      "final_output": {
        "data": "processed output from final stage",
        "format": "detected format type",
        "size_bytes": integer
      },

      "workflow_metrics": {
        "total_execution_time_ms": integer,
        "total_validation_attempts": integer,
        "stages_passed": integer,
        "stages_failed": integer,
        "documents_loaded": integer,
        "cache_hit_rate": float
      },

      "errors_warnings": [
        {
          "type": "error | warning",
          "phase": "initialization | discovery | loading | execution",
          "message": "string",
          "file_path": "string (if applicable)"
        }
      ]
    }
  </execution_report>

  <validation_structure_report>
    Only generated when execution_mode = "validate_structure".

    {
      "structure_valid": boolean,
      "workflow_root_path": "string",
      "required_folders_present": {
        "/global/": boolean,
        "/workflows/": boolean,
        "/templates/": boolean
      },
      "workflows_discovered": ["workflow IDs"],
      "selected_workflow_structure": {
        "workflow_id": "string",
        "metadata_valid": boolean,
        "stages_found": integer,
        "stages_details": [
          {
            "stage_id": "string",
            "required_files_present": {
              "instructions.md": boolean,
              "validation-rules.json": boolean,
              "stage-config.json": boolean,
              "examples/good/": boolean,
              "examples/bad/": boolean
            }
          }
        ]
      },
      "issues_found": ["string descriptions"],
      "recommendations": ["string suggestions"]
    }
  </validation_structure_report>
</output_format>

<steps>
  <step1>Accept inputs: workflow_root_path, workflow_id, input_data, optional parameters</step1>
  <step2>Initialize: validate folder access, load global configs, establish baseline settings</step2>
  <step3>Discover workflow: navigate to workflow folder, load metadata and workflow-level config</step3>
  <step4>Load all stages: read stage configs, instructions, validation rules, and examples</step4>
  <step5>Aggregate examples hierarchically: merge global + workflow + stage examples</step5>
  <step6>Execute workflow: process input through stages sequentially with validation gates</step6>
  <step7>For each stage: apply instructions, validate output, loop if needed, advance when passed</step7>
  <step8>Compile final output and execution report with complete metrics</step8>
  <step9>Return execution report with final_output, stage_results, and workflow_metrics</step9>
</steps>

<examples>
  <good_example>
    Input:
    - workflow_root_path: "/My Drive/workflow-orchestration"
    - workflow_id: "data-sanitization"
    - input_data: "User John Doe, SSN 123-45-6789, purchased item #5432"
    - execution_mode: "execute"

    Process:
    1. Load global configs from /global/config/
    2. Load workflow metadata from /workflows/data-sanitization/workflow-metadata.json
    3. Discover 3 stages: pii-detection, data-masking, output-validation
    4. Load stage 1 docs, execute, validate → PASS (attempt 1)
    5. Load stage 2 docs, execute, validate → FAIL (attempt 1), retry → PASS (attempt 2)
    6. Load stage 3 docs, execute, validate → PASS (attempt 1)

    Output:
    {
      "status": "completed",
      "final_output": {"data": "User [REDACTED], SSN [REDACTED], purchased item #5432"},
      "workflow_metrics": {
        "total_validation_attempts": 4,
        "stages_passed": 3,
        "total_execution_time_ms": 2340
      }
    }
  </good_example>

  <good_example>
    Input:
    - workflow_root_path: "https://drive.google.com/drive/folders/ABC123"
    - workflow_id: "content-moderation"
    - input_data: "This is a test comment for moderation"
    - execution_mode: "validate_structure"

    Process:
    1. Navigate folder structure
    2. Verify all required folders exist
    3. Check workflow metadata is valid JSON
    4. Verify all stage folders have required files
    5. Count examples in each category

    Output:
    {
      "structure_valid": true,
      "workflows_discovered": ["data-sanitization", "content-moderation", "report-generation"],
      "selected_workflow_structure": {
        "workflow_id": "content-moderation",
        "metadata_valid": true,
        "stages_found": 3,
        "stages_details": [...]
      },
      "issues_found": [],
      "recommendations": ["Add more bad examples to stage 02-sentiment-analysis"]
    }
  </good_example>

  <bad_example>
    Scenario: Workflow folder missing instructions.md for a stage

    Incorrect behavior:
    - Continue execution with empty instructions
    - Use previous stage's instructions

    Correct behavior:
    - Check fallback: /global/shared-stages/{stage_id}/instructions.md
    - If still not found: halt workflow with clear error
    - Log: "Required file not found: /workflows/{workflow_id}/stages/{stage_id}/instructions.md"
    - Suggest: "Check folder structure or add missing file"
  </bad_example>

  <bad_example>
    Scenario: Validation fails 3 times at stage 2

    Incorrect behavior:
    - Skip validation gate and continue to stage 3
    - Return partial output without indicating failure

    Correct behavior:
    - Log: "Stage 02-data-masking exceeded max attempts (3)"
    - Set status: "escalated"
    - Return execution report with:
      - stage_results showing ESCALATED status
      - partial final_output up to last successful stage
      - Clear error in errors_warnings array
    - Do NOT proceed to stage 3
  </bad_example>
</examples>

<domain_knowledge>
  Document-driven architecture, dynamic workflow orchestration, hierarchical configuration management, Google Drive API integration, file system traversal, JSON/YAML parsing, validation gate patterns, iterative refinement loops, test-driven development (TDD), configuration precedence resolution, example-based validation, path resolution, error handling strategies, workflow state management, execution reporting
</domain_knowledge>

<special_instructions>
  <gdrive_integration>
    When accessing Google Drive:
    - Use provided GDrive folder URLs or paths
    - Handle both shared drives and personal My Drive locations
    - Respect file permissions and handle access errors gracefully
    - Support folder IDs and full URLs as input formats
    - Cache folder structure during single execution to minimize API calls
  </gdrive_integration>

  <extensibility>
    This system is designed to be extended:
    - New workflows added by creating new folders in /workflows/
    - New stages added to existing workflows without code changes
    - Validation logic tuned by editing validation-rules.json
    - Examples expanded by adding files to examples folders
    - Global standards updated by modifying /global/config/ files
    - No system restart or redeployment required for any changes
  </extensibility>

  <debugging_support>
    When debug_mode = true:
    - Log every file read operation with timestamp and file size
    - Show configuration merging steps with before/after values
    - Display validation check details for each attempt
    - Include document content previews in execution report
    - Track and report cache performance metrics
  </debugging_support>
</special_instructions>
xml

Usage Notes
This rebuilt XML prompt (doc-drv-wkf) transforms the original staged validation workflow into a fully document-driven system. Key improvements include:

Dynamic Discovery: Automatically discovers and loads all configurations from the Google Drive folder structure designed in wkf-fld-str
Hierarchical Configuration: Implements proper precedence (stage > workflow > global) for config merging
Complete Externalization: All logic, rules, and examples live in documents, not code
Folder-Based Input: Accepts a folder path and workflow ID, then self-configures from the discovered structure
Validation Structure Mode: Can validate folder structure before execution to catch configuration errors
Comprehensive Reporting: Detailed execution reports showing what was loaded from where and how validation progressed
The system enables non-technical workflow tuning through document editing in Google Drive, supports A/B testing through parallel workflow folders, and maintains full auditability through version-controlled documentation. Point it at any compliant folder structure and it will execute the defined workflow with zero code changes.