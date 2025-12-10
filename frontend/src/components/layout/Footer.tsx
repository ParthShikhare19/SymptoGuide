import { Heart, Mail, Phone, MapPin } from "lucide-react";
import { Link } from "react-router-dom";

export const Footer = () => {
  return (
    <footer className="bg-secondary/50 border-t border-border">
      <div className="container mx-auto px-4 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div className="space-y-4">
            <Link to="/" className="flex items-center gap-2">
              <div className="bg-gradient-to-br from-primary to-accent p-2 rounded-lg">
                <Heart className="h-5 w-5 text-primary-foreground" fill="currentColor" />
              </div>
              <span className="font-bold text-xl">
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
            <h4 className="font-semibold text-foreground mb-4">Quick Links</h4>
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
            <h4 className="font-semibold text-foreground mb-4">Contact</h4>
            <ul className="space-y-3">
              <li className="flex items-center gap-2 text-muted-foreground text-sm">
                <Phone className="h-4 w-4 text-primary" />
                <span>+91 9876543210</span>
              </li>
              <li className="flex items-center gap-2 text-muted-foreground text-sm">
                <Mail className="h-4 w-4 text-primary" />
                <span>symptoguide@gmail.com</span>
              </li>
              <li className="flex items-start gap-2 text-muted-foreground text-sm">
                <MapPin className="h-4 w-4 text-primary mt-0.5" />
                <span>Available Worldwide</span>
              </li>
            </ul>
          </div>

          {/* Emergency */}
          <div>
            <h4 className="font-semibold text-foreground mb-4">Emergency</h4>
            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 space-y-3">
              <div>
                <p className="text-xs text-destructive/80 font-medium">Ambulance</p>
                <p className="text-2xl font-bold text-destructive">102</p>
              </div>
              <div>
                <p className="text-xs text-destructive/80 font-medium">Emergency Medical Service</p>
                <p className="text-2xl font-bold text-destructive">108</p>
              </div>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="border-t border-border pt-8">
          <div className="bg-warning/10 border border-warning/20 rounded-lg p-4 mb-6">
            <p className="text-sm text-muted-foreground text-center">
              <strong className="text-warning">Disclaimer:</strong> This tool provides preliminary insights and does NOT replace professional medical diagnosis. 
              Always consult with a qualified healthcare provider for medical advice, diagnosis, and treatment.
            </p>
          </div>
          
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-muted-foreground">
            <p>© 2025 SymptoGuide. All rights reserved.</p>
            <div className="flex gap-6">
              <Link to="#" className="hover:text-primary transition-colors">Privacy Policy</Link>
              <Link to="#" className="hover:text-primary transition-colors">Terms of Service</Link>
              <Link to="#" className="hover:text-primary transition-colors">Cookie Policy</Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};
