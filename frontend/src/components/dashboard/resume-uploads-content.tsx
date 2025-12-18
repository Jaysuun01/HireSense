// components/dashboard/resume-uploads-content.tsx
"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Upload, FileText, CheckCircle, Briefcase, Users, Calendar, MapPin, Award, Target, BrainCircuit, Scale, XCircle, ArrowLeft } from "lucide-react"
import { jobPosts } from "@/lib/script"
import { UploadResumeDialog } from "./upload-resume-dialog"
import { AnalysisInProgress } from "./analysis-in-progress"
import { RadialProgress } from "@/components/ui/radial-progress"
import { UseCaseSelector } from "./use-case-selector"
import { ResumeBuilderContent } from "./resume-builder-content"

interface DatabaseJobPost {
  id: string
  title: string
  summary: string
  description: string
  location: string
  employment_type: string
  salary: string
  requirements: string
  skills: string[]
  status: string
  applicants_count: number
  created_at: string
}

interface ResumeAnalysis {
  candidate_name: string
  skills: string[]
  experience_years: number
  experience_level: string
  key_achievements: string[]
  analysis: string
}

interface IntersectionAnalysis {
  analysis: string
  overall_compatibility: number
  skill_matches: string[]
  skill_gaps: string[]
  experience_match: string
}

interface Reasoning {
  summary: string
  pros: string[]
  cons: string[]
}

interface Decision {
  decision: string
  confidence: number
  reasoning: Reasoning
  key_factors: string[]
}

interface TranscriptEntry {
  agent_name: string
  position: "evaluation" | "pro" | "anti" | "decision"
  content: string
  details: any
}

interface AnalysisResult {
  resume_analysis: ResumeAnalysis
  intersection_analysis: IntersectionAnalysis
  decision: Decision
  transcript: TranscriptEntry[]
}

