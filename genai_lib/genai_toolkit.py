#
# 
#
from IPython.display import display, Markdown

def process_response(response):
    """
    Verarbeitet die Antwort eines LLM-Aufrufs und extrahiert strukturierte Informationen.

    Diese Hilfsfunktion nimmt ein Antwortobjekt (z. B. vom Typ `AIMessage`) entgegen,
    extrahiert den Textinhalt sowie Token-Nutzungsdaten und gibt diese als Wörterbuch zurück.

    Args:
        response (AIMessage): Das Antwortobjekt des LLMs mit Metadaten.

    Returns:
        dict: Ein Dictionary mit folgenden Schlüsseln:
            - 'text' (str): Der bereinigte Textinhalt der Modellantwort.
            - 'tokens_total' (int or None): Gesamtanzahl der verwendeten Tokens.
            - 'tokens_prompt' (int or None): Anzahl Tokens für den Prompt.
            - 'tokens_completion' (int or None): Anzahl Tokens für die generierte Antwort.
    """
    meta = response.response_metadata or {}
    usage = meta.get("token_usage", {})

    return {
        "text": response.content.strip(),
        "tokens_total": usage.get("total_tokens"),
        "tokens_prompt": usage.get("prompt_tokens"),
        "tokens_completion": usage.get("completion_tokens")
    }