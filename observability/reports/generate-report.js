#!/usr/bin/env node

const { TimelineReportGenerator } = require('./timeline-generator');

/**
 * CLI tool for generating timeline reports
 *
 * Usage:
 *   node generate-report.js --session-id <uuid>
 *   node generate-report.js --latest
 *   node generate-report.js --date 2026-01-26
 *   node generate-report.js --all
 */

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    sessionId: null,
    latest: false,
    date: null,
    all: false,
    help: false
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    switch (arg) {
      case '--session-id':
      case '-s':
        options.sessionId = args[++i];
        break;

      case '--latest':
      case '-l':
        options.latest = true;
        break;

      case '--date':
      case '-d':
        options.date = args[++i];
        break;

      case '--all':
      case '-a':
        options.all = true;
        break;

      case '--help':
      case '-h':
        options.help = true;
        break;

      default:
        console.error(`Unknown option: ${arg}`);
        options.help = true;
    }
  }

  return options;
}

function printHelp() {
  console.log(`
Timeline Report Generator

Usage:
  node generate-report.js [options]

Options:
  --session-id, -s <uuid>    Generate report for specific session ID
  --latest, -l               Generate report for latest session (default)
  --date, -d <YYYY-MM-DD>    Generate report for specific date
  --all, -a                  Generate reports for all sessions today
  --help, -h                 Show this help message

Examples:
  # Generate report for latest session
  node generate-report.js --latest

  # Generate report for specific session
  node generate-report.js --session-id abc123-def456

  # Generate reports for all sessions today
  node generate-report.js --all

  # Generate reports for specific date
  node generate-report.js --date 2026-01-26
  `);
}

async function main() {
  const options = parseArgs();

  if (options.help) {
    printHelp();
    process.exit(0);
  }

  const generator = new TimelineReportGenerator();

  try {
    if (options.sessionId) {
      // Generate for specific session
      const date = options.date ? new Date(options.date) : new Date();
      const reportPath = await generator.generate(options.sessionId, date);
      console.log(`\n📊 Open report: open ${reportPath}\n`);

    } else if (options.all) {
      // Generate for all sessions on date
      const date = options.date ? new Date(options.date) : new Date();
      const reportPaths = await generator.generateForDate(date);
      console.log(`\n📊 Generated ${reportPaths.length} reports\n`);

    } else {
      // Generate for latest session (default)
      const date = options.date ? new Date(options.date) : new Date();
      const reportPath = await generator.generateLatest(date);
      console.log(`\n📊 Open report: open ${reportPath}\n`);
    }

    process.exit(0);
  } catch (error) {
    console.error('\n❌ Error:', error.message);
    console.error('\nTry --help for usage information\n');
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { parseArgs, printHelp };
