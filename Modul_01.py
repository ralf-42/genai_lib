#
# -- Utility Test
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