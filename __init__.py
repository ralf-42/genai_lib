"""
genai_lib – Eine Mini-Bibliothek für Einsteiger in Generative KI

Diese Bibliothek stellt eine einfache, strukturierte Schnittstelle zur Nutzung von
LLMs wie GPT-4 bereit. Sie richtet sich an Lernende, die erste praktische Erfahrungen
mit generativer KI sammeln möchten, ohne sich direkt mit komplexen APIs oder Frameworks
auseinandersetzen zu müssen.

Module:
- config      : Zentrale Konfiguration wie Modellname, Temperatur usw.
- setup       : Funktionen zur Erstellung von LLM, Prompt und Parser
- chat        : Hauptfunktion zum Durchführen eines Chat-Durchlaufs mit Verlauf
- tools       : Hilfsfunktionen wie Textzusammenfassung, Ausgabeformatierung
- output (optional): Parser für strukturierte Ausgaben (JSON, Pydantic etc.)

Beispiel:
    from genai_lib.setup import get_llm, get_prompt, get_parser
    from genai_lib.chat import run_chat

    history = []
    antwort, history = run_chat(get_llm(), get_prompt(), history, "Was ist KI?", get_parser())
    print(antwort)
"""