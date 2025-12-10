import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { commonSymptoms } from "@/data/mockData";
import { apiService, SymptomAnalysisResponse } from "@/services/api";
import {
  Activity,
  X,
  Plus,
  AlertCircle,
  Clock,
  User,
  ArrowRight,
  ArrowLeft,
  Stethoscope,
  CheckCircle2,
} from "lucide-react";
import { toast } from "sonner";

const SymptomChecker = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [customSymptom, setCustomSymptom] = useState("");
  const [description, setDescription] = useState("");
  const [duration, setDuration] = useState("");
  const [severity, setSeverity] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [medicalHistory, setMedicalHistory] = useState("");
  const [currentMedications, setCurrentMedications] = useState("");
  const [allergies, setAllergies] = useState("");
  const [followUpQuestions, setFollowUpQuestions] = useState<Array<{question: string; type: 'yesno' | 'scale' | 'text' | 'choice'; options?: string[]; answer: string}>>([]);
  const [isLoading, setIsLoading] = useState(false);

  const totalSteps = 6;

  const addSymptom = (symptom: string) => {
    if (!symptoms.includes(symptom) && symptoms.length < 10) {
      setSymptoms([...symptoms, symptom]);
    }
  };

  const removeSymptom = (symptom: string) => {
    setSymptoms(symptoms.filter((s) => s !== symptom));
  };

  const addCustomSymptom = () => {
    if (customSymptom.trim() && !symptoms.includes(customSymptom.trim())) {
      addSymptom(customSymptom.trim());
      setCustomSymptom("");
    }
  };

  // Generate dynamic follow-up questions based on symptoms
  const generateFollowUpQuestions = () => {
    const questions: Array<{question: string; type: 'yesno' | 'scale' | 'text' | 'choice'; options?: string[]; answer: string}> = [];
    
    if (symptoms.some(s => s.toLowerCase().includes('fever') || s.toLowerCase().includes('temperature'))) {
      questions.push({ question: "Have you measured your temperature?", type: 'yesno', answer: '' });
    }
    if (symptoms.some(s => s.toLowerCase().includes('pain') || s.toLowerCase().includes('ache'))) {
      questions.push({ question: "On a scale of 1-10, how would you rate your pain?", type: 'scale', answer: '' });
    }
    if (symptoms.some(s => s.toLowerCase().includes('cough'))) {
      questions.push({ 
        question: "What type of cough are you experiencing?", 
        type: 'choice',
        options: ['Dry cough', 'Wet/Productive cough', 'Both'],
        answer: '' 
      });
    }
    if (symptoms.some(s => s.toLowerCase().includes('nausea') || s.toLowerCase().includes('vomit'))) {
      questions.push({ question: "Have you been able to keep food or liquids down?", type: 'yesno', answer: '' });
    }
    if (symptoms.some(s => s.toLowerCase().includes('headache'))) {
      questions.push({ question: "Where is the headache located and does light bother you?", type: 'text', answer: '' });
    }
    
    // Generic questions if none of the above match
    if (questions.length === 0) {
      questions.push({ question: "Does anything make your symptoms better or worse?", type: 'text', answer: '' });
      questions.push({ question: "Have you taken any medication for these symptoms?", type: 'yesno', answer: '' });
    }
    
    // Always add up to 5 questions
    const defaultQuestions: Array<{question: string; type: 'yesno' | 'scale' | 'text'; answer: string}> = [
      { question: "Have you had any recent injuries or accidents?", type: 'yesno', answer: '' },
      { question: "Are you currently taking any medications?", type: 'yesno', answer: '' },
      { question: "Do you have any known allergies?", type: 'yesno', answer: '' },
      { question: "Have you traveled recently?", type: 'yesno', answer: '' },
      { question: "Has anyone close to you been sick with similar symptoms?", type: 'yesno', answer: '' }
    ];
    
    while (questions.length < 5) {
      const next = defaultQuestions[questions.length - questions.length + defaultQuestions.length - (5 - questions.length)];
      if (next && !questions.some(q => q.question === next.question)) {
        questions.push(next);
      } else if (defaultQuestions[questions.length]) {
        questions.push(defaultQuestions[questions.length]);
      } else {
        break;
      }
    }
    
    return questions.slice(0, 5);
  };

  const toggleFollowUpAnswer = (index: number, answer: string) => {
    const updated = [...followUpQuestions];
    updated[index].answer = answer;
    setFollowUpQuestions(updated);
  };

  const nextStep = () => {
    if (currentStep === 1 && symptoms.length === 0) {
      toast.error("Please select at least one symptom");
      return;
    }
    if (currentStep === 2 && !severity) {
      toast.error("Please select the severity of your symptoms");
      return;
    }
    if (currentStep === 3 && currentStep < totalSteps) {
      // Generate follow-up questions when moving from step 3 to 4
      if (followUpQuestions.length === 0) {
        setFollowUpQuestions(generateFollowUpQuestions());
      }
    }
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleAnalyze = async () => {
    if (symptoms.length === 0 && !description.trim()) {
      toast.error("Please add at least one symptom or describe your condition");
      return;
    }

    if (!severity) {
      toast.error("Please select the severity of your symptoms");
      return;
    }

    setIsLoading(true);

    try {
      // Try ML model API first
      try {
        const response: SymptomAnalysisResponse = await apiService.analyzeSymptoms({
          symptoms,
          description,
          age,
          gender,
          duration,
          severity,
          medicalHistory,
          currentMedications,
          allergies,
          followUpAnswers: followUpQuestions.reduce((acc, q) => {
            if (q.answer) acc[q.question] = q.answer;
            return acc;
          }, {} as Record<string, string>),
        });

        if (response.success) {
          sessionStorage.setItem("symptomData", JSON.stringify({
            symptoms,
            description,
            duration,
            severity,
            age,
            gender,
            medicalHistory,
            currentMedications,
            allergies,
            followUpAnswers: followUpQuestions.reduce((acc, q) => {
              if (q.answer) acc[q.question] = q.answer;
              return acc;
            }, {} as Record<string, string>),
          }));
          
          sessionStorage.setItem("analysisResults", JSON.stringify(response));
          
          toast.success("Analysis complete!");
          navigate("/results");
          return;
        }
      } catch (mlError) {
        console.log("ML API not available, falling back to simple assessment");
      }

      // Fallback to simple assessment endpoint
      const res = await fetch("http://127.0.0.1:5000/api/assess", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symptoms,
          description,
          duration,
          severity,
          age,
          gender,
        }),
      });

      if (!res.ok) {
        throw new Error("Backend error");
      }

      const assessment = await res.json();

      sessionStorage.setItem(
        "symptomData",
        JSON.stringify({
          symptoms,
          description,
          duration,
          severity,
          age,
          gender,
          assessment,
        })
      );

      toast.success("Analysis complete!");
      navigate("/results");
    } catch (error) {
      console.error("Analysis error:", error);
      toast.error(
        "Unable to analyze symptoms. Please ensure the backend server is running."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const availableSymptoms = commonSymptoms.filter((s) => !symptoms.includes(s));

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-secondary/30 to-background py-12">
        <div className="container mx-auto px-4 lg:px-8">
          {/* Header */}
          <div className="text-center max-w-2xl mx-auto mb-8">
            <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-2 rounded-full text-sm font-medium mb-4">
              <Activity className="h-4 w-4" />
              <span>Symptom Assessment</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold mb-4">
              Tell Us About Your <span className="gradient-text">Symptoms</span>
            </h1>
            <p className="text-muted-foreground">
              Step-by-step symptom assessment for personalized health insights.
            </p>
          </div>

          {/* Progress Indicator */}
          <div className="max-w-3xl mx-auto mb-8">
            <div className="flex items-center justify-between">
              {[1, 2, 3, 4, 5, 6].map((step) => (
                <div key={step} className="flex items-center flex-1 last:flex-none">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all ${
                    step < currentStep 
                      ? 'bg-primary border-primary text-primary-foreground' 
                      : step === currentStep 
                      ? 'border-primary text-primary bg-primary/10' 
                      : 'border-border text-muted-foreground'
                  }`}>
                    {step < currentStep ? (
                      <CheckCircle2 className="h-5 w-5" />
                    ) : (
                      <span className="text-sm font-semibold">{step}</span>
                    )}
                  </div>
                  {step < 6 && (
                    <div className={`h-0.5 flex-1 mx-2 transition-all ${
                      step < currentStep ? 'bg-primary' : 'bg-border'
                    }`} />
                  )}
                </div>
              ))}
            </div>
            <div className="flex justify-between mt-2 text-xs text-muted-foreground">
              <span>Symptoms</span>
              <span>Severity</span>
              <span>Details</span>
              <span>Questions</span>
              <span>Medical</span>
              <span>Personal</span>
            </div>
          </div>

          <div className="max-w-3xl mx-auto">
            {/* Step 1: Select Symptoms */}
            {currentStep === 1 && (
              <Card className="healthcare-card animate-in fade-in slide-in-from-bottom-4 duration-500">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Stethoscope className="h-6 w-6 text-primary" />
                    What Symptoms Are You Experiencing?
                  </CardTitle>
                  <CardDescription>
                    Select from common symptoms or add your own
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Selected Symptoms */}
                  <div className="flex flex-wrap gap-2 min-h-[60px] p-4 bg-secondary/50 rounded-xl border-2 border-dashed border-border">
                    {symptoms.length === 0 ? (
                      <span className="text-muted-foreground text-sm flex items-center gap-2">
                        <Plus className="h-4 w-4" />
                        Click symptoms below to add them...
                      </span>
                    ) : (
                      symptoms.map((symptom) => (
                        <Badge
                          key={symptom}
                          variant="secondary"
                          className="bg-primary/10 text-primary hover:bg-primary/20 px-3 py-2 text-sm font-medium cursor-pointer group"
                          onClick={() => removeSymptom(symptom)}
                        >
                          {symptom}
                          <X className="h-3 w-3 ml-2 group-hover:text-destructive transition-colors" />
                        </Badge>
                      ))
                    )}
                  </div>

                  {/* Common Symptoms Grid */}
                  <div>
                    <Label className="text-sm font-medium mb-3 block">Common Symptoms</Label>
                    <div className="grid grid-cols-3 md:grid-cols-4 gap-2">
                      {availableSymptoms.slice(0, 16).map((symptom) => (
                        <Button
                          key={symptom}
                          variant="outline"
                          size="sm"
                          className="justify-start h-auto py-2 px-3 text-xs hover:bg-primary/10 hover:text-primary hover:border-primary"
                          onClick={() => addSymptom(symptom)}
                        >
                          <Plus className="h-3 w-3 mr-1.5 flex-shrink-0" />
                          <span className="text-left truncate">{symptom}</span>
                        </Button>
                      ))}
                    </div>
                  </div>

                  {/* Custom Symptom */}
                  <div>
                    <Label className="text-sm font-medium mb-2 block">Add Custom Symptom</Label>
                    <div className="flex gap-2">
                      <Input
                        placeholder="Type a symptom not listed above..."
                        value={customSymptom}
                        onChange={(e) => setCustomSymptom(e.target.value)}
                        onKeyPress={(e) => e.key === "Enter" && addCustomSymptom()}
                        className="flex-1"
                      />
                      <Button onClick={addCustomSymptom} variant="secondary" size="icon">
                        <Plus className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  {/* Navigation */}
                  <div className="flex justify-end pt-4">
                    <Button onClick={nextStep} size="lg" className="gap-2">
                      Continue
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Step 2: Severity & Duration */}
            {currentStep === 2 && (
              <Card className="healthcare-card animate-in fade-in slide-in-from-bottom-4 duration-500">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertCircle className="h-6 w-6 text-primary" />
                    How Severe Are Your Symptoms?
                  </CardTitle>
                  <CardDescription>
                    Help us understand the intensity and duration
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <Label className="text-base font-semibold mb-3 block">Severity Level *</Label>
                    <div className="grid gap-3">
                      {[
                        { value: 'mild', label: 'Mild', desc: 'Manageable, minor discomfort' },
                        { value: 'moderate', label: 'Moderate', desc: 'Affecting daily activities' },
                        { value: 'severe', label: 'Severe', desc: 'Significant impact on life' }
                      ].map((option) => (
                        <button
                          key={option.value}
                          onClick={() => setSeverity(option.value)}
                          className={`p-4 rounded-xl border-2 text-left transition-all hover:border-primary/50 ${
                            severity === option.value 
                              ? 'border-primary bg-primary/5' 
                              : 'border-border'
                          }`}
                        >
                          <div className="font-semibold">{option.label}</div>
                          <div className="text-sm text-muted-foreground">{option.desc}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <Label className="text-base font-semibold flex items-center gap-2 mb-3">
                      <Clock className="h-5 w-5 text-primary" />
                      How Long Have You Had These Symptoms?
                    </Label>
                    <Select value={duration} onValueChange={setDuration}>
                      <SelectTrigger className="h-12">
                        <SelectValue placeholder="Select duration" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="today">Just started today</SelectItem>
                        <SelectItem value="days">A few days (2-3 days)</SelectItem>
                        <SelectItem value="week">About a week</SelectItem>
                        <SelectItem value="weeks">2-4 weeks</SelectItem>
                        <SelectItem value="month">More than a month</SelectItem>
                        <SelectItem value="chronic">Chronic / Recurring</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Navigation */}
                  <div className="flex justify-between pt-4">
                    <Button onClick={prevStep} variant="outline" size="lg" className="gap-2">
                      <ArrowLeft className="h-4 w-4" />
                      Back
                    </Button>
                    <Button onClick={nextStep} size="lg" className="gap-2">
                      Continue
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Step 3: Additional Details */}
            {currentStep === 3 && (
              <Card className="healthcare-card animate-in fade-in slide-in-from-bottom-4 duration-500">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertCircle className="h-6 w-6 text-primary" />
                    Describe Your Condition
                  </CardTitle>
                  <CardDescription>
                    Provide additional context about your symptoms (optional but helpful)
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <Label className="text-sm font-medium mb-2 block">
                      Additional Details
                    </Label>
                    <Textarea
                      placeholder="Describe when symptoms started, what makes them better or worse, any patterns you've noticed, etc."
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      className="min-h-[160px] resize-none"
                    />
                    <p className="text-xs text-muted-foreground mt-2">
                      The more details you provide, the better we can assist you
                    </p>
                  </div>

                  {/* Navigation */}
                  <div className="flex justify-between pt-4">
                    <Button onClick={prevStep} variant="outline" size="lg" className="gap-2">
                      <ArrowLeft className="h-4 w-4" />
                      Back
                    </Button>
                    <Button onClick={nextStep} size="lg" className="gap-2">
                      Continue
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Step 4: Follow-up Questions */}
            {currentStep === 4 && (
              <Card className="healthcare-card animate-in fade-in slide-in-from-bottom-4 duration-500">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-6 w-6 text-primary" />
                    A Few More Questions
                  </CardTitle>
                  <CardDescription>
                    These questions help us provide more accurate recommendations
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {followUpQuestions.map((q, index) => (
                    <div key={index} className="space-y-3">
                      <Label className="text-sm font-medium">{q.question}</Label>
                      
                      {/* Yes/No Questions */}
                      {q.type === 'yesno' && (
                        <div className="flex gap-2">
                          <Button
                            variant={q.answer === 'yes' ? 'default' : 'outline'}
                            className="flex-1"
                            onClick={() => toggleFollowUpAnswer(index, 'yes')}
                          >
                            Yes
                          </Button>
                          <Button
                            variant={q.answer === 'no' ? 'default' : 'outline'}
                            className="flex-1"
                            onClick={() => toggleFollowUpAnswer(index, 'no')}
                          >
                            No
                          </Button>
                          <Button
                            variant={q.answer === 'unsure' ? 'default' : 'outline'}
                            className="flex-1"
                            onClick={() => toggleFollowUpAnswer(index, 'unsure')}
                          >
                            Not Sure
                          </Button>
                        </div>
                      )}

                      {/* Scale Questions (1-10) */}
                      {q.type === 'scale' && (
                        <div className="space-y-3">
                          <div className="flex justify-between gap-2">
                            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                              <Button
                                key={num}
                                variant={q.answer === num.toString() ? 'default' : 'outline'}
                                className="h-10 w-10 rounded-full p-0 flex-shrink-0"
                                onClick={() => toggleFollowUpAnswer(index, num.toString())}
                              >
                                {num}
                              </Button>
                            ))}
                          </div>
                          <div className="flex justify-between text-xs text-muted-foreground px-1">
                            <span>Minimal</span>
                            <span>Moderate</span>
                            <span>Severe</span>
                          </div>
                        </div>
                      )}

                      {/* Multiple Choice Questions */}
                      {q.type === 'choice' && q.options && (
                        <div className="space-y-2">
                          {q.options.map((option) => (
                            <Button
                              key={option}
                              variant={q.answer === option ? 'default' : 'outline'}
                              className="w-full justify-start"
                              onClick={() => toggleFollowUpAnswer(index, option)}
                            >
                              {q.answer === option && <CheckCircle2 className="h-4 w-4 mr-2" />}
                              {option}
                            </Button>
                          ))}
                        </div>
                      )}

                      {/* Text Input Questions */}
                      {q.type === 'text' && (
                        <Textarea
                          placeholder="Type your answer here..."
                          value={q.answer}
                          onChange={(e) => toggleFollowUpAnswer(index, e.target.value)}
                          className="min-h-[80px] resize-none"
                        />
                      )}
                    </div>
                  ))}

                  {/* Navigation */}
                  <div className="flex justify-between pt-4">
                    <Button onClick={prevStep} variant="outline" size="lg" className="gap-2">
                      <ArrowLeft className="h-4 w-4" />
                      Back
                    </Button>
                    <Button onClick={nextStep} size="lg" className="gap-2">
                      Continue
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Step 5: Medical History */}
            {currentStep === 5 && (
              <Card className="healthcare-card animate-in fade-in slide-in-from-bottom-4 duration-500">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-6 w-6 text-primary" />
                    Medical History
                  </CardTitle>
                  <CardDescription>
                    This information helps provide more accurate recommendations (optional)
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <Label className="text-sm font-medium mb-2 block">
                      Current Medications
                    </Label>
                    <Textarea
                      placeholder="List any medications you're currently taking..."
                      value={currentMedications}
                      onChange={(e) => setCurrentMedications(e.target.value)}
                      className="min-h-[80px] resize-none"
                    />
                  </div>

                  <div>
                    <Label className="text-sm font-medium mb-2 block">
                      Known Allergies
                    </Label>
                    <Textarea
                      placeholder="List any allergies you have (medications, food, etc.)..."
                      value={allergies}
                      onChange={(e) => setAllergies(e.target.value)}
                      className="min-h-[80px] resize-none"
                    />
                  </div>

                  <div>
                    <Label className="text-sm font-medium mb-2 block">
                      Relevant Medical History
                    </Label>
                    <Textarea
                      placeholder="Any chronic conditions, past surgeries, or relevant medical history..."
                      value={medicalHistory}
                      onChange={(e) => setMedicalHistory(e.target.value)}
                      className="min-h-[100px] resize-none"
                    />
                  </div>

                  {/* Navigation */}
                  <div className="flex justify-between pt-4">
                    <Button onClick={prevStep} variant="outline" size="lg" className="gap-2">
                      <ArrowLeft className="h-4 w-4" />
                      Back
                    </Button>
                    <Button onClick={nextStep} size="lg" className="gap-2">
                      Continue
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Step 6: Personal Info & Submit */}
            {currentStep === 6 && (
              <Card className="healthcare-card animate-in fade-in slide-in-from-bottom-4 duration-500">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-6 w-6 text-primary" />
                    Personal Information & Review
                  </CardTitle>
                  <CardDescription>
                    Final details to complete your health assessment
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <Label className="text-sm font-medium mb-2 block">Age</Label>
                      <Input
                        type="number"
                        placeholder="Your age (optional)"
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                        min="0"
                        max="120"
                        className="h-12"
                      />
                    </div>
                    <div>
                      <Label className="text-sm font-medium mb-2 block">Gender</Label>
                      <Select value={gender} onValueChange={setGender}>
                        <SelectTrigger className="h-12">
                          <SelectValue placeholder="Select (optional)" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="male">Male</SelectItem>
                          <SelectItem value="female">Female</SelectItem>
                          <SelectItem value="other">Other / Prefer not to say</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {/* Summary */}
                  <div className="p-4 bg-secondary/50 rounded-xl space-y-2">
                    <h4 className="font-semibold text-sm mb-3">Assessment Summary</h4>
                    <div className="text-sm space-y-2">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Symptoms:</span>
                        <span className="font-medium">{symptoms.length} selected</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Severity:</span>
                        <span className="font-medium capitalize">{severity || 'Not specified'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Duration:</span>
                        <span className="font-medium">{duration || 'Not specified'}</span>
                      </div>
                      {followUpQuestions.filter(q => q.answer).length > 0 && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Questions answered:</span>
                          <span className="font-medium">{followUpQuestions.filter(q => q.answer).length}/{followUpQuestions.length}</span>
                        </div>
                      )}
                      {(currentMedications || allergies || medicalHistory) && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Medical history:</span>
                          <span className="font-medium text-green-600">✓ Provided</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Submit */}
                  <div className="space-y-4">
                    <Button
                      onClick={handleAnalyze}
                      variant="hero"
                      size="xl"
                      className="w-full"
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <>
                          <div className="h-5 w-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                          Analyzing Your Symptoms...
                        </>
                      ) : (
                        <>
                          Get Health Assessment
                          <ArrowRight className="h-5 w-5" />
                        </>
                      )}
                    </Button>
                    <Button 
                      onClick={prevStep} 
                      variant="ghost" 
                      className="w-full"
                      disabled={isLoading}
                    >
                      <ArrowLeft className="h-4 w-4 mr-2" />
                      Back to Medical History
                    </Button>
                    <p className="text-center text-xs text-muted-foreground">
                      Your information is secure and will not be stored or shared.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Disclaimer */}
            <div className="mt-6 p-4 bg-warning/10 border border-warning/20 rounded-xl">
              <p className="text-sm text-muted-foreground text-center">
                <strong className="text-warning">Important:</strong> This tool provides general health information only and is not intended as medical advice.
                Always consult a qualified healthcare professional for proper diagnosis and treatment.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default SymptomChecker;
