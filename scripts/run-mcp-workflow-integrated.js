#!/usr/bin/env node

/**
 * Integrated A/B Agent Workflow with Context Analysis
 * Properly uses the two-agent system with context management
 *
 * Enhanced with OpenTelemetry observability
 */

const fs = require('fs');
const path = require('path');

// OpenTelemetry imports
const { initializeOTel, shutdown: shutdownOTel, getLogger } = require('../observability/otel-setup');
const { WorkflowInstrumentation } = require('../observability/instrumentation');

// Initialize OpenTelemetry
initializeOTel();

const args = process.argv.slice(2);
const config = {
  mode: getArg('--mode'),
  task: getArg('--task'),
  file: getArg('--file'),
  output: getArg('--output') || 'output/prompt.xml',
  maxAttempts: parseInt(getArg('--max-attempts') || '3'),
  analyzeContext: getArg('--analyze-context') !== 'false'
};

function getArg(name) {
  const index = args.indexOf(name);
  return index !== -1 ? args[index + 1] : null;
}

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m'
};

// Enhanced logging with structured logs
const structuredLogger = getLogger();

function log(message, color = 'reset', context = {}) {
  // Console output (for user visibility)
  console.log(`${colors[color]}${message}${colors.reset}`);

  // Structured log (for observability)
  const level = color === 'red' ? 'error' :
                color === 'yellow' ? 'warn' :
                color === 'green' || color === 'cyan' ? 'info' : 'debug';

  structuredLogger.log(level, message, context);
}

/**
 * AGENT A: prompt-generator-001
 * Generates XML prompts with context analysis
 */
async function callAgentA(input) {
  log(`\n🤖 Agent A (prompt-generator-001)`, 'blue');
  log(`   Mode: ${input.analyze_context ? 'Context Analysis Enabled' : 'Basic Generation'}`, 'cyan');
  log(`   Attempt: ${input.attempt_number}/${config.maxAttempts}`, 'cyan');

  if (input.feedback && input.feedback.length > 0) {
    log(`   Applying ${input.feedback.length} feedback items from Agent B`, 'yellow');
  }

  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 500));

  // This simulates the agent call
  // In production, this would be: POST to Glean MCP server /tools/generate_xml_prompt
  const result = await simulateAgentA(input);

  log(`   ✓ Generated prompt: ${result.prompt_name}`, 'green');
  if (result.input_analysis) {
    log(`   ✓ Input analysis:`, 'magenta');
    log(`     - Required inputs: ${result.input_analysis.required_inputs.length}`, 'cyan');
    log(`     - Optional inputs: ${result.input_analysis.optional_inputs.length}`, 'cyan');
    log(`     - Context sources: ${result.input_analysis.context_sources.length}`, 'cyan');
    if (result.input_analysis.glean_integrations.length > 0) {
      log(`     - Glean tools: ${[...new Set(result.input_analysis.glean_integrations)].join(', ')}`, 'magenta');
    }
  }

  return result;
}

/**
 * AGENT B: prompt-validator-001
 * Validates XML prompts including context requirements
 */
async function callAgentB(input) {
  log(`\n🤖 Agent B (prompt-validator-001)`, 'blue');
  log(`   Validating quality with context checks...`, 'cyan');

  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 300));

  // This simulates the agent call
  // In production, this would be: POST to Glean MCP server /tools/validate_prompt_quality
  const result = await simulateAgentB(input);

  log(`   ✓ Validation complete`, 'green');

  return result;
}

/**
 * Simulate Agent A call (replace with actual Glean API in production)
 */
