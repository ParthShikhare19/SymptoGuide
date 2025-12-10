import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { symptomCategories, specialists } from "@/data/mockData";
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Stethoscope,
  Building2,
  ArrowRight,
  ArrowLeft,
  Wind,
  Utensils,
  Droplets,
  Brain,
  Heart,
  Thermometer,
  Ear,
  Bone,
  Phone,
  AlertCircle,
} from "lucide-react";

const iconMap: Record<string, React.ElementType> = {
  Wind,
  Utensils,
  Droplets,
  Brain,
  Heart,
  Thermometer,
  Stethoscope,
  Ear,
  Bone,
};

const Results = () => {
  const navigate = useNavigate();
  const [symptomData, setSymptomData] = useState<any>(null);
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const data = sessionStorage.getItem("symptomData");
    const results = sessionStorage.getItem("analysisResults");
    
    if (!data) {
      navigate("/symptom-checker");
      return;
    }
    
    setSymptomData(JSON.parse(data));
    if (results) {
      setAnalysisResults(JSON.parse(results));
    }
    
    setTimeout(() => setIsLoading(false), 800);
  }, [navigate]);

  if (isLoading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-secondary/30 to-background">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-primary/30 border-t-primary rounded-full animate-spin mx-auto mb-4" />
            <p className="text-muted-foreground">Analyzing your symptoms...</p>
          </div>
        </div>
      </Layout>
    );
  }

  // Get ML model results if available
  const prediction = analysisResults?.prediction;
  const severity = analysisResults?.severity;
  const recommendations = analysisResults?.recommendations;
  
  // Get assessment data (fallback)
  const assessment = symptomData?.assessment;
  const concernLevel: "low" | "moderate" | "high" =
    assessment?.concern_level || "low";
  const isEmergencyBackend = concernLevel === "high";
  const isEmergency = severity?.is_emergency || isEmergencyBackend || symptomData?.severity === "severe";
  
  const allSymptoms: string[] = symptomData?.symptoms || [];
  const departments: string[] =
    assessment?.recommended_departments || ["Primary Care"];

  // Generate dynamic concern areas based on ML severity or fallback to mock categories
  const getConcernAreas = () => {
    if (severity?.symptom_details) {
      // Use ML model data
      const concerns: Array<{
        id: string;
        name: string;
        description: string;
        severity: 'low' | 'medium' | 'high';
        icon: string;
      }> = [];

      const sortedSymptoms = Object.entries(severity.symptom_details)
        .sort(([, a], [, b]) => (b as number) - (a as number))
        .slice(0, 5);

      sortedSymptoms.forEach(([symptom, severityScore], index) => {
        const score = severityScore as number;
        const symptomName = symptom.replace(/_/g, ' ').split(' ').map(w => 
          w.charAt(0).toUpperCase() + w.slice(1)
        ).join(' ');
        
        let severityLevel: 'low' | 'medium' | 'high' = 'low';
        if (score >= 6) severityLevel = 'high';
        else if (score >= 4) severityLevel = 'medium';
        
        const getIconForSymptom = (sym: string) => {
          if (sym.includes('breath') || sym.includes('respiratory')) return 'Wind';
          if (sym.includes('heart') || sym.includes('chest')) return 'Heart';
          if (sym.includes('head') || sym.includes('brain') || sym.includes('mental')) return 'Brain';
          if (sym.includes('fever') || sym.includes('temperature')) return 'Thermometer';
          if (sym.includes('ear') || sym.includes('hearing')) return 'Ear';
          if (sym.includes('bone') || sym.includes('joint') || sym.includes('muscle')) return 'Bone';
          if (sym.includes('stomach') || sym.includes('digest') || sym.includes('nausea')) return 'Utensils';
          if (sym.includes('fluid') || sym.includes('swelling') || sym.includes('blood')) return 'Droplets';
          return 'Stethoscope';
        };
        
        concerns.push({
          id: `concern-${index}`,
          name: symptomName,
          description: `Severity score: ${score}/10`,
          severity: severityLevel,
          icon: getIconForSymptom(symptom.toLowerCase())
        });
      });

      return concerns;
    }
    
    // Fallback to mock categories based on symptoms
    const relevantCategories = symptomCategories
      .filter((cat) => {
        const keywords = (cat.keywords || []) as string[];
        const text = keywords.join(" ").toLowerCase();
        return allSymptoms.some((s) => text.includes(s.toLowerCase()));
      })
      .slice(0, 3);

    return relevantCategories.length > 0 ? relevantCategories : symptomCategories.slice(0, 3);
  };

  // Get specialist info based on ML recommendation or fallback to mock specialists
  const getSpecialistInfo = () => {
    if (recommendations?.specialist) {
      // Use ML model recommendation
      const specialistName = recommendations.specialist;
      
      const getConditionsForSpecialist = () => {
        if (!prediction?.disease) return [];
        const conditions = [prediction.disease];
        if (prediction.alternatives) {
          prediction.alternatives.slice(0, 2).forEach((alt: any) => {
            conditions.push(alt.disease);
          });
        }
        return conditions;
      };

      const getIconForSpecialist = (specialist: string) => {
        const s = specialist.toLowerCase();
        if (s.includes('cardio') || s.includes('heart')) return 'Heart';
        if (s.includes('neuro') || s.includes('brain')) return 'Brain';
        if (s.includes('ent') || s.includes('ear')) return 'Ear';
        if (s.includes('ortho') || s.includes('bone')) return 'Bone';
        if (s.includes('respir') || s.includes('lung')) return 'Wind';
        if (s.includes('gastro') || s.includes('digest')) return 'Utensils';
        return 'Stethoscope';
      };

      return {
        id: 'specialist-1',
        name: specialistName,
        title: 'Medical Specialist',
        description: recommendations.description || `Specialized in treating ${prediction?.disease || 'your condition'}`,
        icon: getIconForSpecialist(specialistName),
        conditions: getConditionsForSpecialist()
      };
    }
    return null;
  };

  const concernAreas = getConcernAreas();
  const specialistInfo = getSpecialistInfo();
  
  // Fallback specialists list
  const recommendedSpecialists = specialists
    .filter((sp) => {
      const spDepts = (sp.departments || []) as string[];
      return departments.some((d) => spDepts.includes(d));
    })
    .slice(0, 4);

  const finalSpecialists =
    recommendedSpecialists.length > 0
      ? recommendedSpecialists
      : specialists.slice(0, 4);

  const firstDepartment = departments[0] || "Primary Care";

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-secondary/30 to-background py-12">
        <div className="container mx-auto px-4 lg:px-8">
          {/* Header */}
          <div className="text-center max-w-2xl mx-auto mb-8">
            <div className="inline-flex items-center gap-2 bg-success/10 text-success px-4 py-2 rounded-full text-sm font-medium mb-4">
              <CheckCircle className="h-4 w-4" />
              <span>Analysis Complete</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold mb-4">
              Your Symptom <span className="gradient-text">Analysis</span>
            </h1>
            <p className="text-muted-foreground">
              Based on your symptoms:{" "}
              {symptomData?.symptoms?.join(", ") || "General assessment"}
            </p>
          </div>

          {/* Back Button */}
          <div className="max-w-4xl mx-auto mb-6">
            <Link to="/symptom-checker">
              <Button variant="ghost" className="gap-2">
                <ArrowLeft className="h-4 w-4" />
                Modify Symptoms
              </Button>
            </Link>
          </div>

          <div className="max-w-4xl mx-auto space-y-8">
            {/* ML Prediction Results */}
            {prediction && (
              <section className="healthcare-card p-6 md:p-8 bg-gradient-to-br from-primary/5 to-accent/5">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Brain className="h-5 w-5 text-primary" />
                  </div>
                  <h2 className="text-xl font-bold">AI-Powered Diagnosis</h2>
                </div>
                
                <div className="space-y-4">
                  {/* Primary Prediction */}
                  <div className="p-5 rounded-xl bg-white/50 dark:bg-secondary/50 border-2 border-primary/30">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className="bg-primary">Primary Prediction</Badge>
                          <Badge variant="outline" className="text-xs">
                            {(prediction.confidence * 100).toFixed(1)}% Confidence
                          </Badge>
                        </div>
                        <h3 className="text-2xl font-bold mb-2">{prediction.disease}</h3>
                        {recommendations?.description && (
                          <p className="text-muted-foreground text-sm">{recommendations.description}</p>
                        )}
                      </div>
                      <CheckCircle className="h-8 w-8 text-primary flex-shrink-0" />
                    </div>
                  </div>

                  {/* Alternative Predictions */}
                  {prediction.alternatives && prediction.alternatives.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold mb-3 text-muted-foreground">Other Possibilities</h4>
                      <div className="grid gap-3">
                        {prediction.alternatives.map((alt: any, index: number) => (
                          <div key={index} className="p-4 rounded-lg bg-secondary/30 border border-border">
                            <div className="flex items-center justify-between">
                              <span className="font-medium">{alt.disease}</span>
                              <Badge variant="secondary" className="text-xs">
                                {(alt.probability * 100).toFixed(1)}%
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </section>
            )}

            {/* Severity Assessment */}
            {severity && (
              <section className="healthcare-card p-6 md:p-8">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-warning/10 rounded-lg">
                    <Thermometer className="h-5 w-5 text-warning" />
                  </div>
                  <h2 className="text-xl font-bold">Severity Assessment</h2>
                </div>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="p-5 rounded-xl bg-secondary/50 border border-border">
                    <p className="text-sm text-muted-foreground mb-1">Severity Score</p>
                    <p className="text-3xl font-bold">{severity.score}</p>
                  </div>
                  <div className="p-5 rounded-xl bg-secondary/50 border border-border">
                    <p className="text-sm text-muted-foreground mb-1">Average Severity</p>
                    <p className="text-3xl font-bold">{severity.average.toFixed(1)}</p>
                  </div>
                </div>
              </section>
            )}

            {/* Recommendations */}
            {recommendations && (
              <section className="healthcare-card p-6 md:p-8">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-accent/10 rounded-lg">
                    <Stethoscope className="h-5 w-5 text-accent" />
                  </div>
                  <h2 className="text-xl font-bold">Medical Recommendations</h2>
                </div>
                
                <div className="space-y-6">
                  {/* Recommended Specialist */}
                  {recommendations.specialist && (
                    <div>
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        <Stethoscope className="h-4 w-4 text-primary" />
                        Recommended Specialist
                      </h4>
                      <p className="text-lg text-primary font-medium">{recommendations.specialist}</p>
                    </div>
                  )}

                  {/* Precautions */}
                  {recommendations.precautions && recommendations.precautions.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-3 flex items-center gap-2">
                        <AlertCircle className="h-4 w-4 text-warning" />
                        Precautions
                      </h4>
                      <ul className="space-y-2">
                        {recommendations.precautions.map((precaution: string, index: number) => (
                          <li key={index} className="flex items-start gap-2 text-sm">
                            <CheckCircle className="h-4 w-4 text-success mt-0.5 flex-shrink-0" />
                            <span>{precaution}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Medications */}
                  {recommendations.medications && (
                    <div className="p-4 rounded-lg bg-blue-500/5 border border-blue-500/20">
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        <Droplets className="h-4 w-4 text-blue-500" />
                        Medications
                      </h4>
                      <p className="text-sm">{recommendations.medications}</p>
                    </div>
                  )}

                  {/* Diet Recommendations */}
                  {recommendations.diet && (
                    <div className="p-4 rounded-lg bg-green-500/5 border border-green-500/20">
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        <Utensils className="h-4 w-4 text-green-500" />
                        Diet Recommendations
                      </h4>
                      <p className="text-sm">{recommendations.diet}</p>
                    </div>
                  )}

                  {/* Workout Recommendations */}
                  {recommendations.workout && (
                    <div className="p-4 rounded-lg bg-purple-500/5 border border-purple-500/20">
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        <Activity className="h-4 w-4 text-purple-500" />
                        Exercise Recommendations
                      </h4>
                      <p className="text-sm">{recommendations.workout}</p>
                    </div>
                  )}
                </div>
              </section>
            )}

            {/* Emergency Alert */}
            {isEmergency && (
              <div className="animate-scale-in bg-destructive/10 border-2 border-destructive/30 rounded-2xl p-6">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-destructive rounded-xl">
                    <AlertTriangle className="h-6 w-6 text-destructive-foreground" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-destructive mb-2">
                      {severity?.score >= 30 ? 'Critical Symptoms Detected' : 'Severe Symptoms Detected'}
                    </h3>
                    <p className="text-muted-foreground mb-4">
                      {severity?.score >= 30 
                        ? `With a severity score of ${severity.score}, your symptoms require immediate medical attention. Please do not delay seeking emergency care.`
                        : severity?.score
                        ? `Based on the severity of your symptoms (score: ${severity.score}), we recommend seeking medical attention promptly. This is not a diagnosis. If you experience chest pain, difficulty breathing, or other emergency symptoms, please call emergency services immediately.`
                        : `Based on the severity of your symptoms, we recommend seeking medical attention promptly. This is not a diagnosis. If you experience chest pain, difficulty breathing, or other emergency symptoms, please call emergency services immediately.`
                      }
                    </p>
                    <div className="flex flex-wrap gap-3">
                      <Button variant="destructive" className="gap-2">
                        <Phone className="h-4 w-4" />
                        Call 102 (Ambulance) / 108 (EMS)
                      </Button>
                      <Link to="/hospitals" state={{ department: "Emergency" }}>
                        <Button
                          variant="outline"
                          className="gap-2 border-destructive/50 text-destructive hover:bg-destructive hover:text-destructive-foreground"
                        >
                          Find Emergency Room
                          <ArrowRight className="h-4 w-4" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Backend Assessment Summary */}
            {assessment && (
              <section className="healthcare-card p-6 md:p-8">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Activity className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold">Preliminary Assessment</h2>
                    <p className="text-sm text-muted-foreground">
                      This is an automated, non-diagnostic assessment based on
                      your reported symptoms.
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-3 mb-4">
                  <span className="text-sm font-medium text-muted-foreground">
                    Concern level:
                  </span>
                  <Badge
                    variant="outline"
                    className={
                      concernLevel === "high"
                        ? "bg-destructive/10 text-destructive border-destructive/40"
                        : concernLevel === "moderate"
                        ? "bg-warning/10 text-warning border-warning/40"
                        : "bg-success/10 text-success border-success/40"
                    }
                  >
                    {concernLevel.toUpperCase()}
                  </Badge>
                </div>

                {assessment.suggestions && (
                  <div className="mb-4">
                    <p className="text-sm font-semibold mb-2">Suggestions:</p>
                    <ul className="list-disc list-inside text-sm text-muted-foreground">
                      {assessment.suggestions.map(
                        (s: string, idx: number) => (
                          <li key={idx}>{s}</li>
                        )
                      )}
                    </ul>
                  </div>
                )}

                {assessment.recommended_departments && (
                  <div className="flex flex-wrap gap-2">
                    <span className="text-sm font-semibold">
                      Recommended departments:
                    </span>
                    {assessment.recommended_departments.map((d: string) => (
                      <Badge key={d} variant="secondary">
                        {d}
                      </Badge>
                    ))}
                  </div>
                )}
              </section>
            )}

            {/* Potential Concern Areas - Dynamic based on symptom severity */}
            {concernAreas.length > 0 && (
              <section className="healthcare-card p-6 md:p-8">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Activity className="h-5 w-5 text-primary" />
                  </div>
                  <h2 className="text-xl font-bold">
                    {severity?.symptom_details ? 'Symptom Severity Analysis' : 'Potential Concern Areas'}
                  </h2>
                </div>
                
                <div className="grid md:grid-cols-3 gap-4">
                  {concernAreas.map((concern, index) => {
                    const Icon = iconMap[concern.icon] || Activity;
                    const severityColors = {
                      low: "bg-success/10 text-success border-success/30",
                      medium: "bg-warning/10 text-warning border-warning/30",
                      high: "bg-destructive/10 text-destructive border-destructive/30",
                    };
                    
                    return (
                      <div
                        key={concern.id}
                        className={`p-5 rounded-xl border-2 ${severityColors[concern.severity]} transition-all hover:scale-[1.02]`}
                        style={{ animationDelay: `${index * 0.1}s` }}
                      >
                        <Icon className="h-8 w-8 mb-3" />
                        <h3 className="font-semibold mb-1">{concern.name}</h3>
                        <p className="text-sm opacity-80">{concern.description}</p>
                        <Badge
                          variant="secondary"
                          className={`mt-3 ${
                            concern.severity === "high"
                              ? "bg-destructive/20 text-destructive"
                              : concern.severity === "medium"
                              ? "bg-warning/20 text-warning"
                              : "bg-success/20 text-success"
                          }`}
                        >
                          {concern.severity.charAt(0).toUpperCase() + concern.severity.slice(1)} Priority
                        </Badge>
                      </div>
                    );
                  })}
                </div>
              </section>
            )}

            {/* Recommended Specialists */}
            {specialistInfo ? (
              <section className="healthcare-card p-6 md:p-8">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-accent/10 rounded-lg">
                      <Stethoscope className="h-5 w-5 text-accent" />
                    </div>
                    <h2 className="text-xl font-bold">Recommended Specialist</h2>
                  </div>
                  <Link to="/specialists">
                    <Button variant="ghost" size="sm" className="gap-1">
                      Find Specialists
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                </div>

                <div className="p-6 rounded-xl bg-gradient-to-br from-primary/5 to-accent/5 border-2 border-primary/20">
                  <div className="flex items-start gap-4">
                    <div className="p-4 bg-gradient-to-br from-primary to-accent rounded-xl">
                      {(() => {
                        const Icon = iconMap[specialistInfo.icon] || Stethoscope;
                        return <Icon className="h-8 w-8 text-primary-foreground" />;
                      })()}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold mb-1">{specialistInfo.name}</h3>
                      <p className="text-sm text-primary font-medium mb-3">
                        {specialistInfo.title}
                      </p>
                      <p className="text-sm text-muted-foreground mb-4">
                        {specialistInfo.description}
                      </p>
                      {specialistInfo.conditions.length > 0 && (
                        <div>
                          <p className="text-xs font-semibold text-muted-foreground mb-2">Related Conditions:</p>
                          <div className="flex flex-wrap gap-2">
                            {specialistInfo.conditions.map((condition, idx) => (
                              <Badge key={idx} variant="secondary" className="text-xs">
                                {condition}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </section>
            ) : finalSpecialists.length > 0 && (
              <section className="healthcare-card p-6 md:p-8">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-accent/10 rounded-lg">
                      <Stethoscope className="h-5 w-5 text-accent" />
                    </div>
                    <h2 className="text-xl font-bold">Recommended Specialists</h2>
                  </div>
                  <Link to="/specialists">
                    <Button variant="ghost" size="sm" className="gap-1">
                      View All
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  {finalSpecialists.map((specialist, index) => {
                    const Icon = iconMap[specialist.icon] || Stethoscope;
                    return (
                      <div
                        key={specialist.id}
                        className="p-5 rounded-xl bg-secondary/50 border border-border hover:border-primary/50 transition-all hover:shadow-lg group"
                        style={{ animationDelay: `${index * 0.1}s` }}
                      >
                        <div className="flex items-start gap-4">
                          <div className="p-3 bg-gradient-to-br from-primary to-accent rounded-xl group-hover:scale-110 transition-transform">
                            <Icon className="h-6 w-6 text-primary-foreground" />
                          </div>
                          <div className="flex-1">
                            <h3 className="font-semibold mb-1">
                              {specialist.name}
                            </h3>
                            <p className="text-sm text-primary font-medium mb-2">
                              {specialist.title}
                            </p>
                            <p className="text-sm text-muted-foreground mb-3">
                              {specialist.description}
                            </p>
                            <div className="flex flex-wrap gap-1">
                              {specialist.conditions
                                .slice(0, 3)
                                .map((condition: string) => (
                                  <Badge
                                    key={condition}
                                    variant="outline"
                                    className="text-xs"
                                  >
                                    {condition}
                                  </Badge>
                                ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </section>
            )}

            {/* Find Hospitals CTA */}
            <section className="healthcare-card p-6 md:p-8 bg-gradient-to-br from-primary/5 to-accent/5">
              <div className="flex flex-col md:flex-row items-center gap-6">
                <div className="p-4 bg-gradient-to-br from-primary to-accent rounded-2xl">
                  <Building2 className="h-10 w-10 text-primary-foreground" />
                </div>
                <div className="flex-1 text-center md:text-left">
                  <h3 className="text-xl font-bold mb-2">
                    Find Hospitals Near You
                  </h3>
                  <p className="text-muted-foreground">
                    Search for hospitals and clinics with the specialists you
                    need, complete with contact information and directions.
                  </p>
                </div>
                <Link to="/hospitals" state={{ department: firstDepartment }}>
                  <Button variant="hero" size="lg" className="gap-2">
                    Find Hospitals
                    <ArrowRight className="h-5 w-5" />
                  </Button>
                </Link>
              </div>
            </section>

            {/* Disclaimer */}
            <div className="p-4 bg-muted rounded-xl flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-muted-foreground mt-0.5 flex-shrink-0" />
              <p className="text-sm text-muted-foreground">
                <strong>Disclaimer:</strong> This analysis is for informational
                purposes only and does not constitute medical advice, diagnosis,
                or treatment. Always seek the advice of your physician or other
                qualified health provider with any questions you may have
                regarding a medical condition.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Results;
