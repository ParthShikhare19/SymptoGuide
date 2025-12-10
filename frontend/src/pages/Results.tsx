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
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const data = sessionStorage.getItem("symptomData");
    if (!data) {
      navigate("/symptom-checker");
      return;
    }
    setSymptomData(JSON.parse(data));
    
    // Simulate loading
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

  // Mock analysis results based on symptoms
  const relevantCategories = symptomCategories.slice(0, 3);
  const recommendedSpecialists = specialists.slice(0, 4);
  const isEmergency = symptomData?.severity === "severe";

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
              Based on your symptoms: {symptomData?.symptoms?.join(", ") || "General assessment"}
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
            {/* Emergency Alert */}
            {isEmergency && (
              <div className="animate-scale-in bg-destructive/10 border-2 border-destructive/30 rounded-2xl p-6">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-destructive rounded-xl">
                    <AlertTriangle className="h-6 w-6 text-destructive-foreground" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-destructive mb-2">
                      Severe Symptoms Detected
                    </h3>
                    <p className="text-muted-foreground mb-4">
                      Based on the severity of your symptoms, we recommend seeking medical attention promptly. 
                      This is not a diagnosis. If you experience chest pain, difficulty breathing, or other 
                      emergency symptoms, please call emergency services immediately.
                    </p>
                    <div className="flex flex-wrap gap-3">
                      <Button variant="destructive" className="gap-2">
                        <Phone className="h-4 w-4" />
                        Call 911
                      </Button>
                      <Link to="/hospitals">
                        <Button variant="outline" className="gap-2 border-destructive/50 text-destructive hover:bg-destructive hover:text-destructive-foreground">
                          Find Emergency Room
                          <ArrowRight className="h-4 w-4" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Potential Concern Areas */}
            <section className="healthcare-card p-6 md:p-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Activity className="h-5 w-5 text-primary" />
                </div>
                <h2 className="text-xl font-bold">Potential Concern Areas</h2>
              </div>
              
              <div className="grid md:grid-cols-3 gap-4">
                {relevantCategories.map((category, index) => {
                  const Icon = iconMap[category.icon] || Activity;
                  const severityColors = {
                    low: "bg-success/10 text-success border-success/30",
                    medium: "bg-warning/10 text-warning border-warning/30",
                    high: "bg-destructive/10 text-destructive border-destructive/30",
                  };
                  
                  return (
                    <div
                      key={category.id}
                      className={`p-5 rounded-xl border-2 ${severityColors[category.severity]} transition-all hover:scale-[1.02]`}
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      <Icon className="h-8 w-8 mb-3" />
                      <h3 className="font-semibold mb-1">{category.name}</h3>
                      <p className="text-sm opacity-80">{category.description}</p>
                      <Badge
                        variant="secondary"
                        className={`mt-3 ${
                          category.severity === "high"
                            ? "bg-destructive/20 text-destructive"
                            : category.severity === "medium"
                            ? "bg-warning/20 text-warning"
                            : "bg-success/20 text-success"
                        }`}
                      >
                        {category.severity.charAt(0).toUpperCase() + category.severity.slice(1)} Priority
                      </Badge>
                    </div>
                  );
                })}
              </div>
            </section>

            {/* Recommended Specialists */}
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
                {recommendedSpecialists.map((specialist, index) => {
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
                          <h3 className="font-semibold mb-1">{specialist.name}</h3>
                          <p className="text-sm text-primary font-medium mb-2">
                            {specialist.title}
                          </p>
                          <p className="text-sm text-muted-foreground mb-3">
                            {specialist.description}
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {specialist.conditions.slice(0, 3).map((condition) => (
                              <Badge key={condition} variant="outline" className="text-xs">
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

            {/* Find Hospitals CTA */}
            <section className="healthcare-card p-6 md:p-8 bg-gradient-to-br from-primary/5 to-accent/5">
              <div className="flex flex-col md:flex-row items-center gap-6">
                <div className="p-4 bg-gradient-to-br from-primary to-accent rounded-2xl">
                  <Building2 className="h-10 w-10 text-primary-foreground" />
                </div>
                <div className="flex-1 text-center md:text-left">
                  <h3 className="text-xl font-bold mb-2">Find Hospitals Near You</h3>
                  <p className="text-muted-foreground">
                    Search for hospitals and clinics with the specialists you need, 
                    complete with contact information and directions.
                  </p>
                </div>
                <Link to="/hospitals">
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
                <strong>Disclaimer:</strong> This analysis is for informational purposes only and does not constitute 
                medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified 
                health provider with any questions you may have regarding a medical condition.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Results;
