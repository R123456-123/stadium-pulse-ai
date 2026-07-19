import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Navigation, Clock, Utensils, ShieldQuestion } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './FanChat.css';

interface Message {
  id: string;
  role: 'user' | 'model';
  content: string;
  isTyping?: boolean;
}

const FanChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'model',
      content: 'Hi! I am Pulse, your Continental Park Stadium assistant. How can I help you today?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const API_URL = import.meta.env.VITE_API_URL || 'https://stadium-pulse-ai-t33k.onrender.com';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (messageText?: string) => {
    const textToSend = typeof messageText === 'string' ? messageText : input;
    if (!textToSend.trim() || isLoading) return;

    if (typeof messageText !== 'string') {
        setInput('');
    }
    
    // Add user message
    const newUserMsg: Message = { id: Date.now().toString(), role: 'user', content: textToSend.trim() };
    setMessages(prev => [...prev, newUserMsg]);
    setIsLoading(true);

    try {
      const history = messages
        .filter(m => m.id !== 'welcome')
        .map(m => ({ role: m.role, content: m.content }));

      const response = await fetch(`${API_URL}/api/v1/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: textToSend.trim(), history })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      
      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'model',
        content: data.reply
      };
      setMessages(prev => [...prev, botMsg]);
    } catch {
      // Intentionally swallowing error to show user-friendly message
      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'model',
        content: "Sorry, I'm having trouble connecting to the server right now."
      };
      setMessages(prev => [...prev, botMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSend();
  };

  return (
    <main className="chat-container glass-panel" aria-label="Fan Assistant Chat">
      <header className="chat-header">
        <div className="avatar bot-avatar" aria-hidden="true">
          <Bot size={24} />
        </div>
        <div>
          <h2 id="chat-heading">Pulse Assistant</h2>
          <p className="status" aria-live="polite">
            <span className="status-dot"></span> Online and ready to help
          </p>
        </div>
      </header>

      <section 
        className="messages-area" 
        aria-labelledby="chat-heading"
        aria-live="polite" 
        aria-relevant="additions"
      >
        {messages.map((msg) => (
          <article key={msg.id} className={`message-wrapper ${msg.role}`}>
            <div className={`avatar ${msg.role === 'model' ? 'bot-avatar' : 'user-avatar'}`} aria-hidden="true">
              {msg.role === 'model' ? <Bot size={18} /> : <User size={18} />}
            </div>
            <div className={`message-bubble ${msg.role} markdown-content`}>
              {msg.role === 'model' ? (
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              ) : (
                msg.content
              )}
            </div>
          </article>
        ))}
        {isLoading && (
          <article className="message-wrapper model">
            <div className="avatar bot-avatar" aria-hidden="true">
              <Bot size={18} />
            </div>
            <div className="message-bubble model typing" aria-label="Pulse is typing">
              <Loader2 size={16} className="spinner" />
              <span>Pulse is thinking...</span>
            </div>
          </article>
        )}
        <div ref={messagesEndRef} />
      </section>

      <div className="chat-input-container">
        {/* Quick Action Buttons for UX/Functionality Points */}
        <div className="quick-actions" aria-label="Quick questions">
          <button onClick={() => handleSend("Where is the nearest restroom?")} className="quick-btn" disabled={isLoading} aria-label="Ask about restrooms">
             <Navigation size={14} /> Nearest Restroom
          </button>
          <button onClick={() => handleSend("What are the current gate wait times?")} className="quick-btn" disabled={isLoading} aria-label="Ask about gate queues">
             <Clock size={14} /> Gate Queues
          </button>
          <button onClick={() => handleSend("What food options are available in the Fan Zone?")} className="quick-btn" disabled={isLoading} aria-label="Ask about food">
             <Utensils size={14} /> Food Options
          </button>
          <button onClick={() => handleSend("What is the bag policy?")} className="quick-btn" disabled={isLoading} aria-label="Ask about bag policy">
             <ShieldQuestion size={14} /> Bag Policy
          </button>
        </div>

        <form className="chat-input-area" onSubmit={handleFormSubmit} aria-label="Message Input Form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me about restrooms, food, or gate queues..."
            className="chat-input"
            disabled={isLoading}
            aria-label="Message text"
          />
          <button type="submit" className="send-btn" disabled={!input.trim() || isLoading} aria-label="Send message">
            <Send size={20} />
          </button>
        </form>
      </div>
    </main>
  );
};

export default FanChat;
