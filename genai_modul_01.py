#
# genai_modul_01.py
#
#
# -- Utility 
#
def setup_api_keys(key_names):
    """
    Setzt angegebene API-Keys aus Google Colab userdata als Umgebungsvariablen.

    Args:
        key_names (list[str]): Liste der Namen der API-Keys (z. B. ["OPENAI_API_KEY", "HF_TOKEN"]).

    Hinweis:
        Die API-Keys werden direkt in die Umgebungsvariablen geschrieben,
        aber NICHT zurückgegeben, um unbeabsichtigte Sichtbarkeit zu vermeiden.
    """
    from google.colab import userdata
    from os import environ

    for key in key_names:
        value = userdata.get(key)
        if value:
            environ[key] = value
#
# -- Standards
#
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


def run_chain(llm, prompt, history, user_input):
    """
    Führt einen LLM-gestützten Chat-Durchlauf mit Prompt und Verlauf aus.

    Diese Funktion übernimmt ein LLM-Modell, ein ChatPromptTemplate, den bisherigen Chatverlauf
    und eine neue Benutzereingabe. Sie formatiert die Eingaben, ruft das Modell auf, aktualisiert
    den Verlauf und verarbeitet die Antwort.

    Args:
        llm: Ein LangChain-kompatibles LLM-Objekt, z. B. ChatOpenAI.
        prompt: Ein ChatPromptTemplate mit MessagesPlaceholder für den Verlauf.
        history (list): Liste bestehender Nachrichten (HumanMessage/AIMessage).
        user_input (str): Die aktuelle Eingabe des Benutzers.

    Returns:
        tuple:
            - processed (dict): Strukturierte Ausgabe der Modellantwort, z. B. über `process_response()`.
            - history (list): Der aktualisierte Nachrichtenverlauf.
    """
    messages = prompt.format_messages(chat_history=history, input=user_input)
    response = llm.invoke(messages)

    # Verlauf erweitern
    history.append(HumanMessage(content=user_input))
    history.append(AIMessage(content=response.content))

    # Antwort strukturieren
    processed = process_response(response)
    return processed, history



def run_chain_strparser(llm, prompt, history, user_input, parser=StrOutputParser()):
    """
    Führt eine Chat-Anfrage durch, verarbeitet die Antwort und aktualisiert den Chatverlauf.

    Args:
        llm (ChatOpenAI): Das zu verwendende LLM-Modell.
        prompt (ChatPromptTemplate): Der Prompt mit Nachrichtenstruktur.
        history (list): Liste bisheriger Nachrichten (Chatverlauf).
        user_input (str): Neue Benutzereingabe.
        parser (OutputParser): Parser zur Nachverarbeitung der Ausgabe (default: StrOutputParser).

    Returns:
        tuple: (Antworttext, aktualisierter Chatverlauf)
    """
    # Chain vorbereiten
    chain = prompt | llm | parser

    # Eingaben zusammensetzen
    inputs = {
        "chat_history": history,
        "input": user_input
    }

    # Chain ausführen
    output = chain.invoke(inputs)

    # Verlauf aktualisieren
    history.append(HumanMessage(content=user_input))
    history.append(AIMessage(content=output))

    return output, history
