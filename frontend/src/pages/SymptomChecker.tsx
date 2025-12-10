import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
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
  Stethoscope
} from "lucide-react";
import { toast } from "sonner";

const SymptomChecker = () => {
  const navigate = useNavigate();
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [customSymptom, setCustomSymptom] = useState("");
  const [description, setDescription] = useState("");
  const [duration, setDuration] = useState("");
  const [severity, setSeverity] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [isLoading, setIsLoading] = useState(false);

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
      // Call the ML model API
      const response: SymptomAnalysisResponse = await apiService.analyzeSymptoms({
        symptoms,
        description,
        age,
        gender,
        duration,
        severity,
      });

      if (response.success) {
        // Store API response in session storage for results page
        sessionStorage.setItem("symptomData", JSON.stringify({
          symptoms,
          description,
          duration,
          severity,
          age,
          gender,
        }));
        
        sessionStorage.setItem("analysisResults", JSON.stringify(response));
        
        toast.success("Analysis complete!");
        navigate("/results");
      } else {
        toast.error("Analysis failed. Please try again.");
      }
    } catch (error) {
      console.error("Analysis error:", error);
      toast.error(
        error instanceof Error 
          ? error.message 
          : "Failed to analyze symptoms. Please ensure the backend server is running."
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
          <div className="text-center max-w-2xl mx-auto mb-12">
            <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-2 rounded-full text-sm font-medium mb-4">
              <Activity className="h-4 w-4" />
              <span>Symptom Assessment</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold mb-4">
              Tell Us About Your <span className="gradient-text">Symptoms</span>
            </h1>
            <p className="text-muted-foreground">
              Provide information about your symptoms to receive personalized health insights and specialist recommendations.
            </p>
          </div>

          <div className="max-w-3xl mx-auto">
            {/* Main Card */}
            <div className="healthcare-card p-6 md:p-8 space-y-8">
              {/* Selected Symptoms */}
              <div>
                <Label className="text-base font-semibold flex items-center gap-2 mb-4">
                  <Stethoscope className="h-5 w-5 text-primary" />
                  Selected Symptoms
                </Label>
                <div className="flex flex-wrap gap-2 min-h-[48px] p-4 bg-secondary/50 rounded-xl border border-border">
                  {symptoms.length === 0 ? (
                    <span className="text-muted-foreground text-sm">
                      Click symptoms below or add your own...
                    </span>
                  ) : (
                    symptoms.map((symptom) => (
                      <Badge
                        key={symptom}
                        variant="secondary"
                        className="bg-primary/10 text-primary hover:bg-primary/20 px-3 py-1.5 text-sm font-medium cursor-pointer group"
                        onClick={() => removeSymptom(symptom)}
                      >
                        {symptom}
                        <X className="h-3 w-3 ml-2 group-hover:text-destructive transition-colors" />
                      </Badge>
                    ))
                  )}
                </div>
              </div>

              {/* Common Symptoms */}
              <div>
                <Label className="text-sm text-muted-foreground mb-3 block">
                  Quick Add - Common Symptoms
                </Label>
                <div className="flex flex-wrap gap-2">
                  {availableSymptoms.slice(0, 8).map((symptom) => (
                    <Badge
                      key={symptom}
                      variant="outline"
                      className="cursor-pointer hover:bg-primary hover:text-primary-foreground hover:border-primary transition-all px-3 py-1.5"
                      onClick={() => addSymptom(symptom)}
                    >
                      <Plus className="h-3 w-3 mr-1" />
                      {symptom}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Custom Symptom Input */}
              <div>
                <Label className="text-sm text-muted-foreground mb-2 block">
                  Add Custom Symptom
                </Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Type a symptom..."
                    value={customSymptom}
                    onChange={(e) => setCustomSymptom(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && addCustomSymptom()}
                    className="flex-1"
                  />
                  <Button onClick={addCustomSymptom} variant="secondary">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Additional Description */}
              <div>
                <Label className="text-base font-semibold flex items-center gap-2 mb-3">
                  <AlertCircle className="h-5 w-5 text-primary" />
                  Additional Details
                </Label>
                <Textarea
                  placeholder="Describe your symptoms in more detail... (e.g., when they started, what makes them better or worse)"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="min-h-[120px] resize-none"
                />
              </div>

              {/* Duration & Severity */}
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <Label className="text-base font-semibold flex items-center gap-2 mb-3">
                    <Clock className="h-5 w-5 text-primary" />
                    Duration
                  </Label>
                  <Select value={duration} onValueChange={setDuration}>
                    <SelectTrigger>
                      <SelectValue placeholder="How long have you had these symptoms?" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="today">Just started today</SelectItem>
                      <SelectItem value="days">A few days</SelectItem>
                      <SelectItem value="week">About a week</SelectItem>
                      <SelectItem value="weeks">2-4 weeks</SelectItem>
                      <SelectItem value="month">More than a month</SelectItem>
                      <SelectItem value="chronic">Chronic / Recurring</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-base font-semibold mb-3 block">
                    Severity *
                  </Label>
                  <Select value={severity} onValueChange={setSeverity}>
                    <SelectTrigger>
                      <SelectValue placeholder="How severe are your symptoms?" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="mild">Mild - Manageable, minor discomfort</SelectItem>
                      <SelectItem value="moderate">Moderate - Affecting daily activities</SelectItem>
                      <SelectItem value="severe">Severe - Significant impact on life</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Optional: Age & Gender */}
              <div>
                <Label className="text-base font-semibold flex items-center gap-2 mb-3">
                  <User className="h-5 w-5 text-primary" />
                  Optional Information
                </Label>
                <p className="text-sm text-muted-foreground mb-4">
                  Providing age and gender can help improve recommendations.
                </p>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <Label className="text-sm text-muted-foreground mb-2 block">Age</Label>
                    <Input
                      type="number"
                      placeholder="Your age"
                      value={age}
                      onChange={(e) => setAge(e.target.value)}
                      min="0"
                      max="120"
                    />
                  </div>
                  <div>
                    <Label className="text-sm text-muted-foreground mb-2 block">Gender</Label>
                    <Select value={gender} onValueChange={setGender}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select gender" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="male">Male</SelectItem>
                        <SelectItem value="female">Female</SelectItem>
                        <SelectItem value="other">Other / Prefer not to say</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <div className="pt-4 border-t border-border">
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
                      Analyzing Symptoms...
                    </>
                  ) : (
                    <>
                      Analyze Symptoms
                      <ArrowRight className="h-5 w-5" />
                    </>
                  )}
                </Button>
                <p className="text-center text-sm text-muted-foreground mt-4">
                  Your information is secure and will not be stored or shared.
                </p>
              </div>
            </div>

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
