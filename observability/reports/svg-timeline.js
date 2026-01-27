/**
 * Generates SVG timeline visualization
 */
class SvgTimelineRenderer {
  constructor(config = {}) {
    this.config = {
      width: config.width || 1200,
      rowHeight: config.rowHeight || 60,
      headerHeight: config.headerHeight || 80,
      labelWidth: config.labelWidth || 250,
      indentWidth: config.indentWidth || 20,
      ...config
    };

    this.colors = {
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6',
      generation: '#8b5cf6',
      validation: '#10b981',
      feedback: '#f59e0b',
      attempt: '#6366f1'
    };
  }

  /**
   * Renders complete SVG timeline
   */
  render(timeline) {
    const { rows, timeScale, metadata, milestones } = timeline;

    const height = this.config.headerHeight + (rows.length * this.config.rowHeight) + 40;
    const timelineWidth = this.config.width - this.config.labelWidth;

    // Calculate pixels per millisecond with minimum scale to prevent extreme zoom
    // For very short durations, cap the zoom to keep everything visible
    const rawPxPerMs = timelineWidth / timeScale.totalDuration;
    const maxPxPerMs = 10; // Maximum 10 pixels per millisecond (prevents off-screen elements)
    const pxPerMs = Math.min(rawPxPerMs, maxPxPerMs);

    // If we're limiting the scale, adjust the effective width
    const effectiveWidth = Math.min(timelineWidth, timeScale.totalDuration * pxPerMs);

    // Use viewBox for responsive scaling instead of fixed width
    let svg = `<svg viewBox="0 0 ${this.config.width} ${height}" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" class="workflow-timeline" data-session-id="${metadata.sessionId || ''}">`;

    // Add styles
    svg += this.renderStyles();

    // Add time axis
    svg += this.renderTimeAxis(timeScale, pxPerMs);

    // Add rows
    rows.forEach((row, index) => {
      const y = this.config.headerHeight + (index * this.config.rowHeight);
      svg += this.renderRow(row, y, pxPerMs);
    });

    // Add milestones
    svg += this.renderMilestones(milestones, pxPerMs, height);

    svg += '</svg>';
    return svg;
  }

  /**
   * Renders embedded CSS styles
   */
  renderStyles() {
    return `
      <defs>
        <style>
          .timeline-row { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
          .row-label { font-size: 14px; fill: #374151; }
          .duration-label { font-size: 12px; fill: white; font-weight: 600; }
          .time-marker { font-size: 11px; fill: #6b7280; }
          .time-axis-line { stroke: #d1d5db; stroke-width: 1; }
          .duration-block { cursor: pointer; transition: opacity 0.2s; }
          .duration-block:hover { opacity: 0.8; }
          .status-icon { font-size: 16px; }
          .milestone-line { stroke: #9ca3af; stroke-width: 1; stroke-dasharray: 4,4; }
          .milestone-label { font-size: 10px; fill: #6b7280; }
        </style>
      </defs>
    `;
  }

  /**
   * Renders time axis with markers
   */
  renderTimeAxis(timeScale, pxPerMs) {
    const { markers } = timeScale;
    const yPos = this.config.headerHeight - 20;

    let svg = '<g class="time-axis">';

    // Draw axis line
    svg += `<line x1="${this.config.labelWidth}" y1="${yPos}" x2="${this.config.width}" y2="${yPos}" class="time-axis-line"/>`;

    // Draw markers
    markers.forEach(marker => {
      const x = this.config.labelWidth + (marker.offset * pxPerMs);

      // Vertical tick
      svg += `<line x1="${x}" y1="${yPos}" x2="${x}" y2="${yPos + 5}" class="time-axis-line"/>`;

      // Label
      svg += `<text x="${x}" y="${yPos - 5}" text-anchor="middle" class="time-marker">${marker.label}</text>`;
    });

    svg += '</g>';
    return svg;
  }

