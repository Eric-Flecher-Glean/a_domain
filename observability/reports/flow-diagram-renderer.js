/**
 * Flow Diagram Renderer
 *
 * Renders vertical process flow diagram showing agent collaboration,
 * decision points, and data flow between stages.
 */

const { getAgentInfo, getQualityScoreClass } = require('./agent-identity');

class FlowDiagramRenderer {
  constructor(config = {}) {
    this.config = {
      nodeWidth: 200,
      nodeHeight: 80,
      verticalGap: 100,
      horizontalGap: 250,
      arrowHeight: 40,
      canvasWidth: 300,
      ...config
    };
  }

  /**
   * Renders complete flow diagram from timeline data
   */
  render(timeline) {
    const { rows, metadata } = timeline;

    // Build flow structure
    const attempts = this.groupByAttempts(rows);
    const nodes = this.buildFlowNodes(attempts);
    const connections = this.buildConnections(nodes, attempts);

    // Calculate canvas height
    const maxY = Math.max(...nodes.map(n => n.y + n.height));
    const svgHeight = maxY + 50;

    return this.renderSVG(nodes, connections, svgHeight, metadata);
  }

  /**
   * Groups rows by attempt number
   */
  groupByAttempts(rows) {
    const attempts = [];

    // Find unique attempt numbers
    const attemptNumbers = [...new Set(rows
      .filter(r => r.attemptNumber)
      .map(r => r.attemptNumber)
    )].sort((a, b) => a - b);

    if (attemptNumbers.length === 0) {
      // No attempts - treat as single flow
      return [{
        number: 1,
        rows: rows,
        score: rows.find(r => r.qualityScore)?.qualityScore || null,
        isValid: rows.find(r => r.isValid !== null)?.isValid ?? true,
        feedback: rows.find(r => r.feedback?.length > 0)?.feedback || []
      }];
    }

    // Group rows by attempt
    attemptNumbers.forEach(attemptNum => {
      const attemptRows = rows.filter(r => r.attemptNumber === attemptNum);
      const validationRow = attemptRows.find(r => r.hasQualityData);

      attempts.push({
        number: attemptNum,
        rows: attemptRows,
        score: validationRow?.qualityScore || null,
        isValid: validationRow?.isValid ?? true,
        feedback: validationRow?.feedback || []
      });
    });

    return attempts;
  }

  /**
   * Builds flow nodes from attempts
   */
  buildFlowNodes(attempts) {
    const nodes = [];
    let yPosition = 50;

    // Start node
    nodes.push({
      id: 'start',
      type: 'start',
      label: 'START WORKFLOW',
      x: this.config.canvasWidth / 2 - this.config.nodeWidth / 2,
      y: yPosition,
      width: this.config.nodeWidth,
      height: 40
    });

    yPosition += 80;

    attempts.forEach((attempt, attemptIndex) => {
      // Add attempt header if multiple attempts
      if (attempts.length > 1) {
        nodes.push({
          id: `attempt-header-${attempt.number}`,
          type: 'attempt-header',
          label: `ATTEMPT ${attempt.number}`,
          score: attempt.score,
          x: this.config.canvasWidth / 2 - this.config.nodeWidth / 2,
          y: yPosition,
          width: this.config.nodeWidth,
          height: 40
        });

        yPosition += 70;
      }

      // Add agent nodes for this attempt
      attempt.rows.forEach((row, rowIndex) => {
        const agentInfo = getAgentInfo(row.agentId);

        nodes.push({
          id: row.spanId,
          type: 'agent',
          agentInfo: agentInfo,
          label: row.displayName || row.name,
          duration: row.duration,
          status: row.status,
          qualityScore: row.qualityScore,
          qualityScoreClass: row.qualityScoreClass,
          feedback: row.feedback,
          x: this.config.canvasWidth / 2 - this.config.nodeWidth / 2,
          y: yPosition,
          width: this.config.nodeWidth,
          height: this.config.nodeHeight,
          attemptNumber: attempt.number,
          rowData: row
        });

        yPosition += this.config.nodeHeight + this.config.verticalGap;
      });

      // Add decision node if there's another attempt (failed validation)
      if (attemptIndex < attempts.length - 1) {
        nodes.push({
          id: `decision-${attempt.number}`,
          type: 'decision',
          label: 'Quality Check',
          decision: 'RETRY',
          score: attempt.score,
          threshold: 90,
          reason: attempt.feedback[0] || 'Score below threshold',
          feedback: attempt.feedback,
          x: this.config.canvasWidth / 2 - this.config.nodeWidth / 2,
          y: yPosition,
          width: this.config.nodeWidth,
          height: 80
        });

        yPosition += 120;
      }
    });

    // End node
    const lastAttempt = attempts[attempts.length - 1];
    nodes.push({
      id: 'end',
      type: 'end',
      label: lastAttempt.isValid ? 'SUCCESS ✓' : 'COMPLETED',
      score: lastAttempt.score,
      x: this.config.canvasWidth / 2 - this.config.nodeWidth / 2,
      y: yPosition,
      width: this.config.nodeWidth,
      height: 40
    });

    return nodes;
  }