async function simulateAgentA(input) {
  const { user_request, analyze_context, feedback, previous_attempt, attempt_number } = input;

  // Context analysis (if enabled)
  let inputAnalysis = null;
  if (analyze_context) {
    inputAnalysis = analyzeTaskForInputs(user_request);
  }

  // Generate XML with or without context specs
  const xml = generateXmlWithContext(user_request, inputAnalysis, attempt_number, feedback);
  const promptName = generatePromptName();

  return {
    xml_prompt: xml,
    prompt_name: promptName,
    input_analysis: inputAnalysis,
    components_extracted: {
      primary_goal: user_request,
      role: 'AI Assistant',
      task: user_request
    },
    generation_metadata: {
      attempt: attempt_number,
      refinements_applied: feedback || [],
      timestamp: new Date().toISOString(),
      feedback_addressed: feedback || [],
      context_analysis_performed: analyze_context
    }
  };
}

/**
 * Simulate Agent B call (replace with actual Glean API in production)
 */
async function simulateAgentB(input) {
  const { xml_prompt, attempt_number } = input;

  // Parse XML to check for context sections
  const hasInputSpec = xml_prompt.includes('<input_specification>');
  const hasContextReq = xml_prompt.includes('<context_requirements>');
  const hasGoodExamples = (xml_prompt.match(/<good>/g) || []).length >= 2;
  const hasBadExamples = (xml_prompt.match(/<bad>/g) || []).length >= 1;
  const requiredInputsCount = (xml_prompt.match(/<required>true<\/required>/g) || []).length;
  const contextSourcesCount = (xml_prompt.match(/<context>/g) || []).length;

  // Extract Glean integrations
  const gleanIntegrations = [];
  if (xml_prompt.includes('glean_search')) gleanIntegrations.push('mcp__glean__search');
  if (xml_prompt.includes('glean_meeting_lookup')) gleanIntegrations.push('mcp__glean__meeting_lookup');
  if (xml_prompt.includes('glean_code_search')) gleanIntegrations.push('mcp__glean__code_search');
  if (xml_prompt.includes('glean_document')) gleanIntegrations.push('mcp__glean__read_document');

  // Calculate scores by category (updated weights)
  let structuralScore = 35; // out of 35
  let completenessScore = 30; // out of 30
  let qualityScore = 25; // out of 25
  let contextScore = 10; // out of 10

  const checks = [];
  const feedback = [];

  // Structural checks (35%)
  checks.push({
    rule_id: 'xml_well_formed',
    status: 'pass',
    message: 'XML is well-formed',
    severity: 'info',
    section: 'structure',
    score_impact: 0
  });

  // Completeness checks (30%)
  if (!hasInputSpec) {
    checks.push({
      rule_id: 'input_specification_present',
      status: 'fail',
      message: 'Missing <input_specification> section',
      severity: 'warning',
      section: 'completeness',
      score_impact: -5
    });
    completenessScore -= 5;
    feedback.push('Add <input_specification> section to define required inputs');
  }

  if (!hasGoodExamples || !hasBadExamples) {
    checks.push({
      rule_id: 'examples_quality',
      status: 'fail',
      message: 'Need at least 2 good and 1 bad example',
      severity: 'error',
      section: 'completeness',
      score_impact: -10
    });
    completenessScore -= 10;
    if (!hasGoodExamples) feedback.push('Add at least 2 good examples');
    if (!hasBadExamples) feedback.push('Add 1 bad example with explanation');
  } else {
    checks.push({
      rule_id: 'examples_quality',
      status: 'pass',
      message: 'Examples meet quality standards',
      severity: 'info',
      section: 'completeness',
      score_impact: 0
    });
  }

  // Context quality checks (10%)
  if (hasInputSpec) {
    if (requiredInputsCount === 0) {
      checks.push({
        rule_id: 'required_inputs_defined',
        status: 'fail',
        message: 'No required inputs specified',
        severity: 'warning',
        section: 'context_quality',
        score_impact: -3
      });
      contextScore -= 3;
      feedback.push('Define at least one required input in <input_specification>');
    } else {
      checks.push({
        rule_id: 'required_inputs_defined',
        status: 'pass',
        message: `${requiredInputsCount} required inputs defined`,
        severity: 'info',
        section: 'context_quality',
        score_impact: 0
      });
    }
  }

  // Calculate total score
  const totalScore = structuralScore + completenessScore + qualityScore + contextScore;
  const isValid = totalScore >= 90;

  // Context validation details
  const contextValidation = {
    input_specification_present: hasInputSpec,
    context_requirements_present: hasContextReq,
    required_inputs_count: requiredInputsCount,
    context_sources_count: contextSourcesCount,
    glean_integrations: gleanIntegrations,
    validation_issues: feedback.filter(f => f.includes('input') || f.includes('context'))
  };

  return {
    isValid,
    qualityScore: totalScore,
    checks,
    feedback,
    recommendations: isValid ? ['Consider adding more domain-specific examples'] : [],
    scoreBreakdown: {
      structural: structuralScore,
      completeness: completenessScore,
      quality: qualityScore,
      context_quality: contextScore,
      bonuses: 0,
      penalties: 0
    },
    examplesAnalysis: {
      good_examples_found: (xml_prompt.match(/<good>/g) || []).length,
      bad_examples_found: (xml_prompt.match(/<bad>/g) || []).length,
      examples_quality_score: (hasGoodExamples && hasBadExamples) ? 85 : 50
    },
    contextValidation
  };
}

