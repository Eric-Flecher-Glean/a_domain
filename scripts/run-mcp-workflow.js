#!/usr/bin/env node

/**
 * MCP Workflow Runner
 * Orchestrates the prompt generation and validation workflow
 *
 * Usage:
 *   node run-mcp-workflow.js --mode generate --task "your task" --output file.xml
 *   node run-mcp-workflow.js --mode validate --file prompt.xml
 */

const fs = require('fs');
const path = require('path');

// Parse command line arguments
const args = process.argv.slice(2);
const config = {
  mode: getArg('--mode'),
  task: getArg('--task'),
  file: getArg('--file'),
  output: getArg('--output') || 'output/prompt.xml',
  maxAttempts: parseInt(getArg('--max-attempts') || '3')
};

function getArg(name) {
  const index = args.indexOf(name);
  return index !== -1 ? args[index + 1] : null;
}

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  red: '\x1b[31m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

/**
 * Simulate MCP tool call to generate_xml_prompt
 * In production, this would call the actual Glean MCP server
 */
async function callGenerateXmlPrompt(userRequest, feedback = [], previousAttempt = null, attemptNumber = 1) {
  log(`\n📝 Calling generate_xml_prompt (attempt ${attemptNumber}/3)...`, 'blue');
  log(`   Request: ${userRequest}`, 'cyan');

  if (feedback.length > 0) {
    log(`   Feedback items: ${feedback.length}`, 'yellow');
    feedback.forEach((item, i) => log(`     ${i + 1}. ${item}`, 'yellow'));
  }

  // Simulate MCP server call
  // TODO: Replace with actual Glean MCP server API call
  const response = await simulateAgentCall('prompt-generator-001', {
    user_request: userRequest,
    feedback,
    previous_attempt: previousAttempt,
    attempt_number: attemptNumber
  });

  return response;
}

/**
 * Simulate MCP tool call to validate_prompt_quality
 * In production, this would call the actual Glean MCP server
 */
async function callValidatePromptQuality(xmlPrompt, previousResults = [], attemptNumber = 1) {
  log(`\n✓ Calling validate_prompt_quality (attempt ${attemptNumber}/3)...`, 'blue');

  // Simulate MCP server call
  // TODO: Replace with actual Glean MCP server API call
  const response = await simulateAgentCall('prompt-validator-001', {
    xml_prompt: xmlPrompt,
    previous_validation_results: previousResults,
    attempt_number: attemptNumber
  });

  return response;
}

/**
 * Simulate agent call - replace with actual Glean API
 */
async function simulateAgentCall(agentId, input) {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 500));

  if (agentId === 'prompt-generator-001') {
    return {
      xml_prompt: generateMockXmlPrompt(input.user_request),
      prompt_name: generatePromptName(),
      components_extracted: {
        primary_goal: `Process: ${input.user_request}`,
        role: 'AI Assistant',
        task: 'Execute the requested operation',
        context: 'General purpose task execution',
        constraints: ['Follow best practices', 'Be concise'],
        output_format: 'Structured response'
      },
      generation_metadata: {
        attempt: input.attempt_number,
        refinements_applied: input.feedback || [],
        timestamp: new Date().toISOString(),
        feedback_addressed: input.feedback || []
      }
    };
  }

  if (agentId === 'prompt-validator-001') {
    const score = input.attempt_number === 1 ? 85 : 95; // Simulate improvement
    const isValid = score >= 90;

    return {
      isValid,
      qualityScore: score,
      checks: [
        { rule_id: 'xml_well_formed', status: 'pass', message: 'XML is well-formed', severity: 'info', section: 'structure', score_impact: 0 },
        { rule_id: 'required_sections', status: isValid ? 'pass' : 'fail', message: isValid ? 'All required sections present' : 'Missing examples section', severity: 'error', section: 'completeness', score_impact: isValid ? 0 : -20 }
      ],
      feedback: isValid ? [] : [
        'Add at least 2 good examples',
        'Add 1 bad example with explanation',
        'Improve instruction clarity'
      ],
      recommendations: isValid ? ['Consider adding more context-specific examples'] : [],
      scoreBreakdown: {
        structural: 40,
        completeness: isValid ? 30 : 20,
        quality: 25,
        bonuses: 0,
        penalties: isValid ? 0 : -20
      },
      examplesAnalysis: {
        good_examples_found: isValid ? 2 : 0,
        bad_examples_found: isValid ? 1 : 0,
        examples_quality_score: isValid ? 85 : 0
      }
    };
  }
}

/**
 * Generate a mock XML prompt (replace with actual generation)
 */
function generateMockXmlPrompt(task) {
  return `<metadata>
  <name>${generatePromptName()}</name>
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

<instructions>
1. Understand the user's specific need
2. Apply relevant expertise and best practices
3. Generate a clear, actionable response
4. Validate output quality before delivery
</instructions>

<output_format>
Provide responses in a clear, structured format with:
- Summary of key points
- Detailed explanation
- Actionable recommendations
</output_format>

<examples>
  <good>
    <input>Example input for ${task}</input>
    <output>Example high-quality output</output>
    <explanation>This is good because it's clear and actionable</explanation>
  </good>

  <good>
    <input>Another example input</input>
    <output>Another high-quality output</output>
    <explanation>This demonstrates best practices</explanation>
  </good>

  <bad>
    <input>Example input</input>
    <output>Vague, unhelpful output</output>
    <explanation>This is bad because it lacks specificity</explanation>
  </bad>
</examples>`;
}

/**
 * Generate unique prompt name in xxx-xxx-xxx format
 */