  /**
   * Builds connections between nodes
   */
  buildConnections(nodes, attempts) {
    const connections = [];

    for (let i = 0; i < nodes.length - 1; i++) {
      const from = nodes[i];
      const to = nodes[i + 1];

      const connType = this.getConnectionType(from, to);
      const label = this.getConnectionLabel(from, to);

      connections.push({
        from: from.id,
        to: to.id,
        type: connType,
        label: label
      });
    }

    return connections;
  }

  /**
   * Determines connection type between nodes
   */
  getConnectionType(from, to) {
    if (from.type === 'decision') return 'retry';
    if (to.type === 'decision') return 'validation';
    if (to.type === 'end') return 'completion';
    return 'data-flow';
  }

  /**
   * Gets label for connection
   */
  getConnectionLabel(from, to) {
    if (from.type === 'start') return 'Task';
    if (from.type === 'agent' && to.type === 'agent') {
      // Check row types to determine label
      if (from.rowData?.type === 'generation' && to.rowData?.type === 'validation') {
        return 'Prompt';
      }
      if (from.rowData?.type === 'feedback' && to.rowData?.type === 'generation') {
        return 'Analysis';
      }
    }
    if (to.type === 'decision') return 'Output';
    if (from.type === 'decision') return 'Feedback';
    if (to.type === 'end') return 'Final';
    return '';
  }

  /**
   * Renders complete SVG diagram
   */
  renderSVG(nodes, connections, svgHeight, metadata) {
    return `
      <svg viewBox="0 0 ${this.config.canvasWidth} ${svgHeight}"
           preserveAspectRatio="xMidYMid meet"
           xmlns="http://www.w3.org/2000/svg"
           class="flow-diagram"
           data-session-id="${metadata.sessionId || ''}">
        ${this.renderStyles()}
        ${this.renderConnections(connections, nodes)}
        ${this.renderNodes(nodes)}
      </svg>
    `;
  }

