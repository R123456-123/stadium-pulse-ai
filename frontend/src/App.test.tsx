import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';

// ResizeObserver and WebSocket mocks are in setupTests.ts

describe('App Component', () => {
  it('renders the layout with navigation links', () => {
    render(<App />);
    expect(screen.getAllByText(/Fan Assistant/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Ops Dashboard/i).length).toBeGreaterThan(0);
    // Accessibility check: Ensure menu button exists
    expect(screen.getByLabelText('Open mobile menu')).toBeInTheDocument();
  });
});