function generatePromptName() {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  const part = () => Array.from({ length: 3 }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
  return `${part()}-${part()}-${part()}`;
}

/**
 * Main workflow: Generate and validate with feedback loop
 */
async function runGenerateWorkflow(task, outputPath, maxAttempts) {
  log('\n🚀 Starting XML Prompt Generation Workflow', 'green');
  log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`, 'green');

  let currentAttempt = 1;
  let xmlPrompt = null;
  let promptName = null;
  let validationResults = [];
  let feedback = [];
  let previousAttempt = null;

  while (currentAttempt <= maxAttempts) {
    // Step 1: Generate XML prompt
    const genResult = await callGenerateXmlPrompt(task, feedback, previousAttempt, currentAttempt);
    xmlPrompt = genResult.xml_prompt;
    promptName = genResult.prompt_name;

    log(`✓ Generated prompt: ${promptName}`, 'green');

    // Step 2: Validate quality
    const valResult = await callValidatePromptQuality(xmlPrompt, validationResults, currentAttempt);
    validationResults.push(valResult);

    log(`\n📊 Validation Results (Attempt ${currentAttempt}):`, 'cyan');
    log(`   Quality Score: ${valResult.qualityScore}/100`, valResult.qualityScore >= 90 ? 'green' : 'yellow');
    log(`   Status: ${valResult.isValid ? 'PASS ✓' : 'NEEDS IMPROVEMENT'}`, valResult.isValid ? 'green' : 'yellow');

    if (valResult.scoreBreakdown) {
      log(`\n   Score Breakdown:`, 'cyan');
      log(`     Structural:   ${valResult.scoreBreakdown.structural}/40`, 'cyan');
      log(`     Completeness: ${valResult.scoreBreakdown.completeness}/30`, 'cyan');
      log(`     Quality:      ${valResult.scoreBreakdown.quality}/30`, 'cyan');
    }

    // Step 3: Check if we're done
    if (valResult.isValid) {
      log(`\n✅ SUCCESS! Prompt validated successfully.`, 'green');
      break;
    }

    // Step 4: If not valid and we have attempts left, refine
    if (currentAttempt < maxAttempts) {
      log(`\n⚠️  Validation failed. Refining with feedback...`, 'yellow');
      feedback = valResult.feedback;
      previousAttempt = { xml_prompt: xmlPrompt, prompt_name: promptName };
      currentAttempt++;
    } else {
      log(`\n❌ Max attempts reached. Best score: ${valResult.qualityScore}/100`, 'red');
      break;
    }
  }

  // Save output
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(outputPath, xmlPrompt);
  log(`\n💾 Saved to: ${outputPath}`, 'green');

  // Save validation report
  const reportPath = outputPath.replace('.xml', '-report.json');
  fs.writeFileSync(reportPath, JSON.stringify({
    prompt_name: promptName,
    task,
    attempts: currentAttempt,
    final_score: validationResults[validationResults.length - 1].qualityScore,
    validation_history: validationResults
  }, null, 2));
  log(`📋 Report saved to: ${reportPath}`, 'green');

  log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`, 'green');
}

/**
 * Validate existing prompt file
 */
async function runValidateWorkflow(filePath) {
  log('\n🔍 Starting Prompt Validation', 'green');
  log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`, 'green');

  if (!fs.existsSync(filePath)) {
    log(`❌ Error: File not found: ${filePath}`, 'red');
    process.exit(1);
  }

  const xmlPrompt = fs.readFileSync(filePath, 'utf8');
  const valResult = await callValidatePromptQuality(xmlPrompt, [], 1);

  log(`\n📊 Validation Results:`, 'cyan');
  log(`   Quality Score: ${valResult.qualityScore}/100`, valResult.qualityScore >= 90 ? 'green' : 'yellow');
  log(`   Status: ${valResult.isValid ? 'PASS ✓' : 'FAIL ✗'}`, valResult.isValid ? 'green' : 'red');

  if (valResult.scoreBreakdown) {
    log(`\n   Score Breakdown:`, 'cyan');
    log(`     Structural:   ${valResult.scoreBreakdown.structural}/40`, 'cyan');
    log(`     Completeness: ${valResult.scoreBreakdown.completeness}/30`, 'cyan');
    log(`     Quality:      ${valResult.scoreBreakdown.quality}/30`, 'cyan');
  }

  if (valResult.feedback.length > 0) {
    log(`\n   Feedback:`, 'yellow');
    valResult.feedback.forEach((item, i) => log(`     ${i + 1}. ${item}`, 'yellow'));
  }

  if (valResult.recommendations.length > 0) {
    log(`\n   Recommendations:`, 'cyan');
    valResult.recommendations.forEach((item, i) => log(`     ${i + 1}. ${item}`, 'cyan'));
  }

  log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`, 'green');
}

// Main entry point
(async () => {
  try {
    if (config.mode === 'generate') {
      if (!config.task) {
        log('❌ Error: --task parameter required for generate mode', 'red');
        process.exit(1);
      }
      await runGenerateWorkflow(config.task, config.output, config.maxAttempts);
    } else if (config.mode === 'validate') {
      if (!config.file) {
        log('❌ Error: --file parameter required for validate mode', 'red');
        process.exit(1);
      }
      await runValidateWorkflow(config.file);
    } else {
      log('❌ Error: --mode must be either "generate" or "validate"', 'red');
      process.exit(1);
    }
  } catch (error) {
    log(`\n❌ Error: ${error.message}`, 'red');
    console.error(error);
    process.exit(1);
  }
})();
