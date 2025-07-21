#
# utilities.py
#
# Stand: 21.07.2025
#
from IPython.display import display, Markdown
import requests
import sys
import warnings
import subprocess
#
# -- Sammlung von Standard-Funktionen für den Kurs
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

# Importiere die IPython-Umgebung, um Shell-Befehle wie !uv pip install ausführen zu können
from IPython import get_ipython

# Unterdrücke ImportWarnings, die z. B. durch inkompatible Import-Hooks in Colab ausgelöst werden können
import warnings
warnings.simplefilter("ignore", ImportWarning)

def install_packages(packages):
    """
    Installiert eine Liste von Python-Paketen mit 'uv pip install' in einer Google-Colab-Umgebung,
    wenn sie noch nicht importierbar sind.
    
    Parameter:
    ----------
    packages : list of str or list of tuple
        Eine Liste von Paketnamen oder Tupeln (install_name, import_name).
        Beispiele:
        - ['numpy', 'pandas'] 
        - [('markitdown[all]', 'markitdown'), 'langchain_chroma']
    
    Funktionsweise:
    ---------------
    - Trennt zwischen Installationsname (für pip) und Importname (für Python).
    - Versucht, jedes angegebene Modul mit 'import' zu laden.
    - Falls der Import fehlschlägt: führt 'uv pip install --system -q <paketname>' aus.
    - Gibt für jedes Paket eine Erfolgsmeldung oder eine Fehlermeldung aus.
    
    Voraussetzungen:
    ----------------
    - Die Funktion ist für die Ausführung in Google Colab gedacht.
    - 'uv' muss bereits installiert sein.
    - Die IPython-Umgebung muss aktiv sein (z. B. in Colab-Notebooks).
    """
    import importlib
    
    # Zugriff auf das aktuelle IPython-Shell-Objekt
    shell = get_ipython()
    
    for package in packages:
        # Bestimme Install- und Import-Namen
        if isinstance(package, tuple):
            install_name, import_name = package
        else:
            # Falls nur ein Name gegeben ist, verwende ihn für beide
            install_name = import_name = package
        
        try:
            # Versuche, das Modul zu importieren
            # Verwende importlib anstatt exec für sicheren Import
            importlib.import_module(import_name)
            print(f"✅ {import_name} bereits verfügbar")
            
        except ImportError:
            try:
                # Falls ImportError: Installiere das Paket über uv
                print(f"🔄 Installiere {install_name}...")
                shell.run_line_magic("system", f"uv pip install --system -q {install_name}")
                
                # Versuche erneut zu importieren nach der Installation
                importlib.import_module(import_name)
                print(f"✅ {install_name} erfolgreich installiert und importiert")
                
            except ImportError as import_error:
                print(f"❌ {install_name} installiert, aber Import von {import_name} fehlgeschlagen: {import_error}")
            except Exception as install_error:
                print(f"⚠️ Fehler bei der Installation von {install_name}: {install_error}")


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


def setup_api_keys(key_names, create_globals=True):
    """
    Setzt angegebene API-Keys aus Google Colab userdata als Umgebungsvariablen
    und optional als globale Variablen.
    
    Args:
        key_names (list[str]): Liste der Namen der API-Keys (z.B. ["OPENAI_API_KEY", "HF_TOKEN"]).
        create_globals (bool): Wenn True, werden auch globale Variablen erstellt (Standard: True).
    
    Hinweis:
        Die API-Keys werden direkt in die Umgebungsvariablen geschrieben,
        aber NICHT zurückgegeben, um unbeabsichtigte Sichtbarkeit zu vermeiden.
        Bei create_globals=True werden zusätzlich globale Variablen mit den Key-Namen erstellt.
    """
    from google.colab import userdata
    from os import environ
    import inspect
    
    # Zugriff auf den globalen Namespace des aufrufenden Moduls
    caller_frame = inspect.currentframe().f_back
    caller_globals = caller_frame.f_globals
    
    for key in key_names:
        try:
            value = userdata.get(key)
            if value:
                # Umgebungsvariable setzen
                environ[key] = value
                
                # Optional: Globale Variable im aufrufenden Modul erstellen
                if create_globals:
                    caller_globals[key] = value
                    
                print(f"✓ {key} erfolgreich gesetzt")
            else:
                print(f"⚠ {key} nicht in userdata gefunden")
                
        except Exception as e:
            print(f"✗ Fehler beim Setzen von {key}: {e}")


# Beispiel für die Verwendung:
if __name__ == "__main__":
    # API-Keys setzen (mit globalen Variablen)
    setup_api_keys([
        "OPENAI_API_KEY", 
        "HF_TOKEN", 
        "ANTHROPIC_API_KEY"
    ])
    
    # Jetzt können die Keys sowohl als Umgebungsvariable als auch als globale Variable verwendet werden:
    # print(OPENAI_API_KEY)  # Globale Variable
    # print(os.environ["OPENAI_API_KEY"])  # Umgebungsvariable
    
    # Ohne globale Variablen (nur Umgebungsvariablen):
    # setup_api_keys(["ANOTHER_KEY"], create_globals=False)            


def mprint(text):
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


