import os
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OpenAI.api_key = OPENAI_API_KEY

client = OpenAI(
    # This is the default and can be omitted
    api_key=OPENAI_API_KEY,
)

def generar_respuesta(prompt):
    try:
        response = client.responses.create(
            model="gpt-4o",
            instructions="Eres un asistente",
            input=prompt,
        )
        return response.output_text
    except Exception as e:
        return f"Error: {str(e)}"

# Ejemplo de uso
if __name__ == "__main__":
    while True:
        user_input = input("Tú: ")
        if user_input.lower() in ["salir", "exit"]:
            break
        respuesta = generar_respuesta(user_input)
        print(f"Bot: {respuesta}")
        