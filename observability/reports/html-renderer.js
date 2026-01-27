const fs = require('fs').promises;
const path = require('path');
const { SvgTimelineRenderer } = require('./svg-timeline');
const { MetricsCalculator } = require('./metrics-calculator');
const { FlowDiagramRenderer } = require('./flow-diagram-renderer');

/**
 * Renders complete HTML timeline report
 */
class HtmlRenderer {
  constructor() {
    this.svgRenderer = new SvgTimelineRenderer();
    this.flowRenderer = new FlowDiagramRenderer();
    this.metricsCalculator = new MetricsCalculator();
  }

  /**
   * Renders timeline as complete HTML document
   */
  async render(timeline, outputPath) {
    // Calculate metrics
    const metrics = this.metricsCalculator.calculateMetrics(timeline);

    // Generate HTML
    const html = this.generateHtml(timeline, metrics);

    // Write to file
    await fs.writeFile(outputPath, html, 'utf-8');

    return outputPath;
  }

  /**
   * Generates complete HTML document
   */
  generateHtml(timeline, metrics) {
    const { metadata } = timeline;

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Workflow Timeline - ${this.escapeHtml(metadata.workflowId)}</title>
  ${this.renderStyles()}
</head>
<body>
  <!-- Skip Links for Screen Readers -->
  <a href="#main-timeline" class="skip-link">Skip to timeline</a>
  <a href="#metrics" class="skip-link">Skip to metrics</a>
  <a href="#details" class="skip-link">Skip to details</a>

  <div class="container">
    <header role="banner">
      ${this.renderHeader(timeline, metrics)}
    </header>

    <main id="main-content" role="main">
      <!-- View Switcher -->
      ${this.renderViewSwitcher()}

      <!-- Timeline View Container -->
      <div id="timeline-view" class="view-container active">
        <div class="timeline-container">
          <section id="main-timeline" class="timeline-main" aria-labelledby="timeline-heading">
            <h2 id="timeline-heading" class="visually-hidden">Workflow Timeline Visualization</h2>
            ${this.svgRenderer.render(timeline)}
          </section>

          <aside id="metrics" class="metrics-panel" role="complementary" aria-labelledby="metrics-heading">
            <h2 id="metrics-heading" class="visually-hidden">Performance Metrics</h2>
            ${this.renderMetricsPanel(metrics)}
          </aside>
        </div>
      </div>

      <!-- Flow Diagram View Container -->
      <div id="flow-view" class="view-container">
        <div class="flow-container">
          <section id="flow-diagram" class="flow-main" aria-labelledby="flow-heading">
            <h2 id="flow-heading" class="visually-hidden">Process Flow Diagram</h2>
            ${this.flowRenderer.render(timeline)}
          </section>

          <aside class="flow-legend" role="complementary">
            ${this.renderFlowLegend()}
          </aside>
        </div>
      </div>

      <section id="details" aria-labelledby="details-heading">
        <h2 id="details-heading" class="visually-hidden">Workflow Details</h2>
        ${this.renderDetailsSection(timeline, metrics)}
      </section>
    </main>
  </div>

  ${this.renderModal()}
  ${this.renderTooltip()}
  ${this.renderLiveRegion()}
  ${this.renderScripts(timeline)}
</body>
</html>`;
  }

  /**
   * Renders CSS styles
   */
  renderStyles() {
    return `<style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f9fafb;
      color: #111827;
      line-height: 1.5;
    }

    /* Accessibility - Skip Links */
    .skip-link {
      position: absolute;
      top: -40px;
      left: 0;
      background: #3b82f6;
      color: white;
      padding: 8px 16px;
      text-decoration: none;
      border-radius: 0 0 4px 0;
      font-weight: 600;
      z-index: 10000;
      transition: top 0.2s ease;
    }

    .skip-link:focus {
      top: 0;
      outline: 2px solid #1d4ed8;
      outline-offset: 2px;
    }

    /* Accessibility - Visually Hidden (for screen readers only) */
    .visually-hidden {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border-width: 0;
    }

    .container {
      max-width: 1600px;
      margin: 0 auto;
      padding: 20px;
    }

    .header {
      background: white;
      padding: 30px;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      margin-bottom: 20px;
      position: relative;
    }

    .back-link {
      position: absolute;
      left: 30px;
      top: 30px;
      color: #3b82f6;
      text-decoration: none;
      font-size: 14px;
      font-weight: 500;
      padding: 6px 12px;
      border-radius: 6px;
      transition: all 200ms ease;
    }

    .back-link:hover {
      background: #eff6ff;
      color: #2563eb;
    }

    .header h1 {
      font-size: 28px;
      color: #111827;
      margin-bottom: 10px;
      margin-top: 10px;
    }

    .header .task {
      font-size: 16px;
      color: #6b7280;
      margin-bottom: 15px;
    }

    .header .metadata {
      display: flex;
      gap: 30px;
      font-size: 14px;
      color: #6b7280;
      flex-wrap: wrap;
    }

    .metadata-item {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .metadata-label {
      font-weight: 600;
      color: #374151;
    }

    .status-badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
    }

    .status-badge.success {
      background: #d1fae5;
      color: #065f46;
    }

    .status-badge.error {
      background: #fee2e2;
      color: #991b1b;
    }

    .timeline-container {
      display: flex;
      gap: 20px;
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      margin-bottom: 20px;
    }

    .timeline-main {
      flex: 1;
      overflow-x: auto;
      min-width: 0;
    }

    .workflow-timeline {
      display: block;
      width: 100%;
      height: auto;
      max-width: 100%;
    }

    .metrics-panel {
      width: 320px;
      flex-shrink: 0;
      border-left: 2px solid #e5e7eb;
      padding-left: 20px;
    }

    .metrics-panel h2 {
      font-size: 20px;
      margin-bottom: 20px;
      color: #111827;
    }

    .metric {
      margin-bottom: 20px;
    }

