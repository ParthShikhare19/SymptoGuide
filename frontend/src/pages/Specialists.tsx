import { Link } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { specialists } from "@/data/mockData";
import {
  Stethoscope,
  Heart,
  Droplets,
  Ear,
  Brain,
  Utensils,
  Wind,
  Bone,
  ArrowRight,
  Search,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { useState } from "react";

const iconMap: Record<string, React.ElementType> = {
  Stethoscope,
  Heart,
  Droplets,
  Ear,
  Brain,
  Utensils,
  Wind,
  Bone,
};

const Specialists = () => {
  const [searchTerm, setSearchTerm] = useState("");
  
  const filteredSpecialists = specialists.filter(
    (specialist) =>
      specialist.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      specialist.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      specialist.conditions.some((c) => c.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-secondary/30 to-background py-12">
        <div className="container mx-auto px-4 lg:px-8">
          {/* Header */}
          <div className="text-center max-w-2xl mx-auto mb-12">
            <div className="inline-flex items-center gap-2 bg-accent/10 text-accent px-4 py-2 rounded-full text-sm font-medium mb-4">
              <Stethoscope className="h-4 w-4" />
              <span>Medical Specialists</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold mb-4">
              Find the Right <span className="gradient-text">Specialist</span>
            </h1>
            <p className="text-muted-foreground mb-8">
              Browse our directory of medical specialists to find the right expert for your health needs.
            </p>
            
            {/* Search */}
            <div className="relative max-w-md mx-auto">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <Input
                placeholder="Search by specialty, condition, or name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-12 h-12 text-base"
              />
            </div>
          </div>

          {/* Specialists Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 max-w-7xl mx-auto">
            {filteredSpecialists.map((specialist, index) => {
              const Icon = iconMap[specialist.icon] || Stethoscope;
              return (
                <div
                  key={specialist.id}
                  className="healthcare-card p-6 group hover:-translate-y-1 transition-all duration-300 flex flex-col"
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <div className="flex items-start gap-4 mb-4">
                    <div className="p-3 bg-gradient-to-br from-primary to-accent rounded-xl group-hover:scale-110 transition-transform shadow-lg">
                      <Icon className="h-6 w-6 text-primary-foreground" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">{specialist.name}</h3>
                      <p className="text-sm text-primary font-medium">{specialist.title}</p>
                    </div>
                  </div>
                  
                  <p className="text-sm text-muted-foreground mb-4 flex-grow">
                    {specialist.description}
                  </p>
                  
                  <div className="space-y-4">
                    <div>
                      <p className="text-xs text-muted-foreground mb-2">Common conditions:</p>
                      <div className="flex flex-wrap gap-1">
                        {specialist.conditions.map((condition) => (
                          <Badge key={condition} variant="secondary" className="text-xs">
                            {condition}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <Link to="/hospitals">
                      <Button variant="outline" size="sm" className="w-full gap-2 group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                        Find Hospitals
                        <ArrowRight className="h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>

          {filteredSpecialists.length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No specialists found matching your search.</p>
            </div>
          )}

          {/* CTA */}
          <div className="text-center mt-16">
            <div className="healthcare-card inline-block p-8 max-w-xl">
              <h3 className="text-xl font-bold mb-2">Not Sure Which Specialist You Need?</h3>
              <p className="text-muted-foreground mb-6">
                Use our symptom checker to get personalized recommendations based on your health concerns.
              </p>
              <Link to="/symptom-checker">
                <Button variant="hero" size="lg" className="gap-2">
                  Start Symptom Assessment
                  <ArrowRight className="h-5 w-5" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Specialists;
