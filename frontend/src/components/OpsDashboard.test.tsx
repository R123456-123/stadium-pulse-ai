import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import OpsDashboard from './OpsDashboard';

// Mock ResizeObserver for Recharts
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
global.ResizeObserver = ResizeObserverMock;

// Mock WebSocket
class MockWebSocket {
  onopen: any;
  onmessage: any;
  onclose: any;
  onerror: any;
  readyState: number;

  static instances: MockWebSocket[] = [];

  constructor(public url: string) {
    this.readyState = 0; // CONNECTING
    MockWebSocket.instances.push(this);
    
    // Auto-connect
    setTimeout(() => {
      this.readyState = 1; // OPEN
      if (this.onopen) this.onopen();
    }, 10);
  }

  close() {
    this.readyState = 3; // CLOSED
    if (this.onclose) this.onclose();
  }

  send() {}
  
  // Helper to trigger message from outside
  triggerMessage(data: any) {
    if (this.onmessage) {
      this.onmessage({ data: JSON.stringify(data) });
    }
  }
}

global.WebSocket = MockWebSocket as any;

describe('OpsDashboard Component', () => {
  beforeEach(() => {
    MockWebSocket.instances = [];
    vi.clearAllMocks();
  });

  it('renders initial mock data', () => {
    render(<OpsDashboard />);
    expect(screen.getByText('Operations Command Center')).toBeInTheDocument();
    expect(screen.getByText('RECONNECTING...')).toBeInTheDocument(); // Initially connecting
  });

  it('connects to WebSocket and updates data', async () => {
    render(<OpsDashboard />);
    
    // Wait for connection to establish
    await waitFor(() => {
      expect(screen.getByText('LIVE SYSTEM ACTIVE')).toBeInTheDocument();
    });

    const ws = MockWebSocket.instances[0];
    
    // Trigger message
    ws.triggerMessage({
      zones: [
        { name: 'North Stand', current_occupancy: 5000, capacity: 10000 }
      ],
      alerts: [
        { level: 'critical', zone_name: 'North Stand', message: 'Too crowded' }
      ]
    });

    await waitFor(() => {
      expect(screen.getByText('5,000')).toBeInTheDocument(); // total occupancy updated
      expect(screen.getByText('Out of 10,000')).toBeInTheDocument();
      expect(screen.getByText('Too crowded')).toBeInTheDocument();
    });
  });
});
