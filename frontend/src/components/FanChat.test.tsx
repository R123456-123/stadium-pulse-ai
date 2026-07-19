import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import FanChat from './FanChat';

// Mock fetch for the API calls
const fetchMock = vi.fn();
global.fetch = fetchMock;

describe('FanChat Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the chat interface with initial message', () => {
    render(<FanChat />);
    expect(screen.getByText('Pulse Assistant')).toBeInTheDocument();
    expect(screen.getByText(/Hi! I am Pulse/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Ask me about restrooms/i)).toBeInTheDocument();
  });

  it('sends a message and displays loading state', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ reply: 'The nearest restroom is at Gate 3.' }),
    });

    render(<FanChat />);
    const input = screen.getByPlaceholderText(/Ask me about restrooms/i);
    const sendButton = screen.getByLabelText('Send message');

    fireEvent.change(input, { target: { value: 'Where is the restroom?' } });
    fireEvent.click(sendButton);

    // Should show user message
    expect(screen.getByText('Where is the restroom?')).toBeInTheDocument();
    // Should show loading state
    expect(screen.getByText('Pulse is thinking...')).toBeInTheDocument();

    // Wait for response to render
    await waitFor(() => {
      expect(screen.getByText('The nearest restroom is at Gate 3.')).toBeInTheDocument();
    });
  });

  it('handles quick action buttons', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ reply: 'Restrooms are everywhere.' }),
    });

    render(<FanChat />);
    const quickBtn = screen.getByLabelText('Ask about restrooms');
    
    fireEvent.click(quickBtn);

    // Should immediately show the quick action text
    expect(screen.getByText('Where is the nearest restroom?')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('Restrooms are everywhere.')).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    fetchMock.mockRejectedValueOnce(new Error('Network error'));

    render(<FanChat />);
    const input = screen.getByPlaceholderText(/Ask me about restrooms/i);
    const sendButton = screen.getByLabelText('Send message');

    fireEvent.change(input, { target: { value: 'Test error' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/Sorry, I'm having trouble connecting/i)).toBeInTheDocument();
    });
  });
});
