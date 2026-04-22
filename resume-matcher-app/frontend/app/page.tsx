"use client";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles, CheckCircle2, Zap } from "lucide-react";

export default function Home() {
  const router = useRouter();
  const [checked, setChecked] = useState(false);

  // Redirect logged-in users directly to matcher
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token && token !== "undefined" && token !== "null") {
      router.replace("/matcher");
    } else {
      setChecked(true);
    }
  }, [router]);

  // Don't render until we've checked auth (prevents flash)
  if (!checked) return null;

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-foreground font-sans selection:bg-indigo-500/30 overflow-hidden relative">
      {/* Background Glow Effects */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-indigo-600/20 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 right-[-10%] w-[600px] h-[500px] bg-purple-600/10 blur-[150px] rounded-full pointer-events-none" />

      {/* Navigation (Simple) */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-4 max-w-7xl mx-auto border-b border-white/5">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold shadow-lg shadow-indigo-500/25">
            M
          </div>
          <span className="font-semibold text-lg tracking-tight text-zinc-100">Resume Matcher</span>
        </div>
        <div className="flex gap-4">
          <Button variant="ghost" asChild className="text-zinc-400 hover:text-white hover:bg-white/5">
            <Link href="/login">Log in</Link>
          </Button>
          <Button asChild className="bg-white text-black hover:bg-zinc-200">
            <Link href="/signup">Get Started</Link>
          </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 flex flex-col items-center justify-center px-4 pt-32 pb-24 max-w-5xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-indigo-300 text-sm font-medium mb-8"
        >
          <Sparkles className="w-4 h-4" />
          Powered by Gemini 1.5 AI Core
        </motion.div>

        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-5xl sm:text-7xl font-bold tracking-tight text-white mb-6 leading-[1.1]"
        >
          Land your dream job with{" "}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
            AI precision.
          </span>
        </motion.h1>

        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-4 text-xl sm:text-2xl text-zinc-400 max-w-3xl leading-relaxed"
        >
          Stop guessing what recruiters want. Instantly score your resume against any job description, uncover missing critical skills, and get personalized interview advice.
        </motion.p>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-10 flex flex-col sm:flex-row gap-4 w-full sm:w-auto"
        >
          <Button
            asChild
            size="lg"
            className="h-14 px-8 text-base font-semibold rounded-2xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 shadow-lg shadow-indigo-500/25 transition-all hover:scale-105"
          >
            <Link href="/matcher">
              Start Matching <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
          </Button>
          <Button
            asChild
            size="lg"
            variant="outline"
            className="h-14 px-8 text-base font-semibold rounded-2xl bg-white/5 border-white/10 hover:bg-white/10 text-white backdrop-blur-sm"
          >
            <Link href="/login">View Past Results</Link>
          </Button>
        </motion.div>

        {/* Feature Highlights */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="mt-24 grid sm:grid-cols-3 gap-8 w-full max-w-4xl text-left"
        >
          <div className="flex flex-col p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.04] transition-colors">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4">
              <Zap className="w-6 h-6" />
            </div>
            <h3 className="text-zinc-100 font-semibold text-lg mb-2">Instant Scoring</h3>
            <p className="text-zinc-400 text-sm leading-relaxed">Get mathematically calculated similarity scores powered by BERT natural language models.</p>
          </div>
          
          <div className="flex flex-col p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.04] transition-colors">
            <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center text-purple-400 mb-4">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="text-zinc-100 font-semibold text-lg mb-2">AI Gap Analysis</h3>
            <p className="text-zinc-400 text-sm leading-relaxed">Gemini perfectly identifies the exact technical and soft skills your resume is missing.</p>
          </div>

          <div className="flex flex-col p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:bg-white/[0.04] transition-colors">
            <div className="w-12 h-12 rounded-xl bg-pink-500/20 flex items-center justify-center text-pink-400 mb-4">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h3 className="text-zinc-100 font-semibold text-lg mb-2">Interactive Chat</h3>
            <p className="text-zinc-400 text-sm leading-relaxed">Ask personalized questions to your own AI career assistant with full context of your resume.</p>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
