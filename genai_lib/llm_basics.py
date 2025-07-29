# erste Sammlung für llm_basics

def setup_ChatOpenAI(**kwargs):
    """Setup für Google Colab optimiert"""
    from langchain_openai import ChatOpenAI
    if kwargs == "":
        GENAI_DEFAULTS = {
            "model": "gpt-4o-mini",
            "temperature": 0.0,
        }
        return ChatOpenAI(**GENAI_DEFAULTS)
    else:
        return ChatOpenAI(**kwargs)


def get_all_model_attributes(llm):
    """Liest alle verfügbaren Attribute des LLM-Objekts dynamisch aus"""
    # llm.__dict__ enthält alle Instanzattribute
    attributes = {}
    for key, value in vars(llm).items():
        # Optional: sensible Daten wie API-Keys maskieren
        if "key" in key.lower():
            attributes[key] = "***MASKIERT***"
        else:
            attributes[key] = value
    return attributes


if __name__ == "__main__":
    # 1. LLM initialisieren
    llm = setup_ChatOpenAI()
    
    # 2. Alle Parameter abfragen
    all_params = get_all_model_attributes(llm)
    
    # 3. Ausgabe formatieren
    print("📊 Aktuelle Modell-Attribute:")
    for k, v in all_params.items():
        print(f"   {k}: {v}")