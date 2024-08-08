from flask import session
from groq import Groq, BadRequestError, APIError

api_key = "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"
client = Groq(api_key=api_key)


def get_response(message):
    response_content = ""
    buttons = []

    valid_roles = ["system", "user", "assistant"]
    messages = [{"role": "system", "content": "Du er en assistent som er plassert på uex.no for å hjelpe folk med å forstå hva uex tilbyr. Navnet ditt er Mia."
                                              "Du har et par verktøy du kan bruke for å hjelpe folk med å navigere. Når du skriver disse blir de produsert i chatten som fungerende elementer. Den første av disse er {knapp_1}, som tillater folk å gå til 'om oss' siden av uex.no."
                                              "Du har {knapp_2} som lar folk besøke 'produkter' siden til uex. Du har {skjema} som lar folk ta kontakt med uex direkte. Jobben din er å forklare hva uex er til besøkende på siden."
                                              "Du skal være morsom og konkret. Du svarer hovedsakelig i norsk, med mindre besøkende spør om du kan snakke andre språk"
                                              "Før du har rukket å si noe blir besøkende møtt med meldingen 'Hei, mitt navn er Mia! Kan jeg hjelpe deg med å forstå hva Uex tilbyr?'."
                                              "Dette er beskrivelsen du har av Uex: 'Uex er et selskap som gjør det enkelt for alle å lage skreddersydde chatbotter for nettsidene sine."
                                              "En salgsassistent fra uex kan hjelpe besøkende med å lettere navigere og forstå innholdet i en nettside, og hjelpe kunder mer å enklere ta kontakt gjennom nettsiden."
                                              "Uex gjør det enkelt for alle en hver å integrere intelligens i eksisterende nettsider'. Hver prompt du får har minne over hele chatten du har hatt med brukeren. Du skal bruke samtalehistorikken til å være konsis og passe på at du ikke repeterer deg selv. Alltid prøv å skrive korte svar som leder til samtale, som om du sender tekst-meldinger."}]

    # Validate and append historical messages
    for msg in session.get('chat_history', []):
        if msg["role"] in valid_roles:
            messages.append(msg)
        else:
            print(f"Invalid role found: {msg['role']} in message: {msg}")

    # Append the current user message
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # or "llama3-8b"
            messages=messages,
            temperature=1,
            max_tokens=2024,
            top_p=1,
            stream=True,
            stop=None,
        )

        for chunk in response:
            response_content += chunk.choices[0].delta.content or ""

        # Check for specific keywords to add buttons
        if "{knapp_1}" in response_content:
            buttons.append({"label": "Om oss", "link": "https://example.com/about"})
            response_content = response_content.replace("{knapp_1}", "")

        if "{knapp_2}" in response_content:
            buttons.append({"label": "Produkter", "link": "https://example.com/products"})
            response_content = response_content.replace("{knapp_2}", "")

    except BadRequestError as bre:
        print(f"BadRequestError: {bre}")
        response_content = "An error occurred while processing your request due to bad request. Please try again."
    except APIError as api_error:
        print(f"APIError: {api_error}")
        response_content = "An error occurred with the API. Please try again later."
    except Exception as e:
        print(f"Unexpected error: {e}")
        response_content = "An unexpected error occurred. Please try again later."

    return response_content, buttons

