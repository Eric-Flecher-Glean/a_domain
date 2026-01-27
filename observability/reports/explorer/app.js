/**
 * Report Explorer - Frontend Application
 * Handles UI interactions, data fetching, filtering, and rendering
 */

// =============================================================================
// State Management
// =============================================================================

const state = {
  reports: [],
  filteredReports: [],
  currentPage: 1,
  totalPages: 1,
  filters: {
    search: '',
    status: 'all',
    dateRange: 'week'
  },
  stats: null
};

// =============================================================================
// API Functions
// =============================================================================

/**
 * Fetch reports from server
 */
async function fetchReports() {
  try {
    showLoading(true);

    const params = new URLSearchParams({
      status: state.filters.status,
      dateRange: state.filters.dateRange,
      search: state.filters.search,
      page: state.currentPage,
      limit: 20
    });

    const response = await fetch(`/api/reports?${params}`);

    if (!response.ok) {
      throw new Error('Failed to fetch reports');
    }

    const data = await response.json();

    state.reports = data.reports;
    state.filteredReports = data.reports;
    state.totalPages = data.totalPages;

    renderReports();
    updatePagination(data);

    showLoading(false);
    announce(`Loaded ${data.total} reports`);

    return data;
  } catch (error) {
    console.error('Error fetching reports:', error);
    showError('Failed to load reports. Please try again.');
    showLoading(false);
    return null;
  }
}

/**
 * Fetch statistics
 */
async function fetchStats() {
  try {
    const params = new URLSearchParams({
      dateRange: state.filters.dateRange
    });

    const response = await fetch(`/api/stats?${params}`);

    if (!response.ok) {
      throw new Error('Failed to fetch statistics');
    }

    const stats = await response.json();
    state.stats = stats;

    renderStats(stats);

    return stats;
  } catch (error) {
    console.error('Error fetching stats:', error);
    return null;
  }
}

/**
 * Refresh all data
 */
async function refreshData() {
  const refreshBtn = document.getElementById('refreshBtn');
  refreshBtn.disabled = true;
  refreshBtn.textContent = '⏳ Refreshing...';

  try {
    // Trigger server refresh
    await fetch('/api/refresh');

    // Reload data
    await Promise.all([
      fetchReports(),
      fetchStats()
    ]);

    announce('Reports refreshed successfully');
  } catch (error) {
    console.error('Error refreshing:', error);
    showError('Failed to refresh reports');
  } finally {
    refreshBtn.disabled = false;
    refreshBtn.textContent = '🔄 Refresh';
  }
}

// =============================================================================
// Rendering Functions
// =============================================================================

/**
 * Render statistics cards
 */
function renderStats(stats) {
  document.getElementById('statTotal').textContent = stats.totalRuns;
  document.getElementById('statSuccess').textContent = `${stats.successRate}%`;
  document.getElementById('statDuration').textContent = formatDuration(stats.avgDuration);
  document.getElementById('statErrors').textContent = stats.errorCount;

  // Update result count
  document.getElementById('resultCount').textContent = stats.totalRuns;
}

/**
 * Render reports list
 */
function renderReports() {
  const container = document.getElementById('reportsList');
  const emptyState = document.getElementById('emptyState');

  if (state.filteredReports.length === 0) {
    container.innerHTML = '';
    emptyState.style.display = 'block';
    return;
  }

  emptyState.style.display = 'none';

  const html = state.filteredReports.map(report => createReportCard(report)).join('');
  container.innerHTML = html;

  // Add click handlers
  document.querySelectorAll('.report-item').forEach(item => {
    item.addEventListener('click', () => {
      const sessionId = item.getAttribute('data-session-id');
      openReport(sessionId);
    });

    // Keyboard accessibility
    item.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        const sessionId = item.getAttribute('data-session-id');
        openReport(sessionId);
      }
    });
  });
}

/**
 * Create HTML for a single report card
 */
function createReportCard(report) {
  const date = new Date(report.date);
  const dateStr = formatDate(date);
  const timeStr = formatTime(date);

  const statusClass = report.status === 'success' ? 'status-success' : 'status-error';
  const statusIcon = report.status === 'success' ? '✅' : '❌';
  const statusText = report.status === 'success' ? 'Success' : 'Error';

  const qualityHtml = report.qualityScore !== null
    ? `<span class="quality-score ${getQualityClass(report.qualityScore)}">
         ${report.qualityScore}/100
       </span>`
    : '';

  return `
    <div class="report-item"
         data-session-id="${report.sessionId}"
         tabindex="0"
         role="button"
         aria-label="Open report for ${report.task}">
      <div class="report-info">
        <div class="report-session">
          <div class="session-id">${truncateText(report.sessionId, 36)}</div>
        </div>

        <div class="report-date">
          <div class="date-text">${dateStr}</div>
          <div class="time-text">${timeStr}</div>
        </div>

        <div class="report-task" title="${escapeHtml(report.task)}">
          ${escapeHtml(truncateText(report.task, 80))}
        </div>

        <div class="report-meta">
          <span class="status-badge ${statusClass}">
            ${statusIcon} ${statusText}
          </span>
          <span class="duration-badge">${formatDuration(report.duration)}</span>
          ${qualityHtml}
        </div>
      </div>

      <div class="report-arrow">→</div>
    </div>
  `;
}

/**
 * Update pagination UI
 */
function updatePagination(data) {
  const section = document.getElementById('paginationSection');
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  const pageInfo = document.getElementById('pageInfo');

  if (data.totalPages <= 1) {
    section.style.display = 'none';
    return;
  }

  section.style.display = 'flex';
  pageInfo.textContent = `Page ${data.page} of ${data.totalPages}`;

  prevBtn.disabled = data.page <= 1;
  nextBtn.disabled = data.page >= data.totalPages;
}

