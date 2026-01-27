const path = require('path');
const { DataAggregator } = require('./data-aggregator');
const { TimelineBuilder } = require('./timeline-builder');
const { HtmlRenderer } = require('./html-renderer');

/**
 * Main timeline report generator
 * Orchestrates data aggregation, timeline building, and HTML rendering
 */
class TimelineReportGenerator {
  constructor(options = {}) {
    this.baseDir = options.baseDir || 'observability';
    this.outputDir = options.outputDir || path.join(this.baseDir, 'reports-output');

    this.dataAggregator = new DataAggregator(this.baseDir);
    this.timelineBuilder = new TimelineBuilder();
    this.htmlRenderer = new HtmlRenderer();
  }

  /**
   * Generates timeline report for a specific session
   *
   * @param {string} sessionId - Session ID to generate report for
   * @param {Date} date - Date of the session (defaults to today)
   * @returns {string} Path to generated HTML report
   */
  async generate(sessionId, date = new Date()) {
    console.log(`\n🔨 Generating timeline report for session ${sessionId}...`);

    try {
      // Step 1: Aggregate data from JSONL files
      console.log('  📂 Reading observability data...');
      const aggregatedData = await this.dataAggregator.aggregateSessionData(sessionId, date);
      console.log(`  ✓ Found ${aggregatedData.spans.length} spans, ${aggregatedData.events.length} events`);

      // Step 2: Build timeline structure
      console.log('  🏗️  Building timeline structure...');
      const timeline = this.timelineBuilder.buildTimeline(aggregatedData);
      timeline.sessionId = sessionId;
      timeline.traceId = aggregatedData.traceId;
      console.log(`  ✓ Built timeline with ${timeline.rows.length} rows`);

      // Step 3: Render HTML report
      console.log('  🎨 Rendering HTML report...');
      const outputPath = path.join(this.outputDir, `${sessionId}-timeline.html`);
      await this.htmlRenderer.render(timeline, outputPath);
      console.log(`  ✓ Report saved to ${outputPath}`);

      console.log(`\n✅ Timeline report generated successfully!`);
      console.log(`   View report: open ${outputPath}\n`);

      return outputPath;
    } catch (error) {
      console.error(`\n❌ Failed to generate timeline report:`, error.message);
      throw error;
    }
  }

  /**
   * Generates report for the most recent session
   *
   * @param {Date} date - Date to search for sessions (defaults to today)
   * @returns {string} Path to generated HTML report
   */
  async generateLatest(date = new Date()) {
    console.log('🔍 Finding latest session...');

    const sessionId = await this.dataAggregator.findLatestSession(date);
    console.log(`   Found session: ${sessionId}`);

    return this.generate(sessionId, date);
  }

  /**
   * Generates reports for all sessions on a given date
   *
   * @param {Date} date - Date to generate reports for
   * @returns {string[]} Paths to generated HTML reports
   */
  async generateForDate(date = new Date()) {
    console.log(`\n🔨 Generating reports for all sessions on ${date.toDateString()}...`);

    const dateStr = this.dataAggregator.formatDate(date);
    const tracesPath = path.join(this.baseDir, 'traces', `traces_${dateStr}.jsonl`);

    // Read all unique session IDs from the traces file
    const sessionIds = new Set();
    const { createReadStream } = require('fs');
    const readline = require('readline');

    const fileStream = createReadStream(tracesPath);
    const rl = readline.createInterface({
      input: fileStream,
      crlfDelay: Infinity
    });

    for await (const line of rl) {
      if (!line.trim()) continue;

      try {
        const parsed = JSON.parse(line);
        const sessionId = parsed.attributes?.['session.id'];
        if (sessionId) {
          sessionIds.add(sessionId);
        }
      } catch (err) {
        // Skip invalid lines
      }
    }

    console.log(`   Found ${sessionIds.size} sessions`);

    // Generate report for each session
    const reportPaths = [];
    for (const sessionId of sessionIds) {
      try {
        const reportPath = await this.generate(sessionId, date);
        reportPaths.push(reportPath);
      } catch (error) {
        console.error(`   ⚠️  Failed to generate report for ${sessionId}:`, error.message);
      }
    }

    console.log(`\n✅ Generated ${reportPaths.length} reports`);
    return reportPaths;
  }
}

module.exports = { TimelineReportGenerator };

// If run directly, generate report for latest session
if (require.main === module) {
  const generator = new TimelineReportGenerator();

  generator.generateLatest()
    .then(reportPath => {
      console.log(`\n📊 Report: ${reportPath}`);
      process.exit(0);
    })
    .catch(error => {
      console.error('Error:', error);
      process.exit(1);
    });
}
