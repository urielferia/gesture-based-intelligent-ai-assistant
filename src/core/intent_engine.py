# src/core/intent_engine.py
from google import genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

SYSTEM_PROMPT = """
Eres un asistente de intención pasiva integrado en GBIAS (Gesture-Based Intelligent AI Assistant).
Tu trabajo es observar patrones de gestos del usuario e inferir qué necesita, sin que te lo pida explícitamente.

Recibirás un JSON con el contexto actual: gestos recientes, perfil activo, frecuencia, duración de sesión y hora del día.

Responde ÚNICAMENTE con un JSON con esta estructura exacta, sin texto adicional, sin markdown:
{
  "inferred_intent": "descripción breve de lo que el usuario probablemente necesita",
  "suggested_action": "acción concreta sugerida",
  "confidence": 0.0,
  "reasoning": "explicación corta del razonamiento"
}

Ejemplos de suggested_action: "pause_media", "lower_volume", "suggest_break", "increase_volume", "change_profile", "none".
confidence va de 0.0 a 1.0.
Si no hay suficiente contexto para inferir, usa "none" como suggested_action y confidence menor a 0.4.
"""

class IntentEngine:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "gemini-flash-latest"

    def infer(self, context_snapshot: str) -> dict:
        """Manda el contexto a Gemini y devuelve la intención inferida como dict."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=f"Contexto actual del usuario:\n{context_snapshot}",
                config=genai.types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2
                )
            )

            raw = response.text.strip()

            # Limpiar por si Gemini agrega markdown
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            return json.loads(raw)

        except json.JSONDecodeError:
            return {
                "inferred_intent": "error al parsear respuesta",
                "suggested_action": "none",
                "confidence": 0.0,
                "reasoning": f"Gemini no devolvió JSON válido: {response.text[:100]}"
            }
        except Exception as e:
            return {
                "inferred_intent": "error de conexión",
                "suggested_action": "none",
                "confidence": 0.0,
                "reasoning": str(e)
            }