    .metric-label {
      font-size: 12px;
      color: #6b7280;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }

    .metric-value {
      font-size: 24px;
      font-weight: 700;
      color: #111827;
    }

    .metric-subvalue {
      font-size: 14px;
      color: #6b7280;
      margin-top: 2px;
    }

    .duration-chart {
      margin-top: 30px;
    }

    .duration-chart h3 {
      font-size: 14px;
      color: #374151;
      margin-bottom: 15px;
    }

    .duration-bar {
      margin-bottom: 12px;
    }

    .duration-bar-label {
      font-size: 12px;
      color: #4b5563;
      margin-bottom: 4px;
      display: flex;
      justify-content: space-between;
    }

    .duration-bar-bg {
      width: 100%;
      height: 24px;
      background: #f3f4f6;
      border-radius: 4px;
      overflow: hidden;
    }

    .duration-bar-fill {
      height: 100%;
      border-radius: 4px;
      transition: width 0.3s ease;
    }

    .duration-bar-fill.success { background: #10b981; }
    .duration-bar-fill.warning { background: #f59e0b; }
    .duration-bar-fill.error { background: #ef4444; }
    .duration-bar-fill.info { background: #3b82f6; }

    .details-section {
      background: white;
      padding: 30px;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .details-section h2 {
      font-size: 20px;
      margin-bottom: 20px;
      color: #111827;
    }

    .details-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
    }

    .detail-card {
      padding: 20px;
      background: #f9fafb;
      border-radius: 6px;
      border: 1px solid #e5e7eb;
    }

    .detail-card h3 {
      font-size: 14px;
      color: #6b7280;
      margin-bottom: 10px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .detail-card .value {
      font-size: 18px;
      font-weight: 600;
      color: #111827;
    }

    .quality-progression {
      margin-top: 30px;
    }

    .quality-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
      border-bottom: 1px solid #e5e7eb;
    }

    .quality-item:last-child {
      border-bottom: none;
    }

    .quality-score {
      font-weight: 600;
    }

    .quality-score.passed {
      color: #10b981;
    }

    .quality-score.failed {
      color: #ef4444;
    }

    /* Quality Progression Widget */
    .quality-progression-widget {
      background: #f9fafb;
      border: 2px solid #e5e7eb;
      border-radius: 8px;
      padding: 20px;
      margin: 20px 0;
    }

    .quality-progression-widget h3 {
      font-size: 16px;
      font-weight: 600;
      color: #111827;
      margin-bottom: 16px;
    }

    .score-timeline {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      margin: 20px 0;
      flex-wrap: wrap;
    }

    .score-node {
      position: relative;
      text-align: center;
      flex-shrink: 0;
    }

    .score-value {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      font-weight: bold;
      margin: 0 auto 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .score-node.excellent .score-value {
      background: #10b981;
      color: white;
    }

    .score-node.good .score-value {
      background: #f59e0b;
      color: white;
    }

    .score-node.needs-work .score-value {
      background: #ef4444;
      color: white;
    }

    .score-arrow {
      font-size: 24px;
      color: #6b7280;
      padding: 0 10px;
      align-self: center;
    }

    .attempt-label {
      font-size: 12px;
      color: #6b7280;
      text-align: center;
    }

    .improvement-summary {
      text-align: center;
      margin-top: 16px;
      font-size: 14px;
      color: #374151;
    }

    .improvement-delta {
      display: inline-block;
      padding: 4px 12px;
      background: #d1fae5;
      color: #065f46;
      border-radius: 12px;
      font-weight: 600;
      margin: 0 4px;
    }

    .improvement-delta.negative {
      background: #fee2e2;
      color: #991b1b;
    }

    /* Validation Feedback Display */
    .validation-feedback-section {
      background: #fef3c7;
      border-left: 4px solid #f59e0b;
      border-radius: 6px;
      padding: 16px;
      margin: 16px 0;
    }

    .validation-feedback-section h3 {
      font-size: 14px;
      font-weight: 600;
      color: #92400e;
      margin-bottom: 12px;
    }

    .feedback-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }

    .feedback-item {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      margin-bottom: 12px;
      padding: 8px;
      background: white;
      border-radius: 4px;
    }

    .feedback-item:last-child {
      margin-bottom: 0;
    }

    .feedback-icon {
      font-size: 18px;
      flex-shrink: 0;
    }

    .feedback-text {
      flex: 1;
      color: #374151;
      line-height: 1.5;
    }

    .no-feedback {
      color: #065f46;
      background: #d1fae5;
      border-left-color: #10b981;
      padding: 12px;
      margin: 0;
      border-radius: 4px;
    }

    /* View Switcher */
    .view-switcher {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
      padding: 20px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .view-btn {
      flex: 1;
      padding: 12px 24px;
      background: #f3f4f6;
      border: 2px solid #d1d5db;
      border-radius: 8px;
      font-size: 15px;
      font-weight: 600;
      color: #6b7280;
      cursor: pointer;
      transition: all 200ms ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }

    .view-btn:hover {
      background: #e5e7eb;
      border-color: #9ca3af;
      color: #374151;
    }

    .view-btn.active {
      background: #3b82f6;
      border-color: #3b82f6;
      color: white;
    }

    .view-btn.active:hover {
      background: #2563eb;
      border-color: #2563eb;
    }

    /* View Containers */
    .view-container {
      display: none;
      animation: fadeIn 0.3s ease;
    }

    .view-container.active {
      display: block;
    }

    @keyframes fadeIn {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    /* Flow Diagram Container */
    .flow-container {
      display: flex;
      gap: 20px;
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .flow-main {
      flex: 1;
      overflow-x: auto;
      min-width: 0;
      display: flex;
      justify-content: center;
      align-items: flex-start;
    }

    .flow-diagram {
      display: block;
      max-width: 100%;
      height: auto;
    }

    .flow-legend {
      width: 250px;
      flex-shrink: 0;
      border-left: 2px solid #e5e7eb;
      padding-left: 20px;
    }

    .flow-legend h3 {
      font-size: 16px;
      font-weight: 600;
      color: #111827;
      margin-bottom: 16px;
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;
      font-size: 13px;
      color: #4b5563;
    }

    .legend-icon {
      width: 40px;
      height: 24px;
      flex-shrink: 0;
    }

    .legend-box {
      width: 100%;
      height: 100%;
      border-radius: 4px;
    }

    .legend-diamond {
      width: 24px;
      height: 24px;
      background: #fef3c7;
      border: 2px solid #f59e0b;
      transform: rotate(45deg);
    }

    .legend-line {
      width: 100%;
      height: 2px;
      background: #6b7280;
    }

    .legend-line.dashed {
      border-top: 2px dashed #f59e0b;
      background: none;
    }

    @media (max-width: 1024px) {
      .timeline-container {
        flex-direction: column;
      }

      .metrics-panel {
        width: 100%;
        border-left: none;
        border-top: 2px solid #e5e7eb;
        padding-left: 0;
        padding-top: 20px;
      }

      .flow-container {
        flex-direction: column;
      }

      .flow-legend {
        width: 100%;
        border-left: none;
        border-top: 2px solid #e5e7eb;
        padding-left: 0;
        padding-top: 20px;
      }

      .view-switcher {
        flex-direction: column;
      }
    }

    /* Modal styles */
    .modal {
      display: none;
      position: fixed;
      z-index: 1000;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.5);
      animation: fadeIn 0.2s ease;
    }

    .modal.active {
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .modal-content {
      background-color: white;
      border-radius: 12px;
      max-width: 900px;
      max-height: 90vh;
      width: 90%;
      overflow: hidden;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
      display: flex;
      flex-direction: column;
    }

    .modal-header {
      padding: 20px 24px;
      border-bottom: 1px solid #e5e7eb;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .modal-header h2 {
      font-size: 20px;
      font-weight: 600;
      color: #111827;
      margin: 0;
    }

    .modal-close {
      background: none;
      border: none;
      font-size: 24px;
      color: #6b7280;
      cursor: pointer;
      padding: 4px 8px;
      line-height: 1;
      border-radius: 4px;
    }

    .modal-close:hover {
      background-color: #f3f4f6;
      color: #111827;
    }

    .modal-body {
      padding: 24px;
      overflow-y: auto;
      flex: 1;
    }

    .modal-section {
      margin-bottom: 24px;
    }

    .modal-section:last-child {
      margin-bottom: 0;
    }

    .modal-section h3 {
      font-size: 14px;
      font-weight: 600;
      color: #374151;
      margin-bottom: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .copy-btn {
      background: #f3f4f6;
      border: 1px solid #d1d5db;
      border-radius: 4px;
      padding: 4px 8px;
      font-size: 12px;
      color: #374151;
      cursor: pointer;
      margin-left: auto;
    }

    .copy-btn:hover {
      background: #e5e7eb;
    }

    .data-block {
      background: #f9fafb;
      border: 1px solid #e5e7eb;
      border-radius: 6px;
      padding: 16px;
      font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
      font-size: 13px;
      line-height: 1.6;
      overflow-x: auto;
      white-space: pre-wrap;
      word-wrap: break-word;
    }

    .metadata-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
    }

    .metadata-item-modal {
      background: #f9fafb;
      border: 1px solid #e5e7eb;
      border-radius: 6px;
      padding: 12px;
    }

    .metadata-item-modal .label {
      font-size: 12px;
      color: #6b7280;
      margin-bottom: 4px;
    }

    .metadata-item-modal .value {
      font-size: 14px;
      font-weight: 600;
      color: #111827;
    }

    .error-block {
      background: #fee2e2;
      border: 1px solid #fecaca;
      border-radius: 6px;
      padding: 16px;
      color: #991b1b;
    }

    .loading {
      text-align: center;
      padding: 40px;
      color: #6b7280;
    }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    /* Tab Navigation */
    .modal-tabs {
      display: flex;
      border-bottom: 1px solid #e5e7eb;
      padding: 0 24px;
      background: #f9fafb;
    }

    .modal-tab {
      padding: 12px 20px;
      background: none;
      border: none;
      border-bottom: 2px solid transparent;
      font-size: 14px;
      font-weight: 500;
      color: #6b7280;
      cursor: pointer;
      transition: all 200ms ease;
    }

    .modal-tab:hover {
      color: #374151;
      background: rgba(59, 130, 246, 0.05);
    }

    .modal-tab.active {
      color: #3b82f6;
      border-bottom-color: #3b82f6;
    }

    .modal-tab-content {
      display: none;
    }

    .modal-tab-content.active {
      display: block;
    }

    /* Prompt XML Display */
    .prompt-xml-container {
      background: #1f2937;
      border-radius: 8px;
      padding: 0;
      max-height: 500px;
      overflow: auto;
      margin: 16px 0;
      border: 1px solid #374151;
      position: relative;
    }

    .prompt-xml-header {
      position: sticky;
      top: 0;
      background: #111827;
      padding: 8px 16px;
      border-bottom: 1px solid #374151;
      display: flex;
      align-items: center;
      justify-content: space-between;
      z-index: 10;
    }

    .prompt-xml-header-title {
      font-size: 12px;
      font-weight: 600;
      color: #9ca3af;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .prompt-xml-header-actions {
      display: flex;
      gap: 8px;
    }

    .xml-action-btn {
      background: #374151;
      border: 1px solid #4b5563;
      color: #d1d5db;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 11px;
      cursor: pointer;
      transition: all 150ms;
    }

    .xml-action-btn:hover {
      background: #4b5563;
      color: #fff;
    }

    .prompt-xml-content {
      font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
      font-size: 13px;
      line-height: 1.8;
      color: #e5e7eb;
      white-space: pre;
      padding: 16px;
      counter-reset: line;
    }

    .prompt-xml-content.wrap {
      white-space: pre-wrap;
      word-wrap: break-word;
    }

    .prompt-xml-content.line-numbers {
      padding-left: 60px;
    }

    .prompt-xml-content.line-numbers::before {
      position: absolute;
      left: 0;
      width: 50px;
      padding: 16px 8px;
      color: #6b7280;
      font-size: 11px;
      text-align: right;
      border-right: 1px solid #374151;
      counter-increment: line;
      content: counter(line);
      white-space: pre;
    }

    /* Generate line numbers for each line */
    .xml-line {
      display: block;
      position: relative;
    }

    .xml-line::before {
      position: absolute;
      left: -50px;
      width: 40px;
      text-align: right;
      color: #6b7280;
      font-size: 11px;
      user-select: none;
      content: attr(data-line);
    }

    /* Simple XML Syntax Highlighting */
    .xml-tag {
      color: #8b5cf6;
    }

    .xml-attr {
      color: #3b82f6;
    }

    .xml-value {
      color: #10b981;
    }

    .xml-text {
      color: #e5e7eb;
    }

    .xml-comment {
      color: #6b7280;
      font-style: italic;
    }

    /* Action Buttons */
    .prompt-actions {
      display: flex;
      gap: 12px;
      margin-top: 16px;
    }

    .btn-primary {
      background: #3b82f6;
      color: white;
      padding: 10px 16px;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 200ms ease;
    }

    .btn-primary:hover {
      background: #2563eb;
    }

    .btn-primary.success {
      background: #10b981;
    }

    .btn-primary.copying {
      opacity: 0.7;
      cursor: wait;
    }

    .btn-secondary {
      background: white;
      color: #3b82f6;
      padding: 10px 16px;
      border: 2px solid #3b82f6;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 200ms ease;
    }

    .btn-secondary:hover {
      background: #eff6ff;
    }

    @media print {
      body {
        background: white;
      }

      .container {
        max-width: none;
        padding: 0;
      }

      .timeline-container {
        box-shadow: none;
        break-inside: avoid;
      }

      .modal {
        display: none !important;
      }

      .tooltip {
        display: none !important;
      }
    }

    /* Tooltip Styles */
    .tooltip {
      position: fixed;
      background-color: rgba(17, 24, 39, 0.95);
      color: white;
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 13px;
      line-height: 1.5;
      pointer-events: none;
      z-index: 2000;
      max-width: 350px;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
      opacity: 0;
      transition: opacity 0.15s ease;
      backdrop-filter: blur(4px);
    }

    .tooltip.visible {
      opacity: 1;
    }

    .tooltip-title {
      font-weight: 600;
      font-size: 14px;
      margin-bottom: 8px;
      color: #60a5fa;
    }

    .tooltip-row {
      display: flex;
      justify-content: space-between;
      margin: 4px 0;
      gap: 16px;
    }

    .tooltip-label {
      color: #9ca3af;
      font-size: 12px;
    }

    .tooltip-value {
      color: white;
      font-weight: 500;
      text-align: right;
    }

    .tooltip-status {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
    }

    .tooltip-status.success {
      background-color: #10b981;
      color: white;
    }

    .tooltip-status.warning {
      background-color: #f59e0b;
      color: white;
    }

    .tooltip-status.error {
      background-color: #ef4444;
      color: white;
    }

    .tooltip-status.info {
      background-color: #3b82f6;
      color: white;
    }

    .tooltip-divider {
      height: 1px;
      background-color: rgba(255, 255, 255, 0.2);
      margin: 8px 0;
    }

    .duration-block {
      pointer-events: all;
    }

    .duration-block:hover {
      opacity: 0.85;
      cursor: pointer;
      stroke: #3b82f6;
      stroke-width: 2;
    }

    .duration-block:focus {
      outline: 2px solid #3b82f6;
      outline-offset: 2px;
    }
  </style>`;
  }

  /**
   * Renders view switcher buttons
   */
  renderViewSwitcher() {
    return `
    <div class="view-switcher">
      <button class="view-btn active" id="timeline-view-btn" onclick="switchView('timeline')" aria-label="Switch to timeline view">
        📊 Timeline View
      </button>
      <button class="view-btn" id="flow-view-btn" onclick="switchView('flow')" aria-label="Switch to flow diagram view">
        🔀 Process Flow
      </button>
    </div>
    `;
  }

  /**
   * Renders flow diagram legend
   */
  renderFlowLegend() {
    return `
    <h3>Legend</h3>

    <div class="legend-item">
      <div class="legend-icon">
        <div class="legend-box" style="background: #3b82f6; opacity: 0.85;"></div>
      </div>
      <span>🤖 Prompt Generator</span>
    </div>

    <div class="legend-item">
      <div class="legend-icon">
        <div class="legend-box" style="background: #10b981; opacity: 0.85;"></div>
      </div>
      <span>✅ Quality Validator</span>
    </div>

    <div class="legend-item">
      <div class="legend-icon">
        <div class="legend-box" style="background: #8b5cf6; opacity: 0.85;"></div>
      </div>
      <span>🔍 Feedback Analyzer</span>
    </div>

    <div class="legend-item">
      <div class="legend-icon">
        <div class="legend-diamond"></div>
      </div>
      <span>Quality Decision</span>
    </div>

    <div class="legend-item">
      <div class="legend-icon">
        <div class="legend-line"></div>
      </div>
      <span>Data Flow</span>
    </div>

    <div class="legend-item">
      <div class="legend-icon">
        <div class="legend-line dashed"></div>
      </div>
      <span>Retry Path</span>
    </div>

    <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #e5e7eb;">
      <h3 style="margin-bottom: 12px;">Quality Scores</h3>

      <div class="legend-item">
        <div style="width: 24px; height: 24px; border-radius: 50%; background: #10b981; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 11px;">90</div>
        <span>🟢 Excellent (90+)</span>
      </div>

      <div class="legend-item">
        <div style="width: 24px; height: 24px; border-radius: 50%; background: #f59e0b; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 11px;">75</div>
        <span>🟡 Good (70-89)</span>
      </div>

      <div class="legend-item">
        <div style="width: 24px; height: 24px; border-radius: 50%; background: #ef4444; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 11px;">60</div>
        <span>🔴 Needs Work (<70)</span>
      </div>
    </div>

    <div style="margin-top: 24px; padding: 12px; background: #f9fafb; border-radius: 6px; font-size: 12px; color: #6b7280;">
      <strong style="color: #374151;">Tip:</strong> Click on any agent node to view detailed information, quality scores, and validation feedback.
    </div>
    `;
  }

  /**
   * Renders header section
   */
  renderHeader(timeline, metrics) {
    const { metadata, sessionId, traceId } = timeline;

    return `
    <div class="header">
      <a href="/index.html?from=report" class="back-link">← Back to Explorer</a>
      <h1>${this.escapeHtml(metadata.workflowId)}</h1>
      <div class="task">${this.escapeHtml(metadata.task)}</div>

      <div class="metadata">
        <div class="metadata-item">
          <span class="metadata-label">Session ID:</span>
          <code>${sessionId}</code>
        </div>
        <div class="metadata-item">
          <span class="metadata-label">Start Time:</span>
          <span>${metadata.startTime.toLocaleString()}</span>
        </div>
        <div class="metadata-item">
          <span class="metadata-label">Duration:</span>
          <span>${metrics.totalDuration}</span>
        </div>
        <div class="metadata-item">
          <span class="metadata-label">Status:</span>
          <span class="status-badge ${metadata.status}">${metadata.status.toUpperCase()}</span>
        </div>
      </div>
    </div>`;
  }

  /**
   * Renders metrics panel
   */
  renderMetricsPanel(metrics) {
    return `
    <h2>Metrics</h2>

    <div class="metric" role="group" aria-label="Total duration metric">
      <div class="metric-label" id="metric-duration-label">Total Duration</div>
      <div class="metric-value" aria-labelledby="metric-duration-label">${metrics.totalDuration}</div>
    </div>

    <div class="metric" role="group" aria-label="Number of steps metric">
      <div class="metric-label" id="metric-steps-label">Number of Steps</div>
      <div class="metric-value" aria-labelledby="metric-steps-label">${metrics.numberOfSteps}</div>
    </div>

    <div class="metric" role="group" aria-label="Success rate metric">
      <div class="metric-label" id="metric-success-label">Success Rate</div>
      <div class="metric-value" aria-labelledby="metric-success-label">${metrics.successRate.percentage}%</div>
      <div class="metric-subvalue" aria-label="${metrics.successRate.successful} successful out of ${metrics.successRate.total} total steps">${metrics.successRate.successful} of ${metrics.successRate.total} steps</div>
    </div>

    <div class="metric" role="group" aria-label="Bottleneck metric">
      <div class="metric-label" id="metric-bottleneck-label">Bottleneck</div>
      <div class="metric-value" aria-labelledby="metric-bottleneck-label">${this.escapeHtml(metrics.bottleneck.name)}</div>
      <div class="metric-subvalue" aria-label="Bottleneck duration ${metrics.bottleneck.duration}, which is ${metrics.bottleneck.percentage} percent of total time">${metrics.bottleneck.duration} (${metrics.bottleneck.percentage}%)</div>
    </div>

    ${this.renderDurationChart(metrics.spanComparison)}

    ${metrics.qualityProgression.length > 0 ? this.renderQualityProgression(metrics.qualityProgression) : ''}
    `;
  }

  /**
   * Renders duration comparison chart
   */
  renderDurationChart(spans) {
    if (spans.length === 0) return '';

    const topSpans = spans.slice(0, 5); // Show top 5

    return `
    <div class="duration-chart">
      <h3>Step Durations</h3>
      ${topSpans.map(span => `
        <div class="duration-bar">
          <div class="duration-bar-label">
            <span>${this.escapeHtml(span.name)}</span>
            <span>${span.durationFormatted}</span>
          </div>
          <div class="duration-bar-bg">
            <div class="duration-bar-fill ${span.status}" style="width: ${span.normalized}%"></div>
          </div>
        </div>
      `).join('')}
    </div>`;
  }

  /**
   * Renders quality progression
   */
  renderQualityProgression(progression) {
    return `
    <div class="quality-progression">
      <h3>Quality Progression</h3>
      ${progression.map(p => `
        <div class="quality-item">
          <span>Attempt #${p.attempt}</span>
          <span class="quality-score ${p.passed ? 'passed' : 'failed'}">
            ${p.score}/100 ${p.passed ? '✓' : '✗'}
          </span>
        </div>
      `).join('')}
    </div>`;
  }

  /**
   * Renders details section
   */
  renderDetailsSection(timeline, metrics) {
    return `
    <div class="details-section">
      <h2>Summary</h2>

      <div class="details-grid">
        <div class="detail-card">
          <h3>Status Breakdown</h3>
          <div class="value">
            ✓ ${metrics.statusBreakdown.success} success<br>
            ⚠ ${metrics.statusBreakdown.warning} warning<br>
            ✗ ${metrics.statusBreakdown.error} error<br>
            ℹ ${metrics.statusBreakdown.info} info
          </div>
        </div>

        <div class="detail-card">
          <h3>Average Step Duration</h3>
          <div class="value">${metrics.avgStepDuration.formatted}</div>
        </div>

        <div class="detail-card">
          <h3>Workflow Pattern</h3>
          <div class="value">${this.escapeHtml(timeline.metadata.workflowPattern)}</div>
        </div>

        ${metrics.numberOfAttempts > 0 ? `
        <div class="detail-card">
          <h3>Number of Attempts</h3>
          <div class="value">${metrics.numberOfAttempts}</div>
        </div>` : ''}
      </div>
    </div>`;
  }

  /**
   * Renders modal for viewing span data
   */
  renderModal() {
    return `
    <div id="spanModal" class="modal" role="dialog" aria-labelledby="modalTitle" aria-modal="true">
      <div class="modal-content">
        <div class="modal-header">
          <h2 id="modalTitle">Span Details</h2>
          <button class="modal-close" aria-label="Close" onclick="closeModal()">&times;</button>
        </div>
        <div class="modal-body" id="modalBody">
          <div class="loading">Loading...</div>
        </div>
      </div>
    </div>`;
  }

  /**
   * Renders tooltip element
   */
  renderTooltip() {
    return `
    <div id="spanTooltip" class="tooltip" role="tooltip">
      <div id="tooltipContent"></div>
    </div>`;
  }

  /**
   * Renders live region for screen reader announcements
   */
  renderLiveRegion() {
    return `
    <div id="announcer" class="visually-hidden" role="status" aria-live="polite" aria-atomic="true"></div>`;
  }

  /**
   * Renders client-side JavaScript
   */
  renderScripts(timeline) {
    // Load output file content if available
    const fs = require('fs');
    const path = require('path');
    let outputContent = null;

    if (timeline.metadata['workflow.output_path']) {
      try {
        const outputPath = path.join(process.cwd(), timeline.metadata['workflow.output_path']);
        outputContent = fs.readFileSync(outputPath, 'utf-8');
      } catch (error) {
        console.warn('Could not load output file:', error.message);
      }
    }

    // Embed timeline data for client-side access
    const timelineData = JSON.stringify({
      sessionId: timeline.sessionId,
      startTime: timeline.metadata.startTime,
      task: timeline.metadata.task || 'Unknown Task',
      outputPath: timeline.metadata['workflow.output_path'] || null,
      outputContent: outputContent,
      rows: timeline.rows.map(row => ({
        spanId: row.spanId,
        name: row.name,
        displayName: row.displayName,
        fullDisplayName: row.fullDisplayName,
        role: row.role,
        emoji: row.emoji,
        agentColor: row.agentColor,
        type: row.type,
        status: row.status,
        duration: row.duration,
        startOffset: row.startOffset,
        attributes: row.attributes || {},
        error: row.error,
        attemptNumber: row.attemptNumber,
        hasQualityData: row.hasQualityData,
        qualityScore: row.qualityScore,
        qualityScoreClass: row.qualityScoreClass,
        qualityScoreEmoji: row.qualityScoreEmoji,
        isValid: row.isValid,
        feedback: row.feedback || []
      }))
    });

    return `<script>
    const TIMELINE_DATA = ${timelineData};

    // Helper: Render quality progression widget
    function renderQualityProgression(rowData) {
      // Find all rows with quality scores from the same workflow
      const attemptsWithScores = TIMELINE_DATA.rows
        .filter(r => r.hasQualityData && r.qualityScore !== null && r.attemptNumber)
        .sort((a, b) => a.attemptNumber - b.attemptNumber);

      if (attemptsWithScores.length === 0) {
        return '';
      }

      const scores = attemptsWithScores.map(r => ({
        attempt: r.attemptNumber,
        score: r.qualityScore,
        scoreClass: r.qualityScoreClass,
        scoreEmoji: r.qualityScoreEmoji
      }));

      const firstScore = scores[0].score;
      const lastScore = scores[scores.length - 1].score;
      const improvement = lastScore - firstScore;
      const improvementClass = improvement >= 0 ? '' : 'negative';

      return \`
        <div class="quality-progression-widget">
          <h3>Quality Progression</h3>
          <div class="score-timeline">
            \${scores.map((s, i) => \`
              <div class="score-node \${s.scoreClass}">
                <div class="score-value">\${s.score}</div>
                <div class="attempt-label">Attempt \${s.attempt}</div>
              </div>
              \${i < scores.length - 1 ? '<div class="score-arrow">→</div>' : ''}
            \`).join('')}
          </div>
          <div class="improvement-summary">
            <span class="improvement-delta \${improvementClass}">\${improvement >= 0 ? '+' : ''}\${improvement}</span>
            improvement over \${scores.length} attempt\${scores.length > 1 ? 's' : ''}
          </div>
        </div>
      \`;
    }

    // Helper: Render validation feedback
    function renderValidationFeedback(rowData, attemptNumber) {
      if (!rowData.feedback || rowData.feedback.length === 0) {
        return '<div class="no-feedback">✅ No issues found</div>';
      }

      return \`
        <div class="validation-feedback-section">
          <h3>⚠️ Validation Feedback - Attempt \${attemptNumber || '?'}</h3>
          <ul class="feedback-list">
            \${rowData.feedback.map(item => \`
              <li class="feedback-item">
                <span class="feedback-icon">⚠️</span>
                <span class="feedback-text">\${escapeHtml(item)}</span>
              </li>
            \`).join('')}
          </ul>
        </div>
      \`;
    }

    // Helper: Render agent information
    function renderAgentInfo(rowData) {
      if (!rowData.displayName) return '';

      return \`
        <div class="modal-section">
          <h3>🤖 Agent Information</h3>
          <div class="metadata-grid">
            <div class="metadata-item-modal">
              <div class="label">Name</div>
              <div class="value">\${escapeHtml(rowData.fullDisplayName || rowData.displayName)}</div>
            </div>
            \${rowData.role ? \`
              <div class="metadata-item-modal">
                <div class="label">Role</div>
                <div class="value">\${escapeHtml(rowData.role)}</div>
              </div>
            \` : ''}
            \${rowData.attemptNumber ? \`
              <div class="metadata-item-modal">
                <div class="label">Attempt</div>
                <div class="value">#\${rowData.attemptNumber}</div>
              </div>
            \` : ''}
          </div>
        </div>
      \`;
    }

    // View switching functionality
    function switchView(viewName) {
      // Hide all views
      document.querySelectorAll('.view-container').forEach(view => {
        view.classList.remove('active');
      });

      // Remove active class from all buttons
      document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.remove('active');
      });

      // Show selected view
      const selectedView = document.getElementById(viewName + '-view');
      if (selectedView) {
        selectedView.classList.add('active');
      }

      // Activate selected button
      const selectedBtn = document.getElementById(viewName + '-view-btn');
      if (selectedBtn) {
        selectedBtn.classList.add('active');
      }

      // Save preference to localStorage
      localStorage.setItem('timeline-view-preference', viewName);

      // Announce change for screen readers
      announce(\`Switched to \${viewName === 'timeline' ? 'timeline' : 'process flow'} view\`);

      // Update URL hash
      window.location.hash = viewName;
    }

    // Accessibility - Live region announcer
    function announce(message) {
      const announcer = document.getElementById('announcer');
      announcer.textContent = message;
      // Clear after announcement to allow repeated announcements
      setTimeout(() => {
        announcer.textContent = '';
      }, 1000);
    }

    // Focus management
    let lastFocusedElement = null;

    // Modal functions
    function openModal(triggerElement) {
      // Store the element that triggered the modal
      lastFocusedElement = triggerElement || document.activeElement;

      const modal = document.getElementById('spanModal');
      modal.classList.add('active');

      // Force display as backup (in case CSS doesn't work)
      modal.style.display = 'flex';

      document.body.style.overflow = 'hidden';

      // Hide tooltip when modal opens
      const tooltip = document.getElementById('spanTooltip');
      if (tooltip) {
        tooltip.classList.remove('visible');
      }

      // Focus the modal close button for screen readers
      const closeButton = modal.querySelector('.modal-close');
      if (closeButton) {
        setTimeout(() => closeButton.focus(), 100);
      }

      announce('Modal opened. Press Escape to close.');
    }

    function closeModal() {
      const modal = document.getElementById('spanModal');
      modal.classList.remove('active');
      modal.style.display = '';  // Reset inline style

      document.body.style.overflow = '';
      announce('Modal closed');

      // Keep tooltip hidden after closing modal
      const tooltip = document.getElementById('spanTooltip');
      if (tooltip) {
        tooltip.classList.remove('visible');
      }

      // Restore focus to the element that opened the modal
      if (lastFocusedElement && lastFocusedElement.focus) {
        setTimeout(() => lastFocusedElement.focus(), 100);
      }
    }

    function showModalContent(html) {
      document.getElementById('modalBody').innerHTML = html;
      announce('Span details loaded');
    }

    function copyToClipboard(text, button) {
      const originalHTML = button.innerHTML;
      button.innerHTML = '⏳ Copying...';
      button.classList.add('copying');
      button.disabled = true;

      navigator.clipboard.writeText(text).then(() => {
        button.innerHTML = '✓ Copied!';
        button.classList.remove('copying');
        button.classList.add('success');
        setTimeout(() => {
          button.innerHTML = originalHTML;
          button.classList.remove('success');
          button.disabled = false;
        }, 2000);
      }).catch(err => {
        console.error('Copy failed:', err);
        button.innerHTML = '✗ Failed';
        button.classList.remove('copying');
        setTimeout(() => {
          button.innerHTML = originalHTML;
          button.disabled = false;
        }, 2000);
      });
    }

    function switchTab(tabName) {
      // Hide all tab contents
      document.querySelectorAll('.modal-tab-content').forEach(tab => {
        tab.classList.remove('active');
        tab.style.display = 'none';  // Explicitly hide - overrides inline styles
      });

      // Remove active class from all tabs
      document.querySelectorAll('.modal-tab').forEach(tab => {
        tab.classList.remove('active');
      });

      // Show selected tab content
      const selectedContent = document.getElementById(tabName + '-tab');
      if (selectedContent) {
        selectedContent.classList.add('active');
        selectedContent.style.display = 'block';  // Explicitly show - overrides inline styles
      }

      // Activate selected tab button
      const selectedTab = document.querySelector(\`[data-tab="\${tabName}"]\`);
      if (selectedTab) {
        selectedTab.classList.add('active');
      }
    }

    function highlightXML(xml) {
      // Simple XML syntax highlighting
      return xml
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/&amp;lt;(\\/?[\\w:-]+)&amp;gt;/g, '&amp;lt;<span class="xml-tag">$1</span>&amp;gt;')
        .replace(/([\\w:-]+)=/g, '<span class="xml-attr">$1</span>=')
        .replace(/="([^"]*)"/g, '="<span class="xml-value">$1</span>"')
        .replace(/&amp;lt;!--.*?--&amp;gt;/g, function(match) {
          return '<span class="xml-comment">' + match + '</span>';
        });
    }

    function addLineNumbers(xml) {
      const lines = xml.split('\\n');
      return lines.map((line, index) =>
        \`<span class="xml-line" data-line="\${index + 1}">\${line}</span>\`
      ).join('\\n');
    }

    function toggleXMLWrap() {
      const content = document.querySelector('.prompt-xml-content');
      if (content) {
        content.classList.toggle('wrap');
      }
    }

    function toggleLineNumbers() {
      const content = document.querySelector('.prompt-xml-content');
      if (content) {
        content.classList.toggle('line-numbers');
      }
    }

    function formatJson(obj) {
      try {
        if (typeof obj === 'string') {
          obj = JSON.parse(obj);
        }
        return JSON.stringify(obj, null, 2);
      } catch (e) {
        return obj;
      }
    }

    function escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }

    // Handle timeline block clicks
    document.addEventListener('DOMContentLoaded', () => {
      console.log('Workflow Timeline Report loaded');

      // Restore view preference from localStorage or URL hash
      const savedView = localStorage.getItem('timeline-view-preference');
      const hashView = window.location.hash.substring(1); // Remove #
      const preferredView = hashView || savedView || 'timeline';

      if (preferredView === 'flow') {
        switchView('flow');
      }

      // Click handlers for timeline blocks
      const blocks = document.querySelectorAll('.duration-block');
      console.log('Found', blocks.length, 'duration blocks');

      blocks.forEach(block => {
        block.addEventListener('click', async function(e) {
          console.log('Block clicked:', this.getAttribute('data-row-name'));

          // Declare variables outside try blocks for proper scope
          let spanId, rowName, duration, status, hasError, errorMessage, rowData, errorDetails;

          try {
            // Add visual click feedback
            this.style.opacity = '0.6';
            setTimeout(() => { this.style.opacity = '1'; }, 200);

            spanId = this.getAttribute('data-span-id');
            rowName = this.getAttribute('data-row-name');
            duration = this.getAttribute('data-duration');
            status = this.getAttribute('data-status');
            hasError = this.getAttribute('data-has-error') === 'true';
            errorMessage = this.getAttribute('data-error-message');

            // Find row data for error details
            rowData = TIMELINE_DATA.rows.find(r => r.spanId === spanId);

            if (!rowData) {
              console.error('❌ No data found for span:', spanId);
              alert('Error: No data found for this step. Check console for details.');
              return;
            }

            errorDetails = rowData?.error;

            openModal(this);
            showModalContent('<div class="loading">Loading span data...</div>');

          } catch (outerError) {
            console.error('❌ Error in click handler:', outerError);
            alert('Failed to open step details. See console for error details.');
            return;
          }

          try {
            let errorSection = '';
            if (hasError && errorDetails) {
              const feedbackHtml = errorDetails.feedback && errorDetails.feedback.length > 0
                ? \`<br><br><strong>Validation Feedback:</strong><br>\${errorDetails.feedback.map(f => '• ' + escapeHtml(f)).join('<br>')}\`
                : '';

              const stackHtml = errorDetails.stack
                ? \`<br><br><strong>Stack Trace:</strong><br><pre style="font-size: 11px; margin-top: 8px;">\${escapeHtml(errorDetails.stack)}</pre>\`
                : '';

              errorSection = \`
                <div class="modal-section">
                  <h3>❌ Error Details</h3>
                  <div class="error-block">
                    <strong>\${escapeHtml(errorDetails.message)}</strong><br>
                    <em>Type: \${errorDetails.type}</em>
                    \${errorDetails.score !== undefined ? \`<br>Quality Score: \${errorDetails.score}/100\` : ''}
                    \${feedbackHtml}
                    \${stackHtml}
                  </div>
                </div>
              \`;
            }

            // Build tabbed interface
            const html = \`
              <!-- Tab Navigation -->
              <div class="modal-tabs">
                <button class="modal-tab active" data-tab="overview" onclick="switchTab('overview')">
                  📊 Overview
                </button>
                <button class="modal-tab" data-tab="prompt-xml" onclick="switchTab('prompt-xml')" \${!TIMELINE_DATA.outputContent ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''}>
                  📄 Prompt XML
                </button>
                <button class="modal-tab" data-tab="trace-data" onclick="switchTab('trace-data')">
                  🔍 Trace Data
                </button>
              </div>

              <!-- Overview Tab -->
              <div id="overview-tab" class="modal-tab-content active">
                \${renderQualityProgression(rowData)}
                \${renderAgentInfo(rowData)}
                \${rowData.hasQualityData && rowData.feedback ? renderValidationFeedback(rowData, rowData.attemptNumber) : ''}
                \${errorSection}

                <div class="modal-section">
                  <h3>📋 Metadata</h3>
                  <div class="metadata-grid">
                    <div class="metadata-item-modal">
                      <div class="label">Duration</div>
                      <div class="value">\${duration}ms</div>
                    </div>
                    <div class="metadata-item-modal">
                      <div class="label">Status</div>
                      <div class="value" style="color: \${status === 'error' ? '#dc2626' : status === 'warning' ? '#d97706' : '#059669'}">\${status.toUpperCase()}</div>
                    </div>
                    <div class="metadata-item-modal">
                      <div class="label">Span ID</div>
                      <div class="value">\${spanId || 'N/A'}</div>
                    </div>
                    <div class="metadata-item-modal">
                      <div class="label">Row Name</div>
                      <div class="value">\${rowName}</div>
                    </div>
                  </div>
                </div>

                \${rowData?.attributes ? \`
                  <div class="modal-section">
                    <h3>🔧 Attributes</h3>
                    <div class="data-block">
                      <pre style="font-size: 12px; margin: 0; max-height: 200px; overflow: auto;">\${escapeHtml(JSON.stringify(rowData.attributes, null, 2))}</pre>
                    </div>
                  </div>
                \` : ''}
              </div>

              <!-- Prompt XML Tab -->
              <div id="prompt-xml-tab" class="modal-tab-content" style="display: none;">
                \${TIMELINE_DATA.outputContent ? \`
                  <div class="modal-section">
                    <h3>📄 Generated Prompt XML</h3>
                    <p style="color: #6b7280; margin-bottom: 12px;">
                      Review the generated prompt with syntax highlighting, line numbers, and word wrap controls.
                    </p>

                    <div class="prompt-xml-container">
                      <div class="prompt-xml-header">
                        <div class="prompt-xml-header-title">
                          Prompt Output (\${TIMELINE_DATA.outputContent.split('\\n').length} lines)
                        </div>
                        <div class="prompt-xml-header-actions">
                          <button class="xml-action-btn" onclick="toggleLineNumbers()" title="Toggle line numbers">
                            # Lines
                          </button>
                          <button class="xml-action-btn" onclick="toggleXMLWrap()" title="Toggle word wrap">
                            ↔ Wrap
                          </button>
                          <button class="xml-action-btn" onclick="copyToClipboard(TIMELINE_DATA.outputContent, this)" title="Copy all">
                            📋 Copy
                          </button>
                        </div>
                      </div>
                      <div class="prompt-xml-content line-numbers">\${addLineNumbers(highlightXML(TIMELINE_DATA.outputContent))}</div>
                    </div>

                    <div style="display: flex; gap: 12px; margin-top: 16px; align-items: center;">
                      <button class="btn-primary" onclick="copyToClipboard(TIMELINE_DATA.outputContent, this)">
                        📋 Copy Full Prompt
                      </button>
                      \${TIMELINE_DATA.outputPath ? \`
                        <button class="btn-secondary" onclick="alert('Output file: \${TIMELINE_DATA.outputPath}')">
                          📂 Show File Path
                        </button>
                      \` : ''}
                      <span style="color: #9ca3af; font-size: 12px; margin-left: auto;">
                        \${(TIMELINE_DATA.outputContent.length / 1024).toFixed(1)} KB
                      </span>
                    </div>
                  </div>
                \` : \`
                  <div class="modal-section">
                    <div class="data-block" style="background: #fef3c7; border-color: #fde68a; color: #92400e;">
                      <strong>⚠️ No Prompt Output Available</strong><br><br>
                      The prompt output file could not be loaded. This may happen if:
                      <ul style="margin: 12px 0; padding-left: 24px;">
                        <li>The workflow did not complete the prompt generation step</li>
                        <li>The output file was deleted or moved</li>
                        <li>The workflow metadata does not contain an output path</li>
                      </ul>
                    </div>
                  </div>
                \`}
              </div>

              <!-- Trace Data Tab -->
              <div id="trace-data-tab" class="modal-tab-content" style="display: none;">
                <div class="modal-section">
                  <h3>🔍 Raw Trace Data</h3>
                  <p style="color: #6b7280; margin-bottom: 16px;">
                    Low-level span data from OpenTelemetry traces.
                  </p>

                  <div class="data-block">
                    <pre style="font-size: 12px; margin: 0; max-height: 400px; overflow: auto;">\${escapeHtml(JSON.stringify(rowData, null, 2))}</pre>
                  </div>

                  <div style="margin-top: 16px;">
                    <button class="btn-secondary" onclick="copyToClipboard(JSON.stringify(rowData, null, 2), this)">
                      📋 Copy Raw Data
                    </button>
                  </div>
                </div>
              </div>
            \`;

            showModalContent(html);
          } catch (error) {
            showModalContent(\`
              <div class="error-block">
                <strong>Error loading span data:</strong><br>
                \${escapeHtml(error.message)}
              </div>
            \`);
          }
        });

        // Keyboard accessibility
        block.addEventListener('keypress', function(e) {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            this.click();
          }
        });
      });

      // Close modal on Escape key
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          closeModal();
        }
      });

      // Close modal on background click
      document.getElementById('spanModal').addEventListener('click', (e) => {
        if (e.target.id === 'spanModal') {
          closeModal();
        }
      });

      // Click handlers for flow diagram agent nodes
      const flowNodes = document.querySelectorAll('.agent-node');
      console.log('Found', flowNodes.length, 'flow diagram agent nodes');

      flowNodes.forEach(node => {
        node.addEventListener('click', function() {
          const spanId = this.getAttribute('data-span-id');
          const rowData = TIMELINE_DATA.rows.find(r => r.spanId === spanId);

          if (!rowData) {
            console.error('No data found for span:', spanId);
            return;
          }

          // Reuse the same modal rendering logic as timeline blocks
          openModal(this);
          showModalContent('<div class="loading">Loading agent data...</div>');

          try {
            const html = \`
              <!-- Tab Navigation -->
              <div class="modal-tabs">
                <button class="modal-tab active" data-tab="overview" onclick="switchTab('overview')">
                  📊 Overview
                </button>
                <button class="modal-tab" data-tab="prompt-xml" onclick="switchTab('prompt-xml')" \${!TIMELINE_DATA.outputContent ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''}>
                  📄 Prompt XML
                </button>
                <button class="modal-tab" data-tab="trace-data" onclick="switchTab('trace-data')">
                  🔍 Trace Data
                </button>
              </div>

              <!-- Overview Tab -->
              <div id="overview-tab" class="modal-tab-content active">
                \${renderQualityProgression(rowData)}
                \${renderAgentInfo(rowData)}
                \${rowData.hasQualityData && rowData.feedback ? renderValidationFeedback(rowData, rowData.attemptNumber) : ''}

                <div class="modal-section">
                  <h3>📋 Metadata</h3>
                  <div class="metadata-grid">
                    <div class="metadata-item-modal">
                      <div class="label">Duration</div>
                      <div class="value">\${rowData.duration}ms</div>
                    </div>
                    <div class="metadata-item-modal">
                      <div class="label">Status</div>
                      <div class="value" style="color: \${rowData.status === 'error' ? '#dc2626' : rowData.status === 'warning' ? '#d97706' : '#059669'}">\${rowData.status.toUpperCase()}</div>
                    </div>
                    <div class="metadata-item-modal">
                      <div class="label">Span ID</div>
                      <div class="value">\${rowData.spanId || 'N/A'}</div>
                    </div>
                  </div>
                </div>

                \${rowData?.attributes ? \`
                  <div class="modal-section">
                    <h3>🔧 Attributes</h3>
                    <div class="data-block">
                      <pre style="font-size: 12px; margin: 0; max-height: 200px; overflow: auto;">\${escapeHtml(JSON.stringify(rowData.attributes, null, 2))}</pre>
                    </div>
                  </div>
                \` : ''}
              </div>

              <!-- Prompt XML Tab -->
              <div id="prompt-xml-tab" class="modal-tab-content" style="display: none;">
                \${TIMELINE_DATA.outputContent ? \`
                  <div class="modal-section">
                    <h3>📄 Generated Prompt XML</h3>
                    <p style="color: #6b7280; margin-bottom: 12px;">
                      Review the generated prompt with syntax highlighting, line numbers, and word wrap controls.
                    </p>

                    <div class="prompt-xml-container">
                      <div class="prompt-xml-header">
                        <div class="prompt-xml-header-title">
                          Prompt Output (\${TIMELINE_DATA.outputContent.split('\\n').length} lines)
                        </div>
                        <div class="prompt-xml-header-actions">
                          <button class="xml-action-btn" onclick="toggleLineNumbers()" title="Toggle line numbers">
                            # Lines
                          </button>
                          <button class="xml-action-btn" onclick="toggleXMLWrap()" title="Toggle word wrap">
                            ↔ Wrap
                          </button>
                          <button class="xml-action-btn" onclick="copyToClipboard(TIMELINE_DATA.outputContent, this)" title="Copy all">
                            📋 Copy
                          </button>
                        </div>
                      </div>
                      <div class="prompt-xml-content line-numbers">\${addLineNumbers(highlightXML(TIMELINE_DATA.outputContent))}</div>
                    </div>

                    <div style="display: flex; gap: 12px; margin-top: 16px;">
                      <button class="btn-primary" onclick="copyToClipboard(TIMELINE_DATA.outputContent, this)">
                        📋 Copy Full Prompt
                      </button>
                    </div>
                  </div>
                \` : \`
                  <div class="modal-section">
                    <div class="data-block" style="background: #fef3c7; border-color: #fde68a; color: #92400e;">
                      <strong>⚠️ No Prompt Output Available</strong><br><br>
                      The prompt output file could not be loaded.
                    </div>
                  </div>
                \`}
              </div>

              <!-- Trace Data Tab -->
              <div id="trace-data-tab" class="modal-tab-content" style="display: none;">
                <div class="modal-section">
                  <h3>🔍 Raw Trace Data</h3>
                  <p style="color: #6b7280; margin-bottom: 16px;">
                    Low-level span data from OpenTelemetry traces.
                  </p>

                  <div class="data-block">
                    <pre style="font-size: 12px; margin: 0; max-height: 400px; overflow: auto;">\${escapeHtml(JSON.stringify(rowData, null, 2))}</pre>
                  </div>

                  <div style="margin-top: 16px;">
                    <button class="btn-secondary" onclick="copyToClipboard(JSON.stringify(rowData, null, 2), this)">
                      📋 Copy Raw Data
                    </button>
                  </div>
                </div>
              </div>
            \`;

            showModalContent(html);
          } catch (error) {
            showModalContent(\`
              <div class="error-block">
                <strong>Error loading agent data:</strong><br>
                \${escapeHtml(error.message)}
              </div>
            \`);
          }
        });

        // Keyboard accessibility for flow nodes
        node.addEventListener('keypress', function(e) {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            this.click();
          }
        });
      });

      // Tooltip functionality
      const tooltip = document.getElementById('spanTooltip');
      const tooltipContent = document.getElementById('tooltipContent');
      let tooltipTimeout;

      function showTooltip(block, x, y) {
        // Don't show tooltip if modal is open
        const modal = document.getElementById('spanModal');
        if (modal && modal.classList.contains('active')) {
          return;
        }

        const spanId = block.getAttribute('data-span-id');
        const rowData = TIMELINE_DATA.rows.find(r => r.spanId === spanId);

        if (!rowData) return;

        // Calculate start and end times
        const workflowStart = new Date(TIMELINE_DATA.startTime);
        const startTime = new Date(workflowStart.getTime() + rowData.startOffset);
        const endTime = new Date(startTime.getTime() + rowData.duration);

        // Extract agent name from attributes
        const agentName = rowData.attributes?.['agent.name'] ||
                          rowData.attributes?.['workflow.agent'] ||
                          'Unknown Agent';

        // Format times
        const formatTime = (date) => {
          const hours = String(date.getHours()).padStart(2, '0');
          const minutes = String(date.getMinutes()).padStart(2, '0');
          const seconds = String(date.getSeconds()).padStart(2, '0');
          const ms = String(date.getMilliseconds()).padStart(3, '0');
          return \`\${hours}:\${minutes}:\${seconds}.\${ms}\`;
        };

        // Build tooltip content
        let html = \`
          <div class="tooltip-title">\${escapeHtml(rowData.name)}</div>
          <div class="tooltip-divider"></div>
          <div class="tooltip-row">
            <span class="tooltip-label">Type</span>
            <span class="tooltip-value">\${escapeHtml(rowData.type)}</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">Status</span>
            <span class="tooltip-value"><span class="tooltip-status \${rowData.status}">\${rowData.status}</span></span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">Duration</span>
            <span class="tooltip-value">\${formatDuration(rowData.duration)}</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">Agent</span>
            <span class="tooltip-value">\${escapeHtml(agentName)}</span>
          </div>
        \`;

        // Add attempt number if available
        const attemptNum = rowData.attributes?.['attempt.number'];
        if (attemptNum) {
          html += \`
            <div class="tooltip-row">
              <span class="tooltip-label">Attempt</span>
              <span class="tooltip-value">#\${attemptNum}</span>
            </div>
          \`;
        }

        html += \`
          <div class="tooltip-divider"></div>
          <div class="tooltip-row">
            <span class="tooltip-label">Started</span>
            <span class="tooltip-value">\${formatTime(startTime)}</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">Ended</span>
            <span class="tooltip-value">\${formatTime(endTime)}</span>
          </div>
        \`;

        // Add error indicator if present
        if (rowData.error) {
          html += \`
            <div class="tooltip-divider"></div>
            <div class="tooltip-row">
              <span class="tooltip-label" style="color: #fca5a5;">Error</span>
              <span class="tooltip-value" style="color: #fca5a5;">⚠ See details</span>
            </div>
          \`;
        }

        tooltipContent.innerHTML = html;
        positionTooltip(x, y);

        clearTimeout(tooltipTimeout);
        tooltipTimeout = setTimeout(() => {
          tooltip.classList.add('visible');
        }, 100);
      }

      function hideTooltip() {
        clearTimeout(tooltipTimeout);
        tooltip.classList.remove('visible');
      }

      function positionTooltip(x, y) {
        const padding = 16;
        const tooltipRect = tooltip.getBoundingClientRect();

        let left = x + padding;
        let top = y + padding;

        // Adjust if tooltip would overflow right edge
        if (left + tooltipRect.width > window.innerWidth) {
          left = x - tooltipRect.width - padding;
        }

        // Adjust if tooltip would overflow bottom edge
        if (top + tooltipRect.height > window.innerHeight) {
          top = y - tooltipRect.height - padding;
        }

        // Ensure tooltip doesn't go off left edge
        if (left < padding) {
          left = padding;
        }

        // Ensure tooltip doesn't go off top edge
        if (top < padding) {
          top = padding;
        }

        tooltip.style.left = left + 'px';
        tooltip.style.top = top + 'px';
      }

      function formatDuration(ms) {
        if (ms < 1000) {
          return \`\${Math.round(ms)}ms\`;
        } else if (ms < 60000) {
          return \`\${(ms / 1000).toFixed(2)}s\`;
        } else {
          const minutes = Math.floor(ms / 60000);
          const seconds = ((ms % 60000) / 1000).toFixed(1);
          return \`\${minutes}m \${seconds}s\`;
        }
      }

      // Add tooltip event listeners to all timeline blocks
      document.querySelectorAll('.duration-block').forEach(block => {
        block.addEventListener('mouseenter', function(e) {
          showTooltip(this, e.clientX, e.clientY);
        });

        block.addEventListener('mousemove', function(e) {
          if (tooltip.classList.contains('visible')) {
            positionTooltip(e.clientX, e.clientY);
          }
        });

        block.addEventListener('mouseleave', function() {
          hideTooltip();
        });

        // Keyboard accessibility
        block.addEventListener('focus', function(e) {
          const rect = this.getBoundingClientRect();
          showTooltip(this, rect.left + rect.width / 2, rect.top);
        });

        block.addEventListener('blur', function() {
          hideTooltip();
        });
      });
    });
  </script>`;
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

module.exports = { HtmlRenderer };
