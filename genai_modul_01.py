#
# genai_modul_01.py
#
from IPython.display import display, Markdown

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import requests
import sys
import warnings
import subprocess

#
# -- Utility 
#

def check_environment():
    """
    Gibt die installierte Python-Version aus, listet installierte LangChain-Bibliotheken auf 
    und unterdrückt typische Deprecation-Warnungen im Zusammenhang mit LangChain.

    Diese Funktion ist hilfreich, um schnell die Entwicklungsumgebung für LangChain-Projekte 
    zu überprüfen und störende Warnungen im Notebook oder in der Konsole zu vermeiden.

    Ausgabe:
        - Python-Version
        - Liste installierter Pakete, die mit "langchain" beginnen
    """

    # Python-Version anzeigen
    print(f"Python Version: {sys.version}\n")

    # LangChain-Pakete anzeigen
    print("Installierte LangChain-Bibliotheken:")
    try:
        result = subprocess.run(["pip", "list"], stdout=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            if line.lower().startswith("langchain"):
                print(line)
    except Exception as e:
        print("Fehler beim Abrufen der Paketliste:", e)

    # Warnungen unterdrücken
    warnings.filterwarnings("ignore")
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=UserWarning, module="langsmith.client")




def get_ipinfo():
    """
    Ruft Geoinformationen zur aktuellen öffentlichen IP-Adresse von ipinfo.io ab
    und gibt diese direkt in der Konsole aus.

    Die Ausgabe umfasst:
        - Öffentliche IP-Adresse
        - Hostname
        - Stadt
        - Region
        - Land (ISO-Code)
        - Koordinaten
        - Internetanbieter (Organisation)
        - Postleitzahl
        - Zeitzone

    Beispiel:
        >>> get_ipinfo()
        IP-Adresse: 8.8.8.8
        Stadt: Mountain View
        ...
    """
    try:
        response = requests.get("https://ipinfo.io")
        data = response.json()

        print("IP-Adresse:", data.get("ip"))
        print("Hostname:", data.get("hostname"))
        print("Stadt:", data.get("city"))
        print("Region:", data.get("region"))
        print("Land:", data.get("country"))
        print("Koordinaten:", data.get("loc"))
        print("Provider:", data.get("org"))
        print("Postleitzahl:", data.get("postal"))
        print("Zeitzone:", data.get("timezone"))

    except requests.RequestException as e:
        print("Fehler beim Abrufen der IP-Informationen:", e)


    
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
            

def mdprint(text):
    """
    Gibt den übergebenen Text als Markdown in Jupyter-Notebooks aus.

    Diese Funktion nutzt IPythons `display()` zusammen mit `Markdown()`, 
    um formatierte Markdown-Ausgabe in einem Jupyter-Notebook zu ermöglichen.

    Parameter:
    ----------
    text : str
        Der anzuzeigende Markdown-Text.

    Beispiel:
    ---------
    >>> mdprint("# Überschrift\n**fett** und *kursiv*")
    """
    display(Markdown(text))

#
# -- Standards
#
def build_chat_prompt():
    """
    Erzeugt einen ChatPromptTemplate mit Platzhaltern für:
    - System-Prompt
    - Chatverlauf
    - aktuelle Benutzereingabe

    Returns:
        ChatPromptTemplate: Ein konfigurierter Prompt für Chat-Modelle.
    """
    return ChatPromptTemplate.from_messages([
        ("system", "{system}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{user_input}")
    ])
    
    
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



def run_chain_01(llm, prompt_template, history, user_input):
    """
    Führt einen LLM-gestützten Chat-Durchlauf mit Prompt und Verlauf aus.

    Diese vereinfachte Version verarbeitet die Antwort direkt ohne separate Postprocessing-Funktion.

    Args:
        llm: Ein LangChain-kompatibles LLM-Objekt, z. B. ChatOpenAI.
        prompt_template: Ein ChatPromptTemplate mit MessagesPlaceholder für den Verlauf.
        history (list): Liste bestehender Nachrichten (HumanMessage/AIMessage).
        user_input (str): Die aktuelle Eingabe des Benutzers.

    Returns:
        tuple:
            - response_text (str): Der bereinigte Textinhalt der Modellantwort.
            - history (list): Der aktualisierte Nachrichtenverlauf.
    """
    messages = prompt_template.format_messages(chat_history=history, input=user_input)
    response = llm.invoke(messages)

    # Verlauf erweitern
    history.append(HumanMessage(content=user_input))
    history.append(AIMessage(content=response.content))

    return response.content.strip(), history


def run_chain_02(llm, prompt_template, history, user_input):
    """
    Führt einen LLM-gestützten Chat-Durchlauf mit Prompt und Verlauf aus.

    Diese Funktion übernimmt ein LLM-Modell, ein ChatPromptTemplate, den bisherigen Chatverlauf
    und eine neue Benutzereingabe. Sie formatiert die Eingaben, ruft das Modell auf, aktualisiert
    den Verlauf und verarbeitet die Antwort.

    Args:
        llm: Ein LangChain-kompatibles LLM-Objekt, z. B. ChatOpenAI.
        prompt_template: Ein ChatPromptTemplate mit MessagesPlaceholder für den Verlauf.
        history (list): Liste bestehender Nachrichten (SystemMessage, HumanMessage, AIMessage).
        user_input (str): Die aktuelle Eingabe des Benutzers.

    Returns:
        tuple:
            - processed (dict): Strukturierte Ausgabe der Modellantwort, z. B. über `process_response()`.
            - history (list): Der aktualisierte Nachrichtenverlauf.
    """
    messages = prompt_template.format_messages(chat_history=history, input=user_input)
    response = llm.invoke(messages)

    # Verlauf erweitern
    history.append(HumanMessage(content=user_input))
    history.append(AIMessage(content=response.content))

    # Antwort strukturieren
    processed = process_response(response)
    return processed, history



def run_chain_strparser(llm, prompt_template, history, user_input, parser=StrOutputParser()):
    """
    Führt eine Chat-Anfrage durch, verarbeitet die Antwort und aktualisiert den Chatverlauf.

    Args:
        llm (ChatOpenAI): Das zu verwendende LLM-Modell.
        prompt_template (ChatPromptTemplate): Der Prompt mit Nachrichtenstruktur.
        history (list): Liste bisheriger Nachrichten (Chatverlauf).
        user_input (str): Neue Benutzereingabe.
        parser (OutputParser): Parser zur Nachverarbeitung der Ausgabe (default: StrOutputParser).

    Returns:
        tuple: (Antworttext, aktualisierter Chatverlauf)
    """
    # Chain vorbereiten
    chain = prompt_template | llm | parser

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