  /**
   * Renders embedded CSS styles for flow diagram
   */
  renderStyles() {
    return `
      <defs>
        <style>
          .flow-diagram { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
          .flow-node { cursor: pointer; transition: opacity 0.2s; }
          .flow-node:hover { opacity: 0.9; }
          .node-label { font-size: 14px; font-weight: 600; fill: #111827; }
          .node-role { font-size: 11px; fill: #6b7280; }
          .node-duration { font-size: 10px; fill: #6b7280; }
          .node-emoji { font-size: 20px; }
          .connection-line { stroke: #6b7280; stroke-width: 2; fill: none; }
          .connection-retry { stroke: #f59e0b; stroke-width: 3; fill: none; stroke-dasharray: 5,5; }
          .connection-label { font-size: 11px; fill: #6b7280; text-anchor: middle; }
          .decision-label { font-size: 13px; fill: #92400e; text-anchor: middle; font-weight: 600; }
          .decision-outcome { font-size: 12px; fill: #b45309; text-anchor: middle; }
          .score-badge { font-size: 11px; font-weight: bold; text-anchor: middle; }
          .start-label { font-size: 13px; fill: #059669; text-anchor: middle; font-weight: 600; }
          .end-label { font-size: 13px; fill: #059669; text-anchor: middle; font-weight: 600; }
          .attempt-header-label { font-size: 12px; fill: #4b5563; text-anchor: middle; font-weight: 600; }
        </style>

        <!-- Arrow marker definitions -->
        <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <polygon points="0 0, 10 3, 0 6" fill="#6b7280" />
        </marker>
        <marker id="arrowhead-retry" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <polygon points="0 0, 10 3, 0 6" fill="#f59e0b" />
        </marker>
      </defs>
    `;
  }

  /**
   * Renders all nodes
   */
  renderNodes(nodes) {
    return nodes.map(node => {
      switch (node.type) {
        case 'start':
          return this.renderStartNode(node);
        case 'end':
          return this.renderEndNode(node);
        case 'attempt-header':
          return this.renderAttemptHeader(node);
        case 'agent':
          return this.renderAgentNode(node);
        case 'decision':
          return this.renderDecisionNode(node);
        default:
          return '';
      }
    }).join('\n');
  }

  /**
   * Renders start node
   */
  renderStartNode(node) {
    return `
      <g class="flow-node start-node" transform="translate(${node.x}, ${node.y})">
        <rect width="${node.width}" height="${node.height}"
              rx="20" fill="#d1fae5" stroke="#10b981" stroke-width="2"/>
        <text x="${node.width/2}" y="${node.height/2 + 5}" class="start-label">${node.label}</text>
      </g>
    `;
  }

  /**
   * Renders end node
   */
  renderEndNode(node) {
    return `
      <g class="flow-node end-node" transform="translate(${node.x}, ${node.y})">
        <rect width="${node.width}" height="${node.height}"
              rx="20" fill="#d1fae5" stroke="#10b981" stroke-width="2"/>
        <text x="${node.width/2}" y="${node.height/2 + 5}" class="end-label">${node.label}</text>
        ${node.score !== null ? `
          <text x="${node.width/2}" y="${node.height/2 + 20}"
                style="font-size: 10px; fill: #065f46; text-anchor: middle;">
            Final Score: ${node.score}
          </text>
        ` : ''}
      </g>
    `;
  }

  /**
   * Renders attempt header node
   */
  renderAttemptHeader(node) {
    return `
      <g class="flow-node attempt-header" transform="translate(${node.x}, ${node.y})">
        <rect width="${node.width}" height="${node.height}"
              rx="8" fill="#f3f4f6" stroke="#d1d5db" stroke-width="1" stroke-dasharray="4,4"/>
        <text x="${node.width/2}" y="${node.height/2 + 5}" class="attempt-header-label">${node.label}</text>
      </g>
    `;
  }

  /**
   * Renders agent node
   */
  renderAgentNode(node) {
    const scoreClass = node.qualityScoreClass || 'info';
    const scoreColor = scoreClass === 'excellent' ? '#10b981' :
                       scoreClass === 'good' ? '#f59e0b' : '#ef4444';

    return `
      <g class="flow-node agent-node"
         transform="translate(${node.x}, ${node.y})"
         data-span-id="${node.id}"
         role="button"
         tabindex="0">

        <!-- Background -->
        <rect width="${node.width}" height="${node.height}"
              rx="8" fill="${node.agentInfo.color}" opacity="0.1"/>
        <rect width="${node.width}" height="${node.height}"
              rx="8" fill="none" stroke="${node.agentInfo.color}" stroke-width="2"/>

        <!-- Agent emoji and name -->
        <text x="15" y="28" class="node-emoji">${node.agentInfo.emoji}</text>
        <text x="45" y="28" class="node-label">${this.escapeHtml(node.label)}</text>

        <!-- Role badge -->
        <text x="15" y="48" class="node-role">${this.escapeHtml(node.agentInfo.role)}</text>

        <!-- Quality score (if available) -->
        ${node.qualityScore !== null && node.qualityScore !== undefined ? `
          <circle cx="${node.width - 30}" cy="28" r="18"
                  fill="white" stroke="${scoreColor}" stroke-width="2"/>
          <text x="${node.width - 30}" y="33" class="score-badge" fill="${scoreColor}">
            ${node.qualityScore}
          </text>
        ` : ''}

        <!-- Duration -->
        <text x="15" y="${node.height - 12}" class="node-duration">
          ${this.formatDuration(node.duration)}
        </text>

        <title>${this.escapeHtml(node.label)}: ${this.formatDuration(node.duration)}</title>
      </g>
    `;
  }

