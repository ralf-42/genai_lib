from setuptools import setup, find_packages

# Lies den Inhalt deiner README-Datei für die long_description
# Dies ist eine gute Praxis. Stelle sicher, dass du eine README.md hast.
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Ein Python-Paket für GenAI-Funktionen." # Fallback

setup(
    name="genai_lib",  # Erforderlich: Der Name deines Pakets, wie er auf PyPI erscheinen würde.
                      # Üblicherweise der gleiche Name wie dein Repository oder Hauptmodul.

    version="0.1.0",  # Erforderlich: Die aktuelle Version deines Pakets.
                      # Folge semantischer Versionierung (z.B. MAJOR.MINOR.PATCH).

    author="Ralf Bendig",  # Optional: Dein Name oder der Name deiner Organisation.
    author_email="deine_email@example.com",  # Optional: Deine Kontakt-E-Mail.

    description="Eine kurze Beschreibung deiner GenAI-Bibliothek.",  # Optional, aber empfohlen.
    long_description=long_description,  # Wird von der README.md gelesen.
    long_description_content_type="text/markdown",  # Wichtig, wenn deine README im Markdown-Format ist.

    url="https://github.com/ralf-42/genai_lib",  # Optional: Link zu deinem GitHub-Repository oder Projekt-Homepage.

    # Erforderlich: Hier sagst du setuptools, welche Pakete es einschließen soll.
    # find_packages() findet automatisch alle Pakete (Ordner mit __init__.py)
    # in deinem Projekt.
    # Wenn dein Hauptcode z.B. in einem Ordner namens 'genai_lib' liegt,
    # wird dieser gefunden.
    # packages=find_packages(where="."), # Sucht Pakete im aktuellen Verzeichnis

   

    # Optional: Liste hier alle Abhängigkeiten auf, die dein Paket benötigt.
    # Diese werden automatisch mitinstalliert, wenn dein Paket installiert wird.
    # Beispiel: install_requires=["numpy>=1.20", "requests"],
    install_requires=[
        # "pandas",
        # "openai",
        # "torch"
    ],

    # Optional: Klassifikatoren helfen Benutzern, dein Paket zu finden und geben
    # Auskunft über den Status und die Zielgruppe.
    # Eine vollständige Liste findest du unter https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 3 - Alpha",  # Z.B. 3 - Alpha, 4 - Beta, 5 - Production/Stable
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",  # Wähle eine passende Lizenz
        "Operating System :: OS Independent",
    ],

    python_requires=">=3.11",  # Optional: Gib die minimal erforderliche Python-Version an.
)