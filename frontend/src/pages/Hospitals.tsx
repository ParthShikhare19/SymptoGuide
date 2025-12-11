import { useEffect, useState, useRef } from "react";
import { useLocation } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
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
import L from "leaflet";
import "leaflet/dist/leaflet.css";

interface DynamicHospital {
  id: string;
  name: string;
  address: string;
  lat?: number;
  lng?: number;
  emergency: boolean;
  phone: string;
  specialties: string[];
  rating: number;
  distance: string;
  has_specialties?: boolean;
}

const knownSpecialties = [
  "Cardiology",
  "Gastroenterology",
  "Neurology",
  "Dermatology",
  "ENT",
  "Orthopedics",
];
const knownSpecialtiesLower = knownSpecialties.map((d) => d.toLowerCase());

const Hospitals = () => {
  const location = useLocation();
  const hasInitialized = useRef(false);
  const mapRef = useRef<L.Map | null>(null);
  const markersRef = useRef<L.Marker[]>([]);
  const userLocationRef = useRef<[number, number] | null>(null);

  const [activeDepartment, setActiveDepartmentRaw] = useState<string>(() => {
    const saved = localStorage.getItem("selectedHospitalDepartment");
    console.log("🏥 Initial activeDepartment from localStorage:", saved);
    return saved || "Primary Care";
  });

  const setActiveDepartment = (value: string | ((prev: string) => string)) => {
    const newValue = typeof value === "function" ? value(activeDepartment) : value;
    console.log("🔴 setActiveDepartment called with:", newValue);
    setActiveDepartmentRaw(newValue);
  };

  const [searchTerm, setSearchTerm] = useState("");
  const [showEmergencyOnly, setShowEmergencyOnly] = useState(false);
  const [nearbyHospitals, setNearbyHospitals] = useState<DynamicHospital[] | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(false);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [fallbackUsed, setFallbackUsed] = useState(false);
  const [userLat, setUserLat] = useState<number | null>(null);
  const [userLng, setUserLng] = useState<number | null>(null);

  useEffect(() => {
    if (hasInitialized.current) {
      console.log("💾 Saving to localStorage:", activeDepartment);
      localStorage.setItem("selectedHospitalDepartment", activeDepartment);
    }
  }, [activeDepartment]);

  useEffect(() => {
    hasInitialized.current = true;

    console.log("🔍 Fetching hospitals for department:", activeDepartment);

    if (!navigator.geolocation) {
      setLocationError("Geolocation not supported in this browser.");
      return;
    }

    setIsLoading(true);
    const geolocationId = navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;

        setUserLat(lat);
        setUserLng(lng);
        userLocationRef.current = [lat, lng];

        console.log("📍 Got location:", lat, lng);

        try {
          const departmentParam = encodeURIComponent(activeDepartment || "");
          console.log("🚀 Calling API with department:", departmentParam);

          const res = await fetch(
            `http://127.0.0.1:5000/api/nearby-hospitals?lat=${lat}&lng=${lng}&department=${departmentParam}`
          );
          const data = await res.json();

          console.log("✅ API Response:", data);

          if (data && Array.isArray(data.hospitals) && data.hospitals.length) {
            const mapped: DynamicHospital[] = data.hospitals.map((h: any) => ({
              id: String(h.id),
              name: h.name,
              address: h.address,
              lat: h.lat,
              lng: h.lng,
              emergency: !!h.emergency,
              phone: h.phone || "Not available",
              specialties: h.specialties || [],
              rating: h.rating || 4.5,
              distance: h.distance || "",
              has_specialties:
                h.has_specialties ?? (h.specialties || []).length > 0,
            }));
            setNearbyHospitals(mapped);
            console.log(`📊 Found ${mapped.length} hospitals`);
            setFallbackUsed(Boolean(data.fallback_used));
          } else {
            setLocationError("No nearby hospitals found.");
            setNearbyHospitals([]);
            setFallbackUsed(Boolean(data?.fallback_used));
            console.log("⚠️ No hospitals in response");
          }
        } catch (e) {
          console.error("❌ API Error:", e);
          setLocationError("Unable to fetch nearby hospitals.");
          setNearbyHospitals([]);
          setFallbackUsed(false);
        } finally {
          setIsLoading(false);
        }
      },
      () => {
        console.error("❌ Geolocation permission denied");
        setLocationError("Location permission denied.");
        setIsLoading(false);
        setNearbyHospitals([]);
      }
    );

    return () => {
      console.log("🧹 Cleaning up geolocation watch");
    };
  }, [activeDepartment]);

  // Initialize and update map
  useEffect(() => {
    if (!userLat || !userLng) return;

    // Initialize map if not already done
    if (!mapRef.current) {
      mapRef.current = L.map("map-container").setView([userLat, userLng], 13);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
      }).addTo(mapRef.current);

      // User location marker
      L.circleMarker([userLat, userLng], {
        radius: 8,
        fillColor: "#00a8e8",
        color: "#005a87",
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8,
      })
        .addTo(mapRef.current)
        .bindPopup("You are here");
    } else {
      // Update center if location changed
      mapRef.current.setView([userLat, userLng], 13);
    }

    // Clear existing markers
    markersRef.current.forEach((marker) => mapRef.current?.removeLayer(marker));
    markersRef.current = [];

    // Add hospital markers
    if (nearbyHospitals && nearbyHospitals.length > 0) {
      nearbyHospitals.forEach((hospital) => {
        if (hospital.lat && hospital.lng) {
          const icon = hospital.emergency
            ? L.icon({
                iconUrl:
                  "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIvPjxwYXRoIGQ9Ik0xMiA4djgiLz48cGF0aCBkPSJNOCAxMmg4Ii8+PC9zdmc+",
                iconSize: [32, 32],
                className: "bg-red-500 rounded-full",
              })
            : L.icon({
                iconUrl:
                  "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSIjMDA5Njc2IiBzdHJva2U9IiNmZmYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSI5Ii8+PC9zdmc+",
                iconSize: [32, 32],
                className: "bg-teal-500 rounded-full",
              });

          const marker = L.marker([hospital.lat, hospital.lng], { icon })
            .bindPopup(
              `<div class="p-2">
                <strong>${hospital.name}</strong><br>
                Rating: ${hospital.rating.toFixed(1)} ⭐<br>
                ${hospital.distance || "Distance unknown"}<br>
                <small>${hospital.address}</small>
              </div>`
            )
            .addTo(mapRef.current);

          markersRef.current.push(marker);
        }
      });

      // Auto-fit map to show all markers
      if (markersRef.current.length > 0) {
        const group = L.featureGroup(markersRef.current);
        mapRef.current?.fitBounds(group.getBounds(), { padding: [50, 50] });
      }
    }
  }, [userLat, userLng, nearbyHospitals]);

  const baseHospitals: DynamicHospital[] = nearbyHospitals || [];

  const filteredHospitals = baseHospitals.filter((hospital) => {
    const matchesSearch =
      hospital.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      hospital.address.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesEmergency = showEmergencyOnly ? hospital.emergency : true;

    let matchesDepartment = true;

    const dept = activeDepartment.toLowerCase();
    const specialties = (hospital.specialties || []).map((s) =>
      s.toLowerCase()
    );

    if (fallbackUsed) {
      console.log(
        "📌 Using fallback results - showing all hospitals for:",
        activeDepartment
      );
      matchesDepartment = true;
    } else {
      if (activeDepartment === "Primary Care") {
        matchesDepartment = true;
      } else if (activeDepartment === "Emergency") {
        matchesDepartment =
          hospital.emergency || specialties.includes("emergency");
      } else if (!knownSpecialtiesLower.includes(dept)) {
        matchesDepartment = true;
      } else {
        matchesDepartment =
          specialties.some((s) => s.includes(dept)) ||
          specialties.length === 0;
      }
    }

    return matchesSearch && matchesEmergency && matchesDepartment;
  });

  const handleClearFilters = () => {
    console.log(
      "🧹 Clearing search and emergency filter - NOT changing department!"
    );
    setSearchTerm("");
    setShowEmergencyOnly(false);
  };

  // DYNAMIC MAP TITLE BASED ON ACTIVE DEPARTMENT
  const getMapTitle = () => {
    if (activeDepartment === "Primary Care") {
      return "Primary Care Hospitals";
    } else if (activeDepartment === "Emergency") {
      return "Emergency Hospitals";
    } else {
      return `${activeDepartment} Hospitals`;
    }
  };

  // DYNAMIC LEGEND LABEL BASED ON ACTIVE DEPARTMENT
  const getLegendLabel = () => {
    if (activeDepartment === "Primary Care") {
      return "Primary Care Hospital";
    } else if (activeDepartment === "Emergency") {
      return "Emergency Hospital";
    } else {
      return `${activeDepartment} Hospital`;
    }
  };

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
              Hospitals within approximately 20 km of your location. Filtered for{" "}
              <span className="font-semibold">{activeDepartment}</span>. This is
              for demo purposes and may not list all facilities.
            </p>
            {locationError && (
              <p className="mt-2 text-xs text-muted-foreground">
                {locationError}
              </p>
            )}
            {fallbackUsed && (
              <p className="mt-2 text-xs text-warning-foreground">
                ℹ️ Showing nearby hospitals because no exact matches were found
                for <strong>{activeDepartment}</strong>.
              </p>
            )}
          </div>

          {/* Search and Filters */}
          <div className="max-w-4xl mx-auto mb-8">
            <div className="healthcare-card p-4 md:p-6">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                  <Input
                    placeholder="Search by hospital name or address..."
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
                  <span className="font-semibold text-foreground">
                    {filteredHospitals.length}
                  </span>{" "}
                  hospitals found for{" "}
                  <span className="font-semibold">{activeDepartment}</span>
                </p>
                {isLoading && (
                  <span className="text-xs text-muted-foreground">
                    Detecting location and loading nearby hospitals…
                  </span>
                )}
              </div>

              {filteredHospitals.map((hospital, index) => (
                <div
                  key={hospital.id}
                  className="healthcare-card p-5 md:p-6 hover:shadow-lg transition-all group cursor-pointer hover:border-primary/50"
                  style={{ animationDelay: `${index * 0.05}s` }}
                  onClick={() => {
                    // Center map on hospital when clicked
                    if (mapRef.current && hospital.lat && hospital.lng) {
                      mapRef.current.setView(
                        [hospital.lat, hospital.lng],
                        15
                      );
                    }
                  }}
                >
                  <div className="flex flex-col md:flex-row gap-4">
                    {/* Left placeholder image / icon */}
                    <div className="relative w-full md:w-48 h-40 md:h-32 rounded-xl overflow-hidden flex-shrink-0 bg-secondary flex items-center justify-center">
                      <Building2 className="h-10 w-10 text-muted-foreground" />
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
                          <span className="font-semibold">
                            {hospital.rating.toFixed(1)}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 text-sm text-muted-foreground mb-3">
                        <div className="flex items-center gap-1">
                          <Navigation className="h-4 w-4 text-primary" />
                          <span>{hospital.distance || "distance unknown"}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Phone className="h-4 w-4 text-primary" />
                          <span>{hospital.phone}</span>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-1.5 mb-4">
                        {hospital.specialties && hospital.specialties.length > 0 ? (
                          hospital.specialties.map((specialty) => (
                            <Badge
                              key={specialty}
                              variant="secondary"
                              className="text-xs"
                            >
                              {specialty}
                            </Badge>
                          ))
                        ) : (
                          <span className="text-xs text-muted-foreground">
                            General Hospital
                          </span>
                        )}
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

              {filteredHospitals.length === 0 && !isLoading && (
                <div className="text-center py-12 healthcare-card">
                  <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">
                    No hospitals found matching your search criteria.
                  </p>
                  <Button variant="link" onClick={handleClearFilters}>
                    Clear search and filters
                  </Button>
                </div>
              )}
            </div>

            {/* Live Map */}
            <div className="lg:col-span-1">
              <div className="healthcare-card p-0 sticky top-24 rounded-xl overflow-hidden">
                <div id="map-container" className="w-full h-[500px] rounded-xl" />
                <div className="p-4 bg-background border-t border-border">
                  <div className="flex items-center gap-2 mb-3">
                    <Map className="h-5 w-5 text-primary" />
                    {/* DYNAMIC MAP TITLE */}
                    <h3 className="font-semibold">{getMapTitle()}</h3>
                  </div>
                  <div className="flex flex-col gap-2 text-xs text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-teal-500"></div>
                      {/* DYNAMIC LEGEND LABEL */}
                      <span>{getLegendLabel()}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-red-500"></div>
                      <span>Emergency (24/7)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                      <span>Your Location</span>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground mt-3">
                    Click on a hospital to center the map
                  </p>
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
