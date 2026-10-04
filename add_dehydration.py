import json
from pathlib import Path

def add_dehydration():
    path = Path("data/health_topics.json")
    with open(path, "r", encoding="utf-8") as f:
        topics = json.load(f)
        
    for t in topics:
        if t["intent"] == "dehydration":
            print("Already exists")
            return
            
    dehydration_topic = {
        "intent": "dehydration",
        "topic": "Dehydration",
        "aliases": ["dehydrated", "lack of water", "not drinking enough", "thirst"],
        "keywords": ["water", "fluid", "hydration", "dry"],
        "description": "Dehydration occurs when you use or lose more fluid than you take in, and your body doesn't have enough water and other fluids to carry out its normal functions.",
        "common_symptoms": ["Extreme thirst", "Less frequent urination", "Dark-colored urine", "Fatigue", "Dizziness", "Confusion"],
        "general_guidance": ["Drink plenty of water", "Drink oral rehydration solutions", "Avoid caffeine and alcohol", "Rest in a cool area"],
        "prevention": ["Drink water throughout the day", "Eat fluid-rich foods", "Hydrate extra during exercise or hot weather"],
        "seek_medical_help": "If you have had diarrhea for 24 hours, are irritable or disoriented, can't keep fluids down, or have bloody or black stool.",
        "emergency_warning_signs": ["Lack of urination for 8 hours", "Seizures", "Lethargy or confusion", "Rapid heart rate"],
        "disclaimer": "This is general educational information. Not a medical diagnosis."
    }
    
    topics.append(dehydration_topic)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2)
        
    print("Added dehydration to health_topics.json")

if __name__ == "__main__":
    add_dehydration()
