def apply_prepare_framework(task: str, role: str = "KI-Experte", tone: str = "neutral", word_limit: int = 300) -> str:
    """
    Erstellt einen Prompt nach dem PREPARE-Framework zur strukturierten Modellführung.

    Args:
        task (str): Die eigentliche Aufgabe, die das Modell lösen soll.
        role (str): Die Rolle, die das Modell einnehmen soll.
        tone (str): Der gewünschte Tonfall (z. B. "neutral", "freundlich", "formell").
        word_limit (int): Maximale Wortanzahl für die Modellantwort.

    Returns:
        str: Ein vollständiger Prompt nach PREPARE-Struktur.
    """
    prompt = f"""
[P] Prompt: Bitte bearbeite die folgende Aufgabe:
{task}

[R] Role: Du bist ein {role} mit Fachwissen in diesem Bereich.

[E] Explicit: Gehe die Aufgabe Schritt für Schritt an und achte auf logische Nachvollziehbarkeit.

[P] Parameters: Antworte im Tonfall \"{tone}\". Begrenze die Antwort auf maximal {word_limit} Wörter.

[A] Ask: Wenn du etwas nicht verstehst, erkläre das und stelle ggf. Rückfragen.

[R] Rate: Bewerte deine Antwort am Ende selbst auf einer Skala von 0–10 und schlage Verbesserungen vor.

[E] Emotion: Verwende eine motivierende Ausdrucksweise, um das Interesse zu fördern.
"""
    return prompt.strip()