import React, { useState, useEffect, useRef } from 'react';
import { Send, Minimize2, X, User, Bot, AlertCircle, CheckCircle } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  intent?: string;
  sentiment?: string;
  confidence?: number;
  trustGate?: {
    decision: string;
    riskLevel: string;
    confidence: number;
  };
}

interface ChatbotWidgetProps {
  caseId?: string;
  sessionId?: string;
  onClose?: () => void;
  embedded?: boolean;
}

export const ChatbotWidget: React.FC<ChatbotWidgetProps> = ({
  caseId,
  sessionId: initialSessionId,
  onClose,
  embedded = false,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(initialSessionId);
  const [isMinimized, setIsMinimized] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Initialize chat with greeting
    if (messages.length === 0) {
      setMessages([
        {
          id: '1',
          role: 'assistant',
          content: "Hello! I'm here to help with your account. How can I assist you today?",
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  }, []);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Call chatbot API
      const response = await fetch('/api/v1/chatbot/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputValue,
          session_id: sessionId || undefined,
          case_id: caseId || undefined,
        }),
      });

      const data = await response.json();

      if (!sessionId && data.session_id) {
        setSessionId(data.session_id);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message,
        timestamp: data.timestamp,
        intent: data.intent,
        sentiment: data.sentiment,
        confidence: data.confidence,
        trustGate: data.trust_gate_evaluation,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chatbot error:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: "I'm sorry, I'm having trouble right now. Let me connect you with a representative.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getIntentColor = (intent?: string) => {
    const colors: Record<string, string> = {
      payment: 'green',
      dispute: 'red',
      hardship_request: 'yellow',
      information: 'blue',
      complaint: 'red',
    };
    return colors[intent || ''] || 'gray';
  };

  const getTrustGateColor = (decision?: string) => {
    const colors: Record<string, string> = {
      auto_execute: 'green',
      human_review: 'yellow',
      escalate: 'orange',
      block: 'red',
    };
    return colors[decision || ''] || 'gray';
  };

  const getRiskLevelIcon = (riskLevel?: string) => {
    if (riskLevel === 'low') return <CheckCircle className="w-4 h-4 text-green-500" />;
    if (riskLevel === 'medium') return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    return <AlertCircle className="w-4 h-4 text-red-500" />;
  };

  if (isMinimized) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <Button
          onClick={() => setIsMinimized(false)}
          className="rounded-full w-16 h-16 bg-blue-600 hover:bg-blue-700 shadow-lg"
        >
          <Bot className="w-6 h-6" />
        </Button>
      </div>
    );
  }

  return (
    <div
      className={`${
        embedded ? 'w-full h-full' : 'fixed bottom-4 right-4 w-96 h-[600px]'
      } z-50 flex flex-col`}
    >
      <Card className="flex flex-col h-full shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-t-lg">
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5" />
            <span className="font-semibold">Collection Assistant</span>
          </div>
          <div className="flex items-center gap-2">
            {!embedded && (
              <button
                onClick={() => setIsMinimized(true)}
                className="hover:bg-blue-800 p-1 rounded"
              >
                <Minimize2 className="w-4 h-4" />
              </button>
            )}
            {onClose && (
              <button onClick={onClose} className="hover:bg-blue-800 p-1 rounded">
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
          {messages.map((message) => (
            <div key={message.id}>
              <div
                className={`flex items-start gap-2 ${
                  message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                }`}
              >
                {/* Avatar */}
                <div
                  className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    message.role === 'user'
                      ? 'bg-gray-300'
                      : 'bg-gradient-to-br from-blue-500 to-blue-600'
                  }`}
                >
                  {message.role === 'user' ? (
                    <User className="w-4 h-4 text-gray-700" />
                  ) : (
                    <Bot className="w-4 h-4 text-white" />
                  )}
                </div>

                {/* Message bubble */}
                <div
                  className={`flex-1 max-w-[80%] ${
                    message.role === 'user' ? 'items-end' : 'items-start'
                  }`}
                >
                  <div
                    className={`rounded-lg p-3 ${
                      message.role === 'user'
                        ? 'bg-gray-200 text-gray-900'
                        : 'bg-white border border-gray-200 text-gray-900'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <span className="text-xs text-gray-500 mt-1 block">
                      {new Date(message.timestamp).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>

                  {/* AI Analysis (only for assistant messages) */}
                  {message.role === 'assistant' && showAnalysis && message.intent && (
                    <div className="mt-2 flex flex-wrap gap-2 text-xs">
                      <Badge color={getIntentColor(message.intent)}>
                        Intent: {message.intent}
                      </Badge>
                      {message.sentiment && (
                        <Badge color="gray">Sentiment: {message.sentiment}</Badge>
                      )}
                      {message.confidence && (
                        <Badge color="blue">
                          Confidence: {(message.confidence * 100).toFixed(0)}%
                        </Badge>
                      )}
                      {message.trustGate && (
                        <div className="flex items-center gap-1">
                          {getRiskLevelIcon(message.trustGate.riskLevel)}
                          <Badge color={getTrustGateColor(message.trustGate.decision)}>
                            {message.trustGate.decision.replace('_', ' ')}
                          </Badge>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-white border border-gray-200 rounded-lg p-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.1s' }}
                  />
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.2s' }}
                  />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t p-4 bg-white rounded-b-lg">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <Button
              onClick={handleSendMessage}
              disabled={isLoading || !inputValue.trim()}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>

          {/* Session info */}
          {sessionId && (
            <div className="mt-2 text-xs text-gray-500 flex items-center justify-between">
              <span>Session: {sessionId.slice(0, 8)}</span>
              <button
                onClick={() => setShowAnalysis(!showAnalysis)}
                className="text-blue-600 hover:underline"
              >
                {showAnalysis ? 'Hide' : 'Show'} AI Analysis
              </button>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};
