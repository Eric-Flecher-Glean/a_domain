/**
 * Calculates summary metrics from timeline data
 */
class MetricsCalculator {
  /**
   * Calculates all metrics for the timeline
   */
  calculateMetrics(timeline) {
    const { rows, metadata, milestones } = timeline;

    return {
      totalDuration: this.formatDuration(metadata.totalDuration),
      totalDurationRaw: metadata.totalDuration,
      numberOfSteps: rows.length,
      numberOfAttempts: this.countAttempts(rows),
      successRate: this.calculateSuccessRate(rows),
      bottleneck: this.identifyBottleneck(rows),
      spanComparison: this.compareSpanDurations(rows),
      qualityProgression: this.extractQualityProgression(milestones),
      statusBreakdown: this.calculateStatusBreakdown(rows),
      avgStepDuration: this.calculateAverageStepDuration(rows)
    };
  }

  /**
   * Counts number of attempts in the workflow
   */
  countAttempts(rows) {
    return rows.filter(r => r.type === 'attempt' || r.indentLevel === 1).length;
  }

  /**
   * Calculates success rate based on validation results
   */
  calculateSuccessRate(rows) {
    const validationRows = rows.filter(r => r.type === 'validation');
    if (validationRows.length === 0) {
      // No validations - check overall success
      const successRows = rows.filter(r => r.status === 'success');
      return {
        percentage: rows.length > 0 ? (successRows.length / rows.length * 100).toFixed(1) : 0,
        successful: successRows.length,
        total: rows.length
      };
    }

    const successful = validationRows.filter(r => r.status === 'success').length;

    return {
      percentage: (successful / validationRows.length * 100).toFixed(1),
      successful: successful,
      total: validationRows.length
    };
  }

  /**
   * Identifies the bottleneck (slowest step)
   */
  identifyBottleneck(rows) {
    if (rows.length === 0) {
      return { name: 'N/A', duration: '0ms', percentage: 0 };
    }

    const sorted = [...rows].sort((a, b) => b.duration - a.duration);
    const slowest = sorted[0];
    const totalDuration = rows.reduce((sum, r) => sum + r.duration, 0);

    return {
      name: slowest.name,
      duration: this.formatDuration(slowest.duration),
      durationRaw: slowest.duration,
      percentage: totalDuration > 0 ? ((slowest.duration / totalDuration) * 100).toFixed(1) : 0
    };
  }

  /**
   * Compares span durations for visualization
   */
  compareSpanDurations(rows) {
    if (rows.length === 0) return [];

    const maxDuration = Math.max(...rows.map(r => r.duration));

    return rows.map(row => ({
      name: row.name,
      duration: row.duration,
      durationFormatted: this.formatDuration(row.duration),
      normalized: maxDuration > 0 ? (row.duration / maxDuration) * 100 : 0,
      status: row.status
    }));
  }

  /**
   * Extracts quality score progression from milestones
   */
  extractQualityProgression(milestones) {
    const validationMilestones = milestones.filter(m =>
      (m.type === 'PromptValidated' || m.type === 'PromptRejected') && m.payload?.quality_score != null
    );

    return validationMilestones.map((m, index) => ({
      attempt: index + 1,
      score: m.payload.quality_score,
      passed: m.type === 'PromptValidated' || m.payload.is_valid === true || m.payload.quality_score >= 90,
      offset: m.offset
    }));
  }

  /**
   * Calculates breakdown of statuses
   */
  calculateStatusBreakdown(rows) {
    const breakdown = {
      success: 0,
      warning: 0,
      error: 0,
      info: 0
    };

    rows.forEach(row => {
      if (breakdown.hasOwnProperty(row.status)) {
        breakdown[row.status]++;
      }
    });

    return breakdown;
  }

  /**
   * Calculates average step duration
   */
  calculateAverageStepDuration(rows) {
    if (rows.length === 0) return { formatted: '0ms', raw: 0 };

    const total = rows.reduce((sum, r) => sum + r.duration, 0);
    const avg = total / rows.length;

    return {
      formatted: this.formatDuration(avg),
      raw: avg
    };
  }

  /**
   * Formats duration in human-readable format
   */
  formatDuration(ms) {
    if (ms < 1000) {
      return `${Math.round(ms)}ms`;
    } else if (ms < 60000) {
      return `${(ms / 1000).toFixed(2)}s`;
    } else {
      const minutes = Math.floor(ms / 60000);
      const seconds = ((ms % 60000) / 1000).toFixed(0);
      return `${minutes}m ${seconds}s`;
    }
  }

  /**
   * Calculates performance rating
   */
  calculatePerformanceRating(totalDuration) {
    // Define thresholds (these can be customized per workflow)
    if (totalDuration < 5000) return 'Excellent';
    if (totalDuration < 15000) return 'Good';
    if (totalDuration < 30000) return 'Fair';
    return 'Slow';
  }
}

module.exports = { MetricsCalculator };
