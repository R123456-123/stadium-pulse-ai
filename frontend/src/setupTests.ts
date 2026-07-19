import '@testing-library/jest-dom';

// ── DOM API Mocks ───────────────────────────────────────────
// jsdom doesn't implement scrollIntoView
window.HTMLElement.prototype.scrollIntoView = function () {};

// jsdom doesn't implement ResizeObserver (needed by Recharts)
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
window.ResizeObserver = ResizeObserverMock;

// ── WebSocket Mock ──────────────────────────────────────────
// CRITICAL: This MUST live in setupTests.ts, not in individual
// test files. Vitest's module isolation means component code
// runs in the window/globalThis context set up HERE, not in
// the test file's local `global` scope.

interface MockWebSocketInstance {
  url: string;
  readyState: number;
  onopen: ((event: Event) => void) | null;
  onmessage: ((event: MessageEvent) => void) | null;
  onclose: ((event: CloseEvent) => void) | null;
  onerror: ((event: Event) => void) | null;
  send: () => void;
  close: () => void;
}

class MockWebSocket implements MockWebSocketInstance {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  /** Accumulates every instance created by component code. */
  static instances: MockWebSocket[] = [];

  /** Reset between tests to prevent cross-test pollution. */
  static resetInstances(): void {
    MockWebSocket.instances = [];
  }

  url: string;
  readyState: number;
  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    this.readyState = MockWebSocket.CONNECTING;
    MockWebSocket.instances.push(this);
  }

  send(): void {}

  close(): void {
    this.readyState = MockWebSocket.CLOSED;
  }

  // ── Test helpers (not part of real WebSocket API) ────────
  simulateOpen(): void {
    this.readyState = MockWebSocket.OPEN;
    if (this.onopen) this.onopen(new Event('open'));
  }

  simulateMessage(data: Record<string, unknown>): void {
    if (this.onmessage) {
      this.onmessage({ data: JSON.stringify(data) } as MessageEvent);
    }
  }

  simulateClose(): void {
    this.readyState = MockWebSocket.CLOSED;
    if (this.onclose) this.onclose({ code: 1000 } as CloseEvent);
  }
}

// Override window.WebSocket so ALL component code uses our mock
window.WebSocket = MockWebSocket as unknown as typeof WebSocket;

// Expose the class for test files to access instances & helpers
// eslint-disable-next-line @typescript-eslint/no-explicit-any
(window as any).__MockWebSocket = MockWebSocket;
