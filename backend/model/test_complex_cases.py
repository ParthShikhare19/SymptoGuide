"""
Complex Test Cases for Healthcare Assistant System
Tests the model with realistic, complex symptom descriptions
"""

import os
import sys

# Add the current directory to Python path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Healthcare_Assistant_System import HealthcareAssistant, print_assessment

# Change to model directory for relative imports
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Complex test cases with realistic patient descriptions
COMPLEX_TEST_CASES = [
    {
        "name": "Case 1: Multi-System Involvement - Respiratory & Systemic",
        "description": """I've been feeling really terrible for the past week. It started with a mild 
        fever that has gotten progressively worse. Now I'm running a high temperature of around 103°F. 
        I have this persistent dry cough that won't go away, especially at night. My chest feels tight 
        and sometimes I get short of breath just from walking to the bathroom. I'm also experiencing 
        severe body aches - my muscles and joints feel like they're on fire. I'm constantly sweating, 
        even when I feel cold, and I have terrible chills. I've completely lost my appetite and feel 
        extremely weak and fatigued. Even getting out of bed feels like climbing a mountain.""",
        "symptoms": ['high_fever', 'cough', 'chest_pain', 'shortness_of_breath', 'muscle_pain', 
                    'joint_pain', 'sweating', 'chills', 'loss_of_appetite', 'weakness', 'fatigue']
    },
    
    {
        "name": "Case 2: Gastrointestinal Crisis",
        "description": """I woke up this morning with severe abdominal pain that's been getting worse. 
        The pain is mostly in my upper stomach area and feels like burning and cramping. I've been 
        vomiting multiple times - at first it was just food, but now it's mostly bile. I also have 
        really bad diarrhea that's been happening every hour or so. I feel extremely nauseous all the 
        time and can't keep anything down, not even water. I'm also experiencing heartburn and acid 
        reflux. My mouth is very dry and I feel lightheaded when I stand up. I have no energy whatsoever 
        and feel like I'm getting weaker by the hour.""",
        "symptoms": ['abdominal_pain', 'vomiting', 'diarrhea', 'nausea', 'indigestion', 'fatigue', 
                    'dizziness', 'weakness', 'loss_of_appetite']
    },
    
    {
        "name": "Case 3: Neurological & Sensory Symptoms",
        "description": """I've been having these really bad headaches for the past few days that feel 
        like my head is being squeezed in a vice. The headaches are accompanied by severe dizziness - 
        the room feels like it's spinning. I've also noticed my vision has been blurry and sometimes 
        I see spots or flashes of light. I feel confused and have trouble concentrating on simple tasks. 
        My neck is very stiff and painful, especially when I try to look down. I'm also experiencing 
        numbness and tingling in my hands and fingers. I feel extremely fatigued and have been very 
        sensitive to light and sound. Sometimes I feel nauseous during these episodes.""",
        "symptoms": ['headache', 'dizziness', 'blurred_vision', 'confusion', 'neck_pain', 'numbness', 
                    'fatigue', 'nausea', 'weakness']
    },
    
    {
        "name": "Case 4: Cardiac & Respiratory Emergency",
        "description": """I'm experiencing severe chest pain that feels like pressure and tightness, 
        like someone is sitting on my chest. The pain radiates to my left arm and jaw. I'm having 
        extreme difficulty breathing - I feel like I can't get enough air no matter how hard I try. 
        My heart feels like it's racing and pounding irregularly. I'm breaking out in cold sweats and 
        feel extremely anxious and restless. I also feel very dizzy and lightheaded, like I might 
        pass out. I have this overwhelming sense of doom. My lips and fingertips feel numb and tingly. 
        I'm also experiencing nausea and feel like I might vomit.""",
        "symptoms": ['chest_pain', 'shortness_of_breath', 'sweating', 'anxiety', 'dizziness', 
                    'numbness', 'nausea', 'weakness', 'confusion']
    },
    
    {
        "name": "Case 5: Infectious Disease with Systemic Symptoms",
        "description": """For the past 5 days, I've had a high fever that spikes in the evening, 
        reaching 104°F. I have severe body aches and joint pain - every part of my body hurts. 
        I've developed a red rash all over my torso and arms that's very itchy. I have a terrible 
        headache that pounds with my heartbeat. I'm experiencing extreme fatigue and weakness - 
        I can barely stay awake for more than a few hours. I have chills and uncontrollable shaking, 
        followed by episodes of heavy sweating that soak my clothes. My eyes hurt and are very 
        sensitive to light. I also have a sore throat and swollen lymph nodes in my neck. 
        I've lost my appetite completely and feel nauseous most of the time.""",
        "symptoms": ['high_fever', 'muscle_pain', 'joint_pain', 'skin_rash', 'itching', 'headache', 
                    'fatigue', 'weakness', 'chills', 'sweating', 'eye_pain', 'sore_throat', 
                    'loss_of_appetite', 'nausea']
    },
    
    {
        "name": "Case 6: Metabolic & Endocrine Disorder",
        "description": """I've been feeling extremely thirsty all the time, no matter how much water 
        I drink. I'm urinating very frequently, sometimes having to go to the bathroom every 30 minutes. 
        Despite eating more than usual, I've lost about 15 pounds over the past month. I feel constantly 
        hungry but also nauseous after eating. I'm experiencing severe fatigue and weakness - even simple 
        tasks exhaust me. My vision has become blurry, especially when reading. I have frequent headaches 
        and feel dizzy when I stand up. My skin has been very dry and itchy. I also noticed some wounds 
        on my feet are healing very slowly. I feel irritable and have trouble concentrating.""",
        "symptoms": ['thirst', 'frequent_urination', 'weight_loss', 'hunger', 'nausea', 'fatigue', 
                    'weakness', 'blurred_vision', 'headache', 'dizziness', 'itching', 'confusion']
    },
    
    {
        "name": "Case 7: Mental Health Crisis with Physical Manifestations",
        "description": """I've been feeling extremely anxious and worried all the time for no apparent 
        reason. My heart races and pounds, especially when I'm in crowded places or at night. I have 
        chest tightness and difficulty breathing, like I can't get a full breath. I experience waves 
        of panic where I feel like I'm going to die or lose control. I'm having severe insomnia - 
        I can't fall asleep or stay asleep, averaging only 2-3 hours per night. I feel constantly 
        tired and fatigued but can't rest. I have frequent headaches and muscle tension, especially 
        in my neck and shoulders. I also feel very sad and hopeless, with no interest in things I 
        used to enjoy. My appetite has disappeared and I've lost weight. I feel dizzy and lightheaded 
        frequently. I'm also experiencing numbness and tingling in my hands.""",
        "symptoms": ['anxiety', 'chest_pain', 'shortness_of_breath', 'insomnia', 'fatigue', 
                    'headache', 'muscle_pain', 'depression', 'loss_of_appetite', 'weight_loss', 
                    'dizziness', 'numbness']
    },
    
    {
        "name": "Case 8: Allergic Reaction with Multiple Systems",
        "description": """About 2 hours after eating at a restaurant, I started developing an itchy 
        rash all over my body, especially on my face, neck, and arms. The rash has red, raised bumps 
        like hives. My face, lips, and tongue feel swollen and tingly. I'm having difficulty breathing 
        and my throat feels tight, like it's closing up. I'm wheezing when I breathe and my chest 
        feels tight. I'm also experiencing severe abdominal cramping and have had diarrhea twice. 
        I feel extremely nauseous and dizzy, like I might pass out. My heart is racing and I feel 
        very anxious and restless. I'm also sweating profusely and feel very weak.""",
        "symptoms": ['skin_rash', 'itching', 'swelling', 'shortness_of_breath', 'chest_pain', 
                    'abdominal_pain', 'diarrhea', 'nausea', 'dizziness', 'anxiety', 'sweating', 
                    'weakness']
    },
    
    {
        "name": "Case 9: Chronic Pain with Systemic Effects",
        "description": """I've been dealing with severe, persistent lower back pain for months that 
        radiates down both legs. The pain is constant and gets worse with any movement. My joints, 
        especially knees, hips, and shoulders, are very stiff and painful, particularly in the morning. 
        I also have chronic neck pain and frequent tension headaches. The pain makes it hard to sleep, 
        so I'm constantly fatigued and exhausted. I feel depressed because the pain never goes away. 
        I've lost my appetite because even eating seems like too much effort. I feel weak and have 
        difficulty doing daily activities. Sometimes I also experience numbness and tingling in my 
        legs and feet. I'm also dealing with muscle spasms and cramping.""",
        "symptoms": ['back_pain', 'joint_pain', 'neck_pain', 'headache', 'insomnia', 'fatigue', 
                    'depression', 'loss_of_appetite', 'weakness', 'numbness', 'muscle_pain']
    },
    
    {
        "name": "Case 10: Severe Dermatological Condition",
        "description": """My skin has been in terrible condition for the past two weeks. I have a 
        widespread rash covering my torso, arms, and legs with red, inflamed patches. The itching 
        is unbearable and constant - I can't stop scratching. Some areas are oozing clear fluid and 
        forming crusts. My skin is peeling in large flakes, especially on my arms and scalp. I also 
        have painful swelling in affected areas. The skin feels very hot and burning to the touch. 
        I've developed a low-grade fever and feel generally unwell and fatigued. I have swollen lymph 
        nodes in my neck and armpits. The itching and discomfort are preventing me from sleeping. 
        I also feel very self-conscious and anxious about my appearance.""",
        "symptoms": ['skin_rash', 'itching', 'skin_peeling', 'swelling', 'fever', 'fatigue', 
                    'insomnia', 'anxiety']
    },
    
    {
        "name": "Case 11: Post-Viral Syndrome Complex",
        "description": """I had what seemed like a bad flu about 3 weeks ago, but I never fully 
        recovered. I still have extreme fatigue - I'm tired all the time no matter how much I rest. 
        I experience brain fog and difficulty concentrating on even simple tasks. I have persistent 
        headaches that vary in intensity throughout the day. My body aches, especially my muscles 
        and joints, even though I'm not exercising. I get short of breath easily, even from minimal 
        exertion like walking up stairs. I have a persistent cough that produces some mucus. I'm 
        experiencing heart palpitations randomly throughout the day. My sleep is terrible - I either 
        can't fall asleep or wake up frequently. I also have episodes of dizziness and feel lightheaded 
        when standing. My appetite is poor and I've noticed some weight loss.""",
        "symptoms": ['fatigue', 'confusion', 'headache', 'muscle_pain', 'joint_pain', 
                    'shortness_of_breath', 'cough', 'insomnia', 'dizziness', 'loss_of_appetite', 
                    'weight_loss', 'weakness']
    },
    
    {
        "name": "Case 12: Severe Dehydration and Electrolyte Imbalance",
        "description": """I've had severe diarrhea and vomiting for the past 48 hours - I can't keep 
        anything down, not even water. My mouth and lips are extremely dry and cracked. I feel dizzy 
        and lightheaded, especially when I try to stand up. My heart is racing and feels irregular. 
        I have severe muscle cramps in my legs and abdomen. I'm experiencing extreme weakness and 
        fatigue - I can barely walk without feeling like I'll collapse. My urine is very dark and 
        scanty. I have a persistent headache and feel confused and disoriented. I'm not sweating even 
        though I feel hot. My eyes feel sunken and my skin looks pale and feels clammy. I also have 
        numbness and tingling in my hands and feet.""",
        "symptoms": ['diarrhea', 'vomiting', 'dizziness', 'muscle_pain', 'weakness', 'fatigue', 
                    'headache', 'confusion', 'pale_skin', 'numbness', 'nausea', 'abdominal_pain']
    }
]