/**
 * Analyze task to identify inputs and context (from enhanced workflow)
 */
function analyzeTaskForInputs(userRequest) {
  const analysis = {
    required_inputs: [],
    optional_inputs: [],
    context_sources: [],
    glean_integrations: []
  };

  const taskLower = userRequest.toLowerCase();

  // Meeting tasks
  if (taskLower.includes('meeting') || taskLower.includes('summarize meeting')) {
    analysis.required_inputs.push(
      { name: 'meeting_transcript', type: 'string', source: 'user_provided',
        description: 'Full text transcript of the meeting' },
      { name: 'attendee_list', type: 'array', source: 'user_provided',
        description: 'List of meeting attendees' }
    );
    analysis.optional_inputs.push(
      { name: 'meeting_date', type: 'string', source: 'user_provided', default: 'today' }
    );
    analysis.context_sources.push(
      { name: 'previous_meetings', source: 'glean_meeting_lookup',
        query: 'participants:{{attendee_list}} after:{{meeting_date}}-30d' }
    );
    analysis.glean_integrations.push('mcp__glean__meeting_lookup');
  }

  // Code tasks
  if (taskLower.includes('code') || taskLower.includes('review')) {
    analysis.required_inputs.push(
      { name: 'code_content', type: 'string', source: 'user_provided',
        description: 'Source code to review' },
      { name: 'language', type: 'string', source: 'user_provided',
        description: 'Programming language' }
    );
    analysis.context_sources.push(
      { name: 'coding_standards', source: 'glean_search',
        query: 'coding standards OR style guide language:{{language}}' },
      { name: 'similar_code', source: 'glean_code_search',
        query: '{{code_pattern}}' }
    );
    analysis.glean_integrations.push('mcp__glean__search', 'mcp__glean__code_search');
  }

  // Customer feedback tasks
  if (taskLower.includes('customer') || taskLower.includes('feedback') || taskLower.includes('sentiment')) {
    analysis.required_inputs.push(
      { name: 'feedback_text', type: 'string', source: 'user_provided',
        description: 'Customer feedback content' }
    );
    analysis.optional_inputs.push(
      { name: 'product_name', type: 'string', source: 'user_provided' }
    );
    analysis.context_sources.push(
      { name: 'product_info', source: 'glean_search',
        query: 'product:{{product_name}} known issues OR features' },
      { name: 'sentiment_guidelines', source: 'glean_document',
        document_url: 'docs/analytics/sentiment-guidelines' }
    );
    analysis.glean_integrations.push('mcp__glean__search', 'mcp__glean__read_document');
  }

  // Email tasks
  if (taskLower.includes('email') || taskLower.includes('draft')) {
    analysis.required_inputs.push(
      { name: 'purpose', type: 'string', source: 'user_provided',
        description: 'Purpose of the email' },
      { name: 'recipient', type: 'string', source: 'user_provided',
        description: 'Email recipient' }
    );
    analysis.optional_inputs.push(
      { name: 'tone', type: 'string', source: 'user_provided', default: 'professional' }
    );
    analysis.context_sources.push(
      { name: 'email_templates', source: 'glean_search',
        query: 'email template {{purpose}}' }
    );
    analysis.glean_integrations.push('mcp__glean__search');
  }

  // Fallback
  if (analysis.required_inputs.length === 0) {
    analysis.required_inputs.push(
      { name: 'user_input', type: 'string', source: 'user_provided',
        description: 'Primary input for the task' }
    );
  }

  return analysis;
}

