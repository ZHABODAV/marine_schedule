import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import BaseButton from '../BaseButton.vue';

describe('BaseButton.vue', () => {
  describe('Button Rendering', () => {
    it('should render button with default slot content', () => {
      const wrapper = mount(BaseButton, {
        slots: {
          default: 'Click Me',
        },
      });
      
      expect(wrapper.text()).toBe('Click Me');
      expect(wrapper.find('button').exists()).toBe(true);
    });

    it('should apply default type', () => {
      const wrapper = mount(BaseButton);
      const button = wrapper.find('button').element;
      
      expect(button.type).toBe('button');
    });
  });

  describe('Button Variants', () => {
    it('should apply primary variant class', () => {
      const wrapper = mount(BaseButton, {
        props: { variant: 'primary' },
      });
      
      expect(wrapper.classes()).toContain('btn-primary');
    });

    it('should apply secondary variant class', () => {
      const wrapper = mount(BaseButton, {
        props: { variant: 'secondary' },
      });
      
      expect(wrapper.classes()).toContain('btn-secondary');
    });

    it('should apply danger variant class', () => {
      const wrapper = mount(BaseButton, {
        props: { variant: 'danger' },
      });
      
      expect(wrapper.classes()).toContain('btn-danger');
    });
  });

  describe('Button Sizes', () => {
    it('should apply small size class', () => {
      const wrapper = mount(BaseButton, {
        props: { size: 'small' },
      });
      
      expect(wrapper.classes()).toContain('btn-sm');
    });

    it('should apply large size class', () => {
      const wrapper = mount(BaseButton, {
        props: { size: 'large' },
      });
      
      expect(wrapper.classes()).toContain('btn-lg');
    });
  });

  describe('Button States', () => {
    it('should be disabled when disabled prop is true', () => {
      const wrapper = mount(BaseButton, {
        props: { disabled: true },
      });
      
      const button = wrapper.find('button').element as HTMLButtonElement;
      expect(button.disabled).toBe(true);
      expect(wrapper.classes()).toContain('btn-disabled');
    });

    it('should show loading state', () => {
      const wrapper = mount(BaseButton, {
        props: { loading: true },
      });
      
      expect(wrapper.classes()).toContain('btn-loading');
      expect(wrapper.find('button').element.disabled).toBe(true);
    });
  });

  describe('Button Events', () => {
    it('should emit click event when clicked', async () => {
      const wrapper = mount(BaseButton);
      
      await wrapper.trigger('click');
      
      expect(wrapper.emitted('click')).toBeTruthy();
      expect(wrapper.emitted('click')?.length).toBe(1);
    });

    it('should not emit click when disabled', async () => {
      const wrapper = mount(BaseButton, {
        props: { disabled: true },
      });
      
      await wrapper.trigger('click');
      
      expect(wrapper.emitted('click')).toBeFalsy();
    });

    it('should not emit click when loading', async () => {
      const wrapper = mount(BaseButton, {
        props: { loading: true },
      });
      
      await wrapper.trigger('click');
      
      expect(wrapper.emitted('click')).toBeFalsy();
    });
  });

  describe('Icon Support', () => {
    it('should render icon slot', () => {
      const wrapper = mount(BaseButton, {
        slots: {
          icon: '<svg data-test="icon"></svg>',
        },
      });
      
      expect(wrapper.find('[data-test="icon"]').exists()).toBe(true);
    });

    it('should position icon before text', () => {
      const wrapper = mount(BaseButton, {
        slots: {
          icon: '<span class="icon"></span>',
          default: 'Search',
        },
      });
      
      const html = wrapper.html();
      const iconIndex = html.indexOf('icon');
      const textIndex = html.indexOf('Search');
      
      expect(iconIndex).toBeLessThan(textIndex);
    });
  });

  describe('Full Width', () => {
    it('should apply full width class', () => {
      const wrapper = mount(BaseButton, {
        props: { fullWidth: true },
      });
      
      expect(wrapper.classes()).toContain('btn-block');
    });
  });

  describe('Button Type Attribute', () => {
    it('should set type attribute to submit', () => {
      const wrapper = mount(BaseButton, {
        props: { type: 'submit' },
      });
      
      const button = wrapper.find('button').element;
      expect(button.type).toBe('submit');
    });

    it('should set type attribute to reset', () => {
      const wrapper = mount(BaseButton, {
        props: { type: 'reset' },
      });
      
      const button = wrapper.find('button').element;
      expect(button.type).toBe('reset');
    });
  });
});
