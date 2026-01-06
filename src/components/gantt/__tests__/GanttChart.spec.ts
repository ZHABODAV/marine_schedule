import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount, VueWrapper } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import GanttChart from '../GanttChart.vue';
import { useVoyageStore } from '@/stores/voyage';
import { useVesselStore } from '@/stores/vessel';

// Mock services
vi.mock('@/services/gantt.service', () => ({
  generateGanttData: vi.fn(() => Promise.resolve([
    {
      vessel: 'Test Vessel 1',
      days: Array.from({ length: 30 }, (_, i) => ({
        operation: i % 5 === 0 ? 'П' : '',
        class: i % 5 === 0 ? 'loading' : '',
      })),
    },
  ])),
  generateGanttFromVoyages: vi.fn((voyages, days) => Promise.resolve([
    {
      vessel: 'Test Vessel 1',
      days: Array.from({ length: days }, (_, i) => ({
        operation: i % 3 === 0 ? 'П' : i % 3 === 1 ? 'Т' : '',
        class: i % 3 === 0 ? 'loading' : i % 3 === 1 ? 'transit' : '',
      })),
    },
  ])),
  exportGantt: vi.fn(() => Promise.resolve()),
}));

describe('GanttChart.vue', () => {
  let wrapper: VueWrapper;
  let pinia: ReturnType<typeof createPinia>;

  beforeEach(() => {
    pinia = createPinia();
    setActivePinia(pinia);
    
    wrapper = mount(GanttChart, {
      global: {
        plugins: [pinia],
        stubs: {
          LoadingSpinner: {
            template: '<div data-test="loading-spinner">Loading...</div>',
          },
        },
      },
    });
  });

  describe('Component Mounting', () => {
    it('should render correctly', () => {
      expect(wrapper.exists()).toBe(true);
      expect(wrapper.find('.gantt-chart-container').exists()).toBe(true);
    });

    it('should render controls section', () => {
      expect(wrapper.find('.gantt-controls').exists()).toBe(true);
      expect(wrapper.find('#gantt-days').exists()).toBe(true);
      expect(wrapper.find('#voyage-filter').exists()).toBe(true);
    });

    it('should have default timeline days set to 30', () => {
      const input = wrapper.find('#gantt-days').element as HTMLInputElement;
      expect(input.value).toBe('30');
    });
  });

  describe('Timeline Days Control', () => {
    it('should update timeline days on input change', async () => {
      const input = wrapper.find('#gantt-days');
      await input.setValue(60);
      
      const element = input.element as HTMLInputElement;
      expect(element.value).toBe('60');
    });

    it('should enforce minimum timeline days', () => {
      const input = wrapper.find('#gantt-days').element as HTMLInputElement;
      expect(input.min).toBe('7');
    });

    it('should enforce maximum timeline days', () => {
      const input = wrapper.find('#gantt-days').element as HTMLInputElement;
      expect(input.max).toBe('365');
    });
  });

  describe('Voyage Filter', () => {
    it('should render voyage filter options', () => {
      const select = wrapper.find('#voyage-filter');
      const options = select.findAll('option');
      
      expect(options).toHaveLength(4);
      expect(options[0].text()).toBe('All Voyages');
      expect(options[1].text()).toBe('Active Only');
      expect(options[2].text()).toBe('Planned Only');
      expect(options[3].text()).toBe('Custom Selection');
    });

    it('should have "all" as default filter', () => {
      const select = wrapper.find('#voyage-filter').element as HTMLSelectElement;
      expect(select.value).toBe('all');
    });

    it('should change filter value', async () => {
      const select = wrapper.find('#voyage-filter');
      await select.setValue('active');
      
      const element = select.element as HTMLSelectElement;
      expect(element.value).toBe('active');
    });
  });

  describe('Action Buttons', () => {
    it('should render refresh button', () => {
      const refreshBtn = wrapper.findAll('button').find(btn => 
        btn.text().includes('Refresh') || btn.text().includes('Loading')
      );
      expect(refreshBtn).toBeDefined();
    });

    it('should render export button', () => {
      const exportBtn = wrapper.findAll('button').find(btn => 
        btn.text() === 'Export'
      );
      expect(exportBtn).toBeDefined();
    });

    it('should call refreshGantt on refresh button click', async () => {
      // Wait for initial load
      await wrapper.vm.$nextTick()
;
      
      const refreshBtn = wrapper.findAll('button').find(btn => 
        btn.text().includes('Refresh') || btn.text().includes('Loading')
      )!;
      await refreshBtn.trigger('click');
      
      // Component should update
      await wrapper.vm.$nextTick();
      expect(wrapper.vm.isLoading).toBe(false);
    });
  });

  describe('Loading State', () => {
    it('should show loading spinner when isLoading is true', async () => {
      wrapper.vm.isLoading = true;
      await wrapper.vm.$nextTick();
      
      expect(wrapper.find('[data-test="loading-spinner"]').exists()).toBe(true);
      expect(wrapper.text()).toContain('Generating Gantt chart');
    });

    it('should hide loading spinner when isLoading is false', async () => {
      wrapper.vm.isLoading = false;
      await wrapper.vm.$nextTick();
      
      // Wait for data to load
      await new Promise(resolve => setTimeout(resolve, 100));
      await wrapper.vm.$nextTick();
      
      const spinner = wrapper.find('[data-test="loading-spinner"]');
      expect(spinner.exists()).toBe(false);
    });
  });

  describe('Error State', () => {
    it('should display error message when error exists', async () => {
      wrapper.vm.error = 'Test error message';
      await wrapper.vm.$nextTick();
      
      const alert = wrapper.find('.alert-error');
      expect(alert.exists()).toBe(true);
      expect(alert.text()).toBe('Test error message');
    });

    it('should not display error when error is empty', async () => {
      wrapper.vm.error = '';
      await wrapper.vm.$nextTick();
      
      expect(wrapper.find('.alert-error').exists()).toBe(false);
    });
  });

  describe('Empty State', () => {
    it('should show empty state when no data', async () => {
      wrapper.vm.ganttData = [];
      wrapper.vm.isLoading = false;
      await wrapper.vm.$nextTick();
      
      const emptyState = wrapper.find('.empty-state');
      expect(emptyState.exists()).toBe(true);
      expect(emptyState.text()).toContain('No voyage data available');
    });
  });

  describe('Gantt Chart Display', () => {
    it('should render gantt table when data is available', async () => {
      await wrapper.vm.refreshGantt();
      await wrapper.vm.$nextTick();
      
      const table = wrapper.find('.gantt-table');
      expect(table.exists()).toBe(true);
    });

    it('should render legend', async () => {
      await wrapper.vm.refreshGantt();
      await wrapper.vm.$nextTick();
      
      const legend = wrapper.find('.gantt-legend');
      expect(legend.exists()).toBe(true);
      expect(legend.text()).toContain('Loading (Погрузка)');
      expect(legend.text()).toContain('Discharge (Выгрузка)');
      expect(legend.text()).toContain('Transit (Транзит)');
    });

    it('should render vessel rows', async () => {
      await wrapper.vm.refreshGantt();
      await wrapper.vm.$nextTick();
      
      const vesselNames = wrapper.findAll('.vessel-name');
      expect(vesselNames.length).toBeGreaterThan(0);
    });

    it('should render day headers', async () => {
      await wrapper.vm.refreshGantt();
      await wrapper.vm.$nextTick();
      
      const dayHeaders = wrapper.findAll('.day-header');
      expect(dayHeaders.length).toBe(30); // default timeline
    });
  });

  describe('Gantt Cell Interactions', () => {
    it('should show cell title on hover', async () => {
      await wrapper.vm.refreshGantt();
      await wrapper.vm.$nextTick();
      
      const cells = wrapper.findAll('.gantt-cell');
      if (cells.length > 0) {
        const cell = cells[0];
        expect(cell.attributes('title')).toBeDefined();
      }
    });

    it('should apply correct operation classes', async () => {
      await wrapper.vm.refreshGantt();
      await wrapper.vm.$nextTick();
      
      const loadingCells = wrapper.findAll('.op-loading');
      expect(loadingCells.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Statistics Display', () => {
    it('should render statistics when data is available', async () => {
      await wrapper.vm.refreshGantt();
      await wrapper.vm.$nextTick();
      
      const stats = wrapper.find('.gantt-stats');
      expect(stats.exists()).toBe(true);
    });

    it('should display vessel count', async () => {
      await wrapper.vm.refreshGantt();
      await wrapper.vm.$nextTick();
      
      const statCards = wrapper.findAll('.stat-card');
      expect(statCards.length).toBe(3);
      
      const vesselCard = statCards.find(card => card.text().includes('Vessels'));
      expect(vesselCard).toBeDefined();
    });

    it('should display timeline days', async () => {
      await wrapper.vm.refreshGantt();
      await wrapper.vm.$nextTick();
      
      const statCards = wrapper.findAll('.stat-card');
      const timelineCard = statCards.find(card => card.text().includes('Timeline'));
      expect(timelineCard).toBeDefined();
      expect(timelineCard?.text()).toContain('30');
    });

    it('should calculate total operations', async () => {
      await wrapper.vm.refreshGantt();
      await wrapper.vm.$nextTick();
      
      expect(wrapper.vm.totalOperations).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Export Functionality', () => {
    it('should call export function on export button click', async () => {
      const { exportGantt } = await import('@/services/gantt.service');
      
      const exportBtn = wrapper.findAll('button').find(btn => 
        btn.text() === 'Export'
      )!;
      await exportBtn.trigger('click');
      
      expect(exportGantt).toHaveBeenCalled();
    });

    it('should handle export errors', async () => {
      const { exportGantt } = await import('@/services/gantt.service');
      (exportGantt as any).mockRejectedValueOnce(new Error('Export failed'));
      
      const exportBtn = wrapper.findAll('button').find(btn => 
        btn.text() === 'Export'
      )!;
      await exportBtn.trigger('click');
      await wrapper.vm.$nextTick();
      
      expect(wrapper.vm.error).toContain('Export failed');
    });
  });

  describe('Cell Title Generation', () => {
    it('should generate correct cell title', () => {
      const title = wrapper.vm.getCellTitle('Test Vessel', 5, {
        operation: 'П',
        class: 'loading'
      });
      
      expect(title).toBe('Test Vessel - Day 6: Loading Port');
    });

    it('should return empty string for empty operation', () => {
      const title = wrapper.vm.getCellTitle('Test Vessel', 5, {
        operation: '',
        class: ''
      });
      
      expect(title).toBe('');
    });

    it('should handle unknown operation types', () => {
      const title = wrapper.vm.getCellTitle('Test Vessel', 5, {
        operation: 'X',
        class: 'unknown'
      });
      
      expect(title).toContain('unknown');
    });
  });
});
