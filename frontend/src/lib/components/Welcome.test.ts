import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import Welcome from './Welcome.svelte';

describe('Welcome Component', () => {
  it('should render without errors', () => {
    render(Welcome);
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
  });

  it('should render with default app name', () => {
    render(Welcome);
    expect(screen.getByRole('heading', { level: 1, name: 'IntelliPost AI' })).toBeInTheDocument();
  });

  it('should render with default subtitle', () => {
    render(Welcome);
    expect(screen.getByText('AI-Powered MercadoLibre Listing Assistant')).toBeInTheDocument();
  });

  it('should render with custom app name prop', () => {
    const customAppName = 'Custom App Name';
    render(Welcome, { appName: customAppName });
    expect(screen.getByRole('heading', { level: 1, name: customAppName })).toBeInTheDocument();
  });

  it('should render with custom subtitle prop', () => {
    const customSubtitle = 'Custom Subtitle Text';
    render(Welcome, { subtitle: customSubtitle });
    expect(screen.getByText(customSubtitle)).toBeInTheDocument();
  });

  it('should render both custom props together', () => {
    const customAppName = 'My Custom App';
    const customSubtitle = 'My Custom Subtitle';
    render(Welcome, { appName: customAppName, subtitle: customSubtitle });
    expect(screen.getByRole('heading', { level: 1, name: customAppName })).toBeInTheDocument();
    expect(screen.getByText(customSubtitle)).toBeInTheDocument();
  });

  it('should render description text', () => {
    render(Welcome);
    expect(
      screen.getByText(/Transform your product images into compelling MercadoLibre listings/)
    ).toBeInTheDocument();
  });

  it('should render features list', () => {
    render(Welcome);
    const featuresList = screen.getByRole('list');
    expect(featuresList).toBeInTheDocument();
  });

  it('should render all feature items', () => {
    render(Welcome);
    const features = [
      '📸 Image upload and processing',
      '🤖 AI-generated titles and descriptions',
      '🛍️ Direct MercadoLibre integration',
      '📊 Performance analytics',
    ];

    features.forEach(feature => {
      expect(screen.getByText(feature)).toBeInTheDocument();
    });
  });

  it('should have correct number of feature items', () => {
    render(Welcome);
    const listItems = screen.getAllByRole('listitem');
    expect(listItems).toHaveLength(4);
  });

  it('should have welcome container with correct class', () => {
    const { container } = render(Welcome);
    const welcomeDiv = container.querySelector('.welcome');
    expect(welcomeDiv).toBeInTheDocument();
  });

  it('should have subtitle with correct class', () => {
    const { container } = render(Welcome);
    const subtitleElement = container.querySelector('.subtitle');
    expect(subtitleElement).toBeInTheDocument();
    expect(subtitleElement).toHaveTextContent('AI-Powered MercadoLibre Listing Assistant');
  });

  it('should have description with correct class', () => {
    const { container } = render(Welcome);
    const descriptionElement = container.querySelector('.description');
    expect(descriptionElement).toBeInTheDocument();
    expect(descriptionElement).toHaveTextContent(/Transform your product images/);
  });

  it('should have features container with correct class', () => {
    const { container } = render(Welcome);
    const featuresDiv = container.querySelector('.features');
    expect(featuresDiv).toBeInTheDocument();
  });

  it('should handle empty app name prop', () => {
    render(Welcome, { appName: '' });
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading).toBeInTheDocument();
    expect(heading).toHaveTextContent('');
  });

  it('should handle empty subtitle prop', () => {
    render(Welcome, { subtitle: '' });
    const { container } = render(Welcome, { subtitle: '' });
    const subtitleElement = container.querySelector('.subtitle');
    expect(subtitleElement).toHaveTextContent('');
  });

  it('should have proper semantic structure', () => {
    render(Welcome);
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    expect(screen.getByRole('list')).toBeInTheDocument();
    expect(screen.getAllByRole('listitem')).toHaveLength(4);
  });
});
