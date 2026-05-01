"""
Rule-based symptom → condition mapping (weighted overlap scoring).
Not medical diagnosis — educational / demo API only.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConditionProfile:
    name: str
    symptoms: frozenset[str]
    advice: str


# Normalized symptom tokens (lowercase) for matching
CONDITIONS: tuple[ConditionProfile, ...] = (
    ConditionProfile(
        name="Influenza (Flu)",
        symptoms=frozenset(
            {"fever", "cough", "body ache", "body aches", "fatigue", "chills", "headache"}
        ),
        advice="Rest, fluids, and OTC fever reducers as directed. Seek care if breathing is hard, "
        "symptoms worsen, or high-risk (pregnancy, age 65+, chronic illness).",
    ),
    ConditionProfile(
        name="COVID-19",
        symptoms=frozenset(
            {
                "fever",
                "cough",
                "fatigue",
                "loss of taste",
                "loss of smell",
                "shortness of breath",
                "sore throat",
            }
        ),
        advice="Consider testing and isolation per local guidance. Seek urgent care for trouble "
        "breathing, persistent chest pain, confusion, or bluish lips.",
    ),
    ConditionProfile(
        name="Common cold",
        symptoms=frozenset(
            {"cough", "runny nose", "sore throat", "sneezing", "congestion", "mild fever"}
        ),
        advice="Rest, hydration, and saline rinses often help. See a clinician if fever is high "
        "or symptoms last beyond typical duration.",
    ),
    ConditionProfile(
        name="Strep throat",
        symptoms=frozenset(
            {"sore throat", "fever", "difficulty swallowing", "swollen glands", "headache"}
        ),
        advice="Bacterial strep needs testing and sometimes antibiotics - contact a clinician "
        "for rapid strep/culture.",
    ),
    ConditionProfile(
        name="Migraine",
        symptoms=frozenset(
            {"headache", "nausea", "sensitivity to light", "sensitivity to sound", "vision changes"}
        ),
        advice="Dark quiet room, hydration, and prescribed or OTC options as you already use. "
        "Seek care for sudden severe headache or neuro symptoms.",
    ),
    ConditionProfile(
        name="Gastroenteritis (stomach bug)",
        symptoms=frozenset(
            {"nausea", "vomiting", "diarrhea", "stomach cramps", "fever", "dehydration"}
        ),
        advice="Small sips of oral rehydration; avoid anti-diarrheals if infection suspected. "
        "Seek care for blood in stool, severe dehydration, or high fever.",
    ),
    ConditionProfile(
        name="Allergic rhinitis",
        symptoms=frozenset(
            {"sneezing", "runny nose", "itchy eyes", "congestion", "watery eyes"}
        ),
        advice="Antihistamines and reducing allergen exposure often help. See a clinician if "
        "wheezing or symptoms are severe.",
    ),
    ConditionProfile(
        name="Urinary tract infection (UTI)",
        symptoms=frozenset(
            {"burning urination", "frequent urination", "urgency", "lower abdominal pain", "fever"}
        ),
        advice="Clinical evaluation and urine testing are typical. Seek urgent care if fever, "
        "flank pain, or you are pregnant.",
    ),
)


# Common input variants -> canonical tokens used by the rule set.
SYMPTOM_ALIASES: dict[str, str] = {
    "temperature": "fever",
    "high fever": "fever",
    "feverish": "fever",
    "tiredness": "fatigue",
    "tired": "fatigue",
    "blocked nose": "congestion",
    "stuffy nose": "congestion",
    "nose congestion": "congestion",
    "running nose": "runny nose",
    "breathlessness": "shortness of breath",
    "smell loss": "loss of smell",
    "taste loss": "loss of taste",
    "painful urination": "burning urination",
    "burning while peeing": "burning urination",
    "vomit": "vomiting",
    "loose motion": "diarrhea",
    "loose motions": "diarrhea",
}


def normalize_symptom_token(s: str) -> str:
    normalized = " ".join(s.strip().lower().split())
    return SYMPTOM_ALIASES.get(normalized, normalized)


def parse_symptom_input(raw: str) -> set[str]:
    """Split comma/newline separated symptoms into normalized tokens."""
    parts: list[str] = []
    for chunk in raw.replace("\n", ",").split(","):
        t = normalize_symptom_token(chunk)
        if t:
            parts.append(t)
    return set(parts)


def score_condition(user_symptoms: set[str], profile: ConditionProfile) -> float:
    """Overlap score: matched / len(condition symptoms), with small boost for user coverage."""
    if not profile.symptoms:
        return 0.0
    matched = user_symptoms & profile.symptoms
    if not matched:
        return 0.0
    recall_on_profile = len(matched) / len(profile.symptoms)
    precision_on_user = len(matched) / max(len(user_symptoms), 1)
    return 0.65 * recall_on_profile + 0.35 * precision_on_user


def suggest_conditions(user_symptoms: set[str], top_k: int = 5, min_score: float = 0.12) -> list[tuple[ConditionProfile, float]]:
    ranked: list[tuple[ConditionProfile, float]] = []
    for c in CONDITIONS:
        s = score_condition(user_symptoms, c)
        if s >= min_score:
            ranked.append((c, s))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked[:top_k]
