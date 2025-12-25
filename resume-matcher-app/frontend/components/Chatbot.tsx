"use client";

import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageCircle, X, Send, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { usePathname } from "next/navigation";

interface Message {
    role: "user" | "model";
    text: string;
}

export const Chatbot = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);
    const pathname = usePathname();

    // Reset chat on navigation
    useEffect(() => {
        setMessages([]);
    }, [pathname]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isOpen]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = { role: "user", text: input };
        setMessages((prev) => [...prev, userMsg]);
        setInput("");
        setIsLoading(true);

        try {
            // Convert messages to history format
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

    if (pathname === "/chat") {
        return null;
    }

    if (!isOpen) {
        return (
            <Button
                className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-xl z-50 p-0 bg-primary hover:bg-primary/90 transition-transform hover:scale-105"
                onClick={() => setIsOpen(true)}
            >
                <MessageCircle className="h-8 w-8 text-white" />
            </Button>
        );
    }

    return (
        <Card className="fixed bottom-6 right-6 w-[380px] h-[600px] shadow-2xl z-50 flex flex-col animate-in slide-in-from-bottom-5 fade-in duration-300 border-primary/20 bg-background">
            <CardHeader className="p-4 border-b bg-primary/5 flex flex-col space-y-2">
                <div className="flex flex-row items-center justify-between w-full">
                    <CardTitle className="text-lg font-bold flex items-center gap-2 text-primary">
                        <MessageCircle className="h-5 w-5" />
                        Resume Assistant
                    </CardTitle>
                    <div className="flex items-center gap-1">
                        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setIsOpen(false)}>
                            <X className="h-5 w-5" />
                        </Button>
                    </div>
                </div>
                <p className="text-[10px] text-muted-foreground bg-yellow-500/10 p-2 rounded border border-yellow-500/20 text-center">
                    Note: Chat history is not saved. Navigating to another page will clear the conversation.
                </p>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                {messages.length === 0 && (
                    <div className="text-center text-muted-foreground mt-4">
                        <p>Hi! I can help you improve your resume or answer career questions.</p>
                    </div>
                )}
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={cn(
                            "flex w-full",
                            msg.role === "user" ? "justify-end" : "justify-start"
                        )}
                    >
                        <div
                            className={cn(
                                "max-w-[80%] rounded-lg px-4 py-2 text-sm",
                                msg.role === "user"
                                    ? "bg-primary text-primary-foreground rounded-br-none"
                                    : "bg-muted text-muted-foreground rounded-bl-none"
                            )}
                        >
                            {msg.text}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-muted rounded-lg px-4 py-2 rounded-bl-none">
                            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                        </div>
                    </div>
                )}
            </CardContent>
            <CardFooter className="p-3 border-t bg-background">
                <form
                    className="flex w-full gap-2"
                    onSubmit={(e) => {
                        e.preventDefault();
                        handleSend();
                    }}
                >
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type a message..."
                        className="flex-1"
                        disabled={isLoading}
                    />
                    <Button type="submit" size="icon" disabled={isLoading || !input.trim()}>
                        <Send className="h-4 w-4" />
                    </Button>
                </form>
            </CardFooter>
        </Card>
    );
};
