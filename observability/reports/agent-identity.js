/**
 * Agent Identity System
 *
 * Maps technical agent IDs to human-readable display information including
 * names, roles, emojis, colors, and descriptions.
 */

const AGENT_REGISTRY = {
  'prompt-generator-001': {
    displayName: 'Prompt Generator',
    role: 'Content Creator',
    emoji: '🤖',
    color: '#3b82f6',
    description: 'Generates initial prompt from task description'
  },
  'prompt-validator-001': {
    displayName: 'Quality Validator',
    role: 'Quality Assurance',
    emoji: '✅',
    color: '#10b981',
    description: 'Validates prompt quality and provides feedback'
  },
  'feedback-analyzer-001': {
    displayName: 'Feedback Analyzer',
    role: 'Continuous Improvement',
    emoji: '🔍',
    color: '#8b5cf6',
    description: 'Analyzes feedback and suggests improvements'
  },
  'context-analyzer-001': {
    displayName: 'Context Analyzer',
    role: 'Information Gatherer',
    emoji: '📊',
    color: '#f59e0b',
    description: 'Analyzes task context and requirements'
  },
  'prompt-refiner-001': {
    displayName: 'Prompt Refiner',
    role: 'Enhancement Specialist',
    emoji: '✨',
    color: '#ec4899',
    description: 'Refines and enhances prompt based on feedback'
  }
};

/**
 * Gets agent information by ID with fallback to defaults
 * @param {string} agentId - Technical agent identifier
 * @returns {Object} Agent information with displayName, role, emoji, color, description
 */
function getAgentInfo(agentId) {
  // Return from registry if found
  if (AGENT_REGISTRY[agentId]) {
    return {
      id: agentId,
      ...AGENT_REGISTRY[agentId]
    };
  }

  // Try pattern matching for dynamic agent IDs
  // e.g., "prompt-generator-002" -> matches "prompt-generator"
  const basePattern = agentId.replace(/-\d+$/, '');
  const matchingEntry = Object.entries(AGENT_REGISTRY).find(([key]) =>
    key.startsWith(basePattern)
  );

  if (matchingEntry) {
    return {
      id: agentId,
      ...matchingEntry[1]
    };
  }

  // Fallback for unknown agents
  return {
    id: agentId,
    displayName: formatAgentIdToName(agentId),
    role: 'Unknown Role',
    emoji: '❓',
    color: '#6b7280',
    description: 'Agent type not registered'
  };
}

/**
 * Formats agent ID into a human-readable name
 * @param {string} agentId - Technical identifier like "prompt-generator-001"
 * @returns {string} Formatted name like "Prompt Generator"
 */
function formatAgentIdToName(agentId) {
  return agentId
    .replace(/-\d+$/, '')  // Remove trailing numbers
    .split('-')            // Split by hyphens
    .map(word => word.charAt(0).toUpperCase() + word.slice(1)) // Capitalize
    .join(' ');            // Join with spaces
}

/**
 * Formats agent name with emoji for display
 * @param {string} agentId - Technical agent identifier
 * @returns {string} Formatted string like "🤖 Prompt Generator"
 */
function formatAgentName(agentId) {
  const agent = getAgentInfo(agentId);
  return `${agent.emoji} ${agent.displayName}`;
}

/**
 * Extracts agent ID from span attributes
 * @param {Object} span - OpenTelemetry span object
 * @returns {string|null} Agent ID or null if not found
 */
function extractAgentId(span) {
  if (!span.attributes) return null;

  // Try various attribute names that might contain agent ID
  return span.attributes['stage.agent_id'] ||
         span.attributes['agent.id'] ||
         span.attributes['agent.name'] ||
         span.attributes['workflow.agent'] ||
         inferAgentFromSpanName(span.name);
}

/**
 * Infers agent type from span name when explicit ID is not available
 * @param {string} spanName - Name of the span
 * @returns {string|null} Inferred agent ID or null
 */
function inferAgentFromSpanName(spanName) {
  const patterns = {
    'PromptGeneration': 'prompt-generator-001',
    'PromptValidation': 'prompt-validator-001',
    'FeedbackAnalysis': 'feedback-analyzer-001',
    'ContextAnalysis': 'context-analyzer-001',
    'PromptRefinement': 'prompt-refiner-001'
  };

  for (const [pattern, agentId] of Object.entries(patterns)) {
    if (spanName.includes(pattern)) {
      return agentId;
    }
  }

  return null;
}

/**
 * Gets quality score color class based on score value
 * @param {number} score - Quality score (0-100)
 * @returns {string} CSS class name ('excellent', 'good', 'needs-work')
 */
function getQualityScoreClass(score) {
  if (score >= 90) return 'excellent';
  if (score >= 70) return 'good';
  return 'needs-work';
}

/**
 * Gets quality score emoji based on score value
 * @param {number} score - Quality score (0-100)
 * @returns {string} Emoji representing quality level
 */
function getQualityScoreEmoji(score) {
  if (score >= 90) return '🟢';
  if (score >= 70) return '🟡';
  return '🔴';
}

/**
 * Gets all registered agent IDs
 * @returns {string[]} Array of agent IDs
 */
function getAllAgentIds() {
  return Object.keys(AGENT_REGISTRY);
}

/**
 * Gets all registered agents with their info
 * @returns {Object[]} Array of agent info objects
 */
function getAllAgents() {
  return Object.entries(AGENT_REGISTRY).map(([id, info]) => ({
    id,
    ...info
  }));
}

module.exports = {
  AGENT_REGISTRY,
  getAgentInfo,
  formatAgentIdToName,
  formatAgentName,
  extractAgentId,
  inferAgentFromSpanName,
  getQualityScoreClass,
  getQualityScoreEmoji,
  getAllAgentIds,
  getAllAgents
};