/**
 * Generate XML with context specifications
 */
function generateXmlWithContext(task, inputAnalysis, attemptNumber, feedback) {
  const promptName = generatePromptName();

  let xml = `<metadata>
  <name>${promptName}</name>
  <version>1.0.0</version>
  <description>${task}</description>
</metadata>

<primary_goal>
${task}
</primary_goal>

<role>
You are an expert AI assistant specialized in ${task.toLowerCase()}.
</role>

<task>
Process user requests related to ${task.toLowerCase()} and provide structured, helpful responses.
</task>
`;

  // Add input specification (if context analysis enabled)
  if (inputAnalysis) {
    xml += '\n<input_specification>\n';

    inputAnalysis.required_inputs.forEach(input => {
      xml += `  <input>\n`;
      xml += `    <name>${input.name}</name>\n`;
      xml += `    <type>${input.type}</type>\n`;
      xml += `    <required>true</required>\n`;
      xml += `    <description>${input.description}</description>\n`;
      xml += `    <source>${input.source}</source>\n`;
      xml += `  </input>\n\n`;
    });

    inputAnalysis.optional_inputs.forEach(input => {
      xml += `  <input>\n`;
      xml += `    <name>${input.name}</name>\n`;
      xml += `    <type>${input.type}</type>\n`;
      xml += `    <required>false</required>\n`;
      if (input.description) xml += `    <description>${input.description}</description>\n`;
      xml += `    <source>${input.source}</source>\n`;
      if (input.default) xml += `    <default>${input.default}</default>\n`;
      xml += `  </input>\n\n`;
    });

    xml += '</input_specification>\n';

    // Add context requirements
    if (inputAnalysis.context_sources.length > 0) {
      xml += '\n<context_requirements>\n';
      inputAnalysis.context_sources.forEach(ctx => {
        xml += `  <context>\n`;
        xml += `    <name>${ctx.name}</name>\n`;
        xml += `    <source>${ctx.source}</source>\n`;
        if (ctx.query) xml += `    <query>${ctx.query}</query>\n`;
        if (ctx.document_url) xml += `    <document_url>${ctx.document_url}</document_url>\n`;
        xml += `    <required>false</required>\n`;
        xml += `  </context>\n\n`;
      });
      xml += '</context_requirements>\n';
    }
  }

  xml += `
<instructions>
1. Validate all required inputs are provided
2. Retrieve necessary context from specified sources
3. Apply domain expertise and best practices
4. Generate clear, actionable output
5. Validate output quality
</instructions>

<output_format>
Provide responses in a clear, structured format with:
- Summary of key findings
- Detailed analysis
- Actionable recommendations
</output_format>

<examples>
  <good>
    <input>Well-formed input with all required fields</input>
    <output>High-quality, comprehensive output</output>
    <explanation>This demonstrates proper input validation and context usage</explanation>
  </good>

  <good>
    <input>Another complete example</input>
    <output>Another excellent output</output>
    <explanation>Shows handling of edge cases</explanation>
  </good>

  <bad>
    <input>Incomplete input missing required fields</input>
    <output>Generic, unhelpful response</output>
    <explanation>Fails to validate inputs or use context</explanation>
  </bad>
</examples>`;

  return xml;
}

