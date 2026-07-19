import { render, screen, waitFor, act } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import OpsDashboard from './OpsDashboard';

// Access the shared MockWebSocket from setupTests.ts
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const MockWebSocket = (window as any).__MockWebSocket;

describe('OpsDashboard Component', () => {
  beforeEach(() => {
    MockWebSocket.resetInstances();
  });

  it('renders initial mock data', () => {
    render(<OpsDashboard />);
    expect(screen.getByText('Operations Command Center')).toBeInTheDocument();
    expect(screen.getByText('RECONNECTING...')).toBeInTheDocument();
  });

  it('connects to WebSocket and updates data', async () => {
    render(<OpsDashboard />);

    // The component creates a WebSocket in useEffect — wait for it
    await waitFor(() => {
      expect(MockWebSocket.instances.length).toBeGreaterThan(0);
    });

    const ws = MockWebSocket.instances[0];

    // Simulate the server accepting the connection
    act(() => {
      ws.simulateOpen();
    });

    await waitFor(() => {
      expect(screen.getByText('LIVE SYSTEM ACTIVE')).toBeInTheDocument();
    });

    // Simulate a data push from the server
    act(() => {
      ws.simulateMessage({
        zones: [
          { name: 'North Stand', current_occupancy: 5000, capacity: 10000 },
        ],
        alerts: [
          { level: 'critical', zone_name: 'North Stand', message: 'Too crowded' },
        ],
      });
    });

    await waitFor(() => {
      expect(screen.getByText('5,000')).toBeInTheDocument();
      expect(screen.getByText('Out of 10,000')).toBeInTheDocument();
      expect(screen.getByText('Too crowded')).toBeInTheDocument();
    });
  });
});