def test_complex_cases():
    """Test the healthcare system with complex, realistic cases"""
    print("="*100)
    print("🏥 HEALTHCARE ASSISTANT - COMPLEX CASE TESTING")
    print("="*100)
    
    # Load the trained model
    assistant = HealthcareAssistant()
    
    try:
        assistant.load_model('healthcare_model.pkl')
        print(f"\n✅ Model loaded successfully")
        print(f"📊 Total known symptoms in database: {len(assistant.all_symptoms)}")
    except FileNotFoundError:
        print("\n❌ Model not found. Please run Healthcare_Assistant_System.py first.")
        return
    
    print("\n" + "="*100)
    print(f"🧪 Testing {len(COMPLEX_TEST_CASES)} Complex Clinical Cases")
    print("="*100)
    
    results_summary = []
    
    for i, test_case in enumerate(COMPLEX_TEST_CASES, 1):
        print("\n" + "█"*100)
        print(f"📋 {test_case['name']}")
        print("█"*100)
        
        print(f"\n📝 PATIENT COMPLAINT:")
        print(f"{test_case['description']}")
        
        print(f"\n🎯 EXPECTED SYMPTOMS ({len(test_case['symptoms'])} total):")
        for j, symptom in enumerate(test_case['symptoms'], 1):
            print(f"   {j}. {symptom.replace('_', ' ').title()}")
        
        # Get assessment
        print(f"\n🔬 RUNNING DIAGNOSTIC ANALYSIS...")
        print("-"*100)
        
        assessment = assistant.get_comprehensive_assessment(test_case['symptoms'])
        
        # Print detailed assessment
        print_assessment(assessment)
        
        # Store results
        results_summary.append({
            'case': test_case['name'],
            'disease': assessment['predicted_disease'],
            'confidence': assessment['confidence'],
            'severity': assessment['severity_score'],
            'is_emergency': assessment['is_emergency'],
            'specialist': assessment['recommended_specialist']
        })
        
        print("\n" + "█"*100)
        print(f"✅ Case {i} Analysis Complete")
        print("█"*100)
        
        if i < len(COMPLEX_TEST_CASES):
            input("\n⏸️  Press Enter to continue to next case...")
    
    # Print summary of all cases
    print("\n\n" + "="*100)
    print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
    print("="*100)
    
    print(f"\n{'Case':<50} {'Disease':<25} {'Confidence':<12} {'Emergency':<10} {'Specialist':<25}")
    print("-"*100)
    
    for result in results_summary:
        emergency_flag = "🚨 YES" if result['is_emergency'] else "✅ No"
        print(f"{result['case'][:48]:<50} {result['disease'][:23]:<25} {result['confidence']:>10.1%}  {emergency_flag:<10} {result['specialist']:<25}")
    
    print("\n" + "="*100)
    
    # Statistics
    total_cases = len(results_summary)
    emergency_cases = sum(1 for r in results_summary if r['is_emergency'])
    avg_confidence = sum(r['confidence'] for r in results_summary) / total_cases
    avg_severity = sum(r['severity'] for r in results_summary) / total_cases
    
    print(f"\n📈 TESTING STATISTICS:")
    print(f"   Total Cases Tested: {total_cases}")
    print(f"   Emergency Cases Detected: {emergency_cases} ({emergency_cases/total_cases*100:.1f}%)")
    print(f"   Average Confidence: {avg_confidence:.2%}")
    print(f"   Average Severity Score: {avg_severity:.2f}")
    print(f"   Unique Specialists Recommended: {len(set(r['specialist'] for r in results_summary))}")
    
    print("\n" + "="*100)
    print("🏁 All Complex Cases Testing Complete!")
    print("="*100)


if __name__ == "__main__":
    test_complex_cases()
