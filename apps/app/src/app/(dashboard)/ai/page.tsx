'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Bot,
  Send,
  User,
  Copy,
  Play,
  Sparkles,
  Database,
  Loader2,
  ThumbsUp,
  ThumbsDown,
} from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sql?: string;
  timestamp: Date;
}

const suggestions = [
  'Show me customers who haven\'t ordered in 90 days',
  'Create a stored procedure to archive old orders',
  'Optimize this slow query',
  'Explain the relationship between orders and customers',
  'Generate a monthly sales report query',
];

export default function AIPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your SQL AI assistant. I can help you with:\n\n• Writing SQL queries from natural language\n• Optimizing slow queries\n• Explaining complex queries\n• Generating stored procedures\n• Reviewing SQL for issues\n\nHow can I help you today?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate AI response
    await new Promise((resolve) => setTimeout(resolve, 2000));

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: `Based on your request, I've generated the following SQL query that will find customers who haven't placed an order in the last 90 days:\n\nThis query joins the customers table with orders and filters for those whose last order date is more than 90 days ago, or who have never ordered.`,
      sql: `SELECT
  c.CustomerID,
  c.Name,
  c.Email,
  MAX(o.OrderDate) as LastOrderDate,
  DATEDIFF(DAY, MAX(o.OrderDate), GETDATE()) as DaysSinceLastOrder
FROM Customers c
LEFT JOIN Orders o ON c.CustomerID = o.CustomerID
GROUP BY c.CustomerID, c.Name, c.Email
HAVING MAX(o.OrderDate) < DATEADD(DAY, -90, GETDATE())
    OR MAX(o.OrderDate) IS NULL
ORDER BY LastOrderDate;`,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, assistantMessage]);
    setIsLoading(false);
  };

  const handleSuggestion = (suggestion: string) => {
    setInput(suggestion);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex gap-4">
      {/* Chat Area */}
      <Card className="flex-1 flex flex-col min-h-0">
        <CardHeader className="pb-2 border-b">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
              <Bot className="h-5 w-5 text-primary" />
            </div>
            <div>
              <CardTitle>SQL AI Assistant</CardTitle>
              <p className="text-sm text-muted-foreground">
                Powered by Claude • Connected to Production
              </p>
            </div>
          </div>
        </CardHeader>

        {/* Messages */}
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${
                message.role === 'user' ? 'justify-end' : ''
              }`}
            >
              {message.role === 'assistant' && (
                <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                  <Bot className="h-4 w-4 text-primary" />
                </div>
              )}

              <div
                className={`max-w-[80%] ${
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground rounded-2xl rounded-tr-sm px-4 py-2'
                    : 'space-y-3'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>

                {message.sql && (
                  <div className="rounded-lg border bg-muted/50 overflow-hidden">
                    <div className="flex items-center justify-between px-3 py-2 border-b bg-muted">
                      <span className="text-xs font-medium">Generated SQL</span>
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 px-2"
                          onClick={() => copyToClipboard(message.sql!)}
                        >
                          <Copy className="h-3 w-3 mr-1" />
                          Copy
                        </Button>
                        <Button variant="ghost" size="sm" className="h-7 px-2">
                          <Play className="h-3 w-3 mr-1" />
                          Run
                        </Button>
                      </div>
                    </div>
                    <pre className="p-3 text-xs font-mono overflow-x-auto">
                      {message.sql}
                    </pre>
                  </div>
                )}

                {message.role === 'assistant' && (
                  <div className="flex items-center gap-2 pt-2">
                    <Button variant="ghost" size="sm" className="h-7 px-2">
                      <ThumbsUp className="h-3 w-3" />
                    </Button>
                    <Button variant="ghost" size="sm" className="h-7 px-2">
                      <ThumbsDown className="h-3 w-3" />
                    </Button>
                  </div>
                )}
              </div>

              {message.role === 'user' && (
                <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center shrink-0">
                  <User className="h-4 w-4" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3">
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                <Bot className="h-4 w-4 text-primary" />
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Thinking...
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </CardContent>

        {/* Input */}
        <div className="p-4 border-t">
          <div className="flex gap-2">
            <Input
              placeholder="Ask me anything about your database..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              disabled={isLoading}
            />
            <Button onClick={handleSend} disabled={isLoading || !input.trim()}>
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </Card>

      {/* Sidebar */}
      <div className="w-80 space-y-4">
        {/* Suggestions */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              Suggestions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {suggestions.map((suggestion, i) => (
              <button
                key={i}
                className="w-full text-left p-2 rounded text-xs hover:bg-accent transition-colors"
                onClick={() => handleSuggestion(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </CardContent>
        </Card>

        {/* Context */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Database className="h-4 w-4" />
              Context
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-muted-foreground mb-1">Connected Database</p>
                <p className="font-medium">Production (SQL Server)</p>
              </div>
              <div>
                <p className="text-muted-foreground mb-1">Available Tables</p>
                <p className="text-xs text-muted-foreground">
                  customers, orders, products, order_items, categories...
                </p>
              </div>
              <div>
                <p className="text-muted-foreground mb-1">Session Tokens</p>
                <p className="font-medium">2,450 / 10,000</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
