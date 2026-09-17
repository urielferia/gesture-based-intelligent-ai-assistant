# src/core/intent_engine.py
from google import genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

SYSTEM_PROMPT = """
You are a passive intent assistant integrated into GBIAS (Gesture-Based Intelligent AI Assistant).
Your role is to observe user gesture patterns and infer what they need without being asked explicitly.

You will receive a JSON with the current context: recent gestures, active profile, gesture frequency, session duration, and time of day.

Respond ONLY with a JSON object with this exact structure, with no additional text or markdown formatting:
{
  "inferred_intent": "brief description of what the user likely needs",
  "suggested_action": "concrete suggested action",
  "confidence": 0.0,
  "reasoning": "short explanation of the reasoning"
}

Examples of suggested_action: "pause_media", "lower_volume", "suggest_break", "increase_volume", "change_profile", "none".
confidence ranges from 0.0 to 1.0.
If there is not enough context to make an inference, set suggested_action to "none" and confidence below 0.4.
"""

class IntentEngine:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "gemini-flash-latest"

    def infer(self, context_snapshot: str) -> dict:
        """Sends the context to Gemini and returns the inferred intent as a dict."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=f"Current user context:\n{context_snapshot}",
                config=genai.types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2
                )
            )

            raw = response.text.strip()

            # Clean up in case Gemini wraps the response in markdown
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            return json.loads(raw)

        except json.JSONDecodeError:
            return {
                "inferred_intent": "error parsing response",
                "suggested_action": "none",
                "confidence": 0.0,
                "reasoning": f"Gemini did not return valid JSON: {response.text[:100]}"
            }
        except Exception as e:
            return {
                "inferred_intent": "connection error",
                "suggested_action": "none",
                "confidence": 0.0,
                "reasoning": str(e)
            }