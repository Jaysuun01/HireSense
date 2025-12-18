"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { GraduationCap, Briefcase, ArrowRight, Users, Target, BookOpen, TrendingUp } from "lucide-react"

interface UseCaseSelectorProps {
  onSelectUseCase: (useCase: 1 | 2) => void
}

export function UseCaseSelector({ onSelectUseCase }: UseCaseSelectorProps) {
  return (
    <div className="flex flex-1 flex-col bg-gradient-to-br from-slate-50 via-white to-blue-50/30 dark:from-slate-950 dark:via-slate-900 dark:to-blue-950/20">
      <header className="flex h-20 items-center justify-between border-b border-white/20 bg-white/70 backdrop-blur-xl px-8 shadow-sm dark:bg-slate-900/70 dark:border-slate-800/50">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-violet-600">
            <Target className="h-4 w-4 text-white" />
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-900 via-blue-800 to-violet-800 bg-clip-text text-transparent dark:from-white dark:via-blue-200 dark:to-violet-200">
            Choose Your Path
          </h1>
        </div>
      </header>
      
      <div className="flex-1 p-8">
        <div className="max-w-6xl mx-auto space-y-8">
          <div className="text-center space-y-4">
            <h2 className="text-3xl font-bold bg-gradient-to-r from-slate-800 via-blue-700 to-violet-700 bg-clip-text text-transparent dark:from-white dark:via-blue-300 dark:to-violet-300">
              Welcome to HireSense
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
              Choose how you'd like to use our AI-powered analysis system
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-12">
            {/* Use Case 1: Student Resume Improvement */}
            <Card className="group relative overflow-hidden border-2 border-emerald-200/60 bg-gradient-to-br from-emerald-50 to-green-50/80 backdrop-blur-sm shadow-lg hover:shadow-xl hover:border-emerald-300/80 transition-all duration-300 hover:-translate-y-1 dark:from-emerald-950/30 dark:to-green-950/20 dark:border-emerald-800/60 dark:hover:border-emerald-700/80">
              <CardHeader className="pb-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-green-600 shadow-lg">
                    <GraduationCap className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-xl font-bold text-emerald-800 dark:text-emerald-200">
                      Resume Builder
                    </CardTitle>
                    <p className="text-sm text-emerald-600 dark:text-emerald-400 font-medium">
                      For Students & New Graduates
                    </p>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-6">
                <p className="text-slate-700 dark:text-slate-300">
                  Get personalized guidance to improve your resume based on your major and career interests. Perfect for students and new graduates looking to build their professional profile.
                </p>

                <div className="space-y-3">
                  <h4 className="font-semibold text-emerald-800 dark:text-emerald-200 flex items-center gap-2">
                    <BookOpen className="h-4 w-4" />
                    Features:
                  </h4>
                  <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-2 shrink-0"></div>
                      <span>Enter your major to discover popular career fields</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-2 shrink-0"></div>
                      <span>AI-powered career field recommendations based on your major</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-2 shrink-0"></div>
                      <span>Get targeted recommendations for skill development</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-2 shrink-0"></div>
                      <span>Beginner-friendly guidance and explanations</span>
                    </li>
                  </ul>
                </div>

                <Button 
                  onClick={() => onSelectUseCase(1)}
                  className="w-full bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 group-hover:scale-105"
                  size="lg"
                >
                  Start Building Your Resume
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>

            {/* Use Case 2: Hiring Evaluation */}
            <Card className="group relative overflow-hidden border-2 border-blue-200/60 bg-gradient-to-br from-blue-50 to-violet-50/80 backdrop-blur-sm shadow-lg hover:shadow-xl hover:border-blue-300/80 transition-all duration-300 hover:-translate-y-1 dark:from-blue-950/30 dark:to-violet-950/20 dark:border-blue-800/60 dark:hover:border-blue-700/80">
              <CardHeader className="pb-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-violet-600 shadow-lg">
                    <Briefcase className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-xl font-bold text-blue-800 dark:text-blue-200">
                      Hiring Evaluator
                    </CardTitle>
                    <p className="text-sm text-blue-600 dark:text-blue-400 font-medium">
                      For Recruiters & Hiring Managers
                    </p>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-6">
                <p className="text-slate-700 dark:text-slate-300">
                  Analyze candidates against specific job postings with AI-powered evaluation. Get comprehensive hiring recommendations with detailed reasoning.
                </p>

                <div className="space-y-3">
                  <h4 className="font-semibold text-blue-800 dark:text-blue-200 flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    Features:
                  </h4>
                  <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0"></div>
                      <span>Match candidates to specific job postings</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0"></div>
                      <span>AI debate system for thorough evaluation</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0"></div>
                      <span>Detailed compatibility analysis</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0"></div>
                      <span>Final hiring recommendation with confidence score</span>
                    </li>
                  </ul>
                </div>

                <Button 
                  onClick={() => onSelectUseCase(2)}
                  className="w-full bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-700 hover:to-violet-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 group-hover:scale-105"
                  size="lg"
                >
                  Evaluate Candidates
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          </div>

          <div className="text-center pt-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-100 dark:bg-slate-800 text-sm text-slate-600 dark:text-slate-400">
              <Users className="h-4 w-4" />
              <span>Trusted by students and professionals worldwide</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
