from app.agent import classify_question, detect_emergency_type
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.agent import classify_question, detect_emergency_type

def test_dehydration_is_medical():
    assert classify_question(
        "Comment reconnaître une déshydratation sévère ?"
    ) == "medical"


def test_sudden_breathing_difficulty_is_emergency():
    assert detect_emergency_type(
        "Que faire en cas de difficultés respiratoires soudaines ?"
    ) == "breathing"


def test_severe_shortness_of_breath_is_emergency():
    assert detect_emergency_type(
        "J'ai beaucoup de mal à respirer"
    ) == "breathing"


if __name__ == "__main__":
    test_dehydration_is_medical()
    test_sudden_breathing_difficulty_is_emergency()
    test_severe_shortness_of_breath_is_emergency()
    print("Tous les tests de routage sont passés.")