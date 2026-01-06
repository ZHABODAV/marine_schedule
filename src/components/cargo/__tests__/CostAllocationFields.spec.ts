import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import CostAllocationFields from '../CostAllocationFields.vue';
import type { CostAllocation } from '@/types/cargo.types';

describe('CostAllocationFields.vue', () => {
  let wrapper: any;

  beforeEach(() => {
    wrapper = mount(CostAllocationFields);
  });

  describe('Component Rendering', () => {
    it('renders the component correctly', () => {
      expect(wrapper.find('.cost-allocation-fields').exists()).toBe(true);
    });

    it('renders all cost input fields', () => {
      expect(wrapper.find('#operational-cost').exists()).toBe(true);
      expect(wrapper.find('#overhead-cost').exists()).toBe(true);
      expect(wrapper.find('#other-cost').exists()).toBe(true);
    });

    it('renders total cost display', () => {
      expect(wrapper.find('.total-cost-display').exists()).toBe(true);
      expect(wrapper.find('.total-cost-value').exists()).toBe(true);
    });
  });

  describe('Cost Calculation', () => {
    it('calculates total cost correctly with all positive values', async () => {
      const wrapper = mount(CostAllocationFields, {
        props: {
          modelValue: {
            operationalCost: 1000,
            overheadCost: 500,
            otherCost: 250,
            totalCost: 0,
          },
        },
      });

      await wrapper.vm.$nextTick();
      
      // Total should be 1750
      expect(wrapper.vm.totalCost).toBe(1750);
    });

    it('calculates total cost correctly with zero values', async () => {
      const wrapper = mount(CostAllocationFields, {
        props: {
          modelValue: {
            operationalCost: 0,
            overheadCost: 0,
            otherCost: 0,
            totalCost: 0,
          },
        },
      });

      await wrapper.vm.$nextTick();
      
      expect(wrapper.vm.totalCost).toBe(0);
    });

    it('calculates total cost with only operational cost', async () => {
      const wrapper = mount(CostAllocationFields, {
        props: {
          modelValue: {
            operationalCost: 2500,
            overheadCost: 0,
            otherCost: 0,
            totalCost: 0,
          },
        },
      });

      await wrapper.vm.$nextTick();
      
      expect(wrapper.vm.totalCost).toBe(2500);
    });

    it('handles decimal cost values correctly', async () => {
      const wrapper = mount(CostAllocationFields, {
        props: {
          modelValue: {
            operationalCost: 1000.50,
            overheadCost: 250.25,
            otherCost: 100.75,
            totalCost: 0,
          },
        },
      });

      await wrapper.vm.$nextTick();
      
      expect(wrapper.vm.totalCost).toBe(1351.50);
    });
  });

  describe('Validation', () => {
    it('validates negative operational cost', async () => {
      const wrapper = mount(CostAllocationFields);
      
      wrapper.vm.localCosts.operationalCost = -100;
      const isValid = wrapper.vm.validateCosts();
      
      expect(isValid).toBe(false);
      expect(wrapper.vm.errors.operationalCost).toBe('Operational cost cannot be negative');
    });

    it('validates negative overhead cost', async () => {
      const wrapper = mount(CostAllocationFields);
      
      wrapper.vm.localCosts.overheadCost = -50;
      const isValid = wrapper.vm.validateCosts();
      
      expect(isValid).toBe(false);
      expect(wrapper.vm.errors.overheadCost).toBe('Overhead cost cannot be negative');
    });

    it('validates negative other cost', async () => {
      const wrapper = mount(CostAllocationFields);
      
      wrapper.vm.localCosts.otherCost = -25;
      const isValid = wrapper.vm.validateCosts();
      
      expect(isValid).toBe(false);
      expect(wrapper.vm.errors.otherCost).toBe('Other cost cannot be negative');
    });

    it('validates all positive costs', async () => {
      const wrapper = mount(CostAllocationFields);
      
      wrapper.vm.localCosts = {
        operationalCost: 1000,
        overheadCost: 500,
        otherCost: 250,
        totalCost: 0,
      };
      const isValid = wrapper.vm.validateCosts();
      
      expect(isValid).toBe(true);
      expect(Object.keys(wrapper.vm.errors)).toHaveLength(0);
    });
  });

  describe('Events', () => {
    it('emits update:modelValue when costs change', async () => {
      const wrapper = mount(CostAllocationFields);
      
      wrapper.vm.localCosts = {
        operationalCost: 1000,
        overheadCost: 500,
        otherCost: 250,
        totalCost: 0,
      };
      
      await wrapper.vm.$nextTick();
      wrapper.vm.handleCostChange();
      
      expect(wrapper.emitted('update:modelValue')).toBeTruthy();
      const emitted = wrapper.emitted('update:modelValue');
      if (!emitted || !emitted[0]) throw new Error('Event not emitted');
      const emittedValue = emitted[0][0] as CostAllocation;
      expect(emittedValue.operationalCost).toBe(1000);
      expect(emittedValue.overheadCost).toBe(500);
      expect(emittedValue.otherCost).toBe(250);
      expect(emittedValue.totalCost).toBe(1750);
    });

    it('emits validation-change event', async () => {
      const wrapper = mount(CostAllocationFields);
      
      await wrapper.vm.$nextTick();
      
      expect(wrapper.emitted('validation-change')).toBeTruthy();
    });
  });

  describe('Currency Formatting', () => {
    it('formats currency correctly', () => {
      const wrapper = mount(CostAllocationFields);
      
      expect(wrapper.vm.formatCurrency(1000)).toBe('1,000.00');
      expect(wrapper.vm.formatCurrency(1234.56)).toBe('1,234.56');
      expect(wrapper.vm.formatCurrency(0)).toBe('0.00');
    });
  });

  describe('Reset Functionality', () => {
    it('resets costs to zero', async () => {
      const wrapper = mount(CostAllocationFields, {
        props: {
          modelValue: {
            operationalCost: 1000,
            overheadCost: 500,
            otherCost: 250,
            totalCost: 1750,
          },
        },
      });

      wrapper.vm.resetCosts();
      
      expect(wrapper.vm.localCosts.operationalCost).toBe(0);
      expect(wrapper.vm.localCosts.overheadCost).toBe(0);
      expect(wrapper.vm.localCosts.otherCost).toBe(0);
      expect(wrapper.vm.localCosts.totalCost).toBe(0);
      expect(Object.keys(wrapper.vm.errors)).toHaveLength(0);
    });
  });

  describe('Props Handling', () => {
    it('initializes with provided modelValue', async () => {
      const initialValue: CostAllocation = {
        operationalCost: 1500,
        overheadCost: 750,
        otherCost: 350,
        totalCost: 2600,
      };

      const wrapper = mount(CostAllocationFields, {
        props: {
          modelValue: initialValue,
        },
      });

      await wrapper.vm.$nextTick();

      expect(wrapper.vm.localCosts.operationalCost).toBe(1500);
      expect(wrapper.vm.localCosts.overheadCost).toBe(750);
      expect(wrapper.vm.localCosts.otherCost).toBe(350);
    });

    it('handles null modelValue', async () => {
      const wrapper = mount(CostAllocationFields, {
        props: {
          modelValue: null,
        },
      });

      await wrapper.vm.$nextTick();

      expect(wrapper.vm.localCosts.operationalCost).toBe(0);
      expect(wrapper.vm.localCosts.overheadCost).toBe(0);
      expect(wrapper.vm.localCosts.otherCost).toBe(0);
      expect(wrapper.vm.localCosts.totalCost).toBe(0);
    });
  });

  describe('CSS Classes', () => {
    it('applies has-value class when total cost is greater than zero', async () => {
      const wrapper = mount(CostAllocationFields, {
        props: {
          modelValue: {
            operationalCost: 1000,
            overheadCost: 0,
            otherCost: 0,
            totalCost: 0,
          },
        },
      });

      await wrapper.vm.$nextTick();

      const totalCostElement = wrapper.find('.total-cost-value');
      expect(totalCostElement.classes()).toContain('has-value');
    });

    it('does not apply has-value class when total cost is zero', async () => {
      const wrapper = mount(CostAllocationFields, {
        props: {
          modelValue: {
            operationalCost: 0,
            overheadCost: 0,
            otherCost: 0,
            totalCost: 0,
          },
        },
      });

      await wrapper.vm.$nextTick();

      const totalCostElement = wrapper.find('.total-cost-value');
      expect(totalCostElement.classes()).not.toContain('has-value');
    });
  });
});
