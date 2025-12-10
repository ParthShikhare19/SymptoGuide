import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Heart, Menu, X, Stethoscope, Building2, Home, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

const navLinks = [
  { to: "/", label: "Home", icon: Home },
  { to: "/symptom-checker", label: "Symptom Checker", icon: Activity },
  { to: "/specialists", label: "Specialists", icon: Stethoscope },
  { to: "/hospitals", label: "Hospitals", icon: Building2 },
];

export const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  return (
    <header className="sticky top-0 z-50 glass-effect border-b border-border/50">
      <nav className="container mx-auto px-4 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link 
            to="/" 
            className="flex items-center gap-2 group"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 rounded-lg blur-md group-hover:blur-lg transition-all" />
              <div className="relative bg-gradient-to-br from-primary to-accent p-2 rounded-lg">
                <Heart className="h-5 w-5 text-primary-foreground" fill="currentColor" />
              </div>
            </div>
            <span className="font-bold text-xl tracking-tight">
              <span className="gradient-text">Sympto</span>
              <span className="text-foreground">Guide</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.to;
              return (
                <Link key={link.to} to={link.to}>
                  <Button
                    variant="ghost"
                    className={cn(
                      "gap-2 font-medium",
                      isActive && "bg-secondary text-primary"
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {link.label}
                  </Button>
                </Link>
              );
            })}
          </div>

          {/* CTA Button */}
          <div className="hidden md:block">
            <Link to="/symptom-checker">
              <Button variant="hero" size="default">
                Start Assessment
              </Button>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden py-4 border-t border-border/50 animate-fade-in">
            <div className="flex flex-col gap-2">
              {navLinks.map((link) => {
                const Icon = link.icon;
                const isActive = location.pathname === link.to;
                return (
                  <Link
                    key={link.to}
                    to={link.to}
                    onClick={() => setIsOpen(false)}
                  >
                    <Button
                      variant="ghost"
                      className={cn(
                        "w-full justify-start gap-3 font-medium",
                        isActive && "bg-secondary text-primary"
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      {link.label}
                    </Button>
                  </Link>
                );
              })}
              <Link to="/symptom-checker" onClick={() => setIsOpen(false)}>
                <Button variant="hero" className="w-full mt-2">
                  Start Assessment
                </Button>
              </Link>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
};
