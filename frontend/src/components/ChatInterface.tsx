import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'agent' | 'system';
  content: string;
}

interface ChatInterfaceProps {
  onDataReceived?: (data: any[], query: string) => void;
  onRequireApproval?: (query: string) => void;
}

export default function ChatInterface({ onDataReceived, onRequireApproval }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'agent',
      content: 'Hello! I am DataSleuth. Ask me any data or policy questions.',
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    const timeout = setTimeout(scrollToBottom, 100);
    return () => clearTimeout(timeout);
  }, [messages]);

  useEffect(() => {
    const handleResume = (e: any) => {
      const data = e.detail;
      const agentMsg: Message = { 
        id: Date.now().toString(), 
        role: 'agent', 
        content: data.error ? `Backend Error: ${data.error}` : (data.response || "No response received.")
      };
      setMessages(prev => [...prev, agentMsg]);
      setIsLoading(false);
      
      if (data.sql_result && onDataReceived) {
        try {
          const parsedData = JSON.parse(data.sql_result);
          if (Array.isArray(parsedData)) { onDataReceived(parsedData, data.sql_query); }
        } catch (e) {
          console.error(e);
        }
      }
    };
    
    window.addEventListener('hitl_resume_result', handleResume);
    return () => window.removeEventListener('hitl_resume_result', handleResume);
  }, [onDataReceived]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg.content })
      });
      
      const data = await response.json();
      
      if (data.requires_approval) {
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: 'system',
          content: 'I need your permission to run a dangerous query. Please check the popup modal.'
        }]);
        if (onRequireApproval) onRequireApproval(data.sql_query);
        // We stay in isLoading state until the global event fires
        return; 
      }
      
      const agentMsg: Message = { 
        id: (Date.now() + 1).toString(), 
        role: 'agent', 
        content: data.error ? `Backend Error: ${data.error}` : (data.response || "No response received.")
      };
      
      setMessages(prev => [...prev, agentMsg]);

      if (data.sql_result && onDataReceived) {
        try {
          const parsedData = JSON.parse(data.sql_result);
          if (Array.isArray(parsedData)) { onDataReceived(parsedData, data.sql_query); }
        } catch (e) {
          console.error(e);
        }
      }
      
      setIsLoading(false);
    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'agent',
        content: `Error connecting to backend: ${String(error)}`
      }]);
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full glass rounded-xl overflow-hidden animate-slide-up">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}>
            <div className={`max-w-[90%] rounded-2xl px-4 py-3 ${
              msg.role === 'user' 
                ? 'bg-primary text-white rounded-br-none' 
                : msg.role === 'system' 
                  ? 'bg-red-500/20 text-red-300 border border-red-500/30' 
                  : 'bg-surfaceHover text-textMain rounded-bl-none border border-white/5'
            }`}>
              <p className="text-sm md:text-base whitespace-pre-wrap leading-relaxed">{msg.content}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start animate-fade-in">
             <div className="max-w-[90%] rounded-2xl px-4 py-3 bg-surfaceHover text-textMuted rounded-bl-none border border-white/5 flex items-center gap-2">
               <Loader2 className="animate-spin" size={16} /> Thinking...
             </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="p-4 bg-surface border-t border-white/5">
        <div className="relative flex items-center">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            disabled={isLoading}
            placeholder="Ask a question about your data..."
            className="w-full bg-background border border-white/10 text-textMain rounded-full pl-6 pr-12 py-3 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all placeholder:text-textMuted disabled:opacity-50"
          />
          <button 
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="absolute right-2 p-2 bg-primary hover:bg-primaryHover disabled:bg-gray-700 text-white rounded-full transition-colors"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
