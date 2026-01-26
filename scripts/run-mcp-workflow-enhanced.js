#!/usr/bin/env node

/**
 * Enhanced MCP Workflow Runner with Context Management
 * Demonstrates input identification and context retrieval
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const config = {
  mode: getArg('--mode'),
  task: getArg('--task'),
  file: getArg('--file'),
  output: getArg('--output') || 'output/prompt.xml',
  maxAttempts: parseInt(getArg('--max-attempts') || '3'),
  analyzeContext: getArg('--analyze-context') !== 'false' // default true
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

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

/**
 * ENHANCED: Analyze task to identify required inputs and context
 */
function analyzeTaskForInputs(userRequest) {
  log(`\n🔍 Analyzing task for input requirements...`, 'magenta');

  const analysis = {
    required_inputs: [],
    optional_inputs: [],
    context_sources: [],
    glean_integrations: []
  };

  const taskLower = userRequest.toLowerCase();

  // Pattern matching for common prompt types
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
        query: 'email template {{purpose}}' },
      { name: 'recipient_info', source: 'glean_employee_search',
        query: '{{recipient}}' }
    );
    analysis.glean_integrations.push('mcp__glean__search', 'mcp__glean__employee_search');
  }

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

  // Generic fallback
  if (analysis.required_inputs.length === 0) {
    analysis.required_inputs.push(
      { name: 'user_input', type: 'string', source: 'user_provided',
        description: 'Primary input for the task' }
    );
  }

  log(`   Required inputs: ${analysis.required_inputs.length}`, 'cyan');
  analysis.required_inputs.forEach(input => {
    log(`     - ${input.name} (${input.type}): ${input.description}`, 'cyan');
  });

  if (analysis.optional_inputs.length > 0) {
    log(`   Optional inputs: ${analysis.optional_inputs.length}`, 'cyan');
    analysis.optional_inputs.forEach(input => {
      log(`     - ${input.name} (${input.type}, default: ${input.default || 'none'})`, 'cyan');
    });
  }

  if (analysis.context_sources.length > 0) {
    log(`   Context sources: ${analysis.context_sources.length}`, 'cyan');
    analysis.context_sources.forEach(ctx => {
      log(`     - ${ctx.name} via ${ctx.source}`, 'cyan');
    });
  }

  if (analysis.glean_integrations.length > 0) {
    log(`   Glean MCP tools needed: ${[...new Set(analysis.glean_integrations)].join(', ')}`, 'magenta');
  }

  return analysis;
}

/**
 * Generate input specification XML
 */
function generateInputSpecificationXml(inputAnalysis) {
  let xml = '\n<input_specification>\n';

  // Required inputs
  inputAnalysis.required_inputs.forEach(input => {
    xml += `  <input>\n`;
    xml += `    <name>${input.name}</name>\n`;
    xml += `    <type>${input.type}</type>\n`;
    xml += `    <required>true</required>\n`;
    xml += `    <description>${input.description}</description>\n`;
    xml += `    <source>${input.source}</source>\n`;
    xml += `  </input>\n\n`;
  });

  // Optional inputs
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
  return xml;
}

/**
 * Generate context requirements XML
 */
function generateContextRequirementsXml(inputAnalysis) {
  if (inputAnalysis.context_sources.length === 0) {
    return '';
  }

  let xml = '\n<context_requirements>\n';

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
  return xml;
}

/**
 * Enhanced XML prompt generation
 */
function generateEnhancedXmlPrompt(task, inputAnalysis) {
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

  // Add input specification
  xml += generateInputSpecificationXml(inputAnalysis);

  // Add context requirements
  xml += generateContextRequirementsXml(inputAnalysis);

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

  return { xml, promptName, inputAnalysis };
}

/**
 * Validate prompt with context awareness
 */
