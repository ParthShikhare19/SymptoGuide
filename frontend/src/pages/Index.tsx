import { Link } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { 
  Activity, 
  AlertTriangle, 
  Stethoscope, 
  Building2, 
  Shield, 
  Clock, 
  Heart,
  ArrowRight,
  CheckCircle,
  Users
} from "lucide-react";

const features = [
  {
    icon: Activity,
    title: "Symptom Checker",
    description: "Enter your symptoms and get intelligent analysis of potential health concerns.",
    color: "from-primary to-accent",
  },
  {
    icon: AlertTriangle,
    title: "Emergency Indicators",
    description: "Recognize warning signs that may require immediate medical attention.",
    color: "from-warning to-destructive",
  },
  {
    icon: Stethoscope,
    title: "Specialist Recommendation",
    description: "Get matched with the right medical specialist for your specific symptoms.",
    color: "from-accent to-info",
  },
  {
    icon: Building2,
    title: "Nearby Hospitals",
    description: "Find hospitals and clinics near you with the specialists you need.",
    color: "from-success to-primary",
  },
];

const stats = [
  { value: "10M+", label: "Symptom Checks" },
  { value: "50K+", label: "Hospitals Listed" },
  { value: "98%", label: "User Satisfaction" },
  { value: "24/7", label: "Available" },
];

const benefits = [
  "Quick symptom analysis in under 2 minutes",
  "Privacy-first approach - your data stays secure",
  "Evidence-based recommendations",
  "No appointment or registration required",
];

const Index = () => {
  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-accent/5" />
        <div className="absolute top-20 right-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl" />
        <div className="absolute bottom-10 left-10 w-96 h-96 bg-accent/10 rounded-full blur-3xl" />
        
        <div className="container relative mx-auto px-4 lg:px-8 py-20 lg:py-32">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-2 rounded-full text-sm font-medium mb-8 animate-fade-in">
              <Shield className="h-4 w-4" />
              <span>Trusted Healthcare Guidance</span>
            </div>

            {/* Heading */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6 animate-slide-up">
              Understand Your Symptoms.
              <br />
              <span className="gradient-text">Get Guided Medical Help</span>
              <br />
              Faster and Smarter.
            </h1>

            {/* Subheading */}
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 animate-slide-up" style={{ animationDelay: "0.1s" }}>
              Our intelligent healthcare assistant helps you understand your symptoms and guides you toward the right medical experts—all in one place.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center animate-slide-up" style={{ animationDelay: "0.2s" }}>
              <Link to="/symptom-checker">
                <Button variant="hero" size="xl" className="w-full sm:w-auto">
                  Start Assessment
                  <ArrowRight className="h-5 w-5" />
                </Button>
              </Link>
              <Link to="/specialists">
                <Button variant="outline" size="xl" className="w-full sm:w-auto">
                  Find Specialists
                </Button>
              </Link>
            </div>

            {/* Benefits List */}
            <div className="flex flex-wrap justify-center gap-4 mt-10 animate-fade-in" style={{ animationDelay: "0.3s" }}>
              {benefits.map((benefit, index) => (
                <div key={index} className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="h-4 w-4 text-success" />
                  <span>{benefit}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="border-y border-border bg-secondary/30">
        <div className="container mx-auto px-4 lg:px-8 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold gradient-text mb-1">
                  {stat.value}
                </div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 lg:py-28">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Your Complete Health <span className="gradient-text">Companion</span>
            </h2>
            <p className="text-muted-foreground text-lg">
              Everything you need to understand your health and find the right care—all in one intelligent platform.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className="healthcare-card p-6 group hover:-translate-y-1 transition-all duration-300"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${feature.color} mb-4 group-hover:scale-110 transition-transform`}>
                    <Icon className="h-6 w-6 text-primary-foreground" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 lg:py-28 bg-secondary/30">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How It <span className="gradient-text">Works</span>
            </h2>
            <p className="text-muted-foreground text-lg">
              Get personalized health guidance in three simple steps.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                step: "01",
                title: "Describe Your Symptoms",
                description: "Enter your symptoms, their duration, and severity using our intuitive interface.",
                icon: Activity,
              },
              {
                step: "02",
                title: "Get Analysis",
                description: "Our intelligent system analyzes your symptoms and identifies potential concern areas.",
                icon: Heart,
              },
              {
                step: "03",
                title: "Find Care",
                description: "Receive specialist recommendations and find nearby hospitals with the expertise you need.",
                icon: Building2,
              },
            ].map((item, index) => {
              const Icon = item.icon;
              return (
                <div key={index} className="relative text-center">
                  {index < 2 && (
                    <div className="hidden md:block absolute top-12 left-[60%] w-[80%] border-t-2 border-dashed border-primary/30" />
                  )}
                  <div className="relative inline-flex">
                    <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg">
                      <Icon className="h-10 w-10 text-primary-foreground" />
                    </div>
                    <span className="absolute -top-2 -right-2 w-8 h-8 bg-background border-2 border-primary rounded-full flex items-center justify-center text-sm font-bold text-primary">
                      {item.step}
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold mt-6 mb-3">{item.title}</h3>
                  <p className="text-muted-foreground">{item.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 lg:py-28">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary via-primary to-accent p-8 md:p-16">
            {/* Decorative elements */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary-foreground/10 rounded-full blur-3xl" />
            <div className="absolute bottom-0 left-0 w-96 h-96 bg-accent/20 rounded-full blur-3xl" />
            
            <div className="relative text-center max-w-2xl mx-auto">
              <div className="inline-flex items-center gap-2 bg-primary-foreground/20 text-primary-foreground px-4 py-2 rounded-full text-sm font-medium mb-6">
                <Clock className="h-4 w-4" />
                <span>Takes less than 2 minutes</span>
              </div>
              
              <h2 className="text-3xl md:text-4xl font-bold text-primary-foreground mb-4">
                Ready to Understand Your Health Better?
              </h2>
              <p className="text-primary-foreground/80 text-lg mb-8">
                Start your free symptom assessment now and get personalized recommendations for your healthcare journey.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/symptom-checker">
                  <Button 
                    variant="secondary" 
                    size="xl" 
                    className="w-full sm:w-auto bg-primary-foreground text-primary hover:bg-primary-foreground/90"
                  >
                    Start Free Assessment
                    <ArrowRight className="h-5 w-5" />
                  </Button>
                </Link>
              </div>

              <div className="flex items-center justify-center gap-6 mt-8 text-primary-foreground/70 text-sm">
                <div className="flex items-center gap-2">
                  <Shield className="h-4 w-4" />
                  <span>100% Private</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  <span>10M+ Users</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Index;
