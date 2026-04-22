"use client";
import React, { useRef, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { UploadCloud, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ResumeUploaderProps {
    onFileSelect: (file: File) => void;
}

const ACCEPTED_EXTENSIONS = [".pdf", ".docx", ".txt"];
const ACCEPTED_MIME_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
];

const isValidFile = (file: File): boolean => {
    const ext = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    return ACCEPTED_EXTENSIONS.includes(ext) || ACCEPTED_MIME_TYPES.includes(file.type);
};

export const ResumeUploader = ({ onFileSelect }: ResumeUploaderProps) => {
    const [fileName, setFileName] = useState<string | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const processFile = (file: File) => {
        setError(null);
        if (!isValidFile(file)) {
            setError(`Invalid file type. Please upload a PDF, DOCX, or TXT file.`);
            return;
        }
        setFileName(file.name);
        onFileSelect(file);
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            processFile(file);
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
            processFile(file);
        }
    };

    return (
        <Card
            onClick={() => fileInputRef.current?.click()}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={cn(
                "border-2 border-dashed transition-colors cursor-pointer flex flex-col items-center justify-center h-full min-h-[300px]",
                isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50",
                error && "border-destructive/50"
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
                {fileName ? (
                    <>
                        <div className="p-4 rounded-full bg-green-500/10 text-green-500">
                            <CheckCircle2 className="w-10 h-10" />
                        </div>
                        <div className="space-y-1">
                            <p className="font-semibold text-primary">{fileName}</p>
                            <p className="text-xs text-muted-foreground">Click to change file</p>
                        </div>
                    </>
                ) : (
                    <>
                        <div className="p-4 rounded-full bg-primary/10 text-primary animate-pulse-slow">
                            <UploadCloud className="w-10 h-10" />
                        </div>
                        <div className="space-y-1">
                            <p className="text-lg font-medium">Drop your resume here</p>
                            <p className="text-sm text-muted-foreground">or click to browse (PDF, DOCX, TXT)</p>
                        </div>
                    </>
                )}
                {error && (
                    <p className="text-sm text-destructive font-medium">{error}</p>
                )}
            </CardContent>
        </Card>
    );
};