export function ResumeUploadsContent() {
  const [currentView, setCurrentView] = useState<'selector' | 'use-case-1' | 'use-case-2'>('selector')
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [showTranscript, setShowTranscript] = useState(false)
  const [selectedJob, setSelectedJob] = useState<any | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [databaseJobs, setDatabaseJobs] = useState<DatabaseJobPost[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const transcriptRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchJobPosts()
  }, [])

  const fetchJobPosts = async () => {
    try {
      const response = await fetch('http://localhost:8000/job-postings')
      if (response.ok) {
        const data = await response.json()
        setDatabaseJobs(data)
      }
    } catch (error) {
      console.error('Error fetching job posts:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Combine hardcoded and database job posts
  const allJobPosts = [
    ...jobPosts.map(job => ({
      ...job,
      employment_type: 'Full-time', // Add default employment type for hardcoded jobs
      source: 'hardcoded' as const
    })),
    ...databaseJobs.map(job => ({
      id: job.id,
      title: job.title,
      company: "Nebula Systems", // Default company for database jobs
      location: job.location || "Remote",
      posted: "Recently", // You could calculate this from created_at
      applicants: job.applicants_count || 0,
      status: job.status,
      summary: job.summary || job.description?.substring(0, 150) + "...",
      description: job.description,
      responsibilities: job.requirements ? [job.requirements] : [],
      qualifications: [],
      bonus: [],
      technologies: job.skills || [],
      employment_type: job.employment_type || 'Full-time',
      source: 'database' as const
    }))
  ]

  useEffect(() => {
    if (showTranscript && transcriptRef.current) {
      setTimeout(() => {
        transcriptRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        })
      }, 100) // Small delay to ensure the element is rendered
    }
  }, [showTranscript])

  const formatStatus = (status: string) => {
    if (!status) return ""
    return status.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())
  }

  const handleUploadClick = (job: any) => {
    setAnalysisResult(null)
    setSelectedJob(job)
    setIsDialogOpen(true)
  }

  const handleUploadStart = () => {
    setIsDialogOpen(false)
    setIsAnalyzing(true)
  }

  const handleUploadComplete = (result: AnalysisResult) => {
    setAnalysisResult(result)
    setIsAnalyzing(false)
    setSelectedJob(null)
  }

  const resetState = () => {
    setAnalysisResult(null)
    setIsAnalyzing(false)
    setShowTranscript(false)
  }

  const handleUseCaseSelection = (useCase: 1 | 2) => {
    if (useCase === 1) {
      setCurrentView('use-case-1')
    } else {
      setCurrentView('use-case-2')
    }
  }

  const handleBackToSelector = () => {
    setCurrentView('selector')
    resetState()
  }

  if (isAnalyzing) {
    return <AnalysisInProgress />
  }

  // Show Use Case Selector
  if (currentView === 'selector') {
    return <UseCaseSelector onSelectUseCase={handleUseCaseSelection} />
  }

  // Show Use Case 1: Resume Builder
  if (currentView === 'use-case-1') {
    return <ResumeBuilderContent onBack={handleBackToSelector} />
  }

  // Show Use Case 2: Hiring Evaluator (existing functionality)
  return (
    <div className="flex flex-1 flex-col bg-gradient-to-br from-slate-50 via-white to-blue-50/30 dark:from-slate-950 dark:via-slate-900 dark:to-blue-950/20">
      <header className="flex h-20 items-center justify-between border-b border-white/20 bg-white/70 backdrop-blur-xl px-8 shadow-sm dark:bg-slate-900/70 dark:border-slate-800/50">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={handleBackToSelector} className="mr-2">
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-violet-600">
            <Upload className="h-4 w-4 text-white" />
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-900 via-blue-800 to-violet-800 bg-clip-text text-transparent dark:from-white dark:via-blue-200 dark:to-violet-200">
            Hiring Evaluator
          </h1>
        </div>
        {analysisResult && (
           <Button onClick={resetState} variant="outline">
              ← Upload Another Resume
            </Button>
        )}
      </header>
      <div className="flex-1 p-8 space-y-8">
        {analysisResult ? (
          <div className="space-y-8">
            {/* Header */}
            <div className="text-center">
              <h1 className="text-3xl font-bold bg-gradient-to-r from-slate-800 via-blue-700 to-violet-700 bg-clip-text text-transparent dark:from-white dark:via-blue-300 dark:to-violet-300">
                Analysis for {analysisResult.resume_analysis.candidate_name}
              </h1>
            </div>
            
            {/* Final Decision Card */}
            <Card className="bg-gradient-to-br from-slate-50 to-white dark:from-slate-900 dark:to-slate-800/70 border-t-4 border-b-0 border-x-0 border-violet-500 shadow-xl">
              <CardHeader>
                <CardTitle className="flex items-center justify-center gap-3 text-2xl">
                  <Scale className="h-6 w-6 text-violet-500"/>
                  The Verdict
                </CardTitle>
              </CardHeader>
              <CardContent className="text-center space-y-4">
                <div className={`inline-flex items-center justify-center rounded-full px-8 py-3 text-3xl font-bold ${analysisResult.decision.decision === 'hire' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300' : 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300'}`}>
                  {formatStatus(analysisResult.decision.decision)}
                </div>
                <p className="text-lg text-slate-600 dark:text-slate-400">
                  with <span className="font-bold text-slate-800 dark:text-slate-200">{(analysisResult.decision.confidence * 100).toFixed(0)}%</span> confidence
                </p>
                <div className="max-w-3xl mx-auto text-left pt-4">
                  <p className="mt-1 text-slate-700 dark:text-slate-300 italic text-center">"{analysisResult.decision.reasoning.summary}"</p>
            </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto text-left pt-4">
                  <div className="space-y-2">
                    <h3 className="font-semibold text-lg text-emerald-600 dark:text-emerald-400">Pros</h3>
                    <ul className="space-y-2">
                      {analysisResult.decision.reasoning.pros.map((pro, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                           <CheckCircle className="h-4 w-4 mt-0.5 text-emerald-500 shrink-0"/>
                           <span>{pro}</span>
                        </li>
                      ))}
                    </ul>
            </div>
                  <div className="space-y-2">
                    <h3 className="font-semibold text-lg text-red-600 dark:text-red-400">Cons</h3>
                     <ul className="space-y-2">
                      {analysisResult.decision.reasoning.cons.map((con, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                           <XCircle className="h-4 w-4 mt-0.5 text-red-500 shrink-0"/>
                           <span>{con}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
                
                <div className="max-w-3xl mx-auto text-left pt-4">
                  <Label className="font-semibold text-center block">Key Factors in Decision</Label>
                  <div className="mt-2 flex flex-wrap gap-2 justify-center">
                    {analysisResult.decision.key_factors.map((factor, index) => (
                      <Badge key={index} className="bg-amber-100 border-amber-300 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300 dark:border-amber-700">{factor}</Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Main Analysis Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Resume Analysis Card */}
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2"><FileText className="h-5 w-5 text-blue-500"/>Resume Breakdown</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between items-center">
                     <Label>Experience Level</Label>
                     <Badge variant="secondary">{analysisResult.resume_analysis.experience_level || "N/A"}</Badge>
                  </div>
                   <div className="flex justify-between items-center">
                     <Label>Years of Experience</Label>
                     <Badge variant="outline">{analysisResult.resume_analysis.experience_years} years</Badge>
              </div>
              <div>
                    <Label className="mb-2 block">Technical Skills</Label>
                     <div className="flex flex-wrap gap-2">
                      {analysisResult.resume_analysis.skills.map((skill: string, index: number) => <Badge key={index}>{skill}</Badge>)}
                </div>
              </div>
              <div>
                     <Label className="mb-2 block">Key Achievements</Label>
                     <ul className="space-y-2">
                       {analysisResult.resume_analysis.key_achievements.map((ach, i) => (
                         <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                           <CheckCircle className="h-4 w-4 mt-0.5 text-emerald-500 shrink-0"/>
                           <span>{ach}</span>
                    </li>
                  ))}
                </ul>
              </div>
                </CardContent>
              </Card>
              
              {/* Intersection Analysis Card */}
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2"><Target className="h-5 w-5 text-emerald-500"/>Candidate-Job Fit</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex flex-col items-center">
                    <Label className="mb-2">Overall Compatibility</Label>
                    <RadialProgress value={analysisResult.intersection_analysis.overall_compatibility * 100} className="w-40 h-40"/>
                  </div>
                  <div>
                    <Label className="mb-2 block">Skill Matches</Label>
                     <div className="flex flex-wrap gap-2">
                      {analysisResult.intersection_analysis.skill_matches.map((skill: string, index: number) => <Badge key={index} className="bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300">{skill}</Badge>)}
                     </div>
                  </div>
              <div>
                    <Label className="mb-2 block">Skill Gaps</Label>
                     <div className="flex flex-wrap gap-2">
                      {analysisResult.intersection_analysis.skill_gaps.map((skill: string, index: number) => <Badge key={index} variant="destructive">{skill}</Badge>)}
                     </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <Label>Experience Match</Label>
                    <Badge variant="outline">{formatStatus(analysisResult.intersection_analysis.experience_match)}</Badge>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Debate Transcript Section */}
            <div className="text-center">
              <Button variant="secondary" onClick={() => setShowTranscript(!showTranscript)}>
                {showTranscript ? "Hide" : "Show"} Full Evaluation Transcript
              </Button>
              </div>

            {showTranscript && (
              <Card className="shadow-lg" ref={transcriptRef}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BrainCircuit className="h-5 w-5 text-purple-500" />
                    Full Evaluation Transcript
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {analysisResult.transcript.map((turn, index) => {
                    if (turn.position === 'evaluation') {
                      return (
                        <div key={index} className="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/30">
                          <h4 className="font-semibold text-lg mb-2 flex items-center gap-2 text-blue-600 dark:text-blue-400">
                            <Target className="h-5 w-5" />
                            {turn.agent_name}'s Assessment
                          </h4>
                          <p className="text-slate-700 dark:text-slate-300">{turn.content}</p>
                        </div>
                      )
                    }
                    if (turn.position === 'pro' || turn.position === 'anti') {
                      const isPro = turn.position === 'pro';
                      return (
                        <div key={index} className={`p-4 rounded-lg ${isPro ? 'bg-emerald-50 dark:bg-emerald-900/30' : 'bg-red-50 dark:bg-red-900/30'}`}>
                          <h4 className={`font-semibold text-lg mb-2 flex items-center gap-2 ${isPro ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}`}>
                            {isPro ? <CheckCircle className="h-5 w-5" /> : <XCircle className="h-5 w-5" />}
                             {turn.agent_name}'s Argument (Round {Math.floor(index / 2) + (index % 2)})
                          </h4>
                          <p className="text-slate-700 dark:text-slate-300">{turn.content}</p>
                        </div>
                      )
                    }
                    return null;
                  })}
                  
                  {/* Final Decision in Transcript */}
                  <div className="!mt-8 pt-6 border-t-2 border-dashed border-violet-300 dark:border-violet-700">
                     <div className="p-4 rounded-lg bg-violet-50 dark:bg-violet-900/40 ring-1 ring-violet-200 dark:ring-violet-800">
                      <h4 className="font-semibold text-lg mb-2 flex items-center gap-2 text-violet-600 dark:text-violet-400">
                        <Scale className="h-5 w-5" />
                        Decision Agent's Final Assessment
                      </h4>
                      <p className="text-slate-700 dark:text-slate-300 italic mb-4">
                        "{analysisResult.decision.reasoning.summary}"
                      </p>
                       <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                          <div className="space-y-1">
                              <h5 className="font-semibold text-emerald-600 dark:text-emerald-500">Pros</h5>
                              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400">
                                  {analysisResult.decision.reasoning.pros.map((pro, i) => <li key={`pro-${i}`}>{pro}</li>)}
                              </ul>
                          </div>
                          <div className="space-y-1">
                              <h5 className="font-semibold text-red-600 dark:text-red-500">Cons</h5>
                              <ul className="list-disc list-inside text-slate-600 dark:text-slate-400">
                                  {analysisResult.decision.reasoning.cons.map((con, i) => <li key={`con-${i}`}>{con}</li>)}
                              </ul>
                          </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        ) : (
          <div className="grid gap-6">
            <div className="space-y-1">
              <h2 className="text-xl font-semibold">Select a Job Post</h2>
              <p className="text-muted-foreground">Choose a job to upload a candidate's resume for analysis.</p>
            </div>
            {allJobPosts.map((job) => (
              <Card key={job.id} className="group relative overflow-hidden border border-slate-200/60 bg-white/90 backdrop-blur-sm shadow-sm hover:shadow-lg hover:border-blue-300/60 transition-all duration-300 hover:-translate-y-0.5 dark:bg-slate-800/90 dark:border-slate-700/60 dark:hover:border-blue-600/60">
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between">
                    <div className="space-y-2">
                      <CardTitle className="text-lg font-bold text-slate-800 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                        {job.title}
                      </CardTitle>
                      <div className="flex items-center gap-4 text-sm text-slate-500 dark:text-slate-400">
                        <div className="flex items-center gap-1">
                          <MapPin className="h-4 w-4" />
                          <span>{job.location} • {job.employment_type || 'Full-time'}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          <span>Posted {job.posted}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className="uppercase bg-gradient-to-r from-emerald-500 to-teal-500 text-white border-0 shadow-md shadow-emerald-500/20">
                        {job.status}
                      </Badge>
                      {job.source === 'database' && (
                        <Badge variant="outline" className="uppercase border-blue-300 text-blue-600 dark:border-blue-600 dark:text-blue-400">
                          New
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-end">
                    <Button 
                      size="sm" 
                      variant="ghost"
                      onClick={() => handleUploadClick(job)}
                      className="gap-2 hover:bg-blue-50 hover:text-blue-600 dark:hover:bg-blue-900/20 dark:hover:text-blue-400"
                    >
                      <Upload className="h-4 w-4" />
                      Upload for this Job
                    </Button>
                </div>
            </CardContent>
          </Card>
            ))}
          </div>
        )}
      </div>

      <UploadResumeDialog
        job={selectedJob}
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        onUploadStart={handleUploadStart}
        onUploadComplete={handleUploadComplete}
      />
    </div>
  )
} 