  /**
   * Renders a timeline row
   */
  renderRow(row, y, pxPerMs) {
    const x = this.config.labelWidth + (row.startOffset * pxPerMs);
    const width = Math.max(20, row.duration * pxPerMs); // Minimum 20px width for visibility
    const color = this.getRowColor(row);

    // Calculate label x position with indentation
    const labelX = 10 + (row.indentLevel * this.config.indentWidth);

    let svg = `<g class="timeline-row" data-type="${row.type}" data-status="${row.status}">`;

    // Row label with emoji and role badge
    const displayName = row.fullDisplayName || row.name;
    svg += `<text x="${labelX}" y="${y + 20}" class="row-label">${this.escapeHtml(displayName)}</text>`;

    // Role badge (shown below name if available)
    if (row.role && row.role !== 'Unknown Role') {
      svg += `<text x="${labelX}" y="${y + 35}" class="role-badge" font-size="11" fill="#6b7280">${this.escapeHtml(row.role)}</text>`;
    }

    // Duration block (rectangle) with data attributes for interactivity
    const hasError = row.error !== null && row.error !== undefined;
    const errorMessage = hasError ? this.escapeHtml(row.error.message || 'Error') : '';

    // Use agent color if available, otherwise fall back to type/status color
    const barColor = row.agentColor || color;

    svg += `<rect
      x="${x}"
      y="${y + 5}"
      width="${width}"
      height="40"
      fill="${barColor}"
      fill-opacity="0.85"
      stroke="${hasError ? '#dc2626' : row.agentColor || '#1f2937'}"
      stroke-width="${hasError ? '2' : '2'}"
      rx="4"
      class="duration-block${hasError ? ' has-error' : ''}"
      data-span-id="${row.spanId || ''}"
      data-row-name="${this.escapeHtml(displayName)}"
      data-duration="${row.duration}"
      data-status="${row.status}"
      data-has-error="${hasError}"
      data-error-message="${errorMessage}"
      role="button"
      tabindex="0"
      aria-label="${this.escapeHtml(displayName)}: ${this.formatDuration(row.duration)}, Status: ${row.status}${hasError ? ', Error: ' + errorMessage : ''}"
    >
      <title>${this.escapeHtml(displayName)}: ${this.formatDuration(row.duration)}${hasError ? ' - ' + errorMessage : ''}</title>
    </rect>`;

    // Add quality score badge on the bar if available
    if (row.hasQualityData && row.qualityScore !== null) {
      const badgeX = x + width - 25;
      const badgeY = y + 25;
      const scoreColor = row.qualityScoreClass === 'excellent' ? '#10b981' :
                         row.qualityScoreClass === 'good' ? '#f59e0b' : '#ef4444';

      svg += `<circle cx="${badgeX}" cy="${badgeY}" r="15" fill="white" stroke="${scoreColor}" stroke-width="2"/>`;
      svg += `<text x="${badgeX}" y="${badgeY + 5}" text-anchor="middle" font-size="11" font-weight="bold" fill="${scoreColor}">${row.qualityScore}</text>`;
    }

    // Duration label (if block is wide enough)
    if (width > 60) {
      svg += `<text
        x="${x + width/2}"
        y="${y + 30}"
        text-anchor="middle"
        class="duration-label"
      >${this.formatDuration(row.duration)}</text>`;
    } else if (width > 30) {
      // For smaller blocks, show duration without text
      svg += `<text
        x="${x + width/2}"
        y="${y + 30}"
        text-anchor="middle"
        class="duration-label"
        font-size="10"
      >${this.formatDuration(row.duration)}</text>`;
    }

    // Status icon
    svg += this.renderStatusIcon(row.statusIcon, row.status, x + width + 10, y + 25);

    // Event markers
    row.events.forEach(event => {
      svg += this.renderEventMarker(event, y, pxPerMs);
    });

    svg += '</g>';
    return svg;
  }

  /**
   * Renders status icon
   */
  renderStatusIcon(icon, status, x, y) {
    const color = this.colors[status] || '#6b7280';

    return `
      <circle cx="${x}" cy="${y}" r="14" fill="white" stroke="${color}" stroke-width="2"/>
      <text x="${x}" y="${y + 5}" text-anchor="middle" class="status-icon" fill="${color}">${icon}</text>
    `;
  }

  /**
   * Renders event marker
   */
  renderEventMarker(event, rowY, pxPerMs) {
    const x = this.config.labelWidth + (event.offset * pxPerMs);
    const y = rowY + 45;

    return `
      <circle cx="${x}" cy="${y}" r="4" fill="#6366f1">
        <title>${event.type}</title>
      </circle>
    `;
  }

  /**
   * Renders milestone markers across timeline
   */
  renderMilestones(milestones, pxPerMs, height) {
    let svg = '<g class="milestones">';

    milestones.forEach(milestone => {
      const x = this.config.labelWidth + (milestone.offset * pxPerMs);

      // Vertical dashed line
      svg += `<line
        x1="${x}"
        y1="${this.config.headerHeight}"
        x2="${x}"
        y2="${height - 20}"
        class="milestone-line"
      />`;

      // Label at bottom
      svg += `<text
        x="${x}"
        y="${height - 5}"
        text-anchor="middle"
        class="milestone-label"
      >${this.escapeHtml(milestone.label)}</text>`;
    });

    svg += '</g>';
    return svg;
  }

  /**
   * Gets color for a row based on type and status
   */
  getRowColor(row) {
    // Prefer type-based coloring for visual distinction
    if (this.colors[row.type]) {
      // Darken if error, lighten if warning
      if (row.status === 'error') {
        return this.colors.error;
      }
      return this.colors[row.type];
    }

    // Fall back to status-based coloring
    return this.colors[row.status] || this.colors.info;
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
    return text.replace(/[&<>"']/g, m => map[m]);
  }
}

module.exports = { SvgTimelineRenderer };
