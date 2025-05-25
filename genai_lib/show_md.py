# show.py

from IPython.display import display, Markdown

def show_md(text: str, prefix: str = "") -> None:
    """
    Zeigt einen Markdown-Text im Notebook an, optional mit Prefix-Icon oder -Text.

    Args:
        text (str): Der anzuzeigende Markdown-Text.
        prefix (str, optional): Ein optionaler Prefix-String (z. B. Emoji oder Hinweistext).
    """
    display(Markdown(f"{prefix}{text}"))

def show_title(text: str) -> None:
    """
    Zeigt einen Abschnittstitel im Notebook im Markdown-Format.

    Args:
        text (str): Der Titeltext.
    """
    show_md(f"# {text} 💡")

def show_subtitle(text: str) -> None:
    """
    Zeigt einen Untertitel im Notebook an.

    Args:
        text (str): Der Untertiteltext.
    """
    show_md(f"## {text}")

def show_info(text: str) -> None:
    """
    Zeigt einen allgemeinen Informationstext im Notebook an.

    Args:
        text (str): Der Inhalt der Information.
    """
    show_md(f"ℹ️ **Info:** {text}")

def show_warning(text: str) -> None:
    """
    Zeigt eine Warnmeldung im Notebook an.

    Args:
        text (str): Der Warnungstext.
    """
    show_md(f"⚠️ **Achtung:** {text}")

def show_success(text: str) -> None:
    """
    Zeigt eine Erfolgsmeldung im Notebook an.

    Args:
        text (str): Der Erfolgstext.
    """
    show_md(f"✅ {text}")


