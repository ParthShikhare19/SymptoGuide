import { useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { hospitals } from "@/data/mockData";
import {
  Building2,
  Search,
  MapPin,
  Phone,
  Star,
  Navigation,
  Ambulance,
  Filter,
  Map,
} from "lucide-react";

const Hospitals = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [showEmergencyOnly, setShowEmergencyOnly] = useState(false);

  const filteredHospitals = hospitals.filter((hospital) => {
    const matchesSearch =
      hospital.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      hospital.address.toLowerCase().includes(searchTerm.toLowerCase()) ||
      hospital.specialties.some((s) => s.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesEmergency = showEmergencyOnly ? hospital.emergency : true;
    return matchesSearch && matchesEmergency;
  });

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-secondary/30 to-background py-12">
        <div className="container mx-auto px-4 lg:px-8">
          {/* Header */}
          <div className="text-center max-w-2xl mx-auto mb-12">
            <div className="inline-flex items-center gap-2 bg-success/10 text-success px-4 py-2 rounded-full text-sm font-medium mb-4">
              <Building2 className="h-4 w-4" />
              <span>Find Care Near You</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold mb-4">
              Nearby <span className="gradient-text">Hospitals</span>
            </h1>
            <p className="text-muted-foreground">
              Find hospitals and healthcare facilities near you with the specialists and services you need.
            </p>
          </div>

          {/* Search and Filters */}
          <div className="max-w-4xl mx-auto mb-8">
            <div className="healthcare-card p-4 md:p-6">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                  <Input
                    placeholder="Search by city, pincode, hospital name, or specialty..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-12 h-12 text-base"
                  />
                </div>
                <div className="flex gap-3">
                  <Button
                    variant={showEmergencyOnly ? "destructive" : "outline"}
                    className="gap-2 h-12"
                    onClick={() => setShowEmergencyOnly(!showEmergencyOnly)}
                  >
                    <Ambulance className="h-4 w-4" />
                    Emergency Only
                  </Button>
                  <Button variant="secondary" className="gap-2 h-12">
                    <Filter className="h-4 w-4" />
                    Filters
                  </Button>
                </div>
              </div>
            </div>
          </div>

          <div className="grid lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
            {/* Hospital List */}
            <div className="lg:col-span-2 space-y-4">
              <div className="flex items-center justify-between mb-4">
                <p className="text-muted-foreground">
                  <span className="font-semibold text-foreground">{filteredHospitals.length}</span> hospitals found
                </p>
              </div>

              {filteredHospitals.map((hospital, index) => (
                <div
                  key={hospital.id}
                  className="healthcare-card p-5 md:p-6 hover:shadow-lg transition-all group"
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <div className="flex flex-col md:flex-row gap-4">
                    {/* Image */}
                    <div className="relative w-full md:w-48 h-40 md:h-32 rounded-xl overflow-hidden flex-shrink-0">
                      <img
                        src={hospital.image}
                        alt={hospital.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                      {hospital.emergency && (
                        <div className="absolute top-2 left-2">
                          <Badge className="bg-destructive text-destructive-foreground gap-1">
                            <Ambulance className="h-3 w-3" />
                            24/7 ER
                          </Badge>
                        </div>
                      )}
                    </div>

                    {/* Content */}
                    <div className="flex-1">
                      <div className="flex flex-col md:flex-row md:items-start justify-between gap-2 mb-2">
                        <div>
                          <h3 className="text-lg font-semibold group-hover:text-primary transition-colors">
                            {hospital.name}
                          </h3>
                          <div className="flex items-center gap-1 text-sm text-muted-foreground">
                            <MapPin className="h-4 w-4" />
                            <span>{hospital.address}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-1 bg-warning/10 text-warning px-2 py-1 rounded-lg">
                          <Star className="h-4 w-4 fill-current" />
                          <span className="font-semibold">{hospital.rating}</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 text-sm text-muted-foreground mb-3">
                        <div className="flex items-center gap-1">
                          <Navigation className="h-4 w-4 text-primary" />
                          <span>{hospital.distance}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Phone className="h-4 w-4 text-primary" />
                          <span>{hospital.phone}</span>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-1.5 mb-4">
                        {hospital.specialties.map((specialty) => (
                          <Badge key={specialty} variant="secondary" className="text-xs">
                            {specialty}
                          </Badge>
                        ))}
                      </div>

                      <div className="flex flex-wrap gap-2">
                        <Button size="sm" variant="default" className="gap-2">
                          <Phone className="h-4 w-4" />
                          Call Now
                        </Button>
                        <Button size="sm" variant="outline" className="gap-2">
                          <Navigation className="h-4 w-4" />
                          Get Directions
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {filteredHospitals.length === 0 && (
                <div className="text-center py-12 healthcare-card">
                  <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No hospitals found matching your criteria.</p>
                  <Button variant="link" onClick={() => { setSearchTerm(""); setShowEmergencyOnly(false); }}>
                    Clear filters
                  </Button>
                </div>
              )}
            </div>

            {/* Map Placeholder */}
            <div className="lg:col-span-1">
              <div className="healthcare-card p-4 sticky top-24">
                <div className="flex items-center gap-2 mb-4">
                  <Map className="h-5 w-5 text-primary" />
                  <h3 className="font-semibold">Map View</h3>
                </div>
                <div className="aspect-square bg-secondary rounded-xl flex items-center justify-center">
                  <div className="text-center p-6">
                    <MapPin className="h-12 w-12 text-muted-foreground mx-auto mb-3 animate-pulse" />
                    <p className="text-sm text-muted-foreground">
                      Interactive map coming soon
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">
                      Enable location to see hospitals near you
                    </p>
                    <Button variant="outline" size="sm" className="mt-4 gap-2">
                      <Navigation className="h-4 w-4" />
                      Enable Location
                    </Button>
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="mt-4 p-4 bg-secondary/50 rounded-xl">
                  <h4 className="text-sm font-medium mb-3">Quick Stats</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Total Hospitals</span>
                      <span className="font-medium">{hospitals.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">With Emergency</span>
                      <span className="font-medium">{hospitals.filter(h => h.emergency).length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Nearest</span>
                      <span className="font-medium">{hospitals[0]?.distance}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Hospitals;
