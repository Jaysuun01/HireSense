"use client"

import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { 
  Upload, 
  FileText, 
  ArrowLeft, 
  Code, 
  Database, 
  Cloud, 
  BarChart3, 
  Smartphone,
  Globe,
  Shield,
  Cpu,
  ChevronRight,
  Loader2,
  CheckCircle,
  AlertCircle,
  Lightbulb,
  Target,
  TrendingUp,
  Users
} from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AnalysisInProgress } from "./analysis-in-progress"


interface ResumeBuilderFeedback {
  candidate_name: string
  field_selected: string
  current_strengths: string[]
  skill_gaps: string[]
  recommended_projects: string[]
  recommended_skills: string[]
  actionable_steps: string[]
  overall_score: number
  feedback_summary: string
}

interface ResumeBuilderContentProps {
  onBack: () => void
}

export function ResumeBuilderContent({ onBack }: ResumeBuilderContentProps) {
  const [step, setStep] = useState<'major' | 'field' | 'upload' | 'results'>('major')
  const [selectedMajor, setSelectedMajor] = useState<string>("")
  const [selectedField, setSelectedField] = useState<any>(null)
  const [customField, setCustomField] = useState<string>("")
  const [showCustomField, setShowCustomField] = useState<boolean>(false)
  const [candidateName, setCandidateName] = useState<string>("")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false)
  const [feedback, setFeedback] = useState<ResumeBuilderFeedback | null>(null)
  const [error, setError] = useState<string>("")
  const [careerFields, setCareerFields] = useState<any[]>([])
  const [loadingFields, setLoadingFields] = useState<boolean>(false)

  const onDrop = useCallback((acceptedFiles: File[], fileRejections: any[]) => {
    setError("")
    if (fileRejections.length > 0) {
      const firstError = fileRejections[0].errors[0]
      if (firstError.code === "file-too-large") {
        setError("File is larger than 10MB.")
      } else if (firstError.code === "file-invalid-type") {
        setError("Invalid file type. Please upload a PDF, DOC, or DOCX.")
      } else {
        setError(firstError.message)
      }
      setSelectedFile(null)
    } else if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0])
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/msword": [".doc"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
  })

  const getCareerFields = async (major: string) => {
    setLoadingFields(true)
    setError("")
    
    try {
      const formData = new FormData()
      formData.append("major", major.trim())

      const response = await fetch("http://localhost:8081/get-career-fields-for-major", {
        method: "POST",
        body: formData,
      })

      const result = await response.json()

      if (response.ok && result.career_fields) {
        setCareerFields(result.career_fields)
        setStep('field')
      } else {
        setError(result.message || "Could not get career fields for this major. Please try a different major.")
      }
    } catch (err) {
      console.error("Career fields error:", err)
      setError("Network error. Please check your connection and try again.")
    } finally {
      setLoadingFields(false)
    }
  }

  const handleAnalyze = async () => {
    if (!selectedFile || !candidateName.trim()) {
      setError("Please add a resume file and enter your name.")
      return
    }

    const fieldToAnalyze = customField.trim() || selectedField?.name || ""
    if (!fieldToAnalyze) {
      setError("Please select a field of interest.")
      return
    }

    setIsAnalyzing(true)
    setError("")

    try {
      const formData = new FormData()
      formData.append("resume_file", selectedFile)
      formData.append("candidate_name", candidateName.trim())
      formData.append("field_of_interest", fieldToAnalyze)
      formData.append("major", selectedMajor)

      // Call the new endpoint for Use Case 1
      const response = await fetch("http://localhost:8081/analyze-resume-for-improvement", {
        method: "POST",
        body: formData,
      })

      const result = await response.json()

      if (response.ok) {
        setFeedback(result)
        setStep('results')
      } else {
        setError(result.message || "Analysis failed. Please try again.")
      }
    } catch (err) {
      console.error("Analysis error:", err)
      setError("Network error. Please check your connection and try again.")
    } finally {
      setIsAnalyzing(false)
    }
  }

  const resetState = () => {
    setStep('major')
    setSelectedMajor("")
    setSelectedField(null)
    setCustomField("")
    setShowCustomField(false)
    setCandidateName("")
    setSelectedFile(null)
    setFeedback(null)
    setError("")
    setCareerFields([])
    setLoadingFields(false)
  }

  if (isAnalyzing) {
    return <AnalysisInProgress />
  }

  return (
    <div className="flex flex-1 flex-col bg-gradient-to-br from-slate-50 via-white to-emerald-50/30 dark:from-slate-950 dark:via-slate-900 dark:to-emerald-950/20">
      <header className="flex h-20 items-center justify-between border-b border-white/20 bg-white/70 backdrop-blur-xl px-8 shadow-sm dark:bg-slate-900/70 dark:border-slate-800/50">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={onBack} className="mr-2">
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-600 to-green-600">
            <FileText className="h-4 w-4 text-white" />
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-900 via-emerald-800 to-green-800 bg-clip-text text-transparent dark:from-white dark:via-emerald-200 dark:to-green-200">
            Resume Builder
          </h1>
        </div>
        {feedback && (
          <Button onClick={resetState} variant="outline">
            ← Start Over
          </Button>
        )}
      </header>

      <div className="flex-1 p-8">
        {/* Step 1: Major Selection */}
        {step === 'major' && (
          <div className="max-w-2xl mx-auto space-y-8">
            <div className="text-center space-y-4">
              <h2 className="text-3xl font-bold bg-gradient-to-r from-emerald-800 via-green-700 to-emerald-700 bg-clip-text text-transparent dark:from-emerald-200 dark:via-green-300 dark:to-emerald-300">
                What's Your Major?
              </h2>
              <p className="text-lg text-slate-600 dark:text-slate-400">
                Enter your field of study to discover popular career paths
              </p>
            </div>

            <Card>
              <CardContent className="space-y-6 pt-6">
                <div className="space-y-2">
                  <Label htmlFor="major">Your Major or Field of Study</Label>
                  <Input
                    id="major"
                    value={selectedMajor}
                    onChange={(e) => setSelectedMajor(e.target.value)}
                    placeholder="e.g., Computer Science, Mechanical Engineering, Business, Psychology..."
                    className="text-lg"
                  />
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Enter your current major, degree program, or area of study
                  </p>
                </div>

                {error && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <Button 
                  onClick={() => getCareerFields(selectedMajor)} 
                  size="lg" 
                  className="w-full bg-emerald-600 hover:bg-emerald-700"
                  disabled={!selectedMajor.trim() || loadingFields}
                >
                  {loadingFields ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Finding Career Fields...
                    </>
                  ) : (
                    <>
                      Discover Career Fields
                      <ChevronRight className="ml-2 h-4 w-4" />
                    </>
                  )}
                </Button>

                {/* Popular Majors Examples */}
                <div className="mt-6 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                  <h4 className="font-medium text-sm text-slate-700 dark:text-slate-300 mb-2">Popular majors include:</h4>
                  <div className="flex flex-wrap gap-2">
                    {["Computer Science", "Mechanical Engineering", "Business Administration", "Psychology", "Biology", "Marketing"].map((example) => (
                      <Button
                        key={example}
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedMajor(example)}
                        className="text-xs"
                      >
                        {example}
                      </Button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 2: Field Selection */}
        {step === 'field' && selectedMajor && (
          <div className="max-w-6xl mx-auto space-y-8">
            <div className="flex items-center justify-between mb-6">
              <Button 
                variant="outline" 
                onClick={() => setStep('major')}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Change Major
              </Button>
            </div>
            
            <div className="text-center space-y-4">
              <h2 className="text-3xl font-bold bg-gradient-to-r from-emerald-800 via-green-700 to-emerald-700 bg-clip-text text-transparent dark:from-emerald-200 dark:via-green-300 dark:to-emerald-300">
                Popular Career Fields for {selectedMajor}
              </h2>
              <p className="text-lg text-slate-600 dark:text-slate-400">
                Select a career field that interests you
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {careerFields.map((field) => {
                return (
                  <Card 
                    key={field.id} 
                    className={`cursor-pointer transition-all duration-300 hover:shadow-lg hover:-translate-y-1 ${
                      selectedField?.id === field.id 
                        ? 'ring-2 ring-emerald-500 bg-emerald-50 dark:bg-emerald-950/30' 
                        : 'hover:border-emerald-300'
                    }`}
                    onClick={() => {
                      setSelectedField(field)
                      setShowCustomField(false)
                      setCustomField("")
                    }}
                  >
                    <CardHeader>
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100 dark:bg-emerald-900/50">
                          <Target className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                        </div>
                        <CardTitle className="text-base">{field.name}</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-sm text-slate-600 dark:text-slate-400">{field.description}</p>
                      <div className="flex flex-wrap gap-1">
                        {field.key_skills?.slice(0, 3).map((skill: string, index: number) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {skill}
                          </Badge>
                        ))}
                        {field.key_skills?.length > 3 && (
                          <Badge variant="secondary" className="text-xs">
                            +{field.key_skills.length - 3} more
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-emerald-600 dark:text-emerald-400 font-medium">
                        {field.employment_outlook}
                      </p>
                    </CardContent>
                  </Card>
                )
              })}
            </div>

            {/* Custom Field Option */}
            <Card className="max-w-md mx-auto">
              <CardHeader>
                <CardTitle className="text-center">Don't see your field?</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setShowCustomField(true)
                    setSelectedField(null)
                  }}
                  className="w-full"
                >
                  Enter Custom Field
                </Button>
                {showCustomField && (
                  <div className="space-y-2">
                    <Label htmlFor="custom-field">Field of Interest</Label>
                    <Input
                      id="custom-field"
                      value={customField}
                      onChange={(e) => setCustomField(e.target.value)}
                      placeholder="e.g., Machine Learning, Quantum Computing"
                    />
                  </div>
                )}
              </CardContent>
            </Card>

            {(selectedField || (showCustomField && customField.trim())) && (
              <div className="text-center">
                <Button onClick={() => setStep('upload')} size="lg" className="bg-emerald-600 hover:bg-emerald-700">
                  Next: Upload Resume
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Step 3: Resume Upload */}
        {step === 'upload' && (
          <div className="max-w-2xl mx-auto space-y-8">
            <div className="text-center space-y-4">
              <h2 className="text-3xl font-bold bg-gradient-to-r from-emerald-800 via-green-700 to-emerald-700 bg-clip-text text-transparent dark:from-emerald-200 dark:via-green-300 dark:to-emerald-300">
                Upload Your Resume
              </h2>
              <p className="text-lg text-slate-600 dark:text-slate-400">
                We'll analyze your resume for {selectedField?.name || customField} and provide personalized recommendations
              </p>
            </div>

            <Card>
              <CardContent className="space-y-6 pt-6">
                <div className="space-y-2">
                  <Label htmlFor="name">Your Name</Label>
                  <Input
                    id="name"
                    value={candidateName}
                    onChange={(e) => setCandidateName(e.target.value)}
                    placeholder="Enter your full name"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Resume File</Label>
                  <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                      isDragActive
                        ? "border-emerald-400 bg-emerald-50 dark:bg-emerald-950/30"
                        : "border-slate-300 hover:border-emerald-400 dark:border-slate-700"
                    }`}
                  >
                    <input {...getInputProps()} />
                    {selectedFile ? (
                      <div className="space-y-2">
                        <CheckCircle className="h-12 w-12 text-emerald-500 mx-auto" />
                        <p className="font-medium">{selectedFile.name}</p>
                        <p className="text-sm text-slate-500">
                          {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <Upload className="h-12 w-12 text-slate-400 mx-auto" />
                        <p className="text-lg font-medium">
                          {isDragActive ? "Drop your resume here" : "Upload your resume"}
                        </p>
                        <p className="text-sm text-slate-500">
                          Drag & drop or click to browse (PDF, DOC, DOCX)
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {error && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <Button 
                  onClick={handleAnalyze} 
                  size="lg" 
                  className="w-full bg-emerald-600 hover:bg-emerald-700"
                  disabled={!selectedFile || !candidateName.trim()}
                >
                  Analyze My Resume
                  <Target className="ml-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 4: Results */}
        {step === 'results' && feedback && (
          <div className="max-w-6xl mx-auto space-y-8">
            <div className="text-center space-y-4">
              <h2 className="text-3xl font-bold bg-gradient-to-r from-emerald-800 via-green-700 to-emerald-700 bg-clip-text text-transparent dark:from-emerald-200 dark:via-green-300 dark:to-emerald-300">
                Your Resume Analysis
              </h2>
              <p className="text-lg text-slate-600 dark:text-slate-400">
                Personalized recommendations for {feedback.candidate_name}
              </p>
            </div>

            {/* Overall Score */}
            <Card className="bg-gradient-to-br from-emerald-50 to-green-50 dark:from-emerald-950/30 dark:to-green-950/20 border-emerald-200 dark:border-emerald-800">
              <CardContent className="text-center py-8">
                <div className="space-y-4">
                  <div className="text-6xl font-bold text-emerald-600 dark:text-emerald-400">
                    {feedback.overall_score}/10
                  </div>
                  <p className="text-lg font-medium text-emerald-800 dark:text-emerald-200">
                    Resume Readiness Score
                  </p>
                  <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
                    {feedback.feedback_summary}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Analysis Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Current Strengths */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400">
                    <CheckCircle className="h-5 w-5" />
                    Current Strengths
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {feedback.current_strengths.map((strength, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-2 shrink-0"></div>
                        <span className="text-sm">{strength}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Skill Gaps */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-amber-600 dark:text-amber-400">
                    <AlertCircle className="h-5 w-5" />
                    Areas for Improvement
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {feedback.skill_gaps.map((gap, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-2 shrink-0"></div>
                        <span className="text-sm">{gap}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Recommended Skills */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                    <TrendingUp className="h-5 w-5" />
                    Skills to Learn
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {feedback.recommended_skills.map((skill, index) => (
                      <Badge key={index} variant="secondary" className="bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Recommended Projects */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-violet-600 dark:text-violet-400">
                    <Lightbulb className="h-5 w-5" />
                    Project Ideas
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {feedback.recommended_projects.map((project, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-violet-500 mt-2 shrink-0"></div>
                        <span className="text-sm">{project}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>

            {/* Actionable Steps */}
            <Card className="bg-gradient-to-br from-blue-50 to-violet-50 dark:from-blue-950/30 dark:to-violet-950/20 border-blue-200 dark:border-blue-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                  <Target className="h-5 w-5" />
                  Your Action Plan
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ol className="space-y-4">
                  {feedback.actionable_steps.map((step, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <div className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 text-white text-sm font-bold shrink-0">
                        {index + 1}
                      </div>
                      <span className="text-sm font-medium">{step}</span>
                    </li>
                  ))}
                </ol>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
