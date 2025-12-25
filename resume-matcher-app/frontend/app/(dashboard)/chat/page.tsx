"use client";

import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Send, Loader2, Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";

interface Message {
    role: "user" | "model";
    text: string;
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = { role: "user", text: input };
        setMessages((prev) => [...prev, userMsg]);
        setInput("");
        setIsLoading(true);

        try {
            // Frontend sends history with "parts" matching backend expectations
            const history = messages.map(m => ({
                role: m.role,
                parts: [m.text]
            }));

            const res = await fetch("http://localhost:8000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: userMsg.text,
                    history: history
                }),
            });

            if (!res.ok) throw new Error("Failed to send message");

            const data = await res.json();
            const botMsg: Message = { role: "model", text: data.response };
            setMessages((prev) => [...prev, botMsg]);
        } catch (error) {
            console.error(error);
            setMessages((prev) => [...prev, { role: "model", text: "Sorry, I encountered an error. Please try again." }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-4rem)] p-4 max-w-5xl mx-auto w-full">
            <Card className="flex-1 flex flex-col shadow-sm border border-border/50 bg-background/50 backdrop-blur-sm">
                <div className="p-4 border-b flex flex-col bg-muted/20 gap-2">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Bot className="h-5 w-5 text-primary" />
                            <h2 className="font-semibold text-lg">AI Career Assistant</h2>
                        </div>
                    </div>
                    <p className="text-[10px] text-muted-foreground bg-yellow-500/10 p-2 rounded border border-yellow-500/20 text-center w-full">
                        Note: Chat history is not saved. Navigating to another page will clear the conversation.
                    </p>
                </div>

                <CardContent className="flex-1 overflow-y-auto p-6 space-y-6" ref={scrollRef}>
                    {messages.length === 0 && (
                        <div className="flex flex-col items-center justify-center h-full text-center space-y-4 text-muted-foreground opacity-50">
                            <Bot className="h-16 w-16" />
                            <div className="max-w-md">
                                <h3 className="text-xl font-medium mb-2">How can I help you today?</h3>
                                <p>Ask me to review your resume, suggest skills, or provide interview tips.</p>
                            </div>
                        </div>
                    )}

                    {messages.map((msg, idx) => (
                        <div
                            key={idx}
                            className={cn(
                                "flex gap-3 max-w-[85%]",
                                msg.role === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
                            )}
                        >
                            <div className={cn(
                                "mt-1 h-8 w-8 rounded-full flex items-center justify-center shrink-0",
                                msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                            )}>
                                {msg.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                            </div>

                            <div
                                className={cn(
                                    "rounded-2xl px-5 py-3 text-sm shadow-sm",
                                    msg.role === "user"
                                        ? "bg-primary text-primary-foreground rounded-tr-none"
                                        : "bg-card border border-border rounded-tl-none prose prose-sm dark:prose-invert max-w-none break-words"
                                )}
                            >
                                {msg.role === "user" ? (
                                    msg.text
                                ) : (
                                    <ReactMarkdown components={{
                                        p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                                        ul: ({ node, ...props }) => <ul className="list-disc pl-4 mb-2 space-y-1" {...props} />,
                                        ol: ({ node, ...props }) => <ol className="list-decimal pl-4 mb-2 space-y-1" {...props} />,
                                        li: ({ node, ...props }) => <li className="" {...props} />,
                                        h1: ({ node, ...props }) => <h1 className="text-lg font-bold mb-2 mt-4" {...props} />,
                                        h2: ({ node, ...props }) => <h2 className="text-base font-bold mb-2 mt-3" {...props} />,
                                        h3: ({ node, ...props }) => <h3 className="text-sm font-bold mb-1 mt-2" {...props} />,
                                        code: ({ node, ...props }) => <code className="bg-muted px-1 py-0.5 rounded text-xs font-mono" {...props} />,
                                    }}>
                                        {msg.text}
                                    </ReactMarkdown>
                                )}
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="flex gap-3 mr-auto">
                            <div className="mt-1 h-8 w-8 rounded-full bg-muted text-muted-foreground flex items-center justify-center shrink-0">
                                <Bot className="h-4 w-4" />
                            </div>
                            <div className="bg-card border border-border rounded-2xl rounded-tl-none px-5 py-3 shadow-sm flex items-center">
                                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground mr-2" />
                                <span className="text-sm text-muted-foreground">Thinking...</span>
                            </div>
                        </div>
                    )}
                </CardContent>

                <div className="p-4 border-t bg-background/50 backdrop-blur-sm">
                    <form
                        className="flex w-full gap-2 relative"
                        onSubmit={(e) => {
                            e.preventDefault();
                            handleSend();
                        }}
                    >
                        <Input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type instructions or specific keywords..."
                            className="flex-1 pr-12 py-6"
                            disabled={isLoading}
                        />
                        <Button
                            type="submit"
                            size="icon"
                            className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8"
                            disabled={isLoading || !input.trim()}
                        >
                            <Send className="h-4 w-4" />
                        </Button>
                    </form>
                </div>
            </Card>
        </div>
    );
}