async function validateEnhancedPrompt(xmlPrompt, attemptNumber) {
  log(`\n✓ Validating prompt with context checks (attempt ${attemptNumber}/3)...`, 'blue');

  // Check for input specification
  const hasInputSpec = xmlPrompt.includes('<input_specification>');
  const hasContextReq = xmlPrompt.includes('<context_requirements>');
  const hasRequiredInputs = (xmlPrompt.match(/<required>true<\/required>/g) || []).length > 0;

  let score = 100;
  const checks = [];

  // Structure checks
  checks.push({
    rule_id: 'xml_well_formed',
    status: 'pass',
    message: 'XML is well-formed',
    severity: 'info',
    score_impact: 0
  });

  // Context checks
  if (!hasInputSpec) {
    checks.push({
      rule_id: 'input_specification_present',
      status: 'fail',
      message: 'Missing <input_specification> section',
      severity: 'error',
      score_impact: -15
    });
    score -= 15;
  } else {
    checks.push({
      rule_id: 'input_specification_present',
      status: 'pass',
      message: 'Input specification defined',
      severity: 'info',
      score_impact: 0
    });
  }

  if (!hasRequiredInputs) {
    checks.push({
      rule_id: 'required_inputs_defined',
      status: 'fail',
      message: 'No required inputs specified',
      severity: 'warning',
      score_impact: -5
    });
    score -= 5;
  }

  // Examples check
  const hasGoodExamples = (xmlPrompt.match(/<good>/g) || []).length >= 2;
  const hasBadExamples = (xmlPrompt.match(/<bad>/g) || []).length >= 1;

  if (!hasGoodExamples || !hasBadExamples) {
    checks.push({
      rule_id: 'examples_quality',
      status: 'fail',
      message: 'Need at least 2 good and 1 bad example',
      severity: 'error',
      score_impact: -20
    });
    score -= 20;
  }

  const isValid = score >= 90;
  const feedback = [];

  if (!hasInputSpec) feedback.push('Add <input_specification> section with required inputs');
  if (!hasRequiredInputs) feedback.push('Define at least one required input');
  if (!hasGoodExamples) feedback.push('Add at least 2 good examples');
  if (!hasBadExamples) feedback.push('Add 1 bad example with explanation');
  if (!hasContextReq) feedback.push('Consider adding <context_requirements> for Glean integration');

  return {
    isValid,
    qualityScore: score,
    checks,
    feedback,
    context_validation: {
      input_specification_present: hasInputSpec,
      context_requirements_present: hasContextReq,
      required_inputs_count: (xmlPrompt.match(/<required>true<\/required>/g) || []).length,
      glean_integrations_detected: hasContextReq
    }
  };
}

function generatePromptName() {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  const part = () => Array.from({ length: 3 }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
  return `${part()}-${part()}-${part()}`;
}

/**
 * Main enhanced workflow
 */
async function runEnhancedGenerateWorkflow(task, outputPath, maxAttempts) {
  log('\n🚀 Starting Enhanced XML Prompt Generation Workflow', 'green');
  log('   (with Context Analysis)', 'magenta');
  log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`, 'green');

  // STEP 1: Analyze task for inputs and context
  const inputAnalysis = config.analyzeContext ? analyzeTaskForInputs(task) : null;

  let currentAttempt = 1;
  let xmlPrompt = null;
  let promptName = null;
  let validationResults = [];

  while (currentAttempt <= maxAttempts) {
    log(`\n📝 Generating XML prompt (attempt ${currentAttempt}/${maxAttempts})...`, 'blue');

    // Generate enhanced prompt with input/context specs
    const result = generateEnhancedXmlPrompt(task, inputAnalysis);
    xmlPrompt = result.xml;
    promptName = result.promptName;

    log(`✓ Generated prompt: ${promptName}`, 'green');
    if (inputAnalysis) {
      log(`   Includes: ${inputAnalysis.required_inputs.length} required inputs, ${inputAnalysis.context_sources.length} context sources`, 'cyan');
    }

    // Validate
    await new Promise(resolve => setTimeout(resolve, 300));
    const valResult = await validateEnhancedPrompt(xmlPrompt, currentAttempt);
    validationResults.push(valResult);

    log(`\n📊 Validation Results (Attempt ${currentAttempt}):`, 'cyan');
    log(`   Quality Score: ${valResult.qualityScore}/100`, valResult.qualityScore >= 90 ? 'green' : 'yellow');
    log(`   Status: ${valResult.isValid ? 'PASS ✓' : 'NEEDS IMPROVEMENT'}`, valResult.isValid ? 'green' : 'yellow');

    if (valResult.context_validation) {
      log(`\n   Context Validation:`, 'magenta');
      log(`     Input spec present: ${valResult.context_validation.input_specification_present ? '✓' : '✗'}`, 'cyan');
      log(`     Required inputs: ${valResult.context_validation.required_inputs_count}`, 'cyan');
      log(`     Context sources: ${valResult.context_validation.context_requirements_present ? '✓' : '✗'}`, 'cyan');
    }

    if (valResult.isValid) {
      log(`\n✅ SUCCESS! Prompt validated successfully.`, 'green');
      break;
    }

    if (currentAttempt < maxAttempts) {
      log(`\n⚠️  Validation failed. Would refine with feedback...`, 'yellow');
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

  // Save enhanced report
  const reportPath = outputPath.replace('.xml', '-context-report.json');
  fs.writeFileSync(reportPath, JSON.stringify({
    prompt_name: promptName,
    task,
    attempts: currentAttempt,
    final_score: validationResults[validationResults.length - 1].qualityScore,
    input_analysis: inputAnalysis,
    validation_history: validationResults,
    glean_integrations_needed: inputAnalysis?.glean_integrations || []
  }, null, 2));
  log(`📋 Context report saved to: ${reportPath}`, 'green');

  log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`, 'green');
}

// Main entry point
(async () => {
  try {
    if (config.mode === 'generate') {
      if (!config.task) {
        log('❌ Error: --task parameter required', 'red');
        process.exit(1);
      }
      await runEnhancedGenerateWorkflow(config.task, config.output, config.maxAttempts);
    } else {
      log('❌ Error: --mode must be "generate"', 'red');
      process.exit(1);
    }
  } catch (error) {
    log(`\n❌ Error: ${error.message}`, 'red');
    console.error(error);
    process.exit(1);
  }
})();
