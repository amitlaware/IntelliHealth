import os
import logging
import requests

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.enabled = os.getenv("LLM_ENABLED", "true").lower() == "true"
        self.model = os.getenv("OLLAMA_MODEL", "llama2")
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))

    def generate(self, original_query, context):
        if not self.enabled:
            logger.debug("[LLM] GENERATION_MODE=FALLBACK (LLM_ENABLED=false)")
            return None

        prompt = f"""SYSTEM:
You are a healthcare information assistant.
Provide general educational information only.
Do not diagnose the user.
Do not invent facts that are unsupported by the retrieved context.
If the retrieved context is insufficient, clearly say so.
Recommend professional medical care when appropriate.
Do not use a rigid response template (e.g. do not output "Topic:", "Symptoms:", "Guidance:"). Instead, write a natural, conversational response that directly answers the user's specific question using the retrieved context.
Always include a brief disclaimer that this is educational information, not professional medical advice, and recommend they see a doctor if symptoms persist.

USER:
{original_query}

RETRIEVED CONTEXT:
{context}

Please provide a concise, natural-language response:
"""
        logger.debug(f"[LLM] GENERATION_MODE=LLM. Model={self.model}, Context Length={len(context)}")
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"[LLM] Ollama generation failed: {e}. Falling back to deterministic response.")
            return None
        except Exception as e:
            logger.error(f"[LLM] Unexpected error during generation: {e}. Falling back to deterministic response.")
            return None
