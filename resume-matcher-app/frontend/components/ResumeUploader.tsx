"use client";
import React, { useRef, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { UploadCloud } from "lucide-react";
import { cn } from "@/lib/utils";

interface ResumeUploaderProps {
    onFileSelect: (file: File) => void;
}

export const ResumeUploader = ({ onFileSelect }: ResumeUploaderProps) => {
    const [fileName, setFileName] = useState<string | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setFileName(file.name);
            onFileSelect(file);
        }
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files?.[0];
        if (file) {
            setFileName(file.name);
            onFileSelect(file);
        }
    };

    return (
        <Card
            onClick={() => fileInputRef.current?.click()}
            className={cn(
                "border-2 border-dashed transition-colors cursor-pointer flex flex-col items-center justify-center h-full min-h-[300px]",
                isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50"
            )}
        >
            <CardContent className="flex flex-col items-center justify-center gap-4 text-center p-6">
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    accept=".pdf,.txt,.docx"
                    className="hidden"
                />
                <div className="p-4 rounded-full bg-primary/10 text-primary animate-pulse-slow">
                    <UploadCloud className="w-10 h-10" />
                </div>
                <div className="space-y-1">
                    {fileName ? (
                        <p className="font-semibold text-primary">{fileName}</p>
                    ) : (
                        <>
                            <p className="text-lg font-medium">Drop your resume here</p>
                            <p className="text-sm text-muted-foreground">or click to browse (PDF, TXT)</p>
                        </>
                    )}
                </div>
            </CardContent>
        </Card>
    );
};
