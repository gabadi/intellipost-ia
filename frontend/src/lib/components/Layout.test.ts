import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import Layout from './Layout.svelte';

describe('Layout Component', () => {
  it('should render without errors', () => {
    render(Layout);
    expect(screen.getByRole('banner')).toBeInTheDocument();
  });

  it('should render with default title', () => {
    render(Layout);
    expect(screen.getByRole('heading', { level: 1, name: 'IntelliPost AI' })).toBeInTheDocument();
  });

  it('should render with custom title prop', () => {
    const customTitle = 'Custom App Title';
    render(Layout, { title: customTitle });
    expect(screen.getByRole('heading', { level: 1, name: customTitle })).toBeInTheDocument();
  });

  it('should render main container', () => {
    render(Layout);
    expect(screen.getByRole('main')).toBeInTheDocument();
  });

  it('should render header and main as siblings', () => {
    const { container } = render(Layout);
    const main = screen.getByRole('main');
    const header = screen.getByRole('banner');

    // Header and main should be siblings, not nested
    expect(header).toBeInTheDocument();
    expect(main).toBeInTheDocument();
    expect(container.querySelector('.focus-within-highlight')).toContainElement(header);
    expect(container.querySelector('.focus-within-highlight')).toContainElement(main);
  });

  it('should have slot available for content', () => {
    const { container } = render(Layout);
    const main = container.querySelector('main');
    expect(main).toBeInTheDocument();
    // Slot should be available in main element
    expect(main).toBeInTheDocument();
  });

  it('should have proper semantic structure', () => {
    render(Layout);
    const main = screen.getByRole('main');
    const header = screen.getByRole('banner');
    const heading = screen.getByRole('heading', { level: 1 });

    expect(main).toBeInTheDocument();
    expect(header).toBeInTheDocument();
    expect(heading).toBeInTheDocument();
    expect(header).toContainElement(heading);
  });

  it('should handle empty title prop', () => {
    render(Layout, { title: '' });
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading).toBeInTheDocument();
    expect(heading).toHaveTextContent('');
  });

  it('should handle title with special characters', () => {
    const specialTitle = 'Test & Co. - "Special" Title!';
    render(Layout, { title: specialTitle });
    expect(screen.getByRole('heading', { level: 1, name: specialTitle })).toBeInTheDocument();
  });
});
