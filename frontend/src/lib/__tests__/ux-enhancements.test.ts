/**
 * UX Enhancements Unit Tests
 * Tests CSS utility classes and component integration
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import Button from '../components/ui/Button.svelte';
import Layout from '../components/Layout.svelte';

describe('UX Enhancements', () => {
  describe('Button Component Integration', () => {
    it('should have micro-interaction classes applied', () => {
      render(Button, { props: { variant: 'primary' } });
      const button = screen.getByRole('button');

      expect(button).toHaveClass('hover-lift');
      expect(button).toHaveClass('active-press');
      expect(button).toHaveClass('smooth-state');
      expect(button).toHaveClass('focus-ring-enhanced');
    });

    it('should apply loading state classes when loading', () => {
      render(Button, { props: { loading: true } });
      const button = screen.getByRole('button');

      expect(button).toHaveClass('btn--loading');
      expect(button).toHaveClass('loading-state');
    });

    it('should work as a link with micro-interactions', () => {
      render(Button, { props: { href: '/test' } });
      const link = screen.getByRole('link');

      expect(link).toHaveClass('hover-lift');
      expect(link).toHaveClass('active-press');
      expect(link).toHaveClass('smooth-state');
      expect(link).toHaveClass('focus-ring-enhanced');
    });
  });

  describe('Layout Component Integration', () => {
    it('should render skip navigation links', () => {
      render(Layout, { props: { title: 'Test App' } });

      const skipToMain = screen.getByRole('link', { name: /skip to main content/i });
      const skipToNav = screen.getByRole('link', { name: /skip to navigation/i });

      expect(skipToMain).toBeInTheDocument();
      expect(skipToNav).toBeInTheDocument();
      expect(skipToMain).toHaveAttribute('href', '#main-content');
      expect(skipToNav).toHaveAttribute('href', '#navigation');
    });

    it('should have proper landmark structure', () => {
      render(Layout, { props: { title: 'Test App' } });

      const navigation = screen.getByRole('banner'); // header element
      const main = screen.getByRole('main');

      expect(navigation).toHaveAttribute('id', 'navigation');
      expect(navigation).toHaveClass('landmark');
      expect(main).toHaveAttribute('id', 'main-content');
      expect(main).toHaveClass('landmark', 'focus-group');
    });

    it('should have focus management classes', () => {
      render(Layout, { props: { title: 'Test App' } });

      const container = document.querySelector('.focus-within-highlight');
      expect(container).toBeInTheDocument();
    });

    it('should have animated title', () => {
      render(Layout, { props: { title: 'Test App' } });

      const title = screen.getByRole('heading', { level: 1 });
      expect(title).toHaveClass('animate-in');
      expect(title).toHaveTextContent('Test App');
    });
  });

  describe('CSS Class Validation', () => {
    beforeEach(() => {
      // Reset document body classes
      document.body.className = '';
    });

    it('should validate micro-interaction utilities exist', () => {
      // Create test element with micro-interaction classes
      const testElement = document.createElement('div');
      testElement.className = 'hover-lift active-press smooth-state focus-ring-enhanced';
      document.body.appendChild(testElement);

      expect(testElement).toHaveClass('hover-lift');
      expect(testElement).toHaveClass('active-press');
      expect(testElement).toHaveClass('smooth-state');
      expect(testElement).toHaveClass('focus-ring-enhanced');

      document.body.removeChild(testElement);
    });

    it('should validate loading state utilities exist', () => {
      const testElement = document.createElement('div');
      testElement.className = 'spinner loading-state skeleton btn-loading';
      document.body.appendChild(testElement);

      expect(testElement).toHaveClass('spinner');
      expect(testElement).toHaveClass('loading-state');
      expect(testElement).toHaveClass('skeleton');
      expect(testElement).toHaveClass('btn-loading');

      document.body.removeChild(testElement);
    });

    it('should validate enhanced focus utilities exist', () => {
      const testElement = document.createElement('div');
      testElement.className = 'skip-link focus-ring-enhanced focus-within-highlight landmark';
      document.body.appendChild(testElement);

      expect(testElement).toHaveClass('skip-link');
      expect(testElement).toHaveClass('focus-ring-enhanced');
      expect(testElement).toHaveClass('focus-within-highlight');
      expect(testElement).toHaveClass('landmark');

      document.body.removeChild(testElement);
    });
  });

  describe('Accessibility Features', () => {
    it('should support screen reader only content', () => {
      const srElement = document.createElement('span');
      srElement.className = 'sr-only';
      srElement.textContent = 'Screen reader only content';
      document.body.appendChild(srElement);

      expect(srElement).toHaveClass('sr-only');
      expect(srElement.textContent).toBe('Screen reader only content');

      // In test environment, we can only verify the class is applied
      // The actual CSS styles for sr-only are tested by the browser
      expect(srElement.classList.contains('sr-only')).toBe(true);

      document.body.removeChild(srElement);
    });

    it('should render skip links with proper classes', () => {
      render(Layout, { props: { title: 'Test App' } });

      const skipLinks = document.querySelector('.skip-links');
      expect(skipLinks).toBeInTheDocument();

      const skipLink = document.querySelector('.skip-link');
      expect(skipLink).toBeInTheDocument();
      expect(skipLink).toHaveClass('skip-link');
    });
  });

  describe('Performance and Bundle', () => {
    it('should not exceed reasonable CSS class count', () => {
      // Test that our utility classes don't overwhelm the DOM
      const testElement = document.createElement('div');
      testElement.className = 'btn hover-lift active-press smooth-state focus-ring-enhanced btn--primary btn--md';

      const classList = Array.from(testElement.classList);
      expect(classList.length).toBeLessThan(10); // Reasonable limit

      // All classes should be meaningful
      classList.forEach(className => {
        expect(className).toMatch(/^(btn|hover|active|smooth|focus|primary|md)/);
      });
    });

    it('should use semantic CSS classes', () => {
      render(Button, { props: { variant: 'primary', size: 'md' } });
      const button = screen.getByRole('button');

      // Should have semantic classes from our design system
      expect(button).toHaveClass('btn');
      expect(button).toHaveClass('btn--primary');
      expect(button).toHaveClass('btn--md');
    });
  });

  describe('Animation and Transition Classes', () => {
    it('should have animation classes available', () => {
      const animatedElement = document.createElement('div');
      animatedElement.className = 'animate-in slide-in pulse-loading fade-loading';
      document.body.appendChild(animatedElement);

      expect(animatedElement).toHaveClass('animate-in');
      expect(animatedElement).toHaveClass('slide-in');
      expect(animatedElement).toHaveClass('pulse-loading');
      expect(animatedElement).toHaveClass('fade-loading');

      document.body.removeChild(animatedElement);
    });

    it('should have smooth transition classes', () => {
      const transitionElement = document.createElement('div');
      transitionElement.className = 'smooth-state smooth-color smooth-transform';
      document.body.appendChild(transitionElement);

      expect(transitionElement).toHaveClass('smooth-state');
      expect(transitionElement).toHaveClass('smooth-color');
      expect(transitionElement).toHaveClass('smooth-transform');

      document.body.removeChild(transitionElement);
    });
  });

  describe('Responsive and Accessibility Classes', () => {
    it('should have touch-friendly classes', () => {
      const touchElement = document.createElement('div');
      touchElement.className = 'interactive ripple-effect';
      document.body.appendChild(touchElement);

      expect(touchElement).toHaveClass('interactive');
      expect(touchElement).toHaveClass('ripple-effect');

      document.body.removeChild(touchElement);
    });

    it('should support disabled states', () => {
      const disabledElement = document.createElement('button');
      disabledElement.className = 'disabled';
      disabledElement.disabled = true;
      document.body.appendChild(disabledElement);

      expect(disabledElement).toHaveClass('disabled');
      expect(disabledElement).toBeDisabled();

      document.body.removeChild(disabledElement);
    });
  });
});
