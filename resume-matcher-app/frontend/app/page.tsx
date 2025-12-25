"use client";
import { Button } from "@nextui-org/button";
import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2 bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
      <main className="flex flex-col items-center justify-center w-full flex-1 px-4 sm:px-20 text-center">
        <h1 className="text-4xl sm:text-6xl font-bold mb-8 text-foreground">
          AI-Powered{" "}
          <span className="text-primary bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-600">
            Resume Matcher
          </span>
        </h1>

        <p className="mt-3 text-xl sm:text-2xl text-default-500 max-w-2xl text-gray-600 dark:text-gray-300">
          Optimize your resume for any job description using AI-driven insights.
          Get match scores, missing skills, and tailored suggestions.
        </p>

        {/* Centered single button with improved UI */}
        <div className="mt-12">
          <Button
            as={Link}
            href="/matcher"
            size="lg"
            className="font-semibold text-xl px-10 py-7 rounded-xl shadow-lg
                       bg-gradient-to-r from-indigo-500 to-purple-600 text-white
                       hover:shadow-2xl hover:scale-105 transition-all duration-300"
          >
            Start Matching
          </Button>
        </div>
      </main>
    </div>
  );
}