  /**
   * Renders decision node (diamond shape)
   */
  renderDecisionNode(node) {
    const centerX = node.width / 2;
    const centerY = node.height / 2;

    return `
      <g class="flow-node decision-node" transform="translate(${node.x}, ${node.y})">
        <!-- Diamond shape -->
        <path d="M ${centerX} 0
                 L ${node.width} ${centerY}
                 L ${centerX} ${node.height}
                 L 0 ${centerY} Z"
              fill="#fef3c7" stroke="#f59e0b" stroke-width="2"/>

        <!-- Decision text -->
        <text x="${centerX}" y="${centerY - 8}" class="decision-label">${node.label}</text>
        <text x="${centerX}" y="${centerY + 12}" class="decision-outcome">${node.decision}</text>
        ${node.score !== null ? `
          <text x="${centerX}" y="${centerY + 28}"
                style="font-size: 10px; fill: #92400e; text-anchor: middle;">
            Score: ${node.score} < ${node.threshold}
          </text>
        ` : ''}

        <title>${node.reason}</title>
      </g>
    `;
  }

  /**
   * Renders all connections
   */
  renderConnections(connections, nodes) {
    return connections.map(conn => {
      const from = nodes.find(n => n.id === conn.from);
      const to = nodes.find(n => n.id === conn.to);

      if (!from || !to) return '';

      return this.renderConnection(conn, from, to);
    }).join('\n');
  }

  /**
   * Renders a single connection
   */
  renderConnection(conn, from, to) {
    const x1 = from.x + from.width / 2;
    const y1 = from.y + from.height;
    const x2 = to.x + to.width / 2;
    const y2 = to.y;

    const midY = (y1 + y2) / 2;

    const isRetry = conn.type === 'retry';
    const strokeColor = isRetry ? '#f59e0b' : '#6b7280';
    const strokeClass = isRetry ? 'connection-retry' : 'connection-line';
    const marker = isRetry ? 'arrowhead-retry' : 'arrowhead';

    return `
      <g class="connection ${conn.type}">
        <!-- Connection line -->
        <path d="M ${x1} ${y1} L ${x1} ${midY} L ${x2} ${midY} L ${x2} ${y2}"
              class="${strokeClass}"
              marker-end="url(#${marker})"/>

        <!-- Label (if any) -->
        ${conn.label ? `
          <text x="${x1}" y="${midY - 5}" class="connection-label">
            ${this.escapeHtml(conn.label)}
          </text>
        ` : ''}
      </g>
    `;
  }

  /**
   * Formats duration for display
   */
  formatDuration(ms) {
    if (ms < 1000) {
      return `${Math.round(ms)}ms`;
    } else if (ms < 60000) {
      return `${(ms / 1000).toFixed(1)}s`;
    } else {
      const minutes = Math.floor(ms / 60000);
      const seconds = ((ms % 60000) / 1000).toFixed(0);
      return `${minutes}m${seconds}s`;
    }
  }

  /**
   * Escapes HTML special characters
   */
  escapeHtml(text) {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
  }
}

module.exports = { FlowDiagramRenderer };
