import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { handleApiError } from '@/services/api';
import type {
  ReportConfig,
  ReportGenerationStatus
} from '@/types/reports.types';
import { useAppStore } from './app';

export const useReportsStore = defineStore('reports', () => {
  // State
  const activeReports = ref<ReportGenerationStatus[]>([]);
  const history = ref<ReportGenerationStatus[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const pendingReports = computed(() =>
    activeReports.value.filter(r => r.status === 'pending' || r.status === 'generating')
  );
  const completedReports = computed(() =>
    activeReports.value.filter(r => r.status === 'completed')
  );
  const failedReports = computed(() =>
    activeReports.value.filter(r => r.status === 'failed')
  );
  const recentReports = computed(() =>
    [...history.value].sort((a, b) =>
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    ).slice(0, 10)
  );

  // Actions
  async function generateReport(config: ReportConfig): Promise<ReportGenerationStatus | null> {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('/api/reports/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      if (!response.ok) throw new Error('Failed to initiate report generation');
      const reportStatus: ReportGenerationStatus = await response.json();
      activeReports.value.push(reportStatus);
      appStore.addNotification({
        type: 'info',
        message: 'Report generation started',
      });
      
      // Poll for status updates
      pollReportStatus(reportStatus.id);
      
      return reportStatus;
    } catch (e: any) {
      error.value = handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message: error.value,
      });
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function fetchReportStatus(reportId: string): Promise<ReportGenerationStatus | null> {
    try {
      const response = await fetch(`/api/reports/${reportId}/status`);
      if (!response.ok) throw new Error('Failed to fetch report status');
      const status: ReportGenerationStatus = await response.json();
      
      // Update active reports
      const index = activeReports.value.findIndex(r => r.id === reportId);
      if (index !== -1) {
        activeReports.value[index] = status;
      }
      
      return status;
    } catch (e: any) {
      error.value = handleApiError(e);
      return null;
    }
  }

  async function pollReportStatus(reportId: string) {
    const appStore = useAppStore();
    const maxAttempts = 60; // 5 minutes max (every 5 seconds)
    let attempts = 0;

    const poll = async () => {
      if (attempts >= maxAttempts) {
        appStore.addNotification({
          type: 'warning',
          message: 'Report generation taking longer than expected',
        });
        return;
      }

      const status = await fetchReportStatus(reportId);
      if (!status) return;

      if (status.status === 'completed') {
        appStore.addNotification({
          type: 'success',
          message: 'Report generated successfully',
        });
        // Move to history after a delay
        setTimeout(() => moveToHistory(reportId), 30000); // 30 seconds
      } else if (status.status === 'failed') {
        appStore.addNotification({
          type: 'error',
          message: status.error || 'Report generation failed',
        });
        setTimeout(() => moveToHistory(reportId), 10000); // 10 seconds
      } else {
        // Continue polling
        attempts++;
        setTimeout(poll, 5000); // Poll every 5 seconds
      }
    };

    poll();
  }

  async function downloadReport(reportId: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch(`/api/reports/${reportId}/download`);
      if (!response.ok) throw new Error('Failed to download report');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      
      // Get filename from Content-Disposition header or use default
      const contentDisposition = response.headers.get('Content-Disposition');
      const filenameMatch = contentDisposition?.match(/filename="?(.+)"?/i);
      const filename = (filenameMatch && filenameMatch[1]) || `report_${reportId}.pdf`;
      
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      appStore.addNotification({
        type: 'success',
        message: 'Report downloaded successfully',
      });
    } catch (e: any) {
      error.value = handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message: error.value,
      });
    } finally {
      loading.value = false;
    }
  }

  async function fetchReportHistory() {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('/api/reports/history');
      if (!response.ok) throw new Error('Failed to fetch report history');
      history.value = await response.json();
    } catch (e: any) {
      error.value = handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message: error.value,
      });
    } finally {
      loading.value = false;
    }
  }

  async function deleteReport(reportId: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch(`/api/reports/${reportId}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete report');
      
      // Remove from active and history
      activeReports.value = activeReports.value.filter(r => r.id !== reportId);
      history.value = history.value.filter(r => r.id !== reportId);
      
      appStore.addNotification({
        type: 'success',
        message: 'Report deleted successfully',
      });
      return true;
    } catch (e: any) {
      error.value = handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message: error.value,
      });
      return false;
    } finally {
      loading.value = false;
    }
  }

  function moveToHistory(reportId: string) {
    const index = activeReports.value.findIndex(r => r.id === reportId);
    if (index !== -1) {
      const report = activeReports.value[index];
      if (report) {
        history.value.unshift(report);
        activeReports.value.splice(index, 1);
      }
    }
  }

  function clearError() {
    error.value = null;
  }

  function clearActiveReports() {
    // Move all to history
    activeReports.value.forEach(report => {
      if (!history.value.find(h => h.id === report.id)) {
        history.value.unshift(report);
      }
    });
    activeReports.value = [];
  }

  return {
    // State
    activeReports,
    history,
    loading,
    error,
    // Getters
    pendingReports,
    completedReports,
    failedReports,
    recentReports,
    // Actions
    generateReport,
    fetchReportStatus,
    downloadReport,
    fetchReportHistory,
    deleteReport,
    moveToHistory,
    clearError,
    clearActiveReports,
  };
});
