"""
genai_lib – Eine Mini-Bibliothek für Einsteiger in Generative KI

Diese Bibliothek stellt eine einfache, strukturierte Schnittstelle zur Nutzung von
LLMs wie GPT-4 bereit. Sie richtet sich an Lernende, die erste praktische Erfahrungen
mit generativer KI sammeln möchten, ohne sich direkt mit komplexen APIs oder Frameworks
auseinandersetzen zu müssen.

Module:
- folgt
- folgt

Beispiel:
    from genai_lib.setup import get_llm, get_prompt, get_parser
    from genai_lib.chat import run_chat

    history = []
    antwort, history = run_chat(get_llm(), get_prompt(), history, "Was ist KI?", get_parser())
    print(antwort)
"""