# Personality Trait Predictor Based on Birth Date

personality = {
    "Sun": {
        "dates": [1, 10, 19, 28],
        "traits": [
            "Natural leader",
            "Confident",
            "Independent",
            "Ambitious",
            "Strong willpower",
            "Creative",
            "Likes recognition"
        ]
    },
    "Moon": {
        "dates": [2, 11, 20, 29],
        "traits": [
            "Emotional",
            "Caring",
            "Intuitive",
            "Kind",
            "Supportive",
            "Sensitive",
            "Peace-loving"
        ]
    },
    "Jupiter": {
        "dates": [3, 12, 21, 30],
        "traits": [
            "Wise",
            "Optimistic",
            "Knowledge seeker",
            "Teacher",
            "Spiritual",
            "Generous",
            "Positive thinker"
        ]
    },
    "Rahu": {
        "dates": [4, 13, 22, 31],
        "traits": [
            "Innovative",
            "Unconventional",
            "Risk taker",
            "Ambitious",
            "Curious",
            "Tech-oriented",
            "Thinks differently"
        ]
    },
    "Mercury": {
        "dates": [5, 14, 23],
        "traits": [
            "Excellent communicator",
            "Intelligent",
            "Quick learner",
            "Adaptable",
            "Business-minded",
            "Logical",
            "Witty"
        ]
    },
    "Venus": {
        "dates": [6, 15, 24],
        "traits": [
            "Charming",
            "Romantic",
            "Artistic",
            "Loves luxury",
            "Friendly",
            "Creative",
            "Attractive personality"
        ]
    },
    "Ketu": {
        "dates": [7, 16, 25],
        "traits": [
            "Spiritual",
            "Analytical",
            "Independent thinker",
            "Research-oriented",
            "Mysterious",
            "Introverted",
            "Philosophical"
        ]
    },
    "Saturn": {
        "dates": [8, 17, 26],
        "traits": [
            "Disciplined",
            "Hardworking",
            "Responsible",
            "Patient",
            "Practical",
            "Persistent",
            "Reliable"
        ]
    },
    "Mars": {
        "dates": [9, 18, 27],
        "traits": [
            "Energetic",
            "Courageous",
            "Competitive",
            "Bold",
            "Action-oriented",
            "Fearless",
            "Strong determination"
        ]
    }
}


def predict_personality(day):
    for planet, info in personality.items():
        if day in info["dates"]:
            print("\n" + "=" * 50)
            print("PERSONALITY TRAIT PREDICTION")
            print("=" * 50)
            print(f"Birth Date : {day}")
            print(f"Ruling Planet : {planet}\n")
            print("Personality Traits:")
            for i, trait in enumerate(info["traits"], start=1):
                print(f"{i}. {trait}")
            return

    print("Invalid birth date! Please enter a value between 1 and 31.")


# Main Program
try:
    day = int(input("Enter your birth date (1-31): "))
    if 1 <= day <= 31:
        predict_personality(day)
    else:
        print("Please enter a valid day between 1 and 31.")
except ValueError:
    print("Please enter a numeric value.")