// =============================================================================
// UI Interaction Functions
// =============================================================================

/**
 * Open report in new tab
 */
function openReport(sessionId) {
  const report = state.filteredReports.find(r => r.sessionId === sessionId);
  if (!report) {
    console.error('Report not found:', sessionId);
    return;
  }

  // Store current state in sessionStorage for back navigation
  sessionStorage.setItem('explorerState', JSON.stringify({
    filters: state.filters,
    page: state.currentPage,
    returnUrl: window.location.href
  }));

  window.open(report.reportPath, '_blank');
  announce(`Opened report for ${report.task}`);
}

/**
 * Apply filters and reload data
 */
function applyFilters() {
  state.currentPage = 1; // Reset to first page
  fetchReports();
  fetchStats();
}

/**
 * Handle search input
 */
function handleSearch(event) {
  state.filters.search = event.target.value.trim();

  // Debounce search
  clearTimeout(window.searchTimeout);
  window.searchTimeout = setTimeout(() => {
    applyFilters();
  }, 300);
}

/**
 * Handle status filter
 */
function handleStatusFilter(status) {
  state.filters.status = status;

  // Update button states
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  event.target.classList.add('active');

  applyFilters();
}

/**
 * Handle date range filter
 */
function handleDateFilter(event) {
  state.filters.dateRange = event.target.value;
  applyFilters();
}

/**
 * Handle pagination
 */
function goToPage(page) {
  state.currentPage = page;
  fetchReports();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Format duration in ms to human-readable string
 */
function formatDuration(ms) {
  if (ms < 1000) {
    return `${Math.round(ms)}ms`;
  } else {
    return `${(ms / 1000).toFixed(2)}s`;
  }
}

/**
 * Format date
 */
function formatDate(date) {
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  if (date.toDateString() === today.toDateString()) {
    return 'Today';
  } else if (date.toDateString() === yesterday.toDateString()) {
    return 'Yesterday';
  } else {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined
    });
  }
}

/**
 * Format time
 */
function formatTime(date) {
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
}

/**
 * Truncate text with ellipsis
 */
function truncateText(text, maxLength) {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Get quality score class
 */
function getQualityClass(score) {
  if (score >= 80) return 'high';
  if (score >= 60) return 'medium';
  return 'low';
}

/**
 * Show/hide loading indicator
 */
function showLoading(show) {
  const indicator = document.getElementById('loadingIndicator');
  const reportsList = document.getElementById('reportsList');

  if (show) {
    indicator.style.display = 'flex';
    reportsList.style.display = 'none';
  } else {
    indicator.style.display = 'none';
    reportsList.style.display = 'grid';
  }
}

/**
 * Show error message
 */
function showError(message) {
  const errorEl = document.getElementById('errorMessage');
  errorEl.textContent = message;
  errorEl.style.display = 'block';

  setTimeout(() => {
    errorEl.style.display = 'none';
  }, 5000);
}

/**
 * Announce message to screen readers
 */
function announce(message) {
  const announcer = document.getElementById('announcer');
  announcer.textContent = message;

  // Clear after announcement
  setTimeout(() => {
    announcer.textContent = '';
  }, 1000);
}

// =============================================================================
// Event Listeners
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
  console.log('Report Explorer initialized');

  // Search input
  const searchInput = document.getElementById('searchInput');
  searchInput.addEventListener('input', handleSearch);

  // Status filter buttons
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const status = e.target.getAttribute('data-status');
      state.filters.status = status;

      // Update button states
      document.querySelectorAll('.filter-btn').forEach(b => {
        b.classList.remove('active');
      });
      e.target.classList.add('active');

      applyFilters();
    });
  });

  // Date filter
  const dateFilter = document.getElementById('dateFilter');
  dateFilter.addEventListener('change', handleDateFilter);

  // Refresh button
  const refreshBtn = document.getElementById('refreshBtn');
  refreshBtn.addEventListener('click', refreshData);

  // Back button (shown when coming from a report)
  const backBtn = document.getElementById('backBtn');
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('from') || document.referrer.includes('/reports/')) {
    backBtn.style.display = 'block';
  }
  backBtn.addEventListener('click', () => {
    // Try to restore previous state
    const savedState = sessionStorage.getItem('explorerState');
    if (savedState) {
      const parsed = JSON.parse(savedState);
      state.filters = parsed.filters;
      state.currentPage = parsed.page;

      // Update UI to match filters
      searchInput.value = state.filters.search;
      dateFilter.value = state.filters.dateRange;
      document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-status') === state.filters.status) {
          btn.classList.add('active');
        }
      });

      applyFilters();
      sessionStorage.removeItem('explorerState');
    }

    // Always hide back button after click
    backBtn.style.display = 'none';
  });

  // Pagination
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');

  prevBtn.addEventListener('click', () => {
    if (state.currentPage > 1) {
      goToPage(state.currentPage - 1);
    }
  });

  nextBtn.addEventListener('click', () => {
    if (state.currentPage < state.totalPages) {
      goToPage(state.currentPage + 1);
    }
  });

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    // Cmd/Ctrl + R to refresh
    if ((e.metaKey || e.ctrlKey) && e.key === 'r') {
      e.preventDefault();
      refreshData();
    }

    // / to focus search
    if (e.key === '/' && e.target.tagName !== 'INPUT') {
      e.preventDefault();
      searchInput.focus();
    }
  });

  // Initial data load
  Promise.all([
    fetchReports(),
    fetchStats()
  ]).then(() => {
    console.log('Initial data loaded');
  });
});
