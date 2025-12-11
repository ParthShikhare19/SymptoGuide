export interface SymptomCategory {
  id: string;
  name: string;
  icon: string;
  description: string;
  severity: "low" | "medium" | "high";
  keywords: string[];
}

export interface Specialist {
  id: string;
  name: string;
  title: string;
  description: string;
  icon: string;
  conditions: string[];
  departments: string[];
}

export interface Hospital {
  id: string;
  name: string;
  address: string;
  distance: string;
  rating: number;
  specialties: string[];
  phone: string;
  emergency: boolean;
  image: string;
}

export const symptomCategories: SymptomCategory[] = [
  {
    id: "respiratory",
    name: "Respiratory Issues",
    icon: "Wind",
    description: "Cough, shortness of breath, wheezing, congestion",
    severity: "medium",
    keywords: ["cough", "shortness of breath", "breathing", "wheezing"],
  },
  {
    id: "digestive",
    name: "Digestive Problems",
    icon: "Utensils",
    description: "Stomach pain, nausea, bloating, irregular bowel movements",
    severity: "low",
    keywords: ["stomach pain", "nausea", "vomiting", "diarrhea", "abdomen"],
  },
  {
    id: "skin",
    name: "Skin & Allergy",
    icon: "Droplets",
    description: "Rashes, itching, hives, swelling, allergic reactions",
    severity: "low",
    keywords: ["rash", "skin", "itching", "allergy"],
  },
  {
    id: "neurology",
    name: "Neurological",
    icon: "Brain",
    description: "Headaches, dizziness, numbness, memory issues",
    severity: "medium",
    keywords: ["headache", "migraine", "dizziness", "numbness"],
  },
  {
    id: "cardiovascular",
    name: "Cardiovascular",
    icon: "Heart",
    description: "Chest pain, palpitations, irregular heartbeat",
    severity: "high",
    keywords: ["chest pain", "palpitations", "heart"],
  },
  {
    id: "infection",
    name: "General Infection",
    icon: "Thermometer",
    description: "Fever, fatigue, body aches, swollen lymph nodes",
    severity: "medium",
    keywords: ["fever", "fatigue", "body aches"],
  },
];

export const specialists: Specialist[] = [
  {
    id: "gp",
    name: "General Physician",
    title: "Primary Care",
    description:
      "First point of contact for general health concerns, routine check-ups, and referrals.",
    icon: "Stethoscope",
    conditions: ["Fever", "Cold", "Fatigue", "General Pain"],
    departments: ["Primary Care", "General Medicine"],
  },
  {
    id: "cardiologist",
    name: "Cardiologist",
    title: "Heart Specialist",
    description:
      "Specializes in heart and cardiovascular system disorders and treatments.",
    icon: "Heart",
    conditions: ["Chest Pain", "Palpitations", "High Blood Pressure"],
    departments: ["Cardiology", "Emergency"],
  },
  {
    id: "dermatologist",
    name: "Dermatologist",
    title: "Skin Specialist",
    description:
      "Expert in skin, hair, and nail conditions including allergies and cosmetic concerns.",
    icon: "Droplets",
    conditions: ["Rashes", "Acne", "Eczema", "Skin Allergies"],
    departments: ["Dermatology"],
  },
  {
    id: "ent",
    name: "ENT Specialist",
    title: "Ear, Nose & Throat",
    description:
      "Treats conditions related to ears, nose, throat, and related head structures.",
    icon: "Ear",
    conditions: ["Sore Throat", "Hearing Issues", "Sinus Problems"],
    departments: ["ENT"],
  },
  {
    id: "neurologist",
    name: "Neurologist",
    title: "Brain & Nerve Specialist",
    description:
      "Diagnoses and treats disorders of the nervous system including brain and spine.",
    icon: "Brain",
    conditions: ["Headaches", "Migraines", "Numbness", "Seizures"],
    departments: ["Neurology"],
  },
  {
    id: "gastroenterologist",
    name: "Gastroenterologist",
    title: "Digestive Specialist",
    description:
      "Expert in digestive system disorders from esophagus to intestines.",
    icon: "Utensils",
    conditions: ["Stomach Pain", "Acid Reflux", "IBS", "Liver Issues"],
    departments: ["Gastroenterology"],
  },
  {
    id: "pulmonologist",
    name: "Pulmonologist",
    title: "Lung Specialist",
    description:
      "Specializes in respiratory system diseases and breathing disorders.",
    icon: "Wind",
    conditions: ["Asthma", "COPD", "Breathing Difficulty", "Chronic Cough"],
    departments: ["Pulmonology", "Emergency"],
  },
  {
    id: "orthopedic",
    name: "Orthopedic Surgeon",
    title: "Bone & Joint Specialist",
    description:
      "Treats musculoskeletal issues including bones, joints, muscles, and ligaments.",
    icon: "Bone",
    conditions: ["Joint Pain", "Fractures", "Arthritis", "Sports Injuries"],
    departments: ["Orthopedics"],
  },
];

export const hospitals: Hospital[] = [
  {
    id: "1",
    name: "City General Hospital",
    address: "123 Healthcare Ave, Medical District",
    distance: "2.3 km",
    rating: 4.8,
    specialties: ["Cardiology", "Neurology", "Emergency Care", "Pediatrics"],
    phone: "+1 (555) 123-4567",
    emergency: true,
    image: "https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?w=400",
  },
  {
    id: "2",
    name: "Metropolitan Medical Center",
    address: "456 Wellness Blvd, Downtown",
    distance: "3.7 km",
    rating: 4.6,
    specialties: ["Orthopedics", "Gastroenterology", "Dermatology"],
    phone: "+1 (555) 234-5678",
    emergency: true,
    image: "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=400",
  },
  {
    id: "3",
    name: "Sunrise Health Clinic",
    address: "789 Care Street, Eastside",
    distance: "5.1 km",
    rating: 4.5,
    specialties: ["General Medicine", "ENT", "Pulmonology"],
    phone: "+1 (555) 345-6789",
    emergency: false,
    image: "https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=400",
  },
  {
    id: "4",
    name: "Advanced Care Hospital",
    address: "321 Innovation Park, Techville",
    distance: "6.8 km",
    rating: 4.9,
    specialties: ["Oncology", "Cardiology", "Neurosurgery", "Transplants"],
    phone: "+1 (555) 456-7890",
    emergency: true,
    image: "https://images.unsplash.com/photo-1586773860418-d37222d8fce3?w=400",
  },
  {
    id: "5",
    name: "Community Wellness Center",
    address: "555 Family Lane, Suburbs",
    distance: "8.2 km",
    rating: 4.3,
    specialties: ["Family Medicine", "Pediatrics", "Women's Health"],
    phone: "+1 (555) 567-8901",
    emergency: false,
    image: "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400",
  },
];

export const commonSymptoms = [
  "Headache",
  "Fever",
  "Cough",
  "Fatigue",
  "Nausea",
  "Dizziness",
  "Chest Pain",
  "Shortness of Breath",
  "Stomach Pain",
  "Back Pain",
  "Joint Pain",
  "Sore Throat",
  "Runny Nose",
  "Skin Rash",
  "Muscle Aches",
];

