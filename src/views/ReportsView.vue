<template>
  <div class="reports-view">
    <div class="reports-header">
      <h1> Reports & Analytics</h1>
      <p class="subtitle">Generate comprehensive PDF reports with visualizations and analytics</p>
    </div>

    <!-- Report Type Selector -->
    <section class="report-selector-section">
      <h2>Select Report Type</h2>
      <div class="report-types">
        <div
          v-for="reportType in reportTypes"
          :key="reportType.value"
          class="report-card"
          :class="{ selected: selectedReportType === reportType.value }"
          @click="selectReportType(reportType.value)"
        >
          <div class="report-icon">
            {{ reportType.icon }}
          </div>
          <h3>{{ reportType.label }}</h3>
          <p>{{ reportType.description }}</p>
          <div class="report-features">
            <span v-for="feature in reportType.features" :key="feature" class="feature-tag">
              {{ feature }}
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- Report Configuration Form -->
    <section v-if="selectedReportType" class="config-section">
      <h2>Configure Report</h2>
      <form class="report-config-form" @submit.prevent="handleGenerateReport">
        <div class="form-grid">
          <!-- Module Selection -->
          <div class="form-group">
            <label for="module">Module</label>
            <select id="module" v-model="reportConfig.module" required>
              <option value="">Select Module</option>
              <option value="olya">Olya (River Transport)</option>
              <option value="balakovo">Balakovo (Balker)</option>
              <option value="deepsea">Deep Sea Voyages</option>
            </select>
          </div>

          <!-- Date Range -->
          <div class="form-group">
            <label for="startDate">Start Date</label>
            <input
              id="startDate"
              v-model="reportConfig.dateRange.start"
              type="date"
              required
            />
          </div>

          <div class="form-group">
            <label for="endDate">End Date</label>
            <input
              id="endDate"
              v-model="reportConfig.dateRange.end"
              type="date"
              required
            />
          </div>

          <!-- Vessel Filter (Multi-select) -->
          <div class="form-group full-width" v-if="availableVessels.length">
            <label>Vessels (Optional - Leave empty for all vessels)</label>
            <div class="vessel-tags">
              <label
                v-for="vessel in availableVessels"
                :key="vessel"
                class="vessel-tag"
              >
                <input
                  type="checkbox"
                  :value="vessel"
                  v-model="reportConfig.vessels"
                />
                <span>{{ vessel }}</span>
              </label>
            </div>
          </div>

          <!-- Report Options -->
          <div class="form-group full-width">
            <label class="checkbox-label">
              <input type="checkbox" v-model="reportConfig.includeCharts" />
              <span>Include Charts & Visualizations</span>
            </label>
          </div>

          <div class="form-group full-width">
            <label class="checkbox-label">
              <input type="checkbox" v-model="reportConfig.includeSummary" />
              <span>Include Executive Summary</span>
            </label>
          </div>

          <div class="form-group full-width">
            <label class="checkbox-label">
              <input type="checkbox" v-model="reportConfig.includeDetails" />
              <span>Include Detailed Breakdown</span>
            </label>
          </div>

          <!-- Format Selection -->
          <div class="form-group">
            <label for="format">Export Format</label>
            <select id="format" v-model="reportConfig.format" required>
              <option value="pdf">PDF (Recommended)</option>
              <option value="excel">Excel (.xlsx)</option>
              <option value="csv">CSV (Data Only)</option>
            </select>
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="btn btn-secondary" @click="resetConfig">
            Reset
          </button>
          <button 
            type="submit" 
            class="btn btn-primary"
            :disabled="!canGenerateReport || reportsStore.loading"
          >
            <span v-if="!reportsStore.loading">
               Generate Report
            </span>
            <span v-else class="loading-spinner">
              Generating...
            </span>
          </button>
        </div>
      </form>
    </section>

    <!-- Active Reports & Progress  -->
    <section v-if="reportsStore.activeReports.length" class="active-reports-section">
      <h2>Active Report Generation</h2>
      <div class="active-reports-list">
        <div
          v-for="report in reportsStore.activeReports"
          :key="report.id"
          class="report-item"
        >
          <div class="report-item-header">
            <div class="report-info">
              <h3>{{ getReportTypeLabel(report.id) }}</h3>
              <span class="report-status" :class="`status-${report.status}`">
                {{ report.status }}
              </span>
            </div>
            <small class="report-time">{{ formatDate(report.createdAt) }}</small>
          </div>

          <!-- Progress Indicator -->
          <div v-if="report.status === 'generating'" class="progress-container">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${report.progress}%` }"></div>
            </div>
            <span class="progress-text">{{ report.progress }}%</span>
          </div>

          <!-- Actions -->
          <div class="report-actions">
            <button
              v-if="report.status === 'completed' && report.downloadUrl"
              class="btn btn-sm btn-success"
              @click="downloadReportFile(report.id)"
            >
               Download
            </button>
            <span v-if="report.error" class="error-text">
              {{ report.error }}
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- Report Preview Panel -->
    <section v-if="previewReport" class="preview-section">
      <div class="preview-header">
        <h2>Report Preview</h2>
        <button class="btn btn-sm" @click="closePreview"></button>
      </div>
      <div class="preview-content">
        <iframe
          :src="previewReport.downloadUrl"
          class="preview-iframe"
          frameborder="0"
        ></iframe>
      </div>
    </section>

    <!-- Report History -->
    <section class="history-section">
      <div class="history-header">
        <h2>Report History</h2>
        <button class="btn btn-sm btn-secondary" @click="refreshHistory">
           Refresh
        </button>
      </div>

      <div v-if="reportsStore.recentReports.length" class="history-list">
        <div
          v-for="report in reportsStore.recentReports"
          :key="report.id"
          class="history-item"
        >
          <div class="history-item-header">
            <div>
              <h4>{{ getReportTypeLabel(report.id) }}</h4>
              <small>Generated: {{ formatDate(report.createdAt) }}</small>
            </div>
            <div class="history-actions">
              <button
                v-if="report.downloadUrl"
                class="btn btn-sm btn-primary"
                @click="downloadReportFile(report.id)"
                title="Download"
              >
                
              </button>
              <button
                v-if="report.downloadUrl"
                class="btn btn-sm btn-secondary"
                @click="showPreview(report)"
                title="Preview"
              >
                
              </button>
              <button
                class="btn btn-sm btn-danger"
                @click="deleteReportFile(report.id)"
                title="Delete"
              >
                
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <p>No reports generated yet. Create your first report above!</p>
      </div>
    </section>

    <!-- Quick Export Actions (from other views) -->
    <section class="quick-export-section">
      <h2>Quick Export</h2>
      <p class="section-hint">Generate reports quickly from common views</p>
      <div class="quick-export-buttons">
        <button class="btn btn-outline" @click="exportFromView('voyage-builder')">
           From Voyage Builder
        </button>
        <button class="btn btn-outline" @click="exportFromView('calendar')">
           From Calendar
        </button>
        <button class="btn btn-outline" @click="exportFromView('network')">
           From Network View
        </button>
        <button class="btn btn-outline" @click="exportFromView('financial')">
           From Financial View
        </button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useReportsStore } from '@/stores/reports';
import { useRouter } from 'vue-router';
import type { ReportConfig, ReportType, ExportFormat, ReportGenerationStatus } from '@/types/reports.types';
import type { Module } from '@/types/calendar.types';

const router = useRouter();
const reportsStore = useReportsStore();

// Report type definitions
const reportTypes = [
  {
    value: 'comprehensive' as ReportType,
    label: 'Comprehensive Voyage Report',
    icon: '',
    description: 'Complete voyage analysis with details, calculations, and leg-by-leg breakdown',
    features: ['Voyage Details', 'Leg Analysis', 'Full Calculations', 'Performance Charts']
  },
  {
    value: 'fleet' as ReportType,
    label: 'Fleet Analysis Report',
    icon: '',
    description: 'Fleet utilization, performance metrics, and comparison graphs',
    features: ['Utilization Charts', 'Performance Metrics', 'Comparison Graphs', 'Fleet Stats']
  },
  {
    value: 'schedule' as ReportType,
    label: 'Schedule Timeline Report',
    icon: '',
    description: 'Timeline visualization with Gantt charts and milestone tracking',
    features: ['Timeline View', 'Gantt Charts', 'Milestone Tracking', 'Resource Allocation']
  },
  {
    value: 'financial' as ReportType,
    label: 'Financial Analysis Report',
    icon: '',
    description: 'Cost breakdown, revenue projections, and profitability analysis',
    features: ['Cost Breakdown', 'Revenue Projections', 'Profitability Analysis', 'ROI Metrics']
  }
];

// State
const selectedReportType = ref<ReportType | null>(null);
const previewReport = ref<ReportGenerationStatus | null>(null);

const reportConfig = ref<ReportConfig>({
  type: 'comprehensive',
  format: 'pdf',
  module: '' as Module,
  dateRange: {
    start: new Date(new Date().getFullYear(), 0, 1),
    end: new Date()
  },
  vessels: [],
  includeCharts: true,
  includeSummary: true,
  includeDetails: true
});

// Mock vessels (in real app, fetch from vessel store)
const availableVessels = ref<string[]>([
  'MV Aurora', 'MV Borealis', 'MV Celestia', 'MV Draco',
  'MV Eclipse', 'MV Frontier', 'MV Galaxy', 'MV Horizon'
]);

// Computed
const canGenerateReport = computed(() => {
  return selectedReportType.value 
    && reportConfig.value.module
    && reportConfig.value.dateRange.start
    && reportConfig.value.dateRange.end;
});

// Methods
function selectReportType(type: ReportType) {
  selectedReportType.value = type;
  reportConfig.value.type = type;
}

function resetConfig() {
  reportConfig.value = {
    type: selectedReportType.value || 'comprehensive',
    format: 'pdf',
    module: '' as Module,
    dateRange: {
      start: new Date(new Date().getFullYear(), 0, 1),
      end: new Date()
    },
    vessels: [],
    includeCharts: true,
    includeSummary: true,
    includeDetails: true
  };
}

async function handleGenerateReport() {
  if (!canGenerateReport.value) return;
  
  await reportsStore.generateReport(reportConfig.value);
}

async function downloadReportFile(reportId: string) {
  await reportsStore.downloadReport(reportId);
}

async function deleteReportFile(reportId: string) {
  if (confirm('Are you sure you want to delete this report?')) {
    await reportsStore.deleteReport(reportId);
  }
}

function showPreview(report: ReportGenerationStatus) {
  if (report.downloadUrl && report.status === 'completed') {
    previewReport.value = report;
  }
}

function closePreview() {
  previewReport.value = null;
}

async function refreshHistory() {
  await reportsStore.fetchReportHistory();
}

function exportFromView(viewName: string) {
  // Navigate to the view and trigger export
  router.push({ name: viewName, query: { action: 'export' } });
}

function getReportTypeLabel(reportId: string): string {
  // Extract report type from ID or use a mapping
  const type = reportTypes.find(t => reportId.includes(t.value));
  return type ? type.label : 'Report';
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// Lifecycle
onMounted(async () => {
  await reportsStore.fetchReportHistory();
});
</script>

<style scoped>
.reports-view {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.reports-header {
  margin-bottom: 2rem;
}

.reports-header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #7f8c8d;
  font-size: 1rem;
}

/* Report Type Selector */
.report-selector-section {
  margin-bottom: 3rem;
}

.report-selector-section h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.report-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.report-card {
  background: white;
  border: 2px solid #e1e8ed;
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.report-card:hover {
  border-color: #3498db;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.1);
  transform: translateY(-2px);
}

.report-card.selected {
  border-color: #3498db;
  background: #ecf6fd;
}

.report-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.report-card h3 {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.report-card p {
  color: #7f8c8d;
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.report-features {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.feature-tag {
  font-size: 0.75rem;
  padding: 0.25rem 0.75rem;
  background: #e8f4f8;
  color: #3498db;
  border-radius: 12px;
}

/* Configuration Form */
.config-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.config-section h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.report-config-form {
  width: 100%;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.form-group input,
.form-group select {
  padding: 0.75rem;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3498db;
}

.vessel-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.vessel-tag {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.vessel-tag:hover {
  border-color: #3498db;
  background: #ecf6fd;
}

.vessel-tag input[type="checkbox"] {
  cursor: pointer;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.5rem 0;
}

.checkbox-label input {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

/* Buttons */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-primary:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

.btn-success {
  background: #27ae60;
  color: white;
}

.btn-success:hover {
  background: #229954;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.btn-outline {
  background: white;
  color: #3498db;
  border: 2px solid #3498db;
}

.btn-outline:hover {
  background: #3498db;
  color: white;
}

.loading-spinner {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Active Reports */
.active-reports-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.active-reports-section h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.active-reports-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.report-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  border: 2px solid #e1e8ed;
}

.report-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.report-info h3 {
  font-size: 1.1rem;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.report-status {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-pending {
  background: #fef5e7;
  color: #f39c12;
}

.status-generating {
  background: #ebf5fb;
  color: #3498db;
}

.status-completed {
  background: #eafaf1;
  color: #27ae60;
}

.status-failed {
  background: #fadbd8;
  color: #e74c3c;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e1e8ed;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  transition: width 0.3s ease;
}

.progress-text {
  font-weight: 600;
  color: #3498db;
  min-width: 45px;
}

/* Preview */
.preview-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.preview-header h2 {
  font-size: 1.5rem;
  color: #2c3e50;
}

.preview-content {
  width: 100%;
  height: 600px;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  overflow: hidden;
}

.preview-iframe {
  width: 100%;
  height: 100%;
}

/* History */
.history-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.history-header h2 {
  font-size: 1.5rem;
  color: #2c3e50;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem 1.5rem;
  border: 2px solid #e1e8ed;
}

.history-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-item-header h4 {
  font-size: 1rem;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.history-item-header small {
  color: #7f8c8d;
  font-size: 0.85rem;
}

.history-actions {
  display: flex;
  gap: 0.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #7f8c8d;
}

/* Quick Export */
.quick-export-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.quick-export-section h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.section-hint {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.quick-export-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.error-text {
  color: #e74c3c;
  font-size: 0.9rem;
}

.report-time {
  color: #7f8c8d;
  font-size: 0.85rem;
}

.report-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