function generatePromptName() {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  const part = () => Array.from({ length: 3 }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
  return `${part()}-${part()}-${part()}`;
}

/**
 * Main A/B workflow with context analysis
 */
async function runIntegratedABWorkflow(task, outputPath, maxAttempts) {
  const sessionStartTime = Date.now();

  // Initialize workflow instrumentation
  const instrumentation = new WorkflowInstrumentation('prompt-generation', 'stg-val-wkf');

  // Start workflow session (creates root span)
  instrumentation.startSession(task, {
    'workflow.analyze_context': config.analyzeContext,
    'workflow.max_attempts': maxAttempts,
    'workflow.output_path': outputPath
  });

  log('\n🚀 Starting Integrated A/B Agent Workflow', 'green', {
    session_id: instrumentation.sessionId,
    workflow_id: 'prompt-generation',
    task: task
  });
  log('   (Two-Agent System + Context Analysis)', 'magenta');
  log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`, 'green');

  let currentAttempt = 1;
  let feedback = [];
  let previousAttempt = null;
  let validationHistory = [];
  let finalResult = null;

  while (currentAttempt <= maxAttempts) {
    const attemptStartTime = Date.now();

    log(`\n${'='.repeat(60)}`, 'cyan');
    log(`ATTEMPT ${currentAttempt}/${maxAttempts}`, 'cyan', {
      session_id: instrumentation.sessionId,
      attempt_number: currentAttempt
    });
    log(`${'='.repeat(60)}`, 'cyan');

    // Start attempt span
    instrumentation.startAttempt(currentAttempt, maxAttempts);

    // STEP 1: Agent A generates XML with context analysis
    const genResult = await instrumentation.instrumentStage(
      'PromptGeneration',
      'prompt-generator-001',
      async () => {
        return await callAgentA({
          user_request: task,
          analyze_context: config.analyzeContext,
          feedback: feedback,
          previous_attempt: previousAttempt,
          attempt_number: currentAttempt
        });
      }
    );

    const { xml_prompt, prompt_name, input_analysis, generation_metadata } = genResult;

    // STEP 2: Agent B validates with context checks
    const valResult = await instrumentation.instrumentStage(
      'PromptValidation',
      'prompt-validator-001',
      async () => {
        return await callAgentB({
          xml_prompt: xml_prompt,
          previous_validation_results: validationHistory,
          attempt_number: currentAttempt
        });
      }
    );

    validationHistory.push(valResult);

    // Record validation result
    instrumentation.recordValidation(
      valResult.isValid,
      valResult.qualityScore,
      valResult.feedback
    );

    // Display results
    log(`\n📊 Agent B Validation Results:`, 'cyan');
    log(`   Overall Score: ${valResult.qualityScore}/100`,
        valResult.isValid ? 'green' : 'yellow');
    log(`   Status: ${valResult.isValid ? 'PASS ✓' : 'NEEDS IMPROVEMENT ⚠️'}`,
        valResult.isValid ? 'green' : 'yellow');

    log(`\n   Score Breakdown:`, 'cyan');
    log(`     Structural:    ${valResult.scoreBreakdown.structural}/35`, 'cyan');
    log(`     Completeness:  ${valResult.scoreBreakdown.completeness}/30`, 'cyan');
    log(`     Quality:       ${valResult.scoreBreakdown.quality}/25`, 'cyan');
    log(`     Context:       ${valResult.scoreBreakdown.context_quality}/10`, 'magenta');

    if (valResult.contextValidation) {
      log(`\n   Context Validation:`, 'magenta');
      log(`     Input spec:     ${valResult.contextValidation.input_specification_present ? '✓' : '✗'}`, 'cyan');
      log(`     Required inputs: ${valResult.contextValidation.required_inputs_count}`, 'cyan');
      log(`     Context sources: ${valResult.contextValidation.context_sources_count}`, 'cyan');
      if (valResult.contextValidation.glean_integrations.length > 0) {
        log(`     Glean tools:    ${valResult.contextValidation.glean_integrations.join(', ')}`, 'magenta');
      }
    }

    // Record attempt duration
    const attemptDuration = Date.now() - attemptStartTime;
    instrumentation.recordAttemptDuration(currentAttempt, attemptDuration);

    // STEP 3: Check if validation passed
    if (valResult.isValid) {
      log(`\n✅ SUCCESS! Both agents approved the prompt.`, 'green', {
        session_id: instrumentation.sessionId,
        attempt_number: currentAttempt,
        quality_score: valResult.qualityScore
      });
      finalResult = {
        xml_prompt,
        prompt_name,
        input_analysis,
        validation_history: validationHistory,
        attempts: currentAttempt,
        final_score: valResult.qualityScore
      };
      break;
    }

    // STEP 4: If not valid and attempts remain, prepare for refinement
    if (currentAttempt < maxAttempts) {
      log(`\n⚠️  Agent B rejected. Preparing feedback for Agent A...`, 'yellow', {
        session_id: instrumentation.sessionId,
        attempt_number: currentAttempt,
        feedback_count: valResult.feedback.length
      });
      if (valResult.feedback.length > 0) {
        log(`   Feedback to address:`, 'yellow');
        valResult.feedback.forEach((item, i) => {
          log(`     ${i + 1}. ${item}`, 'yellow');
        });
      }

      // Record feedback cycle
      instrumentation.recordFeedbackCycle(valResult.feedback);

      feedback = valResult.feedback;
      previousAttempt = { xml_prompt, prompt_name };
      currentAttempt++;
    } else {
      log(`\n❌ Max attempts reached. Best score: ${valResult.qualityScore}/100`, 'red', {
        session_id: instrumentation.sessionId,
        attempt_number: currentAttempt,
        final_score: valResult.qualityScore
      });
      finalResult = {
        xml_prompt,
        prompt_name,
        input_analysis,
        validation_history: validationHistory,
        attempts: currentAttempt,
        final_score: valResult.qualityScore
      };
      break;
    }
  }

  // Calculate session duration and complete instrumentation
  const sessionDuration = Date.now() - sessionStartTime;
  instrumentation.recordSessionDuration(sessionDuration);
  instrumentation.completeSession(
    finalResult.final_score,
    finalResult.attempts,
    finalResult.final_score >= 90 ? 'success' : 'partial_success'
  );

  // Save results
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(outputPath, finalResult.xml_prompt);
  log(`\n💾 Saved to: ${outputPath}`, 'green');

  const reportPath = outputPath.replace('.xml', '-ab-report.json');
  fs.writeFileSync(reportPath, JSON.stringify({
    prompt_name: finalResult.prompt_name,
    task,
    attempts: finalResult.attempts,
    final_score: finalResult.final_score,
    input_analysis: finalResult.input_analysis,
    validation_history: finalResult.validation_history,
    glean_integrations_needed: finalResult.input_analysis?.glean_integrations || [],
    workflow_type: 'integrated_ab_with_context'
  }, null, 2));
  log(`📋 A/B report saved to: ${reportPath}`, 'green');

  log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`, 'green');
}

// Main entry point
(async () => {
  try {
    if (config.mode === 'generate') {
      if (!config.task) {
        log('❌ Error: --task parameter required', 'red');
        await shutdownOTel();
        process.exit(1);
      }
      await runIntegratedABWorkflow(config.task, config.output, config.maxAttempts);

      // Shutdown OTel to flush all telemetry
      await shutdownOTel();
    } else {
      log('❌ Error: --mode must be "generate"', 'red');
      await shutdownOTel();
      process.exit(1);
    }
  } catch (error) {
    log(`\n❌ Error: ${error.message}`, 'red');
    console.error(error);
    await shutdownOTel();
    process.exit(1);
  }
})();
