import { Heart, Mail, Phone, MapPin } from "lucide-react";
import { Link } from "react-router-dom";

export const Footer = () => {
  return (
    <footer className="bg-secondary/50 border-t border-border">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8 mb-6 sm:mb-8">
          {/* Brand */}
          <div className="space-y-4">
            <Link to="/" className="flex items-center gap-2">
              <div className="bg-gradient-to-br from-primary to-accent p-1.5 sm:p-2 rounded-lg">
                <Heart className="h-4 w-4 sm:h-5 sm:w-5 text-primary-foreground" fill="currentColor" />
              </div>
              <span className="font-bold text-lg sm:text-xl">
                <span className="gradient-text">Sympto</span>
                <span className="text-foreground">Guide</span>
              </span>
            </Link>
            <p className="text-muted-foreground text-sm leading-relaxed">
              Your intelligent healthcare companion, helping you understand symptoms and find the right medical care.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-semibold text-foreground mb-3 sm:mb-4 text-sm sm:text-base">Quick Links</h4>
            <ul className="space-y-2">
              {["Symptom Checker", "Find Specialists", "Nearby Hospitals", "Emergency Guide"].map((item) => (
                <li key={item}>
                  <Link 
                    to={item === "Symptom Checker" ? "/symptom-checker" : item === "Find Specialists" ? "/specialists" : "/hospitals"} 
                    className="text-muted-foreground hover:text-primary transition-colors text-sm"
                  >
                    {item}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-semibold text-foreground mb-3 sm:mb-4 text-sm sm:text-base">Contact</h4>
            <ul className="space-y-2 sm:space-y-3">
              <li className="flex items-center gap-2 text-muted-foreground text-xs sm:text-sm">
                <Phone className="h-3 w-3 sm:h-4 sm:w-4 text-primary flex-shrink-0" />
                <span className="break-all">+91 9876543210</span>
              </li>
              <li className="flex items-center gap-2 text-muted-foreground text-xs sm:text-sm">
                <Mail className="h-3 w-3 sm:h-4 sm:w-4 text-primary flex-shrink-0" />
                <span className="break-all">symptoguide@gmail.com</span>
              </li>
              <li className="flex items-start gap-2 text-muted-foreground text-xs sm:text-sm">
                <MapPin className="h-3 w-3 sm:h-4 sm:w-4 text-primary mt-0.5 flex-shrink-0" />
                <span>Available Worldwide</span>
              </li>
            </ul>
          </div>

          {/* Emergency */}
          <div>
            <h4 className="font-semibold text-foreground mb-3 sm:mb-4 text-sm sm:text-base">Emergency</h4>
            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-3 sm:p-4 space-y-2 sm:space-y-3">
              <div>
                <p className="text-xs text-destructive/80 font-medium">Ambulance</p>
                <p className="text-xl sm:text-2xl font-bold text-destructive">102</p>
              </div>
              <div>
                <p className="text-xs text-destructive/80 font-medium">Emergency Medical Service</p>
                <p className="text-xl sm:text-2xl font-bold text-destructive">108</p>
              </div>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="border-t border-border pt-6 sm:pt-8">          
          <div className="flex flex-col md:flex-row justify-center items-center text-xs sm:text-sm text-muted-foreground text-center">
            <p className="px-4">© 2025 SymptoGuide. Created by Team Just Debugging It in Nexolve 2025.</p>
          </div>
        </div>
      </div>
    </footer>
  